"""Power / minimal-detectable-effect (MDE) analysis for the G1F co-evolution null.

The G1F headline is a NULL: the survival-selected channel's cross-agent
intelligibility (MII) does not separate from a communication-blind control (the
apparent rise is clonal descent-convergence). A null is only meaningful if it is
POWERED. This script turns "no detectable effect" into a BOUNDED claim: it reports
the bootstrap CI on the paired win-margin (survival MII - comm-blind MII), the power
to detect the observed effect at several seed counts, and the minimal effect we could
have detected at 80% power given the seeds actually run.

Reads a comm-blind verdict JSON (default: the >=12-seed reseed) that contains
per-seed `survival_final_mii` and `commblind_final_mii` arrays (paired by seed/init
by construction). Pure NumPy; deterministic bootstrap.

Usage:
    python -m offscreen.rtc_g1f_power_analysis [verdict.json]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

Z_975 = 1.959963985  # two-sided alpha=0.05
Z_80 = 0.841621234   # 80% power
MDE_K = Z_975 + Z_80  # ~2.8016

OFF = Path(__file__).resolve().parent


def _phi(x):
    """Standard normal CDF via erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_power(effect, sd, n, alpha_z=Z_975):
    """Two-sided power of a one-sample test for a paired mean `effect` with noise `sd`."""
    if sd <= 0:
        return 1.0
    ncp = abs(effect) * math.sqrt(n) / sd
    return _phi(ncp - alpha_z) + _phi(-ncp - alpha_z)


def boot_ci(diffs, B=20000, alpha=0.05, seed=0):
    rng = np.random.default_rng(seed)
    n = len(diffs)
    means = diffs[rng.integers(0, n, size=(B, n))].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else OFF / "rtc_g1f_commblind_verdict_s12.json"
    if not path.exists():
        # graceful fallback to the committed 6-seed artifact
        path = OFF / "rtc_g1f_commblind_verdict.json"
    d = json.load(open(path, encoding="utf-8"))

    surv = np.asarray(d["survival_final_mii"], dtype=float)
    comm = np.asarray(d["commblind_final_mii"], dtype=float)
    assert len(surv) == len(comm), "survival/commblind arrays must be paired"
    diffs = surv - comm
    n = len(diffs)
    mean_diff = float(diffs.mean())
    sd_diff = float(diffs.std(ddof=1)) if n > 1 else 0.0
    ci_lo, ci_hi = boot_ci(diffs)

    # power to detect the OBSERVED effect at various seed counts
    power_at = {int(k): round(normal_power(mean_diff, sd_diff, k), 3) for k in (6, 12, 16, 24, 32)}
    # smallest true effect detectable at 80% power with the seeds actually run
    mde = MDE_K * sd_diff / math.sqrt(n) if n > 0 else float("nan")
    # seeds needed to detect the observed effect at 80% power
    n_needed = (MDE_K * sd_diff / abs(mean_diff)) ** 2 if mean_diff != 0 else float("inf")

    detectable = ci_lo > 0 or ci_hi < 0
    out = {
        "kind": "rtc_g1f_power_analysis",
        "source": path.name,
        "n_seeds": n,
        "survival_mii_mean": round(float(surv.mean()), 5),
        "commblind_mii_mean": round(float(comm.mean()), 5),
        "win_margin_mean": round(mean_diff, 5),
        "win_margin_sd": round(sd_diff, 5),
        "win_margin_ci95": [round(ci_lo, 5), round(ci_hi, 5)],
        "effect_detectable_at_this_n": bool(detectable),
        "power_to_detect_observed_effect": power_at,
        "mde_80pct_power_at_this_n": round(mde, 5),
        "seeds_needed_for_observed_effect_at_80pct": (
            math.ceil(n_needed) if math.isfinite(n_needed) else None),
        "interpretation": (
            f"At n={n}, the survival-minus-commblind win-margin is {mean_diff:.4f} "
            f"(95% CI [{ci_lo:.4f}, {ci_hi:.4f}]). "
            + ("The CI excludes 0: a detectable effect." if detectable else
               f"The CI includes 0: NO detectable effect. This null bounds the true "
               f"effect: with 80% power at n={n} we could have detected an effect "
               f">= {mde:.4f}; the observed {mean_diff:.4f} would need "
               f"{math.ceil(n_needed) if math.isfinite(n_needed) else 'inf'} seeds to reach 80% power.")),
    }
    outpath = OFF / "rtc_g1f_power_analysis.json"
    json.dump(out, open(outpath, "w", encoding="utf-8"), indent=2)
    print(json.dumps(out, indent=2))
    print("wrote", outpath)


if __name__ == "__main__":
    main()
