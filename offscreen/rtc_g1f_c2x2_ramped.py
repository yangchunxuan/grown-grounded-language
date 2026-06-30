"""RTC G1F C2X2 — ramped/stationary mixed non-kin scaffold (spec LOCKED, commit f8fbc54).

After C2X cold-start forced-non-kin crashed viability (alive 0.27->0.045, convergence UNANSWERED), C2X2
keeps kin communication alive while turning on non-kin listening pressure, and asks: can survival
selection move the tied UnifiedIO tables toward a shared cross-founder code from a VIABLE start?

Two PRIMARY treatments (Codex ramp vs Gemini stationary, head-to-head, data settles it):
  C2X2_RAMP_OPEN    p_nonkin ramps 0 (gen0-11) -> 0.75 (gen37-47)
  C2X2_STAT025_OPEN p_nonkin = 0.25 fixed
Shared baselines (run once, reused for both): C1_KIN_ONLY, RAMP_COMMBLIND, RAMP_RANDOM_TOK,
  RAMP_SCRAMBLE, FROZEN_MIXED. Diagnostic: C2X_COLD100_OPEN (reproduces the C2X crash).
Routing = deterministic hash of (seed,gen,round,i,j) -> no RNG consumed -> evolution stream untouched.
Per treatment: 4-condition VIABILITY GUARD + NON-KIN-ONLY final eval (100% non-kin) + painted guards.

Env: RTC_G1F_FORMAL=1 (set below); C2X2_SEEDS (default 8 = POSITIVE-or-INCONCLUSIVE only);
     C2X2_POP/C2X2_GENS override for smoke.
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
POP = int(os.environ.get("C2X2_POP", "96"))
GENS = int(os.environ.get("C2X2_GENS", "48"))
N = int(os.environ.get("C2X2_SEEDS", "8"))
NEFF_MIN = 2.0
COEX_MIN_PER = 3
SESOI = 0.04
OUT = ROOT / "offscreen" / "rtc_g1f_c2x2_ramped_verdict.json"


def p_nonkin_ramp(gen):
    if gen <= 11:
        return 0.0
    if gen >= 37:
        return 0.75
    return 0.75 * (gen - 11) / (37 - 11)  # linear 12..36


def make_route(s, gen, p_nonkin, counters):
    """Deterministic-hash mixed routing; consumes NO rng. Returns (pop,i,j,gr)->speaker."""
    def route(pop, i, j, gr):
        frac = ((s * 2654435761 + gen * 40503 + gr * 12345 + i * 777 + j * 31) % 1000003) / 1000003.0
        if frac < p_nonkin:
            sp = g1f._speaker_for(pop, i, j, gr, ARM, "cross_lineage_balanced")
            if sp is None:
                counters["nonkin_empty"] += 1
                return g1f._speaker_for(pop, i, j, gr, ARM, None)
            counters["nonkin"] += 1
            counters["src"][int(sp.lineage)] += 1
            return sp
        counters["kin"] += 1
        return g1f._speaker_for(pop, i, j, gr, ARM, None)
    return route


# ---- helpers (self-contained) ----
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
    return float(1.0 / sum((c / tot) ** 2 for c in counts))


def living_by_lineage(pop, alive):
    c = Counter()
    for a, al in zip(pop, alive):
        if al:
            c[int(a.lineage)] += 1
    return c


def is_coexist(comp):
    return sum(1 for v in comp.values() if v >= COEX_MIN_PER) >= 2 and neff(list(comp.values())) >= NEFF_MIN


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


def med_l2(tables):
    if len(tables) < 2:
        return float("nan")
    ds = [float(np.linalg.norm(tables[i] - tables[j])) for i in range(len(tables)) for j in range(i + 1, len(tables))]
    return float(np.median(ds))


def equivalence_test():
    g1f.G1F_POP = 8
    pop = g1f._initial_pop_for(123, ARM)
    assert g1f._mii(pop, return_matrix=True)["matrix"] == g1f._mii_matrix_fast(pop)[0], "MII fast!=loop"
    # byte-stability: mixed route at p_nonkin=0 == kin-only (speaker_rule=None)
    p2 = g1f._initial_pop_for(55, ARM)
    z = make_route(55, 0, 0.0, {"kin": 0, "nonkin": 0, "nonkin_empty": 0, "src": Counter()})
    a_kin = g1f._run_episode(777, p2, "open", ARM, speaker_rule=None)["alive"]
    a_mix0 = g1f._run_episode(777, p2, "open", ARM, speaker_rule=z)["alive"]
    assert a_kin == a_mix0, f"mixed@p=0 not byte-identical to kin ({a_kin} vs {a_mix0})"
    print("[equiv] MII fast==loop + mixed@p_nonkin=0 == kin-only OK", flush=True)


def speaker_rule_for(route_kind, s, gen, counters):
    if route_kind == "kin":
        return None
    if route_kind == "cold100":
        return "cross_lineage_balanced"
    if route_kind == "ramp":
        return make_route(s, gen, p_nonkin_ramp(gen), counters)
    if route_kind == "stat025":
        return make_route(s, gen, 0.25, counters)
    raise ValueError(route_kind)


def paired_eval(pop, s, route_kind, gen_for_route):
    """open/mute/scramble alive on `pop` under the arm's routing (paired rng), for content-load/viability."""
    gseed = s * 7919 + 13
    out = {}
    cnt = {"kin": 0, "nonkin": 0, "nonkin_empty": 0, "src": Counter()}
    for md in ("open", "mute", "scramble"):
        sr = speaker_rule_for(route_kind, s, gen_for_route, cnt)
        out[md] = round(float(g1f._run_episode(gseed, pop, md, ARM,
                       rng=np.random.default_rng(gseed), speaker_rule=sr)["alive"]), 4)
    return out


def nonkin_only_eval(pop, s):
    """100% non-kin routing on the evolved pop: open must beat mute/scramble/permute (the clincher)."""
    gseed = s * 4673 + 5
    out = {}
    for md in ("open", "mute", "scramble", "permute"):
        out[md] = round(float(g1f._run_episode(gseed, pop, md, ARM,
                       rng=np.random.default_rng(gseed), speaker_rule="cross_lineage_balanced")["alive"]), 4)
    return out


def run_arm(name, route_kind, mode, commblind, n_seeds, full=False):
    """full=True -> also gate0/non-kin-eval/painted (for the 2 treatments)."""
    g1f.G1F_POP = POP
    g1f.G1F_GENS = GENS
    seeds = []
    for s in range(n_seeds):
        evo_rng = np.random.default_rng(s * 17 + len(ARM))
        cb_rng = np.random.default_rng(s * 131 + 7)
        counters = {"kin": 0, "nonkin": 0, "nonkin_empty": 0, "src": Counter()}
        pop = g1f._initial_pop_for(s * 11 + len(ARM), ARM)
        gens = []
        gen0_tables = {}
        comp = Counter()
        for gen in range(GENS + 1):
            m, l = g1f._mii_matrix_fast(pop)
            cf, wf = cf_wf(m, l)
            sr = speaker_rule_for(route_kind, s, gen, counters)
            ep = g1f._run_episode(s * 1000 + gen * 13 + len(ARM), pop, mode, ARM, speaker_rule=sr)
            comp = living_by_lineage(pop, ep["alive_per_agent"])
            if gen == 0:
                gen0_tables = {int(pop[i].lineage): pop[i].speaker.table.copy() for i in range(len(pop))}
            gens.append({"gen": gen, "cf": round(cf, 5), "wf": round(wf, 5),
                         "neff": round(neff(list(comp.values())), 3), "coexist": is_coexist(comp),
                         "alive": round(ep["alive"], 4)})
            if gen < GENS:
                sel_fit = cb_rng.random(len(pop)) if commblind else ep["fitness"]
                pop = g1f._select_next_soft(s, gen, pop, sel_fit, evo_rng)
        # final living representative tables
        fa = g1f._run_episode(s * 1000 + GENS * 13 + len(ARM), pop, mode, ARM,
                              speaker_rule=speaker_rule_for(route_kind, s, GENS, counters))["alive_per_agent"]
        rep = {}
        for i, a in enumerate(pop):
            if fa[i] and int(a.lineage) not in rep:
                rep[int(a.lineage)] = a.speaker.table
        l2r = med_l2(list(rep.values())) / med_l2(list(gen0_tables.values())) if med_l2(list(gen0_tables.values())) else float("nan")
        coex = [g for g in gens if g["coexist"]]
        src = counters["src"]
        rec = {"seed": s, "n_coexist_gens": len(coex),
               "cf_coex": round(mean_nan([g["cf"] for g in coex]), 5),
               "wf_coex": round(mean_nan([g["wf"] for g in coex]), 5),
               "mean_alive": round(mean_nan([g["alive"] for g in gens]), 4),
               "final_neff": gens[-1]["neff"], "l2_ratio": round(l2r, 4) if l2r == l2r else None,
               "src_neff": round(neff(list(src.values())), 3) if src else None,
               "src_maxshare": round(max(src.values()) / sum(src.values()), 3) if src else None,
               "fallback_nonkin_empty": counters["nonkin_empty"]}
        if full:
            rec["gate0"] = paired_eval(pop, s, route_kind, GENS)
            rec["nonkin_eval"] = nonkin_only_eval(pop, s)
        seeds.append(rec)
        print(f"[{name} s{s}] coex={len(coex):2d} cf={rec['cf_coex']} wf={rec['wf_coex']} "
              f"alive={rec['mean_alive']} neff={rec['final_neff']} l2r={rec['l2_ratio']}"
              + (f" gate0={rec.get('gate0')} nke={rec.get('nonkin_eval')}" if full else ""), flush=True)
    return seeds


def run_floor(n_seeds):
    g1f.G1F_POP = POP
    out = []
    for s in range(n_seeds):
        fpop = g1f._initial_pop_for(s * 11 + len(FLOOR_ARM), FLOOR_ARM)
        m, l = g1f._mii_matrix_fast(fpop)
        out.append(cf_wf(m, l)[0])
    return out


def classify(name, T, C1, COLD100, FLOOR, baseline_cf_by_seed, n_seeds):
    """T = treatment seed records (full). Returns (verdict, detail)."""
    by = {r["seed"]: r for r in T}
    c1a = {r["seed"]: r["mean_alive"] for r in C1}
    cold = {r["seed"]: r["mean_alive"] for r in COLD100}
    # viability guard
    alive = [by[s]["mean_alive"] for s in by]
    mean_alive = mean_nan(alive)
    c1_mean = mean_nan(list(c1a.values()))
    v_rel = mean_alive >= 0.5 * c1_mean
    v_abs = mean_alive >= 0.15
    v_cold = boot_ci([by[s]["mean_alive"] - cold.get(s, 0) for s in by])[0] > 0.05
    g0o = [by[s]["gate0"]["open"] for s in by]
    g0m = [by[s]["gate0"]["mute"] for s in by]
    g0s = [by[s]["gate0"]["scramble"] for s in by]
    v_msg = boot_ci([o - m for o, m in zip(g0o, g0m)])[0] > 0 and boot_ci([o - x for o, x in zip(g0o, g0s)])[0] > 0
    viability = v_rel and v_abs and v_cold and v_msg
    # window
    n_window = sum(1 for s in by if by[s]["n_coexist_gens"] >= 2)
    window_ok = n_window >= (6 if n_seeds == 8 else int(round(0.75 * n_seeds)))
    # CF margin vs shared baseline_max
    margins = []
    for s in by:
        bmax = FLOOR
        for arm_cf in baseline_cf_by_seed:
            v = arm_cf.get(s)
            if v is not None and v == v:
                bmax = max(bmax, v)
        if by[s]["cf_coex"] == by[s]["cf_coex"]:
            margins.append(by[s]["cf_coex"] - bmax)
    CF = mean_nan([by[s]["cf_coex"] for s in by])
    WF = mean_nan([by[s]["wf_coex"] for s in by])
    m_ci = boot_ci(margins)
    cf_above = m_ci[0] > 0 and mean_nan(margins) >= SESOI
    cf_quarter = (WF == WF and WF > 0 and CF >= 0.25 * WF)
    # non-kin-only eval
    no = [by[s]["nonkin_eval"]["open"] for s in by]
    nm = [by[s]["nonkin_eval"]["mute"] for s in by]
    ns = [by[s]["nonkin_eval"]["scramble"] for s in by]
    np_ = [by[s]["nonkin_eval"]["permute"] for s in by]
    nonkin_load = (boot_ci([a - b for a, b in zip(no, nm)])[0] > 0 and
                   boot_ci([a - b for a, b in zip(no, ns)])[0] > 0 and
                   boot_ci([a - b for a, b in zip(no, np_)])[0] > 0)
    # painted
    neffs = [by[s]["final_neff"] for s in by]
    l2s = [by[s]["l2_ratio"] for s in by if by[s]["l2_ratio"] is not None]
    srcsh = [by[s]["src_maxshare"] for s in by if by[s]["src_maxshare"] is not None]
    srcne = [by[s]["src_neff"] for s in by if by[s]["src_neff"] is not None]
    painted = (float(np.median(neffs)) >= 3.0 and float(np.percentile(neffs, 25)) >= 2.0
               and (not srcsh or max(srcsh) <= 0.40) and (not srcne or min(srcne) >= 2.5)
               and (not l2s or mean_nan(l2s) >= 0.5))
    detail = {"mean_alive": round(mean_alive, 4), "c1_mean_alive": round(c1_mean, 4),
              "viability": {"rel>=0.5xC1": v_rel, "abs>=0.15": v_abs, "beats_COLD100": v_cold,
                            "beats_mute_scramble": v_msg, "PASS": viability},
              "window": f"{n_window}/{n_seeds}", "window_ok": window_ok,
              "CF": round(CF, 5), "WF": round(WF, 5), "CF_over_WF": round(CF / WF, 4) if (WF == WF and WF > 0) else None,
              "CF_margin": round(mean_nan(margins), 5), "CF_margin_CI": m_ci, "cf_above": cf_above, "cf_quarter_wf": cf_quarter,
              "nonkin_eval_open": round(mean_nan(no), 4), "nonkin_eval_mute": round(mean_nan(nm), 4),
              "nonkin_eval_scramble": round(mean_nan(ns), 4), "nonkin_load_bearing": nonkin_load,
              "painted": {"neff_med": round(float(np.median(neffs)), 3), "src_maxshare": round(max(srcsh), 3) if srcsh else None,
                          "src_neff_min": round(min(srcne), 3) if srcne else None,
                          "l2_ratio_mean": round(mean_nan(l2s), 4) if l2s else None, "PASS": painted}}
    if not viability:
        v = "C2X2_DESIGN_FAILURE_VIABILITY_CRASH"
    elif not window_ok:
        v = "C2X2_DESIGN_FAILURE_NO_WINDOW"
    elif cf_above and cf_quarter and nonkin_load and painted:
        v = "C2X2_PUBLIC_CODE_EMERGES"
    elif cf_above and cf_quarter and nonkin_load and not painted:
        v = "C2X2_PAINTED_ALIGNMENT"
    elif not nonkin_load:
        v = "C2X2_CONTENT_FREE_SHORTCUT"
    elif n_seeds <= 8:
        v = "C2X2_INCONCLUSIVE_N8"
    else:
        v = "C2X2_PRIVATE_CODES_PERSIST"
    return v, detail


def main():
    equivalence_test()
    print(f"\n=== C2X2 pop={POP} gens={GENS} n={N} (n=8 => POSITIVE or INCONCLUSIVE only) ===", flush=True)
    floor_cf = run_floor(N)
    FLOOR = mean_nan(floor_cf)
    print(f"[FLOOR] {FLOOR:.5f} seed-SD={float(np.std([x for x in floor_cf if x==x], ddof=1)):.5f} computed_before_CF=True", flush=True)

    # shared baselines (run once)
    print("\n--- shared baselines ---", flush=True)
    C1 = run_arm("C1_KIN_ONLY", "kin", "open", False, N)
    COMMBLIND = run_arm("RAMP_COMMBLIND", "ramp", "open", True, N)
    RANDTOK = run_arm("RAMP_RANDOM_TOK", "ramp", "scramble", False, N)
    SCRAM = run_arm("RAMP_SCRAMBLE", "ramp", "permute", False, N)
    COLD100 = run_arm("C2X_COLD100_OPEN", "cold100", "open", False, N)
    base_cf = [{r["seed"]: r["cf_coex"] for r in arm} for arm in (C1, COMMBLIND, RANDTOK, SCRAM)]

    # treatments
    print("\n--- treatments ---", flush=True)
    RAMP = run_arm("C2X2_RAMP_OPEN", "ramp", "open", False, N, full=True)
    STAT = run_arm("C2X2_STAT025_OPEN", "stat025", "open", False, N, full=True)

    v_ramp, d_ramp = classify("RAMP", RAMP, C1, COLD100, FLOOR, base_cf, N)
    v_stat, d_stat = classify("STAT025", STAT, C1, COLD100, FLOOR, base_cf, N)

    result = {
        "spec": "STAGE_C2X2_RAMPED_MIXED_SPEC.md (LOCKED f8fbc54)",
        "tier": f"n={N}" + (" (POSITIVE-or-INCONCLUSIVE only)" if N <= 8 else ""),
        "FLOOR": round(FLOOR, 5), "SESOI": SESOI,
        "RAMP_verdict": v_ramp, "RAMP_detail": d_ramp,
        "STAT025_verdict": v_stat, "STAT025_detail": d_stat,
        "ramp_vs_stationary": {"ramp_CF": d_ramp["CF"], "stat_CF": d_stat["CF"],
                               "ramp_mean_alive": d_ramp["mean_alive"], "stat_mean_alive": d_stat["mean_alive"],
                               "ramp_nonkin_load": d_ramp["nonkin_load_bearing"], "stat_nonkin_load": d_stat["nonkin_load_bearing"]},
        "baseline_CF": {n: round(mean_nan([r["cf_coex"] for r in arm]), 5)
                        for n, arm in [("C1_KIN_ONLY", C1), ("RAMP_COMMBLIND", COMMBLIND),
                                       ("RAMP_RANDOM_TOK", RANDTOK), ("RAMP_SCRAMBLE", SCRAM), ("COLD100", COLD100)]},
        "baseline_mean_alive": {n: round(mean_nan([r["mean_alive"] for r in arm]), 4)
                                for n, arm in [("C1_KIN_ONLY", C1), ("COLD100", COLD100)]},
        "arms_full": {"C2X2_RAMP_OPEN": RAMP, "C2X2_STAT025_OPEN": STAT, "C1_KIN_ONLY": C1,
                      "RAMP_COMMBLIND": COMMBLIND, "RAMP_RANDOM_TOK": RANDTOK, "RAMP_SCRAMBLE": SCRAM,
                      "C2X_COLD100_OPEN": COLD100},
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\n" + "=" * 72, flush=True)
    print(f"RAMP   verdict: {v_ramp} | CF={d_ramp['CF']} CF-base CI={d_ramp['CF_margin_CI']} "
          f"alive={d_ramp['mean_alive']} (viab {d_ramp['viability']['PASS']}) nonkin_load={d_ramp['nonkin_load_bearing']}", flush=True)
    print(f"STAT025 verdict: {v_stat} | CF={d_stat['CF']} CF-base CI={d_stat['CF_margin_CI']} "
          f"alive={d_stat['mean_alive']} (viab {d_stat['viability']['PASS']}) nonkin_load={d_stat['nonkin_load_bearing']}", flush=True)
    print(f"baseline CF: {result['baseline_CF']}", flush=True)
    print(f"C1 alive={result['baseline_mean_alive']['C1_KIN_ONLY']} COLD100 alive={result['baseline_mean_alive']['COLD100']}", flush=True)
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    main()
