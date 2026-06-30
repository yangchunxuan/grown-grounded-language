"""Transient-vs-equilibrium robustness probe for the g1f headline margin.

Gemini's meta-review asked: is the +0.0548 (survival vs random-fitness) cross-agent MII margin an
equilibrium property, or a transient caught at generation 28? This extends BOTH headline arms (the
rng-matched survival arm and the random-fitness control) to a long horizon and records the cross-agent MII
margin at checkpoints, so we can see whether the advantage PERSISTS, grows, or DECAYS after the population
fixates (~gen 28, N_eff ~1.02). Read-only; writes its own verdict JSON. Same arm / seed formulas / rng-fix
as rtc_g1f_commblind_control.

Run: RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_TRANSIENT_SEEDS=24 python -m offscreen.rtc_g1f_transient_probe
"""
import json
import os
from pathlib import Path

import numpy as np

from offscreen import rtc_g1f_coevolve as g1f
from offscreen import rtc_g1f_common as cm
from offscreen.rtc_g1_run import _ci

ARM = "shared_weights_kin"
SEEDS = list(range(int(os.environ.get("RTC_G1F_TRANSIENT_SEEDS", "24"))))
CKPTS = sorted(int(x) for x in os.environ.get("RTC_G1F_TRANSIENT_CKPTS", "28,56,100,150").split(","))


def _run_arm(seed, kind, max_gen):
    """Same evolution as rtc_g1f_commblind_control (rng-fixed), but run to max_gen and snapshot cross-MII."""
    rng = np.random.default_rng(seed * 17 + len(ARM))                      # reproduction rng
    fake_rng = np.random.default_rng(seed * 17 + len(ARM) + 9_000_000)     # independent: random fitness only
    pop = g1f._initial_pop_for(seed * 11 + len(ARM), ARM)
    rec = {}
    for gen in range(max_gen):
        if kind == "survival":
            fit = g1f._run_episode(seed * 1000 + gen * 13 + len(ARM), pop, "open", ARM)["fitness"]
        else:  # random-fitness control
            fit = fake_rng.random(len(pop))
        pop = g1f._select_next(seed, gen, pop, fit, ARM, rng)
        if (gen + 1) in CKPTS:
            rec[gen + 1] = g1f._mii(pop)["cross"]
    return rec


def main():
    max_gen = max(CKPTS)
    print(f"max_gen={max_gen} POP={g1f.G1F_POP} ROUNDS={g1f.G1F_ROUNDS} n={len(SEEDS)} ckpts={CKPTS} "
          f"TOXIC={g1f.rc.RTC_TOXIC_DEATH}", flush=True)
    surv = {c: [] for c in CKPTS}
    blind = {c: [] for c in CKPTS}
    for sd in SEEDS:
        rs = _run_arm(sd, "survival", max_gen)
        rb = _run_arm(sd, "random", max_gen)
        for c in CKPTS:
            surv[c].append(rs[c]); blind[c].append(rb[c])
        print(f"[seed {sd}] " + " ".join(f"g{c}:{rs[c] - rb[c]:+.4f}" for c in CKPTS), flush=True)
    traj = {}
    for c in CKPTS:
        d = [a - b for a, b in zip(surv[c], blind[c])]
        traj[str(c)] = {
            "survival_mii": round(float(np.mean(surv[c])), 5),
            "random_mii": round(float(np.mean(blind[c])), 5),
            "margin": round(float(np.mean(d)), 5),
            "margin_ci": _ci(d, c),
        }
    out = {
        "kind": "rtc_g1f_transient_probe",
        "claim": ("Whether the survival-vs-random-fitness cross-agent MII margin persists past the gen-28 "
                  "fixation point, or is a transient. Trajectory of the paired margin at generation checkpoints."),
        "arm": ARM, "seeds": SEEDS, "checkpoints": CKPTS, "trajectory": traj,
        "provenance": cm.make_provenance(
            "g1f-transient-probe",
            "RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_TRANSIENT_SEEDS=24 python -m offscreen.rtc_g1f_transient_probe",
            ["RTC_G1F_FORMAL", "RTC_TOXIC_DEATH", "RTC_G1F_TRANSIENT_SEEDS", "RTC_G1F_TRANSIENT_CKPTS"],
            effective_config={"POP": g1f.G1F_POP, "ROUNDS": g1f.G1F_ROUNDS, "max_gen": max_gen, "n_seeds": len(SEEDS)}),
    }
    print()
    for c in CKPTS:
        t = traj[str(c)]
        print(f"gen {c:>4}: survival {t['survival_mii']:.4f}  random {t['random_mii']:.4f}  "
              f"margin {t['margin']:+.4f}  CI {t['margin_ci']}")
    Path(__file__).resolve().parent.joinpath("rtc_g1f_transient_probe_verdict.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote rtc_g1f_transient_probe_verdict.json")


if __name__ == "__main__":
    main()
