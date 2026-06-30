"""RTC G1F C2X3 — forced-diversity x cross-lineage pressure (spec v2.1 LOCKED, commit c91d822).

C2X2's "no public code" was a FALSE-NEGATIVE RISK (pressure & diversity never coincided; per-gen data not
saved). C2X3 fixes both: (1) STORE the per-gen trajectory; (2) a diversity QUOTA + constant 0.5 non-kin to
FORCE the overlap, isolating "does CF rise GIVEN maintained diversity?".

Arms (pop96, gens48, same config/seeds):
  C2X3_FORCED        quota(K=4,m=4) + 0.5 non-kin            (primary)
  C2X3_NOQUOTA       no quota       + 0.5 non-kin            (tension diagnostic)
  C2X3_QUOTA_KINONLY quota(K=4,m=4) + 0.0 non-kin (kin)      (quota-control: does quota hold N_eff w/o pressure?)
  C1_KIN_ONLY        no quota + kin                          (baseline ceiling)
  C3_COMMBLIND       quota + 0.5, RANDOM fitness             (baseline)
  C3_RANDOM_TOK      quota + 0.5, iid tokens                 (baseline)
  C3_SCRAMBLE        quota + 0.5, permuted-real              (baseline)
  FROZEN_MIXED       CF floor

Decision (FORCED): four INDEPENDENT checks (alive_viable / diversity_held / treatment_content_load /
CF_success) in an ordered tree; CONTENT_FREE judged in the FORCED arm; QUOTA_KINONLY de-confounds a
diversity-held failure. Deterministic-hash routing (no RNG). Env: RTC_G1F_FORMAL=1; C2X3_SEEDS (default 8).
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
POP = int(os.environ.get("C2X3_POP", "96"))
GENS = int(os.environ.get("C2X3_GENS", "48"))
N = int(os.environ.get("C2X3_SEEDS", "8"))
WORKERS = int(os.environ.get("C2X3_WORKERS", "1"))  # 1 = serial (byte-stable default); >1 = parallelize seeds
K_QUOTA = int(os.environ.get("C2X3_K", "4"))
M_QUOTA = int(os.environ.get("C2X3_M", "4"))
P_NONKIN = 0.5
NEFF_MIN = 2.0
COEX_MIN_PER = 3
SESOI = 0.04
OUT = ROOT / "offscreen" / "rtc_g1f_c2x3_forced_verdict.json"


def make_route(s, p_nonkin, counters):
    """Constant deterministic-hash mixed routing (no RNG). p_nonkin fixed across gens."""
    def route(pop, i, j, gr):
        frac = ((s * 2654435761 + 40503 + gr * 12345 + i * 777 + j * 31) % 1000003) / 1000003.0
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


# Shared metric/stats helpers are now canonical in rtc_g1f_common (de-duplicated). is_coexist there uses
# the same defaults (min_per=3, neff_min=2.0) as this runner's COEX_MIN_PER/NEFF_MIN -> byte-identical.
from offscreen.rtc_g1f_common import (  # noqa: E402
    cf_wf, neff, living_by_lineage, is_coexist, boot_ci, mean_nan, med_l2, make_provenance)


def equivalence_test():
    g1f.G1F_POP = 8
    pop = g1f._initial_pop_for(123, ARM)
    assert g1f._mii(pop, return_matrix=True)["matrix"] == g1f._mii_matrix_fast(pop)[0], "MII fast!=loop"
    # degenerate quota: K=0 must be byte-identical to _select_next_soft (Codex+Opus fix)
    p2 = g1f._initial_pop_for(55, ARM)
    f = np.random.default_rng(1).random(len(p2))
    a = g1f._select_next_soft(55, 3, p2, f, np.random.default_rng(99))
    b = g1f._select_next_quota(55, 3, p2, f, np.random.default_rng(99), K=0, m=0)
    assert [int(x.lineage) for x in a] == [int(x.lineage) for x in b], "quota K=0 != soft (lineages)"
    assert all(np.array_equal(x.speaker.table, y.speaker.table) for x, y in zip(a, b)), "quota K=0 != soft (tables)"
    # quota invariant: each protected lineage gets >= m (use K=2,m=2 — pop=8 fits 2x2 reserved + 4 tournament)
    p3 = g1f._initial_pop_for(7, ARM)
    for i in range(len(p3)):
        p3[i].lineage = i % 4  # 4 lineages of 2 each on pop=8
    src_counts = Counter(int(a.lineage) for a in p3)
    q = g1f._select_next_quota(7, 1, p3, np.random.default_rng(2).random(len(p3)), np.random.default_rng(3), K=2, m=2)
    qc = Counter(int(x.lineage) for x in q)
    top2 = sorted(src_counts, key=lambda L: (-src_counts[L], L))[:2]
    assert all(qc[L] >= 2 for L in top2), f"protected lineage <m offspring: {qc} top2={top2}"
    print("[equiv] MII fast==loop + quota(K=0)==soft + protected>=m OK", flush=True)


def speaker_rule_for(p_nonkin, s, counters):
    return None if p_nonkin == 0.0 else make_route(s, p_nonkin, counters)


def paired_eval(pop, gseed, p_nonkin, s):
    """open/mute/scramble alive under the arm's routing (paired rng) — content-load."""
    out = {}
    for md in ("open", "mute", "scramble"):
        c = {"kin": 0, "nonkin": 0, "nonkin_empty": 0, "src": Counter()}
        sr = speaker_rule_for(p_nonkin, s, c)
        out[md] = round(float(g1f._run_episode(gseed, pop, md, ARM, rng=np.random.default_rng(gseed), speaker_rule=sr)["alive"]), 4)
    return out


def nonkin_only_eval(pop, s):
    gseed = s * 4673 + 5
    return {md: round(float(g1f._run_episode(gseed, pop, md, ARM, rng=np.random.default_rng(gseed),
            speaker_rule="cross_lineage_balanced")["alive"]), 4) for md in ("open", "mute", "scramble")}


def _run_one_seed(name, use_quota, p_nonkin, mode, commblind, full, s):
    """Per-seed computation (module-level so it is picklable for multiprocessing). Identical math to the
    serial path — only the dispatch in run_arm changes. Sets the g1f globals (workers re-import on spawn)."""
    g1f.G1F_POP = POP
    g1f.G1F_GENS = GENS
    if True:
        evo_rng = np.random.default_rng(s * 17 + len(ARM))
        cb_rng = np.random.default_rng(s * 131 + 7)
        counters = {"kin": 0, "nonkin": 0, "nonkin_empty": 0, "src": Counter()}
        pop = g1f._initial_pop_for(s * 11 + len(ARM), ARM)
        traj = []
        gen0_tables = {}
        comp = Counter()
        for gen in range(GENS + 1):
            m, l = g1f._mii_matrix_fast(pop)
            cf, wf = cf_wf(m, l)
            sr = speaker_rule_for(p_nonkin, s, counters)
            ep = g1f._run_episode(s * 1000 + gen * 13 + len(ARM), pop, mode, ARM, speaker_rule=sr)
            comp = living_by_lineage(pop, ep["alive_per_agent"])
            if gen == 0:
                gen0_tables = {int(pop[i].lineage): pop[i].speaker.table.copy() for i in range(len(pop))}
            traj.append({"gen": gen, "p_nonkin": p_nonkin, "cf": round(cf, 5), "wf": round(wf, 5),
                         "neff": round(neff(list(comp.values())), 3), "n_lin": len(comp),
                         "coexist": is_coexist(comp), "alive": round(ep["alive"], 4)})
            if gen < GENS:
                sel_fit = cb_rng.random(len(pop)) if commblind else ep["fitness"]
                pop = (g1f._select_next_quota(s, gen, pop, sel_fit, evo_rng, K=K_QUOTA, m=M_QUOTA) if use_quota
                       else g1f._select_next_soft(s, gen, pop, sel_fit, evo_rng))
        fa = g1f._run_episode(s * 1000 + GENS * 13 + len(ARM), pop, mode, ARM,
                              speaker_rule=speaker_rule_for(p_nonkin, s, counters))["alive_per_agent"]
        rep = {}
        for i, a in enumerate(pop):
            if fa[i] and int(a.lineage) not in rep:
                rep[int(a.lineage)] = a.speaker.table
        l2r = med_l2(list(rep.values())) / med_l2(list(gen0_tables.values())) if med_l2(list(gen0_tables.values())) else float("nan")
        coex = [g for g in traj if g["coexist"]]
        hp_coex = [g for g in coex if g["p_nonkin"] >= 0.5]  # high-pressure AND coexisting
        src = counters["src"]
        rec = {"seed": s, "n_coexist_gens": len(coex),
               "cf_coex": round(mean_nan([g["cf"] for g in coex]), 5),
               "wf_coex": round(mean_nan([g["wf"] for g in coex]), 5),
               "cf_high_pressure_coex": round(mean_nan([g["cf"] for g in hp_coex]), 5),
               "mean_alive": round(mean_nan([g["alive"] for g in traj]), 4),
               "final_neff": traj[-1]["neff"],
               "last_coexist_gen": max([g["gen"] for g in coex], default=-1),
               "max_p_nonkin_during_coexist": round(max([g["p_nonkin"] for g in coex], default=0.0), 3),
               "l2_ratio": round(l2r, 4) if l2r == l2r else None,
               "src_neff": round(neff(list(src.values())), 3) if src else None,
               "src_maxshare": round(max(src.values()) / sum(src.values()), 3) if src else None,
               "fallback_nonkin_empty": counters["nonkin_empty"], "traj": traj}
        if full:
            rec["gate0"] = paired_eval(pop, s * 7919 + 13, p_nonkin, s)        # content-load in THIS arm's routing
            rec["nonkin_eval"] = nonkin_only_eval(pop, s)                       # corroborating
            rec["kin_eval"] = paired_eval(pop, s * 5101 + 3, 0.0, s)            # kin-content context
        return rec


def _run_one_seed_star(args):
    return _run_one_seed(*args)


def run_arm(name, use_quota, p_nonkin, mode, commblind, n_seeds, full=False):
    g1f.G1F_POP = POP
    g1f.G1F_GENS = GENS
    args = [(name, use_quota, p_nonkin, mode, commblind, full, s) for s in range(n_seeds)]
    if WORKERS > 1 and n_seeds > 1:
        import concurrent.futures as cf
        with cf.ProcessPoolExecutor(max_workers=min(WORKERS, n_seeds)) as ex:
            seeds = list(ex.map(_run_one_seed_star, args))  # map preserves input (seed) order -> deterministic
    else:
        seeds = [_run_one_seed(*a) for a in args]
    seeds.sort(key=lambda r: r["seed"])
    for rec in seeds:
        print(f"[{name} s{rec['seed']}] coex={rec['n_coexist_gens']:2d} cf={rec['cf_coex']} "
              f"cf_hp={rec['cf_high_pressure_coex']} wf={rec['wf_coex']} alive={rec['mean_alive']} "
              f"neff={rec['final_neff']} l2r={rec['l2_ratio']}", flush=True)
    return seeds


def run_floor(n_seeds):
    g1f.G1F_POP = POP
    out = []
    for s in range(n_seeds):
        m, l = g1f._mii_matrix_fast(g1f._initial_pop_for(s * 11 + len(FLOOR_ARM), FLOOR_ARM))
        out.append(cf_wf(m, l)[0])
    return out


def classify(FORCED, C1, QK, FLOOR, base_cf, n_seeds):
    by = {r["seed"]: r for r in FORCED}
    c1a = mean_nan([r["mean_alive"] for r in C1])
    alive = mean_nan([by[s]["mean_alive"] for s in by])
    alive_viable = (alive >= 0.5 * c1a) and (alive >= 0.15)  # COLD~0.045 < 0.15, so beats-cold is subsumed
    neffs = [by[s]["final_neff"] for s in by]
    overlap = sum(1 for s in by if by[s]["max_p_nonkin_during_coexist"] >= 0.5) >= max(2, int(round(0.75 * n_seeds)))
    diversity_held = (float(np.median(neffs)) >= 0.75 * K_QUOTA) and overlap
    qk_neff = float(np.median([r["final_neff"] for r in QK]))
    qk_held = qk_neff >= 0.75 * K_QUOTA
    # content-load in FORCED arm
    g0o = [by[s]["gate0"]["open"] for s in by]; g0m = [by[s]["gate0"]["mute"] for s in by]; g0s = [by[s]["gate0"]["scramble"] for s in by]
    content_load = boot_ci([o - mm for o, mm in zip(g0o, g0m)])[0] > 0 and boot_ci([o - x for o, x in zip(g0o, g0s)])[0] > 0
    kin_o = [by[s]["kin_eval"]["open"] for s in by]; kin_m = [by[s]["kin_eval"]["mute"] for s in by]
    kin_load = boot_ci([o - mm for o, mm in zip(kin_o, kin_m)])[0] > 0
    # CF
    margins = []
    for s in by:
        bmax = FLOOR
        for arm_cf in base_cf:
            v = arm_cf.get(s)
            if v is not None and v == v:
                bmax = max(bmax, v)
        if by[s]["cf_coex"] == by[s]["cf_coex"]:
            margins.append(by[s]["cf_coex"] - bmax)
    CF = mean_nan([by[s]["cf_coex"] for s in by]); WF = mean_nan([by[s]["wf_coex"] for s in by])
    m_ci = boot_ci(margins)
    cf_above = m_ci[0] > 0 and mean_nan(margins) >= SESOI
    cf_quarter = WF == WF and WF > 0 and CF >= 0.25 * WF
    cf_hp = mean_nan([by[s]["cf_high_pressure_coex"] for s in by])
    cf_gray = (not cf_above) and (CF > FLOOR + 0.25 * (SESOI)) and (cf_hp > FLOOR + 1e-4)
    # painted
    l2s = [by[s]["l2_ratio"] for s in by if by[s]["l2_ratio"] is not None]
    srcsh = [by[s]["src_maxshare"] for s in by if by[s]["src_maxshare"] is not None]
    srcne = [by[s]["src_neff"] for s in by if by[s]["src_neff"] is not None]
    painted = (float(np.median(neffs)) >= 3.0 and float(np.percentile(neffs, 25)) >= 2.0
               and (not srcsh or max(srcsh) <= 0.40) and (not srcne or min(srcne) >= 2.5)
               and (not l2s or mean_nan(l2s) >= 0.5))
    if not alive_viable:
        v = "C2X3_DESIGN_FAILURE_VIABILITY_CRASH"
    elif not diversity_held:
        v = "C2X3_PRESSURE_COLLAPSES_DIVERSITY" if qk_held else "C2X3_DESIGN_FAILURE_QUOTA"
    elif not content_load:
        v = "C2X3_CONTENT_FREE_UNDER_FORCED_ROUTING"
    elif cf_above and cf_quarter and painted:
        v = "C2X3_SCOPED_PUBLIC_CODE_GIVEN_FORCED_DIVERSITY"
    elif cf_above and cf_quarter and not painted:
        v = "C2X3_PAINTED_ALIGNMENT"
    elif cf_gray:
        v = "C2X3_INCONCLUSIVE_GRAY_CF"
    elif n_seeds <= 8:
        v = "C2X3_INCONCLUSIVE_N8"
    else:
        v = "C2X3_PRIVATE_CODES_PERSIST_UNDER_FORCED_DIVERSITY"
    return v, {"alive_viable": alive_viable, "mean_alive": round(alive, 4), "c1_alive": round(c1a, 4),
               "diversity_held": diversity_held, "final_neff_med": round(float(np.median(neffs)), 3),
               "overlap_seeds_ge0.5": overlap, "QUOTA_KINONLY_neff_med": round(qk_neff, 3), "qk_held": qk_held,
               "content_load": content_load, "kin_content_load": kin_load,
               "CF": round(CF, 5), "WF": round(WF, 5), "CF_margin": round(mean_nan(margins), 5), "CF_margin_CI": m_ci,
               "cf_above": cf_above, "cf_quarter_wf": cf_quarter, "cf_high_pressure_coex": round(cf_hp, 5),
               "cf_gray": cf_gray, "painted": painted}


def main():
    equivalence_test()
    print(f"\n=== C2X3 pop={POP} gens={GENS} n={N} K={K_QUOTA} m={M_QUOTA} (n=8 => POSITIVE/INCONCLUSIVE only) ===", flush=True)
    floor_cf = run_floor(N)
    FLOOR = mean_nan(floor_cf)
    print(f"[FLOOR] {FLOOR:.5f}", flush=True)
    print("\n--- baselines ---", flush=True)
    C1 = run_arm("C1_KIN_ONLY", False, 0.0, "open", False, N)
    CB = run_arm("C3_COMMBLIND", True, P_NONKIN, "open", True, N)
    RT = run_arm("C3_RANDOM_TOK", True, P_NONKIN, "scramble", False, N)
    SC = run_arm("C3_SCRAMBLE", True, P_NONKIN, "permute", False, N)
    QK = run_arm("C2X3_QUOTA_KINONLY", True, 0.0, "open", False, N)
    base_cf = [{r["seed"]: r["cf_coex"] for r in arm} for arm in (C1, CB, RT, SC)]
    print("\n--- treatments ---", flush=True)
    FORCED = run_arm("C2X3_FORCED", True, P_NONKIN, "open", False, N, full=True)
    NOQUOTA = run_arm("C2X3_NOQUOTA", False, P_NONKIN, "open", False, N, full=True)

    v_forced, d_forced = classify(FORCED, C1, QK, FLOOR, base_cf, N)
    v_noq, d_noq = classify(NOQUOTA, C1, QK, FLOOR, base_cf, N)

    result = {"spec": "STAGE_C2X3_FORCED_DIVERSITY_SPEC.md (LOCKED c91d822)",
              "provenance": make_provenance(
                  "C2X3",
                  "RTC_G1F_FORMAL=1 C2X3_POP=96 C2X3_GENS=48 C2X3_SEEDS=8 C2X3_K=4 C2X3_M=4 "
                  "C2X3_WORKERS=6 python -m offscreen.rtc_g1f_c2x3_forced",
                  ["RTC_G1F_FORMAL", "C2X3_POP", "C2X3_GENS", "C2X3_SEEDS", "C2X3_K", "C2X3_M", "C2X3_WORKERS"]),
              "tier": f"n={N}" + (" (POSITIVE-or-INCONCLUSIVE only)" if N <= 8 else ""),
              "FLOOR": round(FLOOR, 5), "SESOI": SESOI, "K": K_QUOTA, "m": M_QUOTA,
              "FORCED_verdict": v_forced, "FORCED_detail": d_forced,
              "NOQUOTA_verdict": v_noq, "NOQUOTA_detail": d_noq,
              "quota_vs_noquota": {"forced_neff_med": d_forced["final_neff_med"], "noquota_neff_med": d_noq["final_neff_med"],
                                   "quota_kinonly_neff_med": d_forced["QUOTA_KINONLY_neff_med"],
                                   "forced_CF": d_forced["CF"], "noquota_CF": d_noq["CF"]},
              "baseline_CF": {n: round(mean_nan([r["cf_coex"] for r in arm]), 5)
                              for n, arm in [("C1_KIN_ONLY", C1), ("C3_COMMBLIND", CB), ("C3_RANDOM_TOK", RT), ("C3_SCRAMBLE", SC)]},
              "arms_full": {"C2X3_FORCED": FORCED, "C2X3_NOQUOTA": NOQUOTA, "C2X3_QUOTA_KINONLY": QK,
                            "C1_KIN_ONLY": C1, "C3_COMMBLIND": CB, "C3_RANDOM_TOK": RT, "C3_SCRAMBLE": SC}}
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\n" + "=" * 72, flush=True)
    print(f"FORCED  : {v_forced}", flush=True)
    print(f"  alive_viable={d_forced['alive_viable']} (alive {d_forced['mean_alive']} vs C1 {d_forced['c1_alive']}) | "
          f"diversity_held={d_forced['diversity_held']} (neff_med {d_forced['final_neff_med']}, QK {d_forced['QUOTA_KINONLY_neff_med']}) | "
          f"content_load={d_forced['content_load']} (kin {d_forced['kin_content_load']})", flush=True)
    print(f"  CF={d_forced['CF']} WF={d_forced['WF']} margin={d_forced['CF_margin']}{d_forced['CF_margin_CI']} "
          f"cf_hp={d_forced['cf_high_pressure_coex']} painted={d_forced['painted']}", flush=True)
    print(f"NOQUOTA : {v_noq} (neff_med {d_noq['final_neff_med']}, CF {d_noq['CF']})", flush=True)
    print(f"quota_vs_noquota: {result['quota_vs_noquota']}", flush=True)
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    main()
