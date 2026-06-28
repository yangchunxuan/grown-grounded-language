"""RTC MVP-1 G1 gate: fusion plus relay channel, no MVP-2."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import numpy as np

import config.prereg_rtc as rc
from rtc_fusion import CTMFilter, aggregate, decoded_packet, packet_score, private_packet
from rtc_language import (
    HolisticCodebook,
    all_band_tuples,
    mute_message,
    neutral_bands,
    scramble_message,
    train_relay_channel,
)
from rtc_metabolism import MetabolicState, eat, metabolic_vector
from rtc_world import RTCWorld

ROOT = Path(__file__).resolve().parents[1]
BASIS = ((0, 1), (2, 3), (0, 2), (1, 3))
CANDIDATES = ((0, -2), (2, 0), (0, 2), (-2, 0))


def _ci(vals, seed):
    vals = np.asarray(vals, float)
    if len(vals) < 2:
        m = round(float(vals.mean()), 4) if len(vals) else float("nan")
        return [m, m]
    rng = np.random.default_rng(seed)
    bs = [float(rng.choice(vals, len(vals), True).mean()) for _ in range(rc.RTC_G1_BOOTSTRAP_REPS)]
    return [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


def _sensor_values(world, x, y, basis, rng):
    lags = np.arange(rc.RTC_SENSOR_LAG, rc.RTC_SENSOR_LAG + 4, dtype=float)
    hist = []
    for lag in lags:
        win = world.window(x, y, basis, lag=int(lag))
        val = win[:, rc.RTC_SENSOR_WIN // 2, rc.RTC_SENSOR_WIN // 2]
        hist.append(val + rng.normal(0, rc.RTC_SENSOR_SIGMA * 0.45, len(basis)))
    yhist = np.stack(hist)
    xfit = np.stack([np.ones_like(lags), -lags], axis=1)
    beta, *_ = np.linalg.lstsq(xfit, yhist, rcond=None)
    return beta[0]


def _collect_forecast_refs(seed, steps=900):
    rng = np.random.default_rng(seed + 3300)
    world = RTCWorld(seed)
    refs = {neutral_bands()}
    x = int(rng.integers(0, rc.RTC_GRID)); y = int(rng.integers(0, rc.RTC_GRID))
    for _ in range(40):
        world.step()
    for t in range(steps):
        world.step()
        dx, dy = CANDIDATES[t % len(CANDIDATES)]
        cx, cy = (x + dx) % rc.RTC_GRID, (y + dy) % rc.RTC_GRID
        parts = []
        for basis in BASIS:
            pkt = private_packet(_sensor_values(world, cx, cy, basis, rng), basis)
            refs.add(pkt.bands)
            parts.append(pkt)
        refs.add(aggregate(parts[0], parts[1:]).bands)
        if t % 9 == 0:
            x = (x + int(rng.integers(-2, 3))) % rc.RTC_GRID
            y = (y + int(rng.integers(-2, 3))) % rc.RTC_GRID
    return sorted(refs)


def _partner_packets(world, channel, cx, cy, rng, mode):
    out = []
    for basis in BASIS:
        pkt = private_packet(_sensor_values(world, cx, cy, basis, rng), basis)
        if mode == "mute":
            out.append(decoded_packet(neutral_bands(), strength=0.0))
            continue
        elif mode == "scramble":
            msg = scramble_message(rng)
        else:
            msg = channel.emit(pkt.bands)
        bands = channel.decode(msg)
        one = 0 if mode == "single_factor_mute" else None
        out.append(decoded_packet(bands, single_factor=one))
    return out


def _candidate_estimate(world, channel, x, y, self_basis, rng, mode):
    scored = []
    for j, (dx, dy) in enumerate(CANDIDATES):
        cx, cy = (x + dx) % rc.RTC_GRID, (y + dy) % rc.RTC_GRID
        self_pkt = private_packet(_sensor_values(world, cx, cy, self_basis, rng), self_basis)
        if mode in ("fusion", "mute", "scramble", "single_factor_mute"):
            msgs = _partner_packets(world, channel, cx, cy, rng, mode)
            pkt = aggregate(self_pkt, msgs)
        else:
            pkt = self_pkt
        scored.append((cx, cy, pkt, j))
    return scored


def _run_survival(seed, policy, channel):
    rng = np.random.default_rng(seed * 17 + len(policy))
    world = RTCWorld(seed)
    weights = metabolic_vector(seed)
    state = MetabolicState(rc.RTC_ENERGY_INIT)
    filt = CTMFilter(seed)
    x = int(rng.integers(0, rc.RTC_GRID)); y = int(rng.integers(0, rc.RTC_GRID))
    self_basis = BASIS[seed % len(BASIS)]
    outcomes = []
    for _ in range(40):
        world.step()
    for step in range(rc.RTC_G1_STEPS):
        if not state.alive:
            break
        world.step()
        estimates = _candidate_estimate(world, channel, x, y, self_basis, rng, policy)
        if policy == "body_follow":
            pick = (step + seed) % len(estimates)
            best = packet_score(estimates[pick][2], weights)
        else:
            scores = []
            for cx, cy, pkt, j in estimates:
                z = filt.latent(pkt, state.energy, state.age)
                scores.append((packet_score(pkt, weights) + 0.01 * float(z[0]), j))
            best, pick = max(scores)
        if best < rc.RTC_EAT_THETA + rc.RTC_G1_ACTION_MARGIN:
            state.age += 1
            state.energy -= rc.RTC_UPKEEP
            if state.energy <= 0:
                state.energy = 0.0
                state.alive = False
            outcomes.append("rest")
            continue
        x, y = estimates[pick][0], estimates[pick][1]
        out = eat(state, world.patch(x, y), weights)
        outcomes.append(out["outcome"])
    return {
        "seed": seed,
        "policy": policy,
        "alive": float(state.alive),
        "age": state.age,
        "final_energy": round(float(state.energy), 4),
        "eat_rate": round(outcomes.count("eat") / max(1, len(outcomes)), 4),
        "bad_rate": round(sum(o not in ("eat", "rest") for o in outcomes) / max(1, len(outcomes)), 4),
        "rest_rate": round(outcomes.count("rest") / max(1, len(outcomes)), 4),
    }


def _summarize(rows):
    out = {}
    for pol in sorted({r["policy"] for r in rows}):
        rs = [r for r in rows if r["policy"] == pol]
        out[pol] = {}
        for key in ("alive", "age", "final_energy", "eat_rate", "bad_rate", "rest_rate"):
            vals = [r[key] for r in rs]
            out[pol][key] = round(float(np.mean(vals)), 4)
            out[pol][key + "_ci"] = _ci(vals, len(key) + len(pol))
        out[pol]["rows"] = rs
    return out


def _joint_probe(seed):
    refs = all_band_tuples()
    held = [r for r in refs if sum((i + 1) * r[i] for i in range(rc.RTC_K)) % rc.RTC_BANDS == seed % rc.RTC_BANDS]
    seen = [r for r in refs if r not in set(held)]
    grown = train_relay_channel(7000 + seed, seen, epochs=rc.RTC_G1_JOINT_EPOCHS)
    hol = HolisticCodebook(8000 + seed, seen)
    ga = np.mean([grown.decode(grown.emit(r)) == r for r in held])
    ha = np.mean([hol.decode(hol.emit(r)) == r for r in held])
    return {
        "seed": seed,
        "heldout_n": len(held),
        "seen_n": len(seen),
        "grown_heldout_joint": round(float(ga), 4),
        "holistic_heldout_joint": round(float(ha), 4),
        "chance": round(float(rc.RTC_G1_JOINT_CHANCE), 5),
    }


def _scan_redline():
    files = ["rtc_perception.py", "rtc_language.py", "rtc_fusion.py"]
    forbidden = (r"world\.patch\s*\(", r"\.field\b", r"patch_label", r"true_coord",
                 r"\bgenome\b", r"find_nearest", r"next_step_action", r"astar")
    hits = {}
    for rel in files:
        src = (ROOT / rel).read_text(encoding="utf-8").lower()
        bad = [pat for pat in forbidden if re.search(pat, src)]
        if bad:
            hits[rel] = bad
    return hits


def main():
    t0 = time.time()
    rows = []
    probes = []
    lang_rows = []
    policies = ("fusion", "solo", "body_follow", "mute", "scramble", "single_factor_mute")
    for sd in range(rc.RTC_G1_SEEDS):
        refs = _collect_forecast_refs(3000 + sd)
        channel = train_relay_channel(4000 + sd, refs)
        lang_rows.append({"seed": sd, "seen_refs": channel.seen_count,
                          "train_full_roundtrip": round(channel.train_accuracy, 4)})
        for pol in policies:
            row = _run_survival(5000 + sd, pol, channel)
            rows.append(row)
            print(f"[seed {sd} {pol}] alive={row['alive']} age={row['age']} "
                  f"energy={row['final_energy']} eat={row['eat_rate']}", flush=True)
        jp = _joint_probe(sd)
        probes.append(jp)
        print(f"[seed {sd} JOINT] grown={jp['grown_heldout_joint']:.3f} "
              f"holistic={jp['holistic_heldout_joint']:.3f}", flush=True)
    summ = _summarize(rows)
    lift = [r["alive"] for r in rows if r["policy"] == "fusion"]
    solo = [r["alive"] for r in rows if r["policy"] == "solo"]
    body = [r["alive"] for r in rows if r["policy"] == "body_follow"]
    mute = [r["alive"] for r in rows if r["policy"] == "mute"]
    scr = [r["alive"] for r in rows if r["policy"] == "scramble"]
    sf_eat = [r["eat_rate"] for r in rows if r["policy"] == "single_factor_mute"]
    fu_eat = [r["eat_rate"] for r in rows if r["policy"] == "fusion"]
    deltas = {
        "fusion_minus_solo_alive": [a - b for a, b in zip(lift, solo)],
        "body_minus_solo_alive": [a - b for a, b in zip(body, solo)],
        "mute_minus_solo_alive": [a - b for a, b in zip(mute, solo)],
        "scramble_minus_solo_alive": [a - b for a, b in zip(scr, solo)],
        "single_factor_eat_frac_of_fusion": [
            a / max(1e-6, b) for a, b in zip(sf_eat, fu_eat)
        ],
    }
    joint_g = [p["grown_heldout_joint"] for p in probes]
    joint_h = [p["holistic_heldout_joint"] for p in probes]
    redline_hits = _scan_redline()
    gates = {
        "fusion_lifts_survival": _ci(deltas["fusion_minus_solo_alive"], 41)[0] > rc.RTC_G1_FUSION_LIFT_MIN,
        "body_follow_null_fails": _ci(deltas["body_minus_solo_alive"], 42)[1] <= rc.RTC_G1_NULL_LIFT_MAX,
        "mute_returns_to_floor": _ci(deltas["mute_minus_solo_alive"], 43)[1] <= rc.RTC_G1_NULL_LIFT_MAX,
        "scramble_returns_to_floor": _ci(deltas["scramble_minus_solo_alive"], 44)[1] <= rc.RTC_G1_NULL_LIFT_MAX,
        "single_factor_mute_fails": _ci(deltas["single_factor_eat_frac_of_fusion"], 45)[1]
        <= rc.RTC_G1_SINGLE_FACTOR_EAT_MAX_FRAC,
        "redline_scan_clean": not redline_hits,
    }
    joint_gate = {
        "grown_ci": _ci(joint_g, 51),
        "holistic_ci": _ci(joint_h, 52),
        "grown_minus_holistic_ci": _ci([g - h for g, h in zip(joint_g, joint_h)], 53),
        "verdict": "GROWN_JOINT_PASS"
        if _ci(joint_g, 51)[0] > rc.RTC_G1_JOINT_CHANCE
        and _ci([g - h for g, h in zip(joint_g, joint_h)], 53)[0] > 0
        else "HALF_COMPOSITIONAL_NULL",
        "rows": probes,
    }
    verdict = "RTC_G1_FUSION_RELAY_PASS" if all(gates.values()) else "RTC_G1_STOP_FAILED_GATE"
    out = {
        "kind": "rtc_mvp1_g1_verdict_v1",
        "block": "powered",
        "seeds": list(range(rc.RTC_G1_SEEDS)),
        "frozen": rc.RTC_FROZEN,
        "language_training": lang_rows,
        "summary": summ,
        "deltas": {k: {"mean": round(float(np.mean(v)), 4), "ci": _ci(v, len(k))} for k, v in deltas.items()},
        "joint_probe": joint_gate,
        "redline_hits": redline_hits,
        "gates": gates,
        "verdict": verdict,
        "honest_claim": (
            "MVP-1 only: relay messages carry self/fused forecast bands; survival lift "
            "is tested against body-follow, mute, scramble, and single-factor controls. "
            "WM legality is deferred to MVP-2/G2."
        ),
        "wall_seconds": round(time.time() - t0, 1),
    }
    path = "offscreen/rtc_g1_verdict.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"VERDICT={verdict} gates={gates} joint={joint_gate['verdict']} -> {path}", flush=True)
    return 0 if verdict == "RTC_G1_FUSION_RELAY_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
