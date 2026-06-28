"""RTC MVP-0 G0 world-validity gate.

The full-channel predictor is intentionally fenced as an oracle ceiling: it
uses the world-side field interface and is only a solvability upper bound.
Legal learnability from perception history is deferred to MVP-2/G2.
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np

import config.prereg_rtc as rc
from rtc_metabolism import MetabolicState, eat, metabolic_vector
from rtc_perception import Body, perceive
from rtc_world import RTCWorld


ROOT = Path(__file__).resolve().parents[1]


def _ci(vals, seed):
    vals = np.asarray(vals, float)
    if len(vals) < 2:
        m = round(float(vals.mean()), 4) if len(vals) else float("nan")
        return [m, m]
    rng = np.random.default_rng(seed)
    bs = [float(rng.choice(vals, len(vals), True).mean()) for _ in range(rc.RTC_G0_BOOTSTRAP_REPS)]
    return [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


class FlowForecaster:
    def __init__(self):
        self.ema = None

    def predict(self, obs4):
        self.ema = obs4.copy() if self.ema is None else 0.68 * self.ema + 0.32 * obs4
        return self.ema


class ReservoirPolicy:
    def __init__(self, seed):
        rng = np.random.default_rng(seed + 700)
        self.w = rng.normal(0, 1, 2)

    def score(self, obs4):
        return np.tensordot(self.w, obs4, axes=(0, 0))


def _smooth_win(a):
    return (a + np.roll(a, 1, -1) + np.roll(a, -1, -1)
            + np.roll(a, 1, -2) + np.roll(a, -1, -2)) / 5.0


def _clock_r2(seed, steps=180):
    w = RTCWorld(seed)
    xs, ys = [], []
    for _ in range(steps):
        phase = w.tide_phase
        feats = [1.0, math.sin(phase), math.cos(phase), math.sin(2 * phase), math.cos(2 * phase)]
        sample = w.field.reshape(rc.RTC_K, -1)[:, ::37].T
        xs.extend([feats] * len(sample))
        ys.extend(sample)
        w.step()
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    cut = len(x) // 2
    r2 = []
    for k in range(rc.RTC_K):
        beta, *_ = np.linalg.lstsq(x[:cut], y[:cut, k], rcond=None)
        pred = x[cut:] @ beta
        var = float(np.var(y[cut:, k])) + 1e-9
        r2.append(max(0.0, 1.0 - float(np.mean((y[cut:, k] - pred) ** 2)) / var))
    return [round(float(v), 4) for v in r2]


def _run_policy(seed, policy):
    rng = np.random.default_rng(seed * 17 + len(policy))
    world = RTCWorld(seed)
    weights = metabolic_vector(seed)
    state = MetabolicState(rc.RTC_ENERGY_INIT)
    x = int(rng.integers(0, rc.RTC_GRID))
    y = int(rng.integers(0, rc.RTC_GRID))
    sensors = tuple(rng.choice(rc.RTC_K, 2, replace=False))
    forecaster = FlowForecaster()
    reservoir = ReservoirPolicy(seed)
    outcomes = []
    for _ in range(40):
        world.step()
    for step in range(rc.RTC_G0_STEPS):
        if not state.alive:
            break
        world.step()
        body = Body(x, y, state.energy, state.age, step % 4, sensors)
        _ = perceive(body, world, (), rng)  # redline seam smoke: return is legal-only
        candidates = world.candidates(x, y, radius=2)
        if policy == "fenced_oracle_ceiling":
            scores = []
            lags = np.arange(rc.RTC_SENSOR_LAG, rc.RTC_SENSOR_LAG + 4, dtype=float)
            xfit = np.stack([np.ones_like(lags), -lags], axis=1)
            for j, (cx, cy) in enumerate(candidates):
                hist = np.stack([world.patch(cx, cy, lag=int(lg)) for lg in lags])
                beta, *_ = np.linalg.lstsq(xfit, hist, rcond=None)
                pred = beta[0]
                scores.append((float(weights @ pred), j))
        elif policy == "solo_no_fusion":
            obs = world.window(x, y, sensors, lag=rc.RTC_SENSOR_LAG)
            obs = obs + rng.normal(0, rc.RTC_SENSOR_SIGMA, obs.shape)
            full = np.zeros((rc.RTC_K, rc.RTC_SENSOR_WIN, rc.RTC_SENSOR_WIN), dtype=np.float32)
            for a, ch in enumerate(sensors):
                full[ch] = obs[a]
            scores = [(float(weights @ full[:, j // 5, j % 5]), j) for j in range(25)]
        elif policy == "reservoir":
            obs = world.window(x, y, sensors, lag=rc.RTC_SENSOR_LAG)
            obs = obs + rng.normal(0, rc.RTC_SENSOR_SIGMA, obs.shape)
            sc = reservoir.score(obs)
            scores = [(float(sc[j // 5, j % 5]), j) for j in range(25)]
        elif policy == "clock_only":
            phase = world.tide_phase
            scores = [(math.sin(phase + j * 1.7) + 0.15 * math.cos(step + j), j) for j in range(25)]
        else:
            scores = [(rng.normal(), j) for j in range(25)]
        best, pick = max(scores)
        if best < rc.RTC_EAT_THETA:
            state.age += 1
            state.energy -= rc.RTC_UPKEEP
            if state.energy <= 0:
                state.energy = 0.0
                state.alive = False
            outcomes.append("rest")
            continue
        x, y = candidates[pick]
        out = eat(state, world.patch(x, y), weights)
        outcomes.append(out["outcome"])
    return {
        "seed": seed, "policy": policy, "alive": float(state.alive),
        "age": state.age, "final_energy": round(float(state.energy), 4),
        "eat_rate": round(outcomes.count("eat") / max(1, len(outcomes)), 4),
        "toxin_rate": round(sum(o != "eat" for o in outcomes) / max(1, len(outcomes)), 4),
    }


def _scan_redline():
    files = ["rtc_perception.py", "rtc_world.py", "rtc_metabolism.py"]
    forbidden = ("astar", "find_nearest", "navigator", "next_step_action")
    hits = {}
    for rel in files:
        src = (ROOT / rel).read_text(encoding="utf-8").lower()
        bad = [tok for tok in forbidden if re.search(r"\b" + re.escape(tok) + r"\b", src)]
        if bad:
            hits[rel] = bad
    return hits


def summarize(rows):
    out = {}
    for pol in sorted({r["policy"] for r in rows}):
        rs = [r for r in rows if r["policy"] == pol]
        out[pol] = {}
        for k in ("alive", "age", "final_energy", "eat_rate", "toxin_rate"):
            vals = [r[k] for r in rs]
            out[pol][k] = round(float(np.mean(vals)), 4)
            out[pol][k + "_ci"] = _ci(vals, len(k) + len(pol))
        out[pol]["rows"] = rs
    return out


def main():
    t0 = time.time()
    policies = ("fenced_oracle_ceiling", "solo_no_fusion", "reservoir", "clock_only")
    rows = []
    clock_r2 = []
    for sd in range(rc.RTC_G0_SEEDS):
        clock_r2.append(_clock_r2(1000 + sd))
        for pol in policies:
            row = _run_policy(2000 + sd, pol)
            rows.append(row)
            print(f"[seed {sd} {pol}] alive={row['alive']} age={row['age']} "
                  f"energy={row['final_energy']} eat={row['eat_rate']}", flush=True)
    summ = summarize(rows)
    max_clock_r2 = float(np.max(clock_r2))
    redline_hits = _scan_redline()
    fore = summ["fenced_oracle_ceiling"]; solo = summ["solo_no_fusion"]
    res = summ["reservoir"]; clk = summ["clock_only"]
    gates = {
        "fenced_oracle_ceiling_lives": fore["alive_ci"][0] >= rc.RTC_G0_FORECASTER_ALIVE_MIN,
        "solo_starves": solo["alive_ci"][1] <= rc.RTC_G0_CONTROL_ALIVE_MAX,
        "reservoir_starves": res["alive_ci"][1] <= rc.RTC_G0_CONTROL_ALIVE_MAX,
        "clock_stays_solo_floor": clk["alive"] <= solo["alive"] + rc.RTC_G0_CLOCK_LIFT_MAX,
        "clock_predicts_variance_lt_0_03": max_clock_r2 < rc.RTC_G0_CLOCK_R2_MAX,
        "redline_scan_clean": not redline_hits,
    }
    verdict = "RTC_G0_WORLD_VALID" if all(gates.values()) else "RTC_G0_WORLD_INVALID_STOP"
    out = {
        "kind": "rtc_mvp0_g0_verdict_v1", "block": "powered",
        "seeds": list(range(rc.RTC_G0_SEEDS)), "frozen": rc.RTC_FROZEN,
        "summary": summ, "clock_r2_by_seed_channel": clock_r2,
        "clock_r2_max": round(max_clock_r2, 5), "redline_hits": redline_hits,
        "gates": gates, "verdict": verdict,
        "honest_claim": (
            "MVP-0 only: hidden rich field, perception seam, metabolism, and G0 "
            "world-validity. Full-channel predictor is fenced oracle ceiling, not "
            "a legal learnability claim."
        ),
        "wall_seconds": round(time.time() - t0, 1),
    }
    path = "offscreen/rtc_g0_verdict.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"VERDICT={verdict} gates={gates} clock_r2_max={max_clock_r2:.4f} -> {path}", flush=True)
    return 0 if verdict == "RTC_G0_WORLD_VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
