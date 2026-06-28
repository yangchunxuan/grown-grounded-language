"""Committed significance artifact for the G1D lethal-signaling result.

The g1d harness's own machine verdict is RTC_G1D_INCONCLUSIVE because it gates on an
ABSOLUTE-majority-survival threshold (fusion survival CI lower bound > 0.5), which a
~0.58 survival rate does not clear. The paper's claim is the weaker, RELATIVE one:
fusion out-survives each degraded control. This script makes that relative claim
reproducible from the committed per-seed rows via an exact two-sided McNemar test
(paired by seed), and writes rtc_g1d_paired_stats.json.

Run:  python -m offscreen.rtc_g1d_paired_stats
"""
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = json.load(open(HERE / "rtc_g1d_lethal_verdict_sig0.3.json", encoding="utf-8"))

by_arm = {}
for r in V["rows"]:
    by_arm.setdefault(r["arm"], {})[r["seed"]] = float(r["alive"])


def mcnemar_exact_two_sided(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)


fusion = by_arm["fusion"]
seeds = sorted(fusion)
out = {
    "kind": "rtc_g1d_paired_stats",
    "source": "rtc_g1d_lethal_verdict_sig0.3.json",
    "machine_verdict": V["verdict"],
    "note": ("Machine verdict is INCONCLUSIVE because it tests ABSOLUTE majority survival "
             "(fusion CI-lower > 0.5). The relative claim (fusion beats each degraded control) "
             "is tested here by an exact paired (by-seed) two-sided McNemar test."),
    "n_seeds": len(seeds),
    "fusion_alive_rate": round(sum(fusion.values()) / len(seeds), 4),
    "tests": {},
}
for ctrl in ("scramble", "misroute", "mute"):
    cm = by_arm[ctrl]
    b = sum(1 for s in seeds if fusion[s] > cm.get(s, 0.0))   # fusion lives, control dies
    c = sum(1 for s in seeds if cm.get(s, 0.0) > fusion[s])   # control lives, fusion dies
    p = mcnemar_exact_two_sided(b, c)
    out["tests"][f"fusion_vs_{ctrl}"] = {
        "discordant_fusion_lives": b, "discordant_control_lives": c,
        "control_alive_rate": round(sum(cm.values()) / len(seeds), 4),
        "mcnemar_exact_two_sided_p": p, "significant_p_lt_5e-4": bool(p < 5e-4),
    }

p_max = max(t["mcnemar_exact_two_sided_p"] for t in out["tests"].values())
out["all_controls_p_lt_5e-4"] = bool(p_max < 5e-4)
out["max_p_across_controls"] = p_max

(HERE / "rtc_g1d_paired_stats.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
for k, t in out["tests"].items():
    print(f"{k}: discordant {t['discordant_fusion_lives']}:{t['discordant_control_lives']}  "
          f"p={t['mcnemar_exact_two_sided_p']:.2e}  sig={t['significant_p_lt_5e-4']}")
print("all controls p<5e-4:", out["all_controls_p_lt_5e-4"], "(max p =", f"{p_max:.2e})")
print("wrote", HERE / "rtc_g1d_paired_stats.json")
