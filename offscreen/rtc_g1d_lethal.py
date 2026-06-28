"""RTC MVP-1 LETHAL-SIGNALING test: the one design that FORCES message content to be
load-bearing, closing every content-free shortcut the foraging worlds (g1b/g1c) leaked.

Setup (a Lewis signaling game with lethal stakes):
- M relay posts sit on vents; each round the true field makes some vents FOOD (w.f>theta)
  and some LETHAL (w.f<TOXIC_DEATH). The mix drifts with the tide.
- The focal agent has NO local perception of the vents (they are remote). Its ONLY
  information about which vent is safe is the partners' grown-channel messages. It MUST
  pick one vent and EAT it each round (no rest/abstain -> no confidence-gate shortcut;
  no traversal -> no movement shortcut; no local sensing -> no perceive-and-check shortcut).
- Picking a lethal vent -> eat() resolves on the true field -> toxic_death. Picking food
  -> energy. So WRONG content kills; only correct decoded content keeps you alive.

Arms (all ACT every round):
  fusion   : pick the vent whose DECODED message has the highest edibility       (treatment)
  scramble : posts send random messages -> ~random pick                          (content control)
  misroute : messages decoded CORRECTLY but bound to PERMUTED vents              (binding control, non-degenerate)
  mute     : no messages -> uniformly random pick                                (no-info baseline)
  oracle   : picks the truly-safest vent (reads true field; FENCED reference, not a win)

no-oracle seam: the fusion/scramble/misroute/mute DECISION reads only decoded messages
(or nothing); the true field is read solely by eat() resolution and the clearly-fenced
oracle reference arm.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

import numpy as np

import config.prereg_rtc as rc
from rtc_language import (all_band_tuples, bands_to_values, scramble_message,
                          train_relay_channel, values_to_bands)
from rtc_metabolism import MetabolicState, eat, metabolic_vector
from rtc_world import RTCWorld
from offscreen.rtc_g1_run import _ci, _sensor_values

ROOT = Path(__file__).resolve().parents[1]
FULL_BASIS = (0, 1, 2, 3)
G = rc.RTC_GRID

LE_SEEDS = list(range(int(os.environ.get("RTC_LE_SEEDS", "8"))))
LE_ROUNDS = int(os.environ.get("RTC_LE_ROUNDS", "60"))
LE_VENTS = int(os.environ.get("RTC_LE_VENTS", "12"))
LE_STEP_PER_ROUND = int(os.environ.get("RTC_LE_STEP", "3"))
LE_CHAN_EPOCHS = int(os.environ.get("RTC_LE_CHAN_EPOCHS", "500"))
ARMS = ("fusion", "scramble", "misroute", "mute", "oracle")


def _decoded_edib(world, posts, channel, w, rng, arm):
    vals_list = [_sensor_values(world, px, py, FULL_BASIS, rng) for (px, py) in posts]
    edib = []
    for vals in vals_list:
        if arm == "scramble":
            dec = channel.decode(scramble_message(rng))
        else:  # fusion / misroute -> real content
            dec = channel.decode(channel.emit(values_to_bands(vals)))
        edib.append(float(np.dot(w, bands_to_values(dec))))
    if arm == "misroute":
        edib = list(np.asarray(edib)[rng.permutation(len(edib))])
    return edib


def _run(seed, arm, channel):
    rng = np.random.default_rng(seed * 41 + len(arm))
    world = RTCWorld(seed)
    w = metabolic_vector(seed)
    state = MetabolicState(rc.RTC_ENERGY_INIT)
    prng = np.random.default_rng(seed + 7001)
    for _ in range(40):
        world.step()
    vflat = np.asarray(world.vents).reshape(-1, 2)
    idx = prng.choice(len(vflat), min(LE_VENTS, len(vflat)), replace=False)
    posts = [(int(vflat[i][0]) % G, int(vflat[i][1]) % G) for i in idx]
    outs, lethal_frac, picked_food = [], [], 0
    for _ in range(LE_ROUNDS):
        if not state.alive:
            break
        for _ in range(LE_STEP_PER_ROUND):
            world.step()
        true_edib = np.asarray([float(np.dot(w, world.patch(px, py))) for (px, py) in posts])
        lethal_frac.append(float(np.mean(true_edib < rc.RTC_TOXIC_DEATH)))
        if arm == "oracle":
            pick = int(np.argmax(true_edib))
        elif arm == "mute":
            pick = int(rng.integers(0, len(posts)))
        else:
            pick = int(np.argmax(_decoded_edib(world, posts, channel, w, rng, arm)))
        out = eat(state, world.patch(*posts[pick]), w)
        outs.append(out["outcome"])
        picked_food += int(out["outcome"] == "eat")
    n = max(1, len(outs))
    return {"seed": seed, "arm": arm, "alive": float(state.alive), "rounds": len(outs),
            "food_pick_rate": round(picked_food / n, 4),
            "death_by_toxin": int(any(o == "toxic_death" for o in outs)),
            "lethal_frac": round(float(np.mean(lethal_frac)), 4)}


def main():
    rows, chan = [], []
    for sd in LE_SEEDS:
        ch = train_relay_channel(9000 + sd, all_band_tuples(), epochs=LE_CHAN_EPOCHS)
        chan.append(round(float(ch.train_accuracy), 4))
        line = [f"[seed {sd}] rt={chan[-1]}"]
        for arm in ARMS:
            r = _run(sd, arm, ch)
            rows.append(r)
            line.append(f"{arm}={r['alive']}(food{r['food_pick_rate']},rnds{r['rounds']})")
        print(" ".join(line) + f" lethalfrac~{rows[-1]['lethal_frac']}", flush=True)

    def col(arm, key="alive"):
        return [r[key] for r in rows if r["arm"] == arm]
    summ = {arm: {"alive": round(float(np.mean(col(arm))), 4), "alive_ci": _ci(col(arm), 7),
                  "food_pick_rate": round(float(np.mean(col(arm, "food_pick_rate"))), 4),
                  "rounds": round(float(np.mean(col(arm, "rounds"))), 4)} for arm in ARMS}
    f = col("fusion")
    deltas = {f"fusion_minus_{a}": _ci([x - y for x, y in zip(f, col(a))], 50 + i)
              for i, a in enumerate(("scramble", "misroute", "mute"))}
    gates = {
        "channel_accurate": float(np.mean(chan)) > 0.7,
        "lethal_stakes_real": float(np.mean(col("mute"))) < 0.5,   # blind pickers actually die
        "fusion_survives": _ci(f, 7)[0] > 0.5,
        "fusion_beats_scramble": deltas["fusion_minus_scramble"][0] > 0.0,
        "fusion_beats_misroute": deltas["fusion_minus_misroute"][0] > 0.0,
        "fusion_beats_mute": deltas["fusion_minus_mute"][0] > 0.0,
    }
    verdict = ("RTC_G1D_LETHAL_CONTENT_LOAD_BEARING" if all(gates.values())
               else "RTC_G1D_INCONCLUSIVE")
    out = {"kind": "rtc_g1d_lethal", "seeds": LE_SEEDS,
           "prereg": {"RTC_SENSOR_SIGMA": rc.RTC_SENSOR_SIGMA, "LE_ROUNDS": LE_ROUNDS,
                      "LE_VENTS": LE_VENTS, "LE_STEP_PER_ROUND": LE_STEP_PER_ROUND,
                      "RTC_ADVECT_SPEED": rc.RTC_ADVECT_SPEED, "RTC_VENTS_PER_CHANNEL": rc.RTC_VENTS_PER_CHANNEL,
                      # G1D task-design stakes: OVERRIDES the MVP-0 frozen metabolism default (-1.8),
                      # selected post-hoc as the moderate-stakes window where content separates. NOT a prereg freeze.
                      "RTC_TOXIC_DEATH_g1d_taskdesign": rc.RTC_TOXIC_DEATH, "RTC_EAT_THETA": rc.RTC_EAT_THETA},
           "channel_roundtrip_mean": round(float(np.mean(chan)), 4),
           "mean_lethal_frac": round(float(np.mean(col("oracle", "lethal_frac"))), 4),
           "summary": summ, "deltas": deltas, "gates": gates, "verdict": verdict, "rows": rows}
    p = ROOT / "offscreen" / f"rtc_g1d_lethal_verdict_sig{rc.RTC_SENSOR_SIGMA}.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nchan_mean={np.mean(chan):.3f} lethal_frac~{out['mean_lethal_frac']}")
    for arm in ARMS:
        print(f"  {arm}: alive={summ[arm]['alive']} ci={summ[arm]['alive_ci']} "
              f"food_pick={summ[arm]['food_pick_rate']} rounds={summ[arm]['rounds']}")
    for k, v in deltas.items():
        print(f"  {k} {v}")
    print(f"VERDICT={verdict} gates={gates}\n-> {p}", flush=True)


if __name__ == "__main__":
    main()
