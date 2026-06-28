"""RTC MVP-1 G1 REDO (scripted-forage fallback, per spec honest_risk #2).

Decouples 'can a from-scratch policy LEARN to act' from 'is the grown channel
LOAD-BEARING'. The original G1 failed because (a) the survival channel was only
0.33-0.48 roundtrip-accurate on the realistic forecast distribution, so the
(already scripted) packet-score policy ate toxins ~46% and died. Here we train
the channel WELL (full band coverage, more epochs) and run the SAME scripted
policy, then measure the open-vs-null survival lift = the clean S5 test.

No new mechanics; reuses rtc_g1_run / rtc_fusion / rtc_language verbatim.
no-oracle preserved: the policy reads only decoded messages + own perception
(packet_score on the fused forecast); the true field is read only by eat()
resolution, which the redline permits.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

import numpy as np

import config.prereg_rtc as rc
from rtc_language import all_band_tuples, train_relay_channel
from offscreen.rtc_g1_run import _ci, _run_survival, _summarize

ROOT = Path(__file__).resolve().parents[1]
SEEDS = list(range(int(os.environ.get("RTC_G1B_SEEDS", "6"))))
ARMS = ("fusion", "mute", "scramble", "body_follow", "solo")  # fusion == open
CHANNEL_EPOCHS = 500


def main():
    rows, chan_acc = [], []
    for sd in SEEDS:
        # train the channel on the FULL band space so forecasts are accurate
        ch = train_relay_channel(9000 + sd, all_band_tuples(), epochs=CHANNEL_EPOCHS)
        chan_acc.append(round(float(ch.train_accuracy), 4))
        print(f"[seed {sd}] channel_roundtrip={chan_acc[-1]}", flush=True)
        for pol in ARMS:
            r = _run_survival(sd, pol, ch)
            rows.append(r)
            print(f"  [{pol}] alive={r['alive']} age={r['age']} eat={r['eat_rate']} "
                  f"bad={r['bad_rate']} rest={r['rest_rate']}", flush=True)

    summ = _summarize(rows)

    def alive(pol):
        return [r["alive"] for r in rows if r["policy"] == pol]
    open_a = alive("fusion")
    open_ci = _ci(open_a, 70)
    nulls = ("mute", "scramble", "body_follow", "solo")
    deltas = {f"open_minus_{p}": _ci([a - b for a, b in zip(open_a, alive(p))], 60 + i)
              for i, p in enumerate(nulls)}

    gates = {
        "channel_accurate": float(np.mean(chan_acc)) > 0.7,
        "open_survives_majority": open_ci[0] > 0.5,
        "open_beats_mute": deltas["open_minus_mute"][0] > rc.RTC_G1_FUSION_LIFT_MIN,
        "open_beats_scramble": deltas["open_minus_scramble"][0] > rc.RTC_G1_FUSION_LIFT_MIN,
        "open_beats_body_follow": deltas["open_minus_body_follow"][0] > rc.RTC_G1_FUSION_LIFT_MIN,
    }
    verdict = ("RTC_G1B_CHANNEL_LOAD_BEARING" if all(gates.values())
               else "RTC_G1B_FAIL")
    out = {
        "kind": "rtc_g1b_scripted_v1", "seeds": SEEDS, "channel_epochs": CHANNEL_EPOCHS,
        "honest_claim": ("Scripted-forage S5 test: well-trained grown channel + scripted "
                         "packet-score policy. open=fusion vs mute/scramble/body_follow/solo "
                         "survival lift. Decouples policy-learning from channel-load-bearing. "
                         "JOINT compositionality (installed FactoredSpeaker) is NOT retested here."),
        "channel_roundtrip_acc": chan_acc, "channel_roundtrip_mean": round(float(np.mean(chan_acc)), 4),
        "open_alive_ci": open_ci, "deltas": deltas, "summary": summ,
        "gates": gates, "verdict": verdict,
    }
    p = ROOT / "offscreen" / "rtc_g1b_scripted_verdict.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nchannel_acc_mean={np.mean(chan_acc):.3f}")
    print(f"open_alive={open_a} ci={open_ci}")
    for k, v in deltas.items():
        print(f"  {k} {v}")
    print(f"VERDICT={verdict} gates={gates} -> {p}", flush=True)


if __name__ == "__main__":
    main()
