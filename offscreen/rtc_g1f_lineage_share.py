"""Measure the FINAL founder-lineage composition of the g1f survival arm (the headline arm).

The headline g1f result (rtc_g1f_commblind_verdict_formal48.json) records cross-agent MII but NOT how
concentrated the population is in one founder lineage. The "~98% single founder lineage" scope claim was
asserted in the writeup without a banked artifact. This script pins it: it replicates the EXACT survival arm
of rtc_g1f_commblind_control.run_survival (same init seed, same per-gen episode/selection seeds, same ARM)
and, at the end of each seed's run, measures the dominant-lineage share and inverse-Simpson N_eff of the
final population. Output is a self-describing verdict JSON (with provenance). No truth-source files are edited.

Run (formal, n=48):
  RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_LINEAGE_SEEDS=48 python -m offscreen.rtc_g1f_lineage_share
"""
import json
import os
from collections import Counter
from pathlib import Path

import numpy as np

from offscreen import rtc_g1f_coevolve as g1f
from offscreen import rtc_g1f_common as cm
from offscreen.rtc_g1_run import _ci

ARM = "shared_weights_kin"
SEEDS = list(range(int(os.environ.get("RTC_G1F_LINEAGE_SEEDS", "48"))))


def run_survival_pop(seed):
    """Byte-for-byte the same evolution as rtc_g1f_commblind_control.run_survival, but return the final pop."""
    rng = np.random.default_rng(seed * 17 + len(ARM))
    pop = g1f._initial_pop_for(seed * 11 + len(ARM), ARM)
    for gen in range(g1f.G1F_GENS):
        ep = g1f._run_episode(seed * 1000 + gen * 13 + len(ARM), pop, "open", ARM)
        pop = g1f._select_next(seed, gen, pop, ep["fitness"], ARM, rng)
    return pop


def main():
    print(f"G1F_GENS={g1f.G1F_GENS} G1F_POP={g1f.G1F_POP} G1F_ROUNDS={g1f.G1F_ROUNDS} "
          f"TOXIC={g1f.rc.RTC_TOXIC_DEATH} n_seeds={len(SEEDS)}", flush=True)
    dom_shares, neffs, n_lineages = [], [], []
    for sd in SEEDS:
        pop = run_survival_pop(sd)
        counts = Counter(int(a.lineage) for a in pop)
        n = sum(counts.values())
        dom = max(counts.values()) / n
        ne = cm.neff(list(counts.values()))
        dom_shares.append(dom); neffs.append(ne); n_lineages.append(len(counts))
        print(f"[seed {sd}] dom_share={dom:.3f} N_eff={ne:.2f} n_lineages={len(counts)} pop={n}", flush=True)

    out = {
        "kind": "rtc_g1f_lineage_share",
        "claim": ("Final founder-lineage composition of the g1f SURVIVAL arm (the headline arm), measured by "
                  "replicating rtc_g1f_commblind_control.run_survival and inspecting the final population. "
                  "dom_lineage_share = fraction of the final population in the single largest founder lineage; "
                  "N_eff = inverse-Simpson effective number of lineages."),
        "arm": ARM,
        "seeds": SEEDS,
        "dom_lineage_share": [round(float(x), 4) for x in dom_shares],
        "dom_share_mean": round(float(np.mean(dom_shares)), 4), "dom_share_ci": _ci(dom_shares, 1),
        "dom_share_median": round(float(np.median(dom_shares)), 4),
        "neff": [round(float(x), 3) for x in neffs],
        "neff_mean": round(float(np.mean(neffs)), 3), "neff_ci": _ci(neffs, 2),
        "n_lineages_final": n_lineages,
        "frac_seeds_single_lineage_ge99pct": round(float(np.mean([s >= 0.99 for s in dom_shares])), 4),
        "frac_seeds_single_lineage_eq100pct": round(float(np.mean([s >= 0.999 for s in dom_shares])), 4),
        "provenance": cm.make_provenance(
            "g1f-lineage-share",
            "RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_LINEAGE_SEEDS=48 python -m offscreen.rtc_g1f_lineage_share",
            ["RTC_G1F_FORMAL", "RTC_TOXIC_DEATH", "RTC_G1F_LINEAGE_SEEDS"],
            effective_config={"POP": g1f.G1F_POP, "GENS": g1f.G1F_GENS, "ROUNDS": g1f.G1F_ROUNDS,
                              "n_seeds": len(SEEDS)},
        ),
    }
    print(f"\ndom_share_mean={out['dom_share_mean']} ci={out['dom_share_ci']} median={out['dom_share_median']}")
    print(f"neff_mean={out['neff_mean']} ci={out['neff_ci']}")
    print(f"frac_seeds_single>=99%={out['frac_seeds_single_lineage_ge99pct']} "
          f"==100%={out['frac_seeds_single_lineage_eq100pct']}")
    p = Path(__file__).resolve().parent / "rtc_g1f_lineage_share_verdict.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote", p)


if __name__ == "__main__":
    main()
