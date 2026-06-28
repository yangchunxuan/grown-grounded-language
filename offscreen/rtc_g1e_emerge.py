"""RTC MVP-1 EMERGENCE test: does USING the grown channel's content EMERGE under
selection, rather than being hardwired? Converts g1d's installed-necessity into an
evolution-of-signal-use result (red-team CONSTRUCTED_NECESSITY firming move).

Each agent has ONE heritable gene trust in [0,1]: per round it uses the decoded
message (pick argmax decoded edibility) with prob=trust, else ignores it (random
pick). trust=0 == mute behaviour; trust=1 == fusion behaviour. The population starts
near trust~0 (message-ignorers) in the g1d lethal-signaling world (moderate-stakes
window) and reproduces by survival fitness with mutation.

Worlds (isolate the two alternative explanations):
  real     : real decoded content + SELECTION (fitness reproduction) -> trust should RISE
  scramble : random-message content + SELECTION -> using garbage can't help -> trust flat
  drift    : real content + NO selection (random reproduction) -> trust flat

Emergence is shown iff trust RISES in 'real' but stays flat in BOTH controls: content-use
is then SELECTED FOR because the content is real, not installed by the experimenter.

no-oracle: per-round decoded/true edibilities are computed once (broadcast); the decision
reads only decoded messages; world.patch (true field) only resolves eat()/true_edib.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

import numpy as np

import config.prereg_rtc as rc
from rtc_language import (all_band_tuples, bands_to_values, scramble_message,
                          train_relay_channel, values_to_bands)
from rtc_metabolism import metabolic_vector
from rtc_world import RTCWorld
from offscreen.rtc_g1_run import _ci, _sensor_values

ROOT = Path(__file__).resolve().parents[1]
FULL_BASIS = (0, 1, 2, 3)
G = rc.RTC_GRID

EM_SEEDS = list(range(int(os.environ.get("RTC_EM_SEEDS", "6"))))
EM_POP = int(os.environ.get("RTC_EM_POP", "40"))
EM_GENS = int(os.environ.get("RTC_EM_GENS", "30"))
EM_T = int(os.environ.get("RTC_EM_T", "60"))
EM_STEP = int(os.environ.get("RTC_EM_STEP", "3"))
EM_VENTS = int(os.environ.get("RTC_EM_VENTS", "12"))
EM_MUT = float(os.environ.get("RTC_EM_MUT", "0.1"))
EM_INIT_MEAN = float(os.environ.get("RTC_EM_INIT_MEAN", "0.15"))
EM_INIT_SD = float(os.environ.get("RTC_EM_INIT_SD", "0.10"))
EM_CHAN_EPOCHS = int(os.environ.get("RTC_EM_CHAN_EPOCHS", "500"))
MODES = ("real", "scramble", "drift")


def _decoded_vec(world, posts, channel, w, rng, scramble):
    out = []
    for (px, py) in posts:
        vals = _sensor_values(world, px, py, FULL_BASIS, rng)
        dec = channel.decode(scramble_message(rng)) if scramble else channel.decode(channel.emit(values_to_bands(vals)))
        out.append(float(np.dot(w, bands_to_values(dec))))
    return np.asarray(out)


def _live_generation(world, posts, channel, w, trust, rng, scramble):
    n = len(trust)
    energy = np.full(n, rc.RTC_ENERGY_INIT)
    alive = np.ones(n, dtype=bool)
    rounds = np.zeros(n)
    for _ in range(EM_T):
        for _ in range(EM_STEP):
            world.step()
        decoded = _decoded_vec(world, posts, channel, w, rng, scramble)
        true = np.asarray([float(np.dot(w, world.patch(px, py))) for (px, py) in posts])
        best = int(np.argmax(decoded))
        live_idx = np.where(alive)[0]
        if live_idx.size == 0:
            break
        use = rng.random(live_idx.size) < trust[live_idx]
        rand_pick = rng.integers(0, len(posts), live_idx.size)
        picks = np.where(use, best, rand_pick)
        for k, i in enumerate(live_idx):
            r = true[picks[k]]
            energy[i] -= rc.RTC_UPKEEP
            if r < rc.RTC_TOXIC_DEATH:
                alive[i] = False
            elif r > rc.RTC_EAT_THETA:
                energy[i] = min(energy[i] + min(rc.RTC_EAT_CLIP, r), 3 * rc.RTC_ENERGY_INIT)
            else:
                energy[i] -= rc.RTC_TOXIN_COST
            if energy[i] <= 0:
                alive[i] = False
            if alive[i]:
                rounds[i] += 1
    return rounds + energy * 0.01  # fitness: rounds survived (+ tiny energy tiebreak)


def _reproduce(trust, fitness, rng, select):
    n = len(trust)
    order = np.argsort(-fitness) if select else rng.permutation(n)
    parents = order[: n // 2]
    child = np.concatenate([trust[parents], trust[parents]])
    return np.clip(child + rng.normal(0, EM_MUT, len(child)), 0.0, 1.0)


def _run_mode(seed, mode):
    rng = np.random.default_rng(seed * 53 + len(mode))
    world = RTCWorld(seed)
    for _ in range(40):
        world.step()
    prng = np.random.default_rng(seed + 7001)
    vflat = np.asarray(world.vents).reshape(-1, 2)
    idx = prng.choice(len(vflat), min(EM_VENTS, len(vflat)), replace=False)
    posts = [(int(vflat[i][0]) % G, int(vflat[i][1]) % G) for i in idx]
    w = metabolic_vector(seed)
    channel = train_relay_channel(9000 + seed, all_band_tuples(), epochs=EM_CHAN_EPOCHS)
    trust = np.clip(rng.normal(EM_INIT_MEAN, EM_INIT_SD, EM_POP), 0.0, 1.0)
    traj = [float(np.mean(trust))]
    scramble = (mode == "scramble")
    select = (mode != "drift")
    for _ in range(EM_GENS):
        fit = _live_generation(world, posts, channel, w, trust, rng, scramble)
        trust = _reproduce(trust, fit, rng, select)
        traj.append(float(np.mean(trust)))
    return {"seed": seed, "mode": mode, "init": round(traj[0], 4),
            "final": round(traj[-1], 4), "rise": round(traj[-1] - traj[0], 4), "traj": [round(t, 3) for t in traj]}


def main():
    rows = []
    for sd in EM_SEEDS:
        line = [f"[seed {sd}]"]
        for mode in MODES:
            r = _run_mode(sd, mode)
            rows.append(r)
            line.append(f"{mode}:{r['init']}->{r['final']}(+{r['rise']})")
        print(" ".join(line), flush=True)

    def fin(mode):
        return [r["final"] for r in rows if r["mode"] == mode]

    def rise(mode):
        return [r["rise"] for r in rows if r["mode"] == mode]
    real_rise_ci = _ci(rise("real"), 11)
    d_scr = _ci([a - b for a, b in zip(fin("real"), fin("scramble"))], 12)
    d_dft = _ci([a - b for a, b in zip(fin("real"), fin("drift"))], 13)
    gates = {
        "real_trust_rises": real_rise_ci[0] > 0.0,
        "real_beats_scramble": d_scr[0] > 0.0,
        "real_beats_drift": d_dft[0] > 0.0,
    }
    verdict = "RTC_G1E_CONTENT_USE_EMERGES" if all(gates.values()) else "RTC_G1E_INCONCLUSIVE"
    out = {"kind": "rtc_g1e_emerge", "seeds": EM_SEEDS,
           "prereg": {"RTC_SENSOR_SIGMA": rc.RTC_SENSOR_SIGMA, "RTC_TOXIC_DEATH_g1d_taskdesign": rc.RTC_TOXIC_DEATH,
                      "EM_POP": EM_POP, "EM_GENS": EM_GENS, "EM_T": EM_T, "EM_VENTS": EM_VENTS,
                      "EM_MUT": EM_MUT, "EM_INIT_MEAN": EM_INIT_MEAN},
           "summary": {m: {"init_mean": round(float(np.mean([r["init"] for r in rows if r["mode"] == m])), 4),
                           "final_mean": round(float(np.mean(fin(m))), 4),
                           "final_ci": _ci(fin(m), 20 + i)} for i, m in enumerate(MODES)},
           "real_rise_ci": real_rise_ci, "real_minus_scramble_ci": d_scr, "real_minus_drift_ci": d_dft,
           "gates": gates, "verdict": verdict, "rows": rows}
    p = ROOT / "offscreen" / f"rtc_g1e_emerge_verdict_tox{rc.RTC_TOXIC_DEATH}.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nreal: {out['summary']['real']['init_mean']}->{out['summary']['real']['final_mean']} ci={out['summary']['real']['final_ci']}")
    print(f"scramble final={out['summary']['scramble']['final_mean']} ci={out['summary']['scramble']['final_ci']}")
    print(f"drift final={out['summary']['drift']['final_mean']} ci={out['summary']['drift']['final_ci']}")
    print(f"real_rise {real_rise_ci}  real-scramble {d_scr}  real-drift {d_dft}")
    print(f"VERDICT={verdict} gates={gates}\n-> {p}", flush=True)


if __name__ == "__main__":
    main()
