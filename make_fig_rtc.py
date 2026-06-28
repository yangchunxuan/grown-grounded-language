"""Regenerate the paper figure (paper/fig_rtc.pdf) from the committed verdict JSONs.

Run from the repo root:  python make_fig_rtc.py
Reads:  offscreen/rtc_g1d_lethal_verdict_sig0.3.json   (Fig a, content load-bearing, 24 seeds)
        offscreen/rtc_g1e_emerge_verdict_tox-0.9.json  (Fig b, use emerges, 8 seeds)
        offscreen/rtc_g1f_coevolve_verdict.json         (Fig c, no co-evolution, 6 seeds)
The g1f communication-blind control bar is from offscreen/rtc_g1f_commblind_control.py
(6 seeds): final mii_cross [0.0992,0.1064,0.1686,0.0303,0.0999,0.0694] -> mean 0.0956,
95% CI [0.0622,0.1301]. Run that script to regenerate those numbers.
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OFF = ROOT / "offscreen"
OUTDIR = ROOT / "paper"
OUTDIR.mkdir(exist_ok=True)


def load(name):
    return json.load(open(OFF / name, encoding="utf-8"))


g1d = load("rtc_g1d_lethal_verdict_sig0.3.json")
g1e = load("rtc_g1e_emerge_verdict_tox-0.9.json")
g1f = load("rtc_g1f_coevolve_verdict.json")

TREAT, CTRL, CTRL2, NULLC, ORC = "#0072B2", "#D55E00", "#E69F00", "#999999", "#009E73"
plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})
fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(11.0, 3.7), constrained_layout=True)


def yerr(mean, ci):
    return [[max(0.0, mean - ci[0])], [max(0.0, ci[1] - mean)]]


def label_bar(ax, x, mean, ci, fmt="{:.2f}"):
    ax.text(x, ci[1] + 0.018, fmt.format(mean), ha="center", va="bottom", fontsize=8.5)


arms = [("fusion", TREAT), ("scramble", CTRL), ("misroute", CTRL2), ("mute", NULLC), ("oracle", ORC)]
for i, (a, c) in enumerate(arms):
    s = g1d["summary"][a]
    axA.bar(i, s["alive"], color=c, width=0.72, yerr=yerr(s["alive"], s["alive_ci"]), capsize=4, error_kw={"lw": 1.1})
    label_bar(axA, i, s["alive"], s["alive_ci"])
axA.set_xticks(range(len(arms))); axA.set_xticklabels([a for a, _ in arms], rotation=22, ha="right")
axA.set_ylabel("survival (alive fraction)"); axA.set_ylim(0, 1.18)
axA.set_title("(a) Content is load-bearing")

modes = [("real", TREAT, "real content"), ("scramble", CTRL, "scrambled"), ("drift", NULLC, "no selection")]
for m, c, lab in modes:
    trajs = np.array([r["traj"] for r in g1e["rows"] if r["mode"] == m], dtype=float)
    gens = np.arange(trajs.shape[1]); mean, sd = trajs.mean(0), trajs.std(0)
    axB.plot(gens, mean, color=c, lw=2.0, label=lab)
    axB.fill_between(gens, mean - sd, mean + sd, color=c, alpha=0.15, lw=0)
axB.set_xlabel("generation"); axB.set_ylabel("mean trust (use of channel)")
axB.set_xlim(0, gens[-1]); axB.set_ylim(0, 1.05)
axB.set_title("(b) Use emerges under selection"); axB.legend(loc="center right", frameon=False)

cb = load("rtc_g1f_commblind_verdict.json")  # committed control artifact
commblind_mean, commblind_ci = cb["commblind_mean"], cb["commblind_ci"]
swk, sfr = g1f["summary"]["shared_weights_kin"], g1f["summary"]["shared_frozen_random"]
bars = [("survival\nselection", swk["final_mii_mean"], swk["final_mii_ci"], TREAT),
        ("comm-blind\ncontrol", commblind_mean, commblind_ci, CTRL),
        ("frozen\nnull", sfr["final_mii_mean"], sfr["final_mii_ci"], NULLC)]
for i, (lab, mean, ci, c) in enumerate(bars):
    axC.bar(i, mean, color=c, width=0.62, yerr=yerr(mean, ci), capsize=4, error_kw={"lw": 1.1})
    label_bar(axC, i, mean, ci, fmt="{:.3f}")
axC.set_xticks(range(len(bars))); axC.set_xticklabels([b[0] for b in bars])
axC.set_ylabel("final cross-agent intelligibility"); axC.set_ylim(0, 0.24)
axC.set_title("(c) Channel does not co-evolve")

fig.savefig(OUTDIR / "fig_rtc.pdf", bbox_inches="tight")
fig.savefig(OUTDIR / "fig_rtc.png", bbox_inches="tight", dpi=240)
print("wrote", OUTDIR / "fig_rtc.pdf")
