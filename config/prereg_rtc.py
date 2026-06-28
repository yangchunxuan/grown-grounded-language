"""Frozen preregistration for RTC staged rich-world gates.

MVP-0 freezes the hidden field, no-oracle perception seam, metabolism, and G0
calibration. MVP-1 adds fusion plus the relay channel only; WM, reproduction,
and cooperation stay out of scope.
"""
from __future__ import annotations

import os


def _i(name: str, default: int) -> int:
    v = os.environ.get(name)
    return default if v in (None, "") else int(v)


def _f(name: str, default: float) -> float:
    v = os.environ.get(name)
    return default if v in (None, "") else float(v)


RTC_VERSION = os.environ.get("RTC_VERSION", "RTC-MVP0-rich-world-v1")
RTC_FREEZE_DATE = os.environ.get("RTC_FREEZE_DATE", "2026-06-28")

RTC_GRID = _i("RTC_GRID", 48)
RTC_K = _i("RTC_K", 4)
RTC_BANDS = _i("RTC_BANDS", 5)
RTC_VOCAB = _i("RTC_VOCAB", 6)
RTC_MSG_LEN = _i("RTC_MSG_LEN", 4)
RTC_RADIUS = _i("RTC_RADIUS", 6)
RTC_SENSOR_WIN = _i("RTC_SENSOR_WIN", 5)
RTC_SENSOR_SIGMA = _f("RTC_SENSOR_SIGMA", 0.8)
RTC_SENSOR_LAG = _i("RTC_SENSOR_LAG", 3)

RTC_ADVECT_SPEED = _f("RTC_ADVECT_SPEED", 0.45)
RTC_DIFFUSE_ALPHA = _f("RTC_DIFFUSE_ALPHA", 0.035)
RTC_DECAY = _f("RTC_DECAY", 0.97)
RTC_VENTS_PER_CHANNEL = _i("RTC_VENTS_PER_CHANNEL", 5)
RTC_VENT_SIGMA = _f("RTC_VENT_SIGMA", 2.2)
RTC_INNOVATION = _f("RTC_INNOVATION", 0.65)
RTC_TIDE_LOCK = _f("RTC_TIDE_LOCK", 0.0)
RTC_TIDE_PERIOD = _i("RTC_TIDE_PERIOD", 96)

RTC_POP = _i("RTC_POP", 80)
RTC_ENERGY_INIT = _f("RTC_ENERGY_INIT", 50.0)
RTC_UPKEEP = _f("RTC_UPKEEP", 0.18)
RTC_EAT_THETA = _f("RTC_EAT_THETA", 0.18)
RTC_EAT_CLIP = _f("RTC_EAT_CLIP", 3.5)
RTC_TOXIN_COST = _f("RTC_TOXIN_COST", 0.7)
RTC_TOXIC_DEATH = _f("RTC_TOXIC_DEATH", -1.8)

RTC_G0_SEEDS = _i("RTC_G0_SEEDS", 6)
RTC_G0_STEPS = _i("RTC_G0_STEPS", 260)
RTC_G0_BOOTSTRAP_REPS = _i("RTC_G0_BOOTSTRAP_REPS", 500)
RTC_G0_CLOCK_R2_MAX = _f("RTC_G0_CLOCK_R2_MAX", 0.03)
RTC_G0_FORECASTER_ALIVE_MIN = _f("RTC_G0_FORECASTER_ALIVE_MIN", 0.80)
RTC_G0_CONTROL_ALIVE_MAX = _f("RTC_G0_CONTROL_ALIVE_MAX", 0.35)
RTC_G0_CLOCK_LIFT_MAX = _f("RTC_G0_CLOCK_LIFT_MAX", 0.10)

RTC_G1_SEEDS = _i("RTC_G1_SEEDS", 6)
RTC_G1_STEPS = _i("RTC_G1_STEPS", 320)
RTC_G1_BOOTSTRAP_REPS = _i("RTC_G1_BOOTSTRAP_REPS", 500)
RTC_G1_LANG_EPOCHS = _i("RTC_G1_LANG_EPOCHS", 240)
RTC_G1_LANG_LR = _f("RTC_G1_LANG_LR", 0.025)
RTC_G1_LANG_TAU = _f("RTC_G1_LANG_TAU", 0.85)
RTC_G1_LANG_HIDDEN = _i("RTC_G1_LANG_HIDDEN", 48)
RTC_G1_JOINT_EPOCHS = _i("RTC_G1_JOINT_EPOCHS", 220)
RTC_G1_FUSION_LIFT_MIN = _f("RTC_G1_FUSION_LIFT_MIN", 0.35)
RTC_G1_NULL_LIFT_MAX = _f("RTC_G1_NULL_LIFT_MAX", 0.12)
RTC_G1_SINGLE_FACTOR_EAT_MAX_FRAC = _f("RTC_G1_SINGLE_FACTOR_EAT_MAX_FRAC", 0.70)
RTC_G1_JOINT_CHANCE = _f("RTC_G1_JOINT_CHANCE", 1.0 / (RTC_BANDS ** RTC_K))
RTC_G1_ACTION_MARGIN = _f("RTC_G1_ACTION_MARGIN", 0.25)

RTC_FROZEN = {
    k: v for k, v in dict(globals()).items()
    if k.startswith("RTC_") and k != "RTC_FROZEN"
}
