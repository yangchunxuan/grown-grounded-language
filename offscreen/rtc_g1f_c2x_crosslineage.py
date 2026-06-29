"""RTC G1F C2X — cross-lineage selection micro-probe (spec v-LOCKED, commit 3b39078).

Tests whether forcing survival to depend on decoding NON-kin (speaker_rule=cross_lineage_balanced),
on top of the C1 soft96 diversity regime, raises cross-founder MII above every non-language baseline.

Arms (all pop96, gens40, soft niching, same seeds/env/instrumentation):
  C2X_OPEN       cross-lineage + open      (treatment)
  C1_KIN_ONLY    kin + open                (the C2X-OFF baseline = C1 soft96 floor)
  C2X_COMMBLIND  cross-lineage + open, RANDOM selection fitness (subtract drift/common-attractor)
  C2X_RANDOM_TOK cross-lineage + scramble  (iid random tokens; content-free)
  C2X_SCRAMBLE   cross-lineage + permute   (permuted REAL message; content-vs-structure)
  C2X_MUTE       cross-lineage + mute      (no message)
  FROZEN_MIXED   frozen unrelated pop96    (architecture FLOOR; no evolution)
  LINEAGE_SHUFFLE diagnostic on C2X_OPEN matrices (NOT a subtracted baseline)
gate-0 paired (open/mute/scramble on the C2X_OPEN final pop) = content-load.

Env: RTC_G1F_FORMAL=1 (set below); C2X_SEEDS (default 8 = fallback tier: POSITIVE or INCONCLUSIVE only).
"""
from __future__ import annotations

import os
os.environ.setdefault("RTC_G1F_FORMAL", "1")
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
POP = int(os.environ.get("C2X_POP", "96"))
GENS = int(os.environ.get("C2X_GENS", "40"))
N = int(os.environ.get("C2X_SEEDS", "8"))
NEFF_MIN = 2.0
COEX_MIN_PER = 3
COEX_MIN_LIN = 2
SESOI = 0.04
OUT = ROOT / "offscreen" / "rtc_g1f_c2x_crosslineage_verdict.json"

# (name, speaker_rule, mode, commblind)
EVO_ARMS = [
    ("C2X_OPEN", "cross_lineage_balanced", "open", False),
    ("C1_KIN_ONLY", None, "open", False),
    ("C2X_COMMBLIND", "cross_lineage_balanced", "open", True),
    ("C2X_RANDOM_TOK", "cross_lineage_balanced", "scramble", False),
    ("C2X_SCRAMBLE", "cross_lineage_balanced", "permute", False),
    ("C2X_MUTE", "cross_lineage_balanced", "mute", False),
]


def cf_wf(matrix, lineages):
    n = len(lineages)
    cross, within = [], []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            (cross if lineages[i] != lineages[j] else within).append(matrix[i][j])
    return (float(np.mean(cross)) if cross else float("nan"),
            float(np.mean(within)) if within else float("nan"))


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


def is_coexist(comp):
    return sum(1 for v in comp.values() if v >= COEX_MIN_PER) >= COEX_MIN_LIN and neff(list(comp.values())) >= NEFF_MIN


def boot_ci(xs, reps=2000, seed=7):
    xs = [x for x in xs if x == x]
    if len(xs) < 2:
        return [float("nan"), float("nan")]
    r = np.random.default_rng(seed)
    a = np.asarray(xs, float)
    bs = [float(np.mean(r.choice(a, len(a), replace=True))) for _ in range(reps)]
    return [round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]


def mean_nan(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


def median_pairwise_l2(tables):
    if len(tables) < 2:
        return float("nan")
    ds = []
    for i in range(len(tables)):
        for j in range(i + 1, len(tables)):
            ds.append(float(np.linalg.norm(tables[i] - tables[j])))
    return float(np.median(ds))


def equivalence_test():
    g1f.G1F_POP = 8
    pop = g1f._initial_pop_for(123, ARM)
    loop = g1f._mii(pop, return_matrix=True)["matrix"]
    fast, _ = g1f._mii_matrix_fast(pop)
    assert loop == fast, "MII fast != loop"
    pop[0].speaker.table[0, :, :] = 1.0
    assert g1f._mii(pop, return_matrix=True)["matrix"] == g1f._mii_matrix_fast(pop)[0], "MII fast != loop on tie"
    # byte-stability: default speaker_rule=None reproduces the original episode alive on a fixed pop
    p2 = g1f._initial_pop_for(55, ARM)
    a1 = g1f._run_episode(777, p2, "open", ARM)["alive"]
    a2 = g1f._run_episode(777, p2, "open", ARM, speaker_rule=None)["alive"]
    assert a1 == a2, "speaker_rule=None not byte-stable"
    print("[equiv] MII fast==loop (incl tie) + speaker_rule=None byte-stable OK", flush=True)


def run_evo_arm(name, speaker_rule, mode, commblind, n_seeds):
    g1f.G1F_POP = POP
    g1f.G1F_GENS = GENS
    seeds_out = []
    for s in range(n_seeds):
        evo_rng = np.random.default_rng(s * 17 + len(ARM))
        cb_rng = np.random.default_rng(s * 131 + 7)
        pop = g1f._initial_pop_for(s * 11 + len(ARM), ARM)
        gens = []
        gen0_self, gen0_fit, gen0_tables = {}, {}, {}
        comp = Counter()
        coex_matrices = []
        for gen in range(GENS + 1):
            m, l = g1f._mii_matrix_fast(pop)
            cf, wf = cf_wf(m, l)
            ep = g1f._run_episode(s * 1000 + gen * 13 + len(ARM), pop, mode, ARM, speaker_rule=speaker_rule)
            fit = np.asarray(ep["fitness"], float)
            comp = living_by_lineage(pop, ep["alive_per_agent"])
            if gen == 0:
                gen0_self = {int(pop[i].lineage): round(m[i][i], 5) for i in range(len(pop))}
                gen0_fit = {int(pop[i].lineage): round(float(fit[i]), 3) for i in range(len(pop))}
                gen0_tables = {int(pop[i].lineage): pop[i].speaker.table.copy() for i in range(len(pop))}
            co = is_coexist(comp)
            if co and name == "C2X_OPEN":
                coex_matrices.append((m, l))
            gens.append({"gen": gen, "cf": round(cf, 5), "wf": round(wf, 5),
                         "neff": round(neff(list(comp.values())), 3), "n_lin": len(comp),
                         "coexist": co, "alive": round(ep["alive"], 4)})
            if gen < GENS:
                sel_fit = cb_rng.random(len(pop)) if commblind else ep["fitness"]
                pop = g1f._select_next_soft(s, gen, pop, sel_fit, evo_rng)
        # final living-lineage representative tables (lowest-index living agent per lineage)
        final_alive = g1f._run_episode(s * 1000 + GENS * 13 + len(ARM), pop, mode, ARM, speaker_rule=speaker_rule)["alive_per_agent"]
        rep = {}
        for i, a in enumerate(pop):
            if final_alive[i] and int(a.lineage) not in rep:
                rep[int(a.lineage)] = a.speaker.table
        l2_final = median_pairwise_l2(list(rep.values()))
        l2_gen0 = median_pairwise_l2(list(gen0_tables.values()))
        l2_ratio = (l2_final / l2_gen0) if (l2_gen0 and l2_gen0 == l2_gen0 and l2_final == l2_final) else float("nan")
        # gate-0 paired on final pop (content-load), via rng= hook + same speaker_rule
        gseed = s * 7919 + 13
        g0 = {md: round(float(g1f._run_episode(gseed, pop, md, ARM,
                      rng=np.random.default_rng(gseed), speaker_rule=speaker_rule)["alive"]), 4)
              for md in ("open", "mute", "scramble")}
        coex = [g for g in gens if g["coexist"]]
        rec = {"seed": s, "n_coexist_gens": len(coex),
               "cf_coex": round(mean_nan([g["cf"] for g in coex]), 5),
               "wf_coex": round(mean_nan([g["wf"] for g in coex]), 5),
               "final_neff": gens[-1]["neff"], "final_n_lin": gens[-1]["n_lin"],
               "mean_alive": round(mean_nan([g["alive"] for g in gens]), 4),
               "l2_ratio": round(l2_ratio, 4) if l2_ratio == l2_ratio else None,
               "gate0": g0, "gen0_self": gen0_self, "gen0_fit": gen0_fit,
               "final_share": {L: comp.get(L, 0) / max(1, sum(comp.values())) for L in gen0_self}}
        if name == "C2X_OPEN":
            # lineage-shuffle diagnostic on coexisting-gen matrices
            sh_rng = np.random.default_rng(s * 53 + 99)
            shs = []
            for (m, l) in coex_matrices:
                lab = list(l); sh_rng.shuffle(lab); shs.append(cf_wf(m, lab)[0])
            rec["shuffle_cf_coex"] = round(mean_nan(shs), 5)
        seeds_out.append(rec)
        print(f"[{name} s{s}] coex={len(coex):2d} cf={rec['cf_coex']} wf={rec['wf_coex']} "
              f"neff={gens[-1]['neff']} alive={rec['mean_alive']} l2r={rec['l2_ratio']} gate0={g0}", flush=True)
    return seeds_out


def run_floor(n_seeds):
    g1f.G1F_POP = POP
    cfs = []
    for s in range(n_seeds):
        fpop = g1f._initial_pop_for(s * 11 + len(FLOOR_ARM), FLOOR_ARM)
        m, l = g1f._mii_matrix_fast(fpop)
        cfs.append(cf_wf(m, l)[0])
    return cfs


def main():
    equivalence_test()
    print(f"\n=== C2X formal: pop={POP} gens={GENS} n={N} (n=8 => POSITIVE or INCONCLUSIVE only) ===", flush=True)
    floor_cf = run_floor(N)
    FLOOR = mean_nan(floor_cf)
    FLOOR_SESOI = float(np.std([x for x in floor_cf if x == x], ddof=1))
    print(f"[FLOOR] {FLOOR:.5f} seed-SD={FLOOR_SESOI:.5f} computed_before_CF=True", flush=True)

    arms = {}
    for (name, srule, mode, cb) in EVO_ARMS:
        print(f"\n----- arm {name} -----", flush=True)
        arms[name] = run_evo_arm(name, srule, mode, cb, N)

    def cf_by_seed(name):
        return {r["seed"]: r["cf_coex"] for r in arms[name]}
    open_cf = cf_by_seed("C2X_OPEN")
    base_arms = ["C1_KIN_ONLY", "C2X_COMMBLIND", "C2X_RANDOM_TOK", "C2X_SCRAMBLE"]
    base_cf = {n: cf_by_seed(n) for n in base_arms}
    # per-seed baseline_max = max over baseline arms + FLOOR
    margins = []
    for s in range(N):
        bmax = FLOOR
        for n in base_arms:
            v = base_cf[n].get(s)
            if v is not None and v == v:
                bmax = max(bmax, v)
        o = open_cf.get(s)
        if o is not None and o == o:
            margins.append(o - bmax)
    CF_OPEN = mean_nan([v for v in open_cf.values()])
    WF_OPEN = mean_nan([r["wf_coex"] for r in arms["C2X_OPEN"]])
    margin_mean = mean_nan(margins)
    margin_ci = boot_ci(margins)
    # gate-0 content-load on C2X_OPEN final pops
    g0o = [r["gate0"]["open"] for r in arms["C2X_OPEN"]]
    g0m = [r["gate0"]["mute"] for r in arms["C2X_OPEN"]]
    g0s = [r["gate0"]["scramble"] for r in arms["C2X_OPEN"]]
    open_mute_ci = boot_ci([o - m for o, m in zip(g0o, g0m)])
    open_scr_ci = boot_ci([o - x for o, x in zip(g0o, g0s)])
    # window gate on C2X_OPEN
    n_window = sum(1 for r in arms["C2X_OPEN"] if r["n_coexist_gens"] >= 2)
    window_ok = n_window >= max(2, int(round(0.5 * N)))
    # painted-collapse guards (C2X_OPEN)
    final_neffs = [r["final_neff"] for r in arms["C2X_OPEN"]]
    l2_ratios = [r["l2_ratio"] for r in arms["C2X_OPEN"] if r["l2_ratio"] is not None]
    neff_median = float(np.median(final_neffs)) if final_neffs else float("nan")
    neff_p25 = float(np.percentile(final_neffs, 25)) if final_neffs else float("nan")
    l2_ok = (mean_nan(l2_ratios) >= 0.5) if l2_ratios else False
    painted_ok = (neff_median >= 3.0 and neff_p25 >= 2.5 and l2_ok)

    cf_above = (margin_ci[0] > 0 and margin_mean >= SESOI)
    cf_quarter_wf = (WF_OPEN == WF_OPEN and WF_OPEN > 0 and CF_OPEN >= 0.25 * WF_OPEN)
    content_load = (open_mute_ci[0] > 0 and open_scr_ci[0] > 0)

    if not window_ok:
        verdict = "DESIGN_FAILURE_NO_WINDOW"
    elif not content_load:
        verdict = "C2X_CONTENT_FREE_SHORTCUT"
    elif cf_above and cf_quarter_wf and content_load:
        verdict = "C2X_CROSS_FOUNDER_CODE_COEVOLVES" if painted_ok else "C2X_PAINTED_COLLAPSE"
    elif N <= 8:
        verdict = "INCONCLUSIVE (n<=8 tier: not POSITIVE; cannot call a scoped negative — rerun n=16)"
    else:
        verdict = "C2X_PRIVATE_CODES_PERSIST"

    result = {
        "verdict": verdict, "spec": "STAGE_C2X_CROSSLINEAGE_SPEC.md (LOCKED, 3b39078)",
        "tier": f"n={N}" + (" (POSITIVE-or-INCONCLUSIVE only)" if N <= 8 else ""),
        "FLOOR": round(FLOOR, 5), "FLOOR_seed_SD": round(FLOOR_SESOI, 5), "SESOI": SESOI,
        "CF_OPEN": round(CF_OPEN, 5), "WF_OPEN": round(WF_OPEN, 5),
        "CF_over_WF": round(CF_OPEN / WF_OPEN, 4) if (WF_OPEN == WF_OPEN and WF_OPEN > 0) else None,
        "CF_margin_vs_baseline_max": round(margin_mean, 5), "CF_margin_CI": margin_ci,
        "window": f"{n_window}/{N}", "window_ok": window_ok,
        "content_load": {"open": round(mean_nan(g0o), 4), "mute": round(mean_nan(g0m), 4),
                         "scramble": round(mean_nan(g0s), 4), "open_minus_mute_CI": open_mute_ci,
                         "open_minus_scramble_CI": open_scr_ci, "passes": content_load},
        "painted_guards": {"neff_median": round(neff_median, 3), "neff_p25": round(neff_p25, 3),
                           "l2_ratio_mean": round(mean_nan(l2_ratios), 4) if l2_ratios else None,
                           "passes": painted_ok},
        "arm_CF": {n: round(mean_nan(list(cf_by_seed(n).values())), 5) for n in [a[0] for a in EVO_ARMS]},
        "arm_WF": {n: round(mean_nan([r["wf_coex"] for r in arms[n]]), 5) for n in [a[0] for a in EVO_ARMS]},
        "arm_mean_alive": {n: round(mean_nan([r["mean_alive"] for r in arms[n]]), 4) for n in [a[0] for a in EVO_ARMS]},
        "lineage_shuffle_cf": round(mean_nan([r.get("shuffle_cf_coex") for r in arms["C2X_OPEN"] if r.get("shuffle_cf_coex") is not None]), 5),
        "arms_full": arms,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\n" + "=" * 72, flush=True)
    print(f"VERDICT: {verdict}", flush=True)
    print(f"  CF_OPEN={CF_OPEN:.5f} WF_OPEN={WF_OPEN:.5f} CF/WF={result['CF_over_WF']}", flush=True)
    print(f"  CF_margin vs baseline_max = {margin_mean:.5f} CI={margin_ci} (SESOI {SESOI})", flush=True)
    print(f"  arm CF: {result['arm_CF']}", flush=True)
    print(f"  window {n_window}/{N} | content-load open-mute{open_mute_ci} open-scr{open_scr_ci} | shuffle_cf={result['lineage_shuffle_cf']}", flush=True)
    print(f"  painted guards: neff_med={neff_median:.2f} l2_ratio={result['painted_guards']['l2_ratio_mean']} pass={painted_ok}", flush=True)
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    main()
