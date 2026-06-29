"""Reconcile the g1f apparent-win against its decisive control, in ONE artifact.

The naive pre-registered gate-bundle in ``rtc_g1f_coevolve.py`` can declare
``RTC_G1F_CHANNEL_COEVOLVES`` (all gates pass; the survival-selected
shared_weights_kin arm's cross-agent MII rises off the floor and the run's own
scramble/mute survival gates pass). That bundle does NOT test against
descent-convergence. The architecture+process-matched comm-blind control
(``rtc_g1f_commblind_control.py``: identical shared-weights reproduction, but with
RANDOM/comm-blind fitness instead of survival fitness, paired per seed) is the
decisive test: if comm-blind reproduction reaches the same MII, the rise is clonal
descent-convergence, not selection FOR communication.

This script reads the two committed n=12 verdicts + the power analysis and writes a
single reconciled verdict that states the apparent win AND the control refutation
side by side. It is a pure derived artifact (no simulation), deterministic.

Canonical commands (formal, n=12):
  RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_SEEDS=12      python -m offscreen.rtc_g1f_coevolve         # -> rtc_g1f_coevolve_verdict_s12.json
  RTC_G1F_FORMAL=1 RTC_G1F_COMMBLIND_SEEDS=12                 python -m offscreen.rtc_g1f_commblind_control # -> rtc_g1f_commblind_verdict_s12.json
  python -m offscreen.rtc_g1f_power_analysis offscreen/rtc_g1f_commblind_verdict_s12.json                   # -> rtc_g1f_power_analysis.json
  python -m offscreen.rtc_g1f_reconcile                                                                     # -> rtc_g1f_reconciled_verdict.json
"""
import json
from pathlib import Path

OFF = Path(__file__).resolve().parent


def load(name):
    return json.load(open(OFF / name, encoding="utf-8"))


co = load("rtc_g1f_coevolve_verdict_s12.json")        # apparent win (naive gate)
cb = load("rtc_g1f_commblind_verdict_formal48.json")  # decisive control (paired, formal n=48 canonical)
pw = load("rtc_g1f_power_analysis.json")              # paired margin + power/MDE

swk = co["summary"]["shared_weights_kin"]
margin = pw["win_margin_mean"]
margin_ci = pw["win_margin_ci95"]
refuted = not pw["effect_detectable_at_this_n"]  # CI includes 0 -> control matches -> refuted

out = {
    "kind": "rtc_g1f_reconciled",
    "n_seeds": cb.get("seeds") and len(cb["seeds"]) or pw["n_seeds"],
    "mode": "formal",
    "decisive_test": "comm-blind control (paired, same-init survival-fitness vs random-fitness reproduction)",
    "apparent_win": {
        "source": "rtc_g1f_coevolve_verdict_s12.json",
        "naive_gate_verdict": co["verdict"],
        "shared_weights_kin_mii_mean": swk["final_mii_mean"],
        "shared_weights_kin_mii_ci": swk["final_mii_ci"],
        "all_gates_pass": all(co["gates"].values()),
        "gates": co["gates"],
    },
    "control_refutation": {
        "source": "rtc_g1f_commblind_verdict_s12.json",
        "survival_fitness_mii_mean": cb["survival_mean"],
        "commblind_fitness_mii_mean": cb["commblind_mean"],
        "frozen_null_mii_mean": cb["frozen_mean"],
        "paired_win_margin_survival_minus_commblind": margin,
        "win_margin_ci95": margin_ci,
        "ci_includes_zero": refuted,
        "mde_80pct_power": pw["mde_80pct_power_at_this_n"],
        "seeds_needed_for_observed_effect_at_80pct": pw["seeds_needed_for_observed_effect_at_80pct"],
    },
    "verdict": (
        "RTC_G1F_APPARENT_COEVOLVE_REFUTED_BY_COMMBLIND" if refuted
        else "RTC_G1F_COEVOLVE_SURVIVES_COMMBLIND_CONTROL"),
    "interpretation": (
        f"The naive pre-registered gate-bundle declares '{co['verdict']}' "
        f"(all gates pass; shared-weights-kin MII rises to {swk['final_mii_mean']:.3f}). "
        f"But the architecture+process-matched comm-blind control reaches the same MII range "
        f"(survival-fitness {cb['survival_mean']:.3f} vs comm-blind-fitness {cb['commblind_mean']:.3f}; "
        f"paired survival-minus-commblind margin {margin:+.3f}, 95% CI {margin_ci}, "
        f"{'includes 0' if refuted else 'excludes 0'}). "
        + (f"So in this regime the MII rise is consistent with clonal descent-convergence rather than "
           f"selection FOR communication: we detect NO load-bearing co-evolution above the matched "
           f"comm-blind control. This BOUNDS the effect (any true effect is below the MDE of "
           f"{pw['mde_80pct_power_at_this_n']:.3f}; point estimate is ~0/slightly negative) but does "
           f"NOT prove impossibility -- a richer world could still produce co-evolution. Note also the "
           f"descent-convergence floor is high ({cb['commblind_mean']:.3f} vs frozen "
           f"{cb['frozen_mean']:.3f}), so a small true effect of comparable size could be masked. The "
           f"naive gate's apparent win is an artifact the matched control exposes -- a live instance of "
           f"the attack-machine."
           if refuted else
           f"The control is BEATEN: survival-fitness selection raises cross-agent MII "
           f"({cb['survival_mean']:.3f}) above the matched comm-blind control "
           f"({cb['commblind_mean']:.3f}) = selection FOR communication, not mere "
           f"descent-convergence. SCOPE (load-bearing limitation): the population collapses "
           f"to ~1 founder lineage, so this is KIN-LINEAGE (within-family) channel "
           f"co-evolution, NOT yet a demonstrated public cross-lineage shared language.")),
}

outpath = OFF / "rtc_g1f_reconciled_verdict.json"
json.dump(out, open(outpath, "w", encoding="utf-8"), indent=2)
print(json.dumps(out, indent=2))
print("wrote", outpath)
