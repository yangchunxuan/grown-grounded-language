"""RTC MVP-1 REBUILD: genuine SPATIAL relay (fixes the red-team's FAKE_DISTRIBUTION
+ CONFIDENCE_GATE_CONFOUND + DEGENERATE_STATS critiques of rtc_g1b).

Mechanism = SPATIAL partial observability (not attribute-split of one cell):
- One focal agent moves on the torus; it perceives ONLY its own cell + 4 neighbours
  (FULL 4-channel, noisy/lagged) -> it can always act locally (NO -1000 gate trap).
- M relay posts sit at fixed scattered locations; each senses its OWN cell (full
  4-channel, noisy) and emits a grown-channel message about it.
- Food (w.field > theta) is sparse and advects; the focal agent can only learn where
  REMOTE blooms are by DECODING post messages. Pure-local foraging starves once the
  run exceeds the ~277-step no-food lifetime.

Arms (all ACT; necessity is spatial information, not a scoring gate):
  fusion    : decode posts -> navigate toward the best real remote bloom        (treatment)
  mute      : no remote info -> greedy local foraging only                       (info baseline)
  scramble  : posts send random messages -> navigate to garbage locations        (CONTENT control, clean)
  misroute  : posts decoded CORRECTLY but bound to PERMUTED locations            (binding control, non-degenerate)
  body_follow: navigate toward nearest post, ignore message content              (proximity control)

Headline clean comparison = fusion vs scramble (both act + both have remote targets;
only message CONTENT differs). misroute carries variance (real content, wrong place),
fixing the degenerate open-vs-zero statistics of rtc_g1b.

no-oracle: the decision reads only noisy/lagged perception + decoded messages; the true
field is read solely by eat() resolution (redline-permitted).
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
NEIGH = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))

# ---- pre-registerable knobs (env-overridable; frozen after the committed pilot) ----
SP_SEEDS = list(range(int(os.environ.get("RTC_SP_SEEDS", "8"))))
SP_STEPS = int(os.environ.get("RTC_SP_STEPS", "360"))
SP_POSTS = int(os.environ.get("RTC_SP_POSTS", "12"))
SP_DIST_COST = float(os.environ.get("RTC_SP_DIST_COST", "0.18"))
SP_MARGIN = float(os.environ.get("RTC_SP_MARGIN", "0.10"))
SP_CHAN_EPOCHS = int(os.environ.get("RTC_SP_CHAN_EPOCHS", "500"))
ARMS = ("fusion", "mute", "scramble", "misroute", "body_follow")
G = rc.RTC_GRID


def _wrap(d):
    d %= G
    return d - G if d > G // 2 else d


def _tdist(ax, ay, bx, by):
    return abs(_wrap(bx - ax)) + abs(_wrap(by - ay))


def _step_toward(x, y, tx, ty, rng):
    dx, dy = _wrap(tx - x), _wrap(ty - y)
    if dx == 0 and dy == 0:
        return x, y
    if abs(dx) >= abs(dy) and dx != 0:
        return (x + np.sign(dx)) % G, y
    return x, (y + np.sign(dy)) % G


def _perceive_edib(world, cx, cy, w, rng):
    vals = _sensor_values(world, cx, cy, FULL_BASIS, rng)
    return float(np.dot(w, vals))


def _remote_targets(world, arm, posts, channel, w, rng):
    if arm in ("mute",):
        return []
    if arm == "body_follow":
        return [(px, py, None) for (px, py) in posts]
    reads = []
    for (px, py) in posts:
        vals = _sensor_values(world, px, py, FULL_BASIS, rng)
        if arm == "scramble":
            dec = channel.decode(scramble_message(rng))
        else:  # fusion / misroute: real content
            dec = channel.decode(channel.emit(values_to_bands(vals)))
        edib = float(np.dot(w, bands_to_values(dec)))
        reads.append((px, py, edib))
    if arm == "misroute":  # real edibilities, permuted onto the wrong post locations
        locs = [(px, py) for (px, py, _) in reads]
        perm = rng.permutation(len(locs))
        reads = [(locs[perm[i]][0], locs[perm[i]][1], reads[i][2]) for i in range(len(reads))]
    return reads


def _run(seed, arm, channel):
    rng = np.random.default_rng(seed * 31 + len(arm))
    world = RTCWorld(seed)
    w = metabolic_vector(seed)
    state = MetabolicState(rc.RTC_ENERGY_INIT)
    prng = np.random.default_rng(seed + 7001)
    for _ in range(40):
        world.step()
    # relay posts SIT ON food sources (vents): a post reports a real local bloom, so
    # decoded messages carry actionable remote-food info (else messages report barren).
    vflat = np.asarray(world.vents).reshape(-1, 2)
    idx = prng.choice(len(vflat), min(SP_POSTS, len(vflat)), replace=False)
    posts = [(int(vflat[i][0]) % G, int(vflat[i][1]) % G) for i in idx]
    x, y = int(rng.integers(0, G)), int(rng.integers(0, G))
    outs = []
    for _ in range(SP_STEPS):
        if not state.alive:
            break
        world.step()
        # local candidates (own + 4 neighbours), distance 0/1
        local = []
        for dx, dy in NEIGH:
            cx, cy = (x + dx) % G, (y + dy) % G
            local.append((cx, cy, _perceive_edib(world, cx, cy, w, rng)))
        remote = _remote_targets(world, arm, posts, channel, w, rng)
        if arm == "body_follow":
            tx, ty = min(posts, key=lambda p: _tdist(x, y, p[0], p[1]))
        else:
            best, tx, ty = -1e9, x, y
            for cx, cy, edib in local:
                s = edib - SP_DIST_COST * _tdist(x, y, cx, cy)
                if s > best:
                    best, tx, ty = s, cx, cy
            for cx, cy, edib in remote:
                s = edib - SP_DIST_COST * _tdist(x, y, cx, cy)
                if s > best:
                    best, tx, ty = s, cx, cy
        x, y = _step_toward(x, y, tx, ty, rng)
        here = _perceive_edib(world, x, y, w, rng)
        if here > rc.RTC_EAT_THETA + SP_MARGIN:
            outs.append(eat(state, world.patch(x, y), w)["outcome"])
        else:
            state.age += 1
            state.energy -= rc.RTC_UPKEEP
            if state.energy <= 0:
                state.energy, state.alive = 0.0, False
            outs.append("rest")
    n = max(1, len(outs))
    return {"seed": seed, "arm": arm, "alive": float(state.alive), "age": state.age,
            "final_energy": round(float(state.energy), 3),
            "eat_rate": round(outs.count("eat") / n, 4),
            "tox_rate": round(sum(o in ("toxin", "toxic_death") for o in outs) / n, 4),
            "rest_rate": round(outs.count("rest") / n, 4)}


def main():
    rows, chan = [], []
    for sd in SP_SEEDS:
        ch = train_relay_channel(9000 + sd, all_band_tuples(), epochs=SP_CHAN_EPOCHS)
        chan.append(round(float(ch.train_accuracy), 4))
        line = [f"[seed {sd}] roundtrip={chan[-1]}"]
        for arm in ARMS:
            r = _run(sd, arm, ch)
            rows.append(r)
            line.append(f"{arm}={r['alive']}(age{r['age']},eat{r['eat_rate']},tox{r['tox_rate']})")
        print(" ".join(line), flush=True)

    def col(arm, key="alive"):
        return [r[key] for r in rows if r["arm"] == arm]
    summ = {arm: {k: round(float(np.mean(col(arm, k))), 4) for k in
                  ("alive", "age", "eat_rate", "tox_rate", "rest_rate")} | {"alive_ci": _ci(col(arm), 7)}
            for arm in ARMS}
    f = col("fusion")
    deltas = {f"fusion_minus_{a}": _ci([x - y for x, y in zip(f, col(a))], 50 + i)
              for i, a in enumerate(("mute", "scramble", "misroute", "body_follow"))}
    gates = {
        "channel_accurate": float(np.mean(chan)) > 0.7,
        "fusion_survives": _ci(f, 7)[0] > 0.0,
        "fusion_beats_scramble": deltas["fusion_minus_scramble"][0] > 0.0,   # HEADLINE clean (content)
        "fusion_beats_misroute": deltas["fusion_minus_misroute"][0] > 0.0,   # location-binding, non-degenerate
        "fusion_beats_mute": deltas["fusion_minus_mute"][0] > 0.0,           # spatial info availability
    }
    verdict = "RTC_G1C_SPATIAL_CONTENT_LOAD_BEARING" if all(gates.values()) else "RTC_G1C_INCONCLUSIVE"
    out = {"kind": "rtc_g1c_spatial", "seeds": SP_SEEDS,
           "prereg": {"RTC_SENSOR_SIGMA": rc.RTC_SENSOR_SIGMA, "SP_STEPS": SP_STEPS,
                      "SP_POSTS": SP_POSTS, "SP_DIST_COST": SP_DIST_COST, "SP_MARGIN": SP_MARGIN,
                      "SP_CHAN_EPOCHS": SP_CHAN_EPOCHS},
           "channel_roundtrip": chan, "channel_roundtrip_mean": round(float(np.mean(chan)), 4),
           "summary": summ, "deltas": deltas, "gates": gates, "verdict": verdict, "rows": rows}
    p = ROOT / "offscreen" / f"rtc_g1c_spatial_verdict_sig{rc.RTC_SENSOR_SIGMA}.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nchan_mean={np.mean(chan):.3f}")
    for arm in ARMS:
        print(f"  {arm}: alive={summ[arm]['alive']} ci={summ[arm]['alive_ci']} "
              f"age={summ[arm]['age']} eat={summ[arm]['eat_rate']} tox={summ[arm]['tox_rate']}")
    for k, v in deltas.items():
        print(f"  {k} {v}")
    print(f"VERDICT={verdict} gates={gates}\n-> {p}", flush=True)


if __name__ == "__main__":
    main()
