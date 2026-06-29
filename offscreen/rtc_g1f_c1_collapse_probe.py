"""RTC G1F C1 COLLAPSE PROBE — intervention + collapse-cause diagnosis (spec v5.1, LOCKED).

ONE run answers three things (Path B): (1) does C1 open coexistence windows? (2) if so, A
(collapse-limited) or C (private codes)? (3) which collapse mechanism dominates?

2x2 factorial {hard, soft} x {pop 16, 96}, ALL same config/seeds/instrumentation:
  hard16 = baseline g1f collapsing regime; hard96 isolates POP/DRIFT; soft16 isolates SELECTION/NICHING
  at small pop; soft96 = full C1.  soft = tournament-k2 on lineage-shared fitness (divisor = GEN-START
  same-lineage count). DUAL coexistence gate: >=2 lineages each >=3 LIVING agents AND inverse-Simpson
  N_eff >= 2.0 (pop-normalized; de-confounds scale). Full vectorized pop x pop MII (no subsample) with a
  numpy-equivalence test (incl. deliberate tie) at startup. gate-0 paired (NOT the _run_arm mode seed).

Env: RTC_G1F_FORMAL=1 (set below); C1_SEEDS16 (default 16), C1_SEEDS96 (default 8).
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
N16 = int(os.environ.get("C1_SEEDS16", "16"))
N96 = int(os.environ.get("C1_SEEDS96", "8"))
COEX_MIN_PER = 3
COEX_MIN_LIN = 2
NEFF_MIN = 2.0
WINDOW_MIN_FRAC = 0.5  # >= 50% of a cell's seeds need >=2 dual-gated coexisting gens
OUT = ROOT / "offscreen" / "rtc_g1f_c1_collapse_probe_verdict.json"

# (name, selection, pop, n_seeds)
CELLS = [("hard16", "hard", 16, N16), ("hard96", "hard", 96, N96),
         ("soft16", "soft", 16, N16), ("soft96", "soft", 96, N96)]


# ---------- metrics ----------
def cf_wf(matrix, lineages):
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


def is_coexist(comp):
    """DUAL gate: >=2 lineages each >=3 living AND N_eff >= 2.0 (pop-normalized)."""
    ge3 = sum(1 for v in comp.values() if v >= COEX_MIN_PER)
    return ge3 >= COEX_MIN_LIN and neff(list(comp.values())) >= NEFF_MIN


def shuffle_cf(matrix, lineages, rng):
    lab = list(lineages)
    rng.shuffle(lab)
    return cf_wf(matrix, lab)[0]


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


def _rankdata(a):
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), float)
    ranks[order] = np.arange(1, len(a) + 1)
    # average ties
    _, inv, cnt = np.unique(a, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt))
    np.add.at(sums, inv, ranks)
    avg = sums / cnt
    return avg[inv]


def spearman(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 3:
        return float("nan")
    rx, ry = _rankdata(x[ok]), _rankdata(y[ok])
    if np.std(rx) == 0 or np.std(ry) == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


# ---------- startup: vectorized MII equivalence test (incl. deliberate tie) ----------
def equivalence_test():
    g1f.G1F_POP = 8
    pop = g1f._initial_pop_for(123, ARM)
    loop = g1f._mii(pop, return_matrix=True)["matrix"]
    fast, _ = g1f._mii_matrix_fast(pop)
    d = float(np.max(np.abs(np.asarray(loop) - np.asarray(fast))))
    assert loop == fast, f"MII fast != loop (max abs diff {d})"
    # deliberate tie: flat table slice -> argmax ties to lowest index in BOTH paths
    pop[0].speaker.table[0, :, :] = 1.0
    pop[3].speaker.table[2, :, :] = -0.5
    loop2 = g1f._mii(pop, return_matrix=True)["matrix"]
    fast2, _ = g1f._mii_matrix_fast(pop)
    assert loop2 == fast2, "MII fast != loop on deliberate-tie case"
    print("[equiv] _mii_matrix_fast == _mii (incl. deliberate tie) OK", flush=True)


# ---------- one cell ----------
def run_cell(name, selection, pop_size, n_seeds):
    g1f.G1F_POP = pop_size
    # FLOOR (frozen-mixed at this pop) -> SESOI, computed BEFORE CF
    floor_cf = []
    for s in range(n_seeds):
        fpop = g1f._initial_pop_for(s * 11 + len(FLOOR_ARM), FLOOR_ARM)
        m, l = g1f._mii_matrix_fast(fpop)
        floor_cf.append(cf_wf(m, l)[0])
    FLOOR = mean_nan(floor_cf)
    SESOI = float(np.std([x for x in floor_cf if x == x], ddof=1)) if len([x for x in floor_cf if x == x]) > 1 else float("nan")

    seeds_out = []
    for s in range(n_seeds):
        evo_rng = np.random.default_rng(s * 17 + len(ARM))
        shuf_rng = np.random.default_rng(s * 53 + 99)
        pop = g1f._initial_pop_for(s * 11 + len(ARM), ARM)
        gens = []
        gen0_self, gen0_fit = {}, {}
        comp = Counter()
        for gen in range(g1f.G1F_GENS + 1):
            m, l = g1f._mii_matrix_fast(pop)
            cf, wf = cf_wf(m, l)
            shuf = shuffle_cf(m, l, shuf_rng)
            ep = g1f._run_episode(s * 1000 + gen * 13 + len(ARM), pop, "open", ARM)
            fit = np.asarray(ep["fitness"], float)
            comp = living_by_lineage(pop, ep["alive_per_agent"])
            # I1: per-lineage mean raw fitness (gen-start grouping) + living count
            lin_fit, lin_all = {}, {}
            for i, a in enumerate(pop):
                lin_all.setdefault(int(a.lineage), []).append(fit[i])
            lin_fit = {L: round(float(np.mean(v)), 2) for L, v in lin_all.items()}
            if gen == 0:  # I2: per-founder gen-0 self-MII (diagonal) + init fitness (1 agent/founder)
                gen0_self = {int(pop[i].lineage): round(m[i][i], 5) for i in range(len(pop))}
                gen0_fit = {int(pop[i].lineage): round(float(fit[i]), 3) for i in range(len(pop))}
            tot = max(1, sum(comp.values()))
            gens.append({
                "gen": gen, "cf": round(cf, 5), "wf": round(wf, 5), "shuffle_cf": round(shuf, 5),
                "neff_living": round(neff(list(comp.values())), 3),
                "n_lineages_living": len(comp),
                "max_share": round(max(comp.values()) / tot, 3) if comp else 0.0,
                "coexist": is_coexist(comp),
                "lin_living": dict(comp), "lin_fit_mean": lin_fit,
            })
            if gen < g1f.G1F_GENS:
                pop = (g1f._select_next(s, gen, pop, ep["fitness"], ARM, evo_rng) if selection == "hard"
                       else g1f._select_next_soft(s, gen, pop, ep["fitness"], evo_rng))
        # final composition = last gen's comp
        final_tot = max(1, sum(comp.values()))
        final_share = {L: comp.get(L, 0) / final_tot for L in gen0_self}
        # gate-0 PAIRED on final pop (NOT _run_arm mode-name seed)
        gseed = s * 7919 + 13
        g0 = {mode: round(float(g1f._run_episode(gseed, pop, mode, ARM,
                       rng=np.random.default_rng(gseed))["alive"]), 4)
              for mode in ("open", "mute", "scramble")}
        coex = [g for g in gens if g["coexist"]]
        # winner trajectory (lucky-start vs WTA): the final dominant lineage's fitness/share over gens
        winner = max(final_share, key=final_share.get) if final_share else None
        win_traj = [{"gen": g["gen"], "fit": g["lin_fit_mean"].get(winner), "living": g["lin_living"].get(winner, 0)}
                    for g in gens] if winner is not None else []
        seeds_out.append({
            "seed": s, "floor_cf": round(floor_cf[s], 5), "gate0": g0,
            "n_coexist_gens": len(coex),
            "cf_coex_mean": round(mean_nan([g["cf"] for g in coex]), 5),
            "wf_coex_mean": round(mean_nan([g["wf"] for g in coex]), 5),
            "shuffle_coex_mean": round(mean_nan([g["shuffle_cf"] for g in coex]), 5),
            "final_neff": gens[-1]["neff_living"], "final_max_share": gens[-1]["max_share"],
            "winner_lineage": winner,
            "gen0_self": gen0_self, "gen0_fit": gen0_fit, "final_share": {k: round(v, 3) for k, v in final_share.items()},
            "winner_traj": win_traj, "gens": gens,
        })
        print(f"[{name} seed {s:2d}] coex={len(coex):2d} cf={seeds_out[-1]['cf_coex_mean']} "
              f"wf={seeds_out[-1]['wf_coex_mean']} final_neff={gens[-1]['neff_living']} "
              f"max_share={gens[-1]['max_share']} gate0={g0}", flush=True)

    # ---- cell aggregate ----
    win = [s for s in seeds_out if s["n_coexist_gens"] >= 2]
    n_window = len(win)
    cf_ps = [s["cf_coex_mean"] for s in win]
    wf_ps = [s["wf_coex_mean"] for s in win]
    margin = [c - f for c, f in zip(cf_ps, [s["floor_cf"] for s in win]) if c == c]
    CF, WF = mean_nan(cf_ps), mean_nan(wf_ps)
    # I2 correlations across founders (pooled over seeds)
    sm_self_x, sm_self_y, sm_fit_x = [], [], []
    for s in seeds_out:
        for L in s["gen0_self"]:
            sm_self_x.append(s["gen0_self"][L]); sm_self_y.append(s["final_share"].get(L, 0.0))
            sm_fit_x.append(s["gen0_fit"][L])
    g0o = [s["gate0"]["open"] for s in seeds_out]
    g0m = [s["gate0"]["mute"] for s in seeds_out]
    g0s = [s["gate0"]["scramble"] for s in seeds_out]
    return {
        "name": name, "selection": selection, "pop": pop_size, "n_seeds": n_seeds,
        "FLOOR": round(FLOOR, 5), "SESOI": round(SESOI, 5) if SESOI == SESOI else None,
        "computed_before_CF": True,
        "n_seeds_with_window": n_window,
        "opens_windows": n_window >= max(2, int(round(WINDOW_MIN_FRAC * n_seeds))),
        "CF": round(CF, 5), "CF_CI": boot_ci(cf_ps), "WF": round(WF, 5),
        "CF_minus_FLOOR": round(mean_nan(margin), 5), "CF_minus_FLOOR_CI": boot_ci(margin),
        "CF_over_WF": round(CF / WF, 4) if (WF == WF and WF > 0) else None,
        "mean_final_neff": round(mean_nan([s["final_neff"] for s in seeds_out]), 3),
        "mean_final_max_share": round(mean_nan([s["final_max_share"] for s in seeds_out]), 3),
        "I2_spearman_self_vs_finalshare": round(spearman(sm_self_x, sm_self_y), 4),
        "I2_spearman_initfit_vs_finalshare": round(spearman(sm_fit_x, sm_self_y), 4),
        "gate0": {"open": round(mean_nan(g0o), 4), "mute": round(mean_nan(g0m), 4),
                  "scramble": round(mean_nan(g0s), 4),
                  "open_minus_mute_CI": boot_ci([o - m for o, m in zip(g0o, g0m)]),
                  "open_minus_scramble_CI": boot_ci([o - x for o, x in zip(g0o, g0s)])},
        "seeds": seeds_out,
    }


def classify_AC(cell):
    if not cell["opens_windows"]:
        return "no_window"
    lo = cell["CF_minus_FLOOR_CI"][0]
    cf, wf, sesoi = cell["CF"], cell["WF"], None
    above = (lo == lo and lo > 0 and cell["CF_minus_FLOOR"] >= (cell["SESOI"] or 0))
    near_wf = (wf == wf and wf > 0 and cf >= 0.5 * wf)
    if above and near_wf:
        return "A_collapse_limited"
    if (not above) and wf == wf and wf > cell["FLOOR"]:
        return "C_private_codes"
    return "PARTIAL"


def main():
    equivalence_test()
    cells = {}
    for name, sel, pop, ns in CELLS:
        print(f"\n===== CELL {name} (selection={sel}, pop={pop}, n={ns}) =====", flush=True)
        cells[name] = run_cell(name, sel, pop, ns)

    # collapse-mechanism decomposition (judged on N_eff-gated windows)
    def opened(c):
        return cells[c]["opens_windows"]
    decomposition = {
        "hard16_windows": cells["hard16"]["n_seeds_with_window"],
        "hard96_windows": cells["hard96"]["n_seeds_with_window"],
        "soft16_windows": cells["soft16"]["n_seeds_with_window"],
        "soft96_windows": cells["soft96"]["n_seeds_with_window"],
        "hard16_final_neff": cells["hard16"]["mean_final_neff"],
        "hard96_final_neff": cells["hard96"]["mean_final_neff"],
        "soft96_final_neff": cells["soft96"]["mean_final_neff"],
        "pop_effect (hard16->hard96)": opened("hard96") and not opened("hard16"),
        "selection_effect (hard96->soft96)": opened("soft96") and not opened("hard96"),
        "selection_at_small_pop (hard16->soft16)": opened("soft16") and not opened("hard16"),
    }
    ac = {name: classify_AC(cells[name]) for name in cells}

    # outcome label
    if opened("soft96") or opened("hard96") or opened("soft16"):
        a_cells = [n for n in cells if ac[n].startswith("A_")]
        c_cells = [n for n in cells if ac[n].startswith("C_")]
        if a_cells:
            label = "C1_OPENS_WINDOW_A"
        elif c_cells:
            label = "C1_OPENS_WINDOW_C"
        else:
            label = "C1_OPENS_WINDOW_PARTIAL"
        if decomposition["pop_effect (hard16->hard96)"]:
            label += " | mechanism=POP_DRIFT"
        elif decomposition["selection_effect (hard96->soft96)"] or decomposition["selection_at_small_pop (hard16->soft16)"]:
            label += " | mechanism=SELECTION_NICHING"
    else:
        # no cell opened windows -> deeper cause, adjudicate by I2 across cells
        self_r = mean_nan([cells[n]["I2_spearman_self_vs_finalshare"] for n in cells])
        fit_r = mean_nan([cells[n]["I2_spearman_initfit_vs_finalshare"] for n in cells])
        if (self_r == self_r and self_r > 0.3) or (fit_r == fit_r and fit_r > 0.3):
            label = "NO_WINDOW_DEEPER_LUCKY"
        else:
            label = "NO_WINDOW_DEEPER_WTA_or_KIN"

    result = {
        "verdict": label,
        "spec": "STAGE_C1_COLLAPSE_PROBE_SPEC.md v5.1 (LOCKED)",
        "cells_summary": {n: {k: cells[n][k] for k in (
            "selection", "pop", "n_seeds", "opens_windows", "n_seeds_with_window",
            "FLOOR", "SESOI", "CF", "CF_CI", "WF", "CF_minus_FLOOR", "CF_minus_FLOOR_CI",
            "CF_over_WF", "mean_final_neff", "mean_final_max_share",
            "I2_spearman_self_vs_finalshare", "I2_spearman_initfit_vs_finalshare", "gate0")}
            for n in cells},
        "AC_classification": ac,
        "collapse_decomposition": decomposition,
        "dual_gate": f">=2 lineages each >=3 living AND N_eff>={NEFF_MIN}",
        "cells_full": cells,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\n" + "=" * 72, flush=True)
    print(f"VERDICT: {label}", flush=True)
    for n in cells:
        c = cells[n]
        print(f"  {n:7s} windows={c['n_seeds_with_window']}/{c['n_seeds']} opens={c['opens_windows']} "
              f"CF={c['CF']} WF={c['WF']} CF-FLOOR={c['CF_minus_FLOOR']}{c['CF_minus_FLOOR_CI']} "
              f"final_neff={c['mean_final_neff']} AC={ac[n]}", flush=True)
    print(f"  decomposition: pop={decomposition['pop_effect (hard16->hard96)']} "
          f"selection={decomposition['selection_effect (hard96->soft96)']}", flush=True)
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    main()
