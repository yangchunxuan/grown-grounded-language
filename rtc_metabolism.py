"""RTC MVP-0 metabolism and eating scorer."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import config.prereg_rtc as rc


@dataclass
class MetabolicState:
    energy: float
    alive: bool = True
    age: int = 0


def metabolic_vector(seed: int, k: int = rc.RTC_K) -> np.ndarray:
    rng = np.random.default_rng(int(seed) + 910)
    w = rng.normal(0, 1, k)
    w += np.sign(w + 1e-6) * 0.35
    w /= max(1e-6, np.linalg.norm(w))
    assert np.all(np.abs(w) > 0.05)
    return w.astype(np.float32)


def edible_value(patch_values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.dot(np.asarray(weights, float), np.asarray(patch_values, float)))


def eat(state: MetabolicState, patch_values: np.ndarray, weights: np.ndarray) -> dict:
    r = edible_value(patch_values, weights)
    state.age += 1
    state.energy -= rc.RTC_UPKEEP
    toxic = r < rc.RTC_TOXIC_DEATH
    if toxic:
        state.alive = False
        state.energy = 0.0
        delta = -state.energy
        outcome = "toxic_death"
    elif r > rc.RTC_EAT_THETA:
        delta = min(rc.RTC_EAT_CLIP, r)
        state.energy += delta
        outcome = "eat"
    else:
        delta = -rc.RTC_TOXIN_COST
        state.energy += delta
        outcome = "toxin"
    if state.energy <= 0:
        state.energy = 0.0
        state.alive = False
    return {"r": round(r, 5), "delta": round(float(delta), 5),
            "outcome": outcome, "energy": round(float(state.energy), 5),
            "alive": bool(state.alive)}
