"""Control for the G1F 'mii moves' confound.

Claude's review hypothesis: the mii_cross rise in shared_weights_kin may be CLONAL
DESCENT-CONVERGENCE (selection -> population descends from a few ancestors -> kin
share near-identical UnifiedIO tables -> cross-mii rises) rather than
selection-FOR-communication. The committed arch-null (shared_frozen_random) is
frozen / no-reproduction, so it conflates 'no selection' with 'no descent'.

This control runs the IDENTICAL shared-weights reproduction (UnifiedIO + preserve
lineage) but with COMM-BLIND random fitness instead of survival fitness. Same init,
same rng seed -> the only difference is whether selection can 'see' communication.

  if commblind final mii ~= survival final mii (both >> frozen) -> mii-moves is a
     descent-convergence ARTIFACT (not a bootstrap escape).
  if survival final mii >> commblind -> mii-moves is real selection-for-communication.
"""
import numpy as np

from offscreen import rtc_g1f_coevolve as g1f
from offscreen.rtc_g1_run import _ci

ARM = "shared_weights_kin"
SEEDS = list(range(6))


def _init(seed):
    return g1f._initial_pop_for(seed * 11 + len(ARM), ARM)


def run_survival(seed):
    rng = np.random.default_rng(seed * 17 + len(ARM))
    pop = _init(seed)
    init = g1f._mii(pop)["cross"]
    for gen in range(g1f.G1F_GENS):
        ep = g1f._run_episode(seed * 1000 + gen * 13 + len(ARM), pop, "open", ARM)
        pop = g1f._select_next(seed, gen, pop, ep["fitness"], ARM, rng)
    return init, g1f._mii(pop)["cross"]


def run_commblind(seed):
    rng = np.random.default_rng(seed * 17 + len(ARM))
    pop = _init(seed)
    init = g1f._mii(pop)["cross"]
    for gen in range(g1f.G1F_GENS):
        fake = rng.random(len(pop))  # COMM-BLIND: random fitness, same reproduction
        pop = g1f._select_next(seed, gen, pop, fake, ARM, rng)
    return init, g1f._mii(pop)["cross"]


def run_frozen(seed):
    pop = g1f._initial_pop_for(seed * 11 + len("shared_frozen_random"), "shared_frozen_random")
    return g1f._mii(pop)["cross"]


def main():
    surv, blind, froz = [], [], []
    print(f"G1F_GENS={g1f.G1F_GENS} G1F_POP={g1f.G1F_POP} G1F_ROUNDS={g1f.G1F_ROUNDS} "
          f"G1F_VENTS={g1f.G1F_VENTS} MII_SAMPLE={g1f.G1F_MII_SAMPLE} TOXIC={g1f.rc.RTC_TOXIC_DEATH}", flush=True)
    for sd in SEEDS:
        _, fs = run_survival(sd)
        _, fb = run_commblind(sd)
        ff = run_frozen(sd)
        surv.append(fs); blind.append(fb); froz.append(ff)
        print(f"[seed {sd}] survival={fs:.4f}  commblind={fb:.4f}  frozen={ff:.4f}", flush=True)
    d = [a - b for a, b in zip(surv, blind)]
    print(f"\nsurvival   final mii mean={np.mean(surv):.4f} ci={_ci(surv, 1)}")
    print(f"commblind  final mii mean={np.mean(blind):.4f} ci={_ci(blind, 2)}")
    print(f"frozen     final mii mean={np.mean(froz):.4f} ci={_ci(froz, 3)}")
    print(f"survival - commblind: mean={np.mean(d):.4f} ci={_ci(d, 4)}")
    artifact = _ci(d, 4)[0] <= 0.0  # survival not CI-clean above commblind => artifact
    print(f"\nMII_MOVES_IS_DESCENT_CONVERGENCE_ARTIFACT = {artifact}")

    import json
    from pathlib import Path
    out = {
        "kind": "rtc_g1f_commblind_control",
        "claim": ("Control for the g1f 'mii moves' result: shared_weights reproduction with "
                  "COMM-BLIND (random) fitness reaches the same cross-agent mii as survival "
                  "selection -> the mii rise is clonal descent-convergence, not selection for "
                  "communication."),
        "seeds": SEEDS,
        "survival_final_mii": [round(float(x), 5) for x in surv],
        "commblind_final_mii": [round(float(x), 5) for x in blind],
        "frozen_final_mii": [round(float(x), 5) for x in froz],
        "survival_mean": round(float(np.mean(surv)), 5), "survival_ci": _ci(surv, 1),
        "commblind_mean": round(float(np.mean(blind)), 5), "commblind_ci": _ci(blind, 2),
        "frozen_mean": round(float(np.mean(froz)), 5), "frozen_ci": _ci(froz, 3),
        "survival_minus_commblind_ci": _ci(d, 4),
        "mii_moves_is_descent_convergence_artifact": bool(artifact),
    }
    p = Path(__file__).resolve().parent / "rtc_g1f_commblind_verdict.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote", p)


if __name__ == "__main__":
    main()
