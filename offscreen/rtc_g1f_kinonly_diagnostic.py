"""RTC G1F KIN-ONLY DIAGNOSTIC — instrumented run (spec v4.1, LOCKED).

Question (narrowed, well-posed, C1-actionable): at generations where >=2 founder
lineages coexist, are non-kin lineages MUTUALLY INTELLIGIBLE (cross-founder MII
near the within-founder ceiling, above the architecture floor = COLLAPSE-LIMITED,
cause A) or diverged into PRIVATE CODES (cross-founder MII ~ floor, cause C)?

This runner REPLICATES the real shared_weights_kin g1f dynamics (same init / episode
/ evolution seed formulas as _run_arm) and only ADDS logging:
  - per gen, gen-start (pre-episode) MII MATRIX + per-agent .lineage  -> CF / WF
  - per gen, post-episode per-agent ALIVE                             -> coexistence gate
  - per gen, lineage-shuffle CF (separate RNG)                        -> metric-keys-on-lineage sanity
  - per seed, PAIRED gate-0 (open/mute/scramble, SAME world+rng)      -> content load-bearing (cause D)
  - FLOOR = shared_frozen_random cross-founder MII; SESOI = 1 seed-SD of FLOOR, computed BEFORE CF.

Instrument-only edits to rtc_g1f_coevolve.py: _run_episode(..., rng=None) + "alive_per_agent";
_mii(..., return_matrix=True) -> {"matrix","lineages"}. Existing g1f arms byte-identical.

Env: RTC_G1F_FORMAL=1 (required, set below), KINONLY_SEEDS (default 16).
"""
from __future__ import annotations

import os
os.environ.setdefault("RTC_G1F_FORMAL", "1")   # FORMAL required (POP16/GENS28/ROUNDS55/MII625)
os.environ.setdefault("RTC_TOXIC_DEATH", "-0.9")

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from offscreen import rtc_g1f_coevolve as g1f  # noqa: E402

ARM = "shared_weights_kin"
FLOOR_ARM = "shared_frozen_random"
N = int(os.environ.get("KINONLY_SEEDS", "16"))
COEX_MIN_PER = 3      # >=3 living agents per lineage
COEX_MIN_LIN = 2      # >=2 such lineages
WINDOW_MIN_SEEDS = 8  # <8/16 seeds with >=2 coexisting gens -> INCONCLUSIVE_NO_WINDOW
OUT = ROOT / "offscreen" / "rtc_g1f_kinonly_diagnostic_verdict.json"


# ---------- metrics ----------
def cf_wf(matrix, lineages):
    """cross-founder = off-diag, different lineage; within-founder = off-diag, same lineage."""
    n = len(lineages)
    cross, within = [], []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            (cross if lineages[i] != lineages[j] else within).append(matrix[i][j])
    cf = float(np.mean(cross)) if cross else float("nan")
    wf = float(np.mean(within)) if within else float("nan")
    return cf, wf


def neff(counts):
    tot = sum(counts)
    if tot == 0:
        return 0.0
    ps = [c / tot for c in counts]
    return float(1.0 / sum(p * p for p in ps))


def living_by_lineage(pop, alive):
    c = Counter()
    for a, al in zip(pop, alive):
        if al:
            c[int(a.lineage)] += 1
    return c


def is_coexist(c):
    return sum(1 for v in c.values() if v >= COEX_MIN_PER) >= COEX_MIN_LIN


def shuffle_cf(matrix, lineages, rng):
    lab = list(lineages)
    rng.shuffle(lab)
    return cf_wf(matrix, lab)[0]


def boot_ci(xs, reps=2000, seed=7):
    xs = [x for x in xs if x == x]  # drop NaN
    if len(xs) < 2:
        return [float("nan"), float("nan")]
    r = np.random.default_rng(seed)
    a = np.asarray(xs, float)
    bs = [float(np.mean(r.choice(a, len(a), replace=True))) for _ in range(reps)]
    return [round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]


def mean_nan(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


# ---------- FLOOR + SESOI (computed BEFORE any CF is read) ----------
floor_cf = []
for seed in range(N):
    fpop = g1f._initial_pop_for(seed * 11 + len(FLOOR_ARM), FLOOR_ARM)
    fm = g1f._mii(fpop, return_matrix=True)
    floor_cf.append(cf_wf(fm["matrix"], fm["lineages"])[0])
FLOOR = mean_nan(floor_cf)
SESOI = float(np.std([x for x in floor_cf if x == x], ddof=1))
FLOOR_CI = boot_ci(floor_cf)
print(f"[floor] FLOOR={FLOOR:.5f} CI={FLOOR_CI} SESOI(1SD)={SESOI:.5f}  computed_before_CF=True", flush=True)


# ---------- survival runs (instrumented; real shared_weights_kin dynamics) ----------
seeds_out = []
for seed in range(N):
    evo_rng = np.random.default_rng(seed * 17 + len(ARM))   # evolution RNG — matches _run_arm:254
    shuf_rng = np.random.default_rng(seed * 53 + 99)        # separate lineage-shuffle RNG
    pop = g1f._initial_pop_for(seed * 11 + len(ARM), ARM)   # matches _run_arm:255
    gens = []
    for gen in range(g1f.G1F_GENS + 1):
        mm = g1f._mii(pop, return_matrix=True)              # gen-start, pre-episode, full pop
        cf, wf = cf_wf(mm["matrix"], mm["lineages"])
        shuf = shuffle_cf(mm["matrix"], mm["lineages"], shuf_rng)
        ep = g1f._run_episode(seed * 1000 + gen * 13 + len(ARM), pop, "open", ARM)  # matches _run_arm:259
        comp = living_by_lineage(pop, ep["alive_per_agent"])  # post-episode LIVING (v4.1)
        gens.append({
            "gen": gen, "cf": round(cf, 5), "wf": round(wf, 5), "shuffle_cf": round(shuf, 5),
            "neff_living": round(neff(list(comp.values())), 3),
            "n_lineages_living": len(comp),
            "lineages_ge3": sum(1 for v in comp.values() if v >= COEX_MIN_PER),
            "coexist": is_coexist(comp), "survival": round(ep["alive"], 4),
        })
        if gen < g1f.G1F_GENS:
            pop = g1f._select_next(seed, gen, pop, ep["fitness"], ARM, evo_rng)
    # gate-0 PAIRED on the final evolved pop (channel exists here); SAME world seed + SAME rng across modes
    gseed = seed * 7919 + 13
    g0 = {m: round(float(g1f._run_episode(gseed, pop, m, ARM,
                    rng=np.random.default_rng(gseed))["alive"]), 4)
          for m in ("open", "mute", "scramble")}
    coex_gens = [g for g in gens if g["coexist"]]
    seeds_out.append({
        "seed": seed, "floor_cf": round(floor_cf[seed], 5), "gate0": g0,
        "n_coexist_gens": len(coex_gens),
        "cf_coex_mean": round(mean_nan([g["cf"] for g in coex_gens]), 5),
        "wf_coex_mean": round(mean_nan([g["wf"] for g in coex_gens]), 5),
        "shuffle_coex_mean": round(mean_nan([g["shuffle_cf"] for g in coex_gens]), 5),
        "cf_peak": round(max([g["cf"] for g in coex_gens], default=float("nan")), 5),
        "cf_final_coex": round(coex_gens[-1]["cf"], 5) if coex_gens else float("nan"),
        "gens": gens,
    })
    print(f"[seed {seed:2d}] coexist_gens={len(coex_gens):2d} "
          f"cf_coex={seeds_out[-1]['cf_coex_mean']} wf_coex={seeds_out[-1]['wf_coex_mean']} "
          f"gate0={g0}", flush=True)


# ---------- aggregation over coexisting gens ----------
seeds_with_window = [s for s in seeds_out if s["n_coexist_gens"] >= 2]
n_window = len(seeds_with_window)

cf_per_seed = [s["cf_coex_mean"] for s in seeds_with_window]
wf_per_seed = [s["wf_coex_mean"] for s in seeds_with_window]
shuf_per_seed = [s["shuffle_coex_mean"] for s in seeds_with_window]
peak_per_seed = [s["cf_peak"] for s in seeds_with_window]
final_per_seed = [s["cf_final_coex"] for s in seeds_with_window]

CF = mean_nan(cf_per_seed)
WF = mean_nan(wf_per_seed)
SHUF = mean_nan(shuf_per_seed)
CF_CI = boot_ci(cf_per_seed)
WF_CI = boot_ci(wf_per_seed)
margin_seed = [c - f for c, f in zip(cf_per_seed, [s["floor_cf"] for s in seeds_with_window]) if c == c]
MARGIN = mean_nan(margin_seed)
MARGIN_CI = boot_ci(margin_seed)

# gate-0 across ALL seeds (final pops)
g0_open = [s["gate0"]["open"] for s in seeds_out]
g0_mute = [s["gate0"]["mute"] for s in seeds_out]
g0_scram = [s["gate0"]["scramble"] for s in seeds_out]
open_ci, mute_ci, scram_ci = boot_ci(g0_open), boot_ci(g0_mute), boot_ci(g0_scram)
open_minus_mute = boot_ci([o - m for o, m in zip(g0_open, g0_mute)])
open_minus_scram = boot_ci([o - s for o, s in zip(g0_open, g0_scram)])

# decline check: final-coexist CF < 0.5 * peak (per seed), fraction
declines = [(f < 0.5 * p) for f, p in zip(final_per_seed, peak_per_seed) if f == f and p == p and p > 0]
frac_decline = float(np.mean(declines)) if declines else float("nan")

# per-seed classification (for the >=12/16 agreement rule)
def classify_seed(cf_s, wf_s, floor_s):
    if cf_s != cf_s:
        return "nan"
    if cf_s >= FLOOR + SESOI and (wf_s == wf_s and wf_s > 0 and cf_s >= 0.5 * wf_s):
        return "A"
    if cf_s < FLOOR + SESOI:
        return "C"
    return "PARTIAL"

per_seed_class = [classify_seed(s["cf_coex_mean"], s["wf_coex_mean"], s["floor_cf"]) for s in seeds_with_window]
class_counts = dict(Counter(per_seed_class))


# ---------- pre-registered decision rule (spec v4.1 §4) ----------
def decide():
    # Gate-0 (cause D): open <= mute OR open CI overlaps scramble CI -> irrelevance
    if mean_nan(g0_open) <= mean_nan(g0_mute) or open_minus_scram[0] <= 0:
        return "FITNESS_IRRELEVANCE_WARNING", "gate-0: message content not load-bearing (open<=mute or open~scramble)"
    if n_window < WINDOW_MIN_SEEDS:
        return "INCONCLUSIVE_NO_WINDOW", f"only {n_window}/{N} seeds have >=2 coexisting gens (<{WINDOW_MIN_SEEDS})"
    near_wf = (WF == WF and WF > 0 and CF >= 0.5 * WF)
    cf_above_floor = (MARGIN_CI[0] > 0 and MARGIN >= SESOI)
    declines_ok = (frac_decline == frac_decline and frac_decline >= 0.5)
    if cf_above_floor and near_wf and declines_ok:
        v = "COLLAPSE_LIMITED_INTELLIGIBILITY_A"
        note = "CF excludes floor by >=SESOI, CF>=0.5*WF, declines with collapse -> C1 (maintain diversity)"
    elif (MARGIN_CI[0] <= 0 or MARGIN < SESOI) and (WF == WF and WF > FLOOR + SESOI):
        v = "PRIVATE_CODES_C"
        note = "CF at architecture floor while WF>>floor -> lineages diverged; shared grounding needed"
    elif cf_above_floor and (WF == WF and CF < 0.5 * WF):
        v = "PARTIAL_INTELLIGIBILITY"
        note = "CF above floor+SESOI but below 0.5*WF -> partial; lean C for intervention scoping (conservative)"
    else:
        v = "PARTIAL_INTELLIGIBILITY"
        note = "mixed signal; conservative partial"
    # per-seed agreement override: non-conservative call needs >=12/16 agreement
    top = max(class_counts, key=class_counts.get) if class_counts else "nan"
    if class_counts.get(top, 0) < 12 and v == "COLLAPSE_LIMITED_INTELLIGIBILITY_A":
        note += f" | per-seed agreement {class_counts} <12/16 -> conservative: report A but flag split"
    return v, note


verdict, rationale = decide()

result = {
    "verdict": verdict,
    "rationale": rationale,
    "spec": "STAGE_KINONLY_DIAGNOSTIC_SPEC.md v4.1 (LOCKED, commit 67ce59b)",
    "arm": ARM, "floor_arm": FLOOR_ARM, "formal": True,
    "n_seeds": N, "n_seeds_with_window": n_window,
    "coexistence_def": f">=2 lineages each >=3 LIVING (post-episode); window=>=2 coexisting gens; INCONCLUSIVE if <{WINDOW_MIN_SEEDS}/{N}",
    "FLOOR": round(FLOOR, 5), "FLOOR_CI": FLOOR_CI,
    "SESOI": round(SESOI, 5), "SESOI_def": "1 seed-SD of FLOOR (frozen-mixed)", "computed_before_CF": True,
    "CF": round(CF, 5), "CF_CI": CF_CI,
    "WF": round(WF, 5), "WF_CI": WF_CI,
    "SHUFFLE_CF": round(SHUF, 5),
    "CF_minus_FLOOR": round(MARGIN, 5), "CF_minus_FLOOR_CI": MARGIN_CI,
    "CF_over_WF_ratio": round(CF / WF, 4) if (WF == WF and WF > 0) else float("nan"),
    "frac_seeds_CF_declines_with_collapse": round(frac_decline, 4) if frac_decline == frac_decline else None,
    "per_seed_class_counts": class_counts,
    "gate0": {
        "open_mean": round(mean_nan(g0_open), 4), "open_CI": open_ci,
        "mute_mean": round(mean_nan(g0_mute), 4), "mute_CI": mute_ci,
        "scramble_mean": round(mean_nan(g0_scram), 4), "scramble_CI": scram_ci,
        "open_minus_mute_CI": open_minus_mute, "open_minus_scramble_CI": open_minus_scram,
    },
    "rng_streams": {
        "evolution": "default_rng(seed*17+len(arm))  [matches _run_arm]",
        "lineage_shuffle": "default_rng(seed*53+99)  [snapshot-local, separate]",
        "gate0_paired": "default_rng(seed*7919+13)  [SAME across open/mute/scramble -> fixes :169 + :269 drift]",
        "mii": "default_rng(12345)  [fixed, offline]",
    },
    "seeds": seeds_out,
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("\n" + "=" * 70, flush=True)
print(f"VERDICT: {verdict}", flush=True)
print(f"  {rationale}", flush=True)
print(f"  CF={CF:.5f} CI={CF_CI} | WF={WF:.5f} | FLOOR={FLOOR:.5f} SESOI={SESOI:.5f}", flush=True)
print(f"  CF-FLOOR={MARGIN:.5f} CI={MARGIN_CI} | CF/WF={result['CF_over_WF_ratio']} | windows={n_window}/{N}", flush=True)
print(f"  gate0 open={result['gate0']['open_mean']} mute={result['gate0']['mute_mean']} scramble={result['gate0']['scramble_mean']}", flush=True)
print(f"  per-seed class {class_counts}", flush=True)
print(f"WROTE {OUT}", flush=True)
