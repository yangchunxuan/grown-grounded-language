"""RTC MVP-0 no-oracle perception seam."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import config.prereg_rtc as rc


@dataclass
class Body:
    x: int
    y: int
    energy: float
    age: int
    heading: int
    sensors: tuple[int, int]
    last_symbol: tuple[int, ...] = ()


def _bearing(dx: int, dy: int) -> int:
    if abs(dx) >= abs(dy):
        return 0 if dx > 0 else 2
    return 1 if dy > 0 else 3


def perceive(body: Body, world, neighbours=(), rng=None) -> dict:
    """Return only body state, two lagged noisy sensor planes, and local hearsay.

    The selected channel ids are consumed here but never returned. The policy
    sees sensor slots, not the inherited selector that chose those slots.
    """
    rng = np.random.default_rng() if rng is None else rng
    win = world.window(body.x, body.y, body.sensors, lag=rc.RTC_SENSOR_LAG)
    noisy = win + rng.normal(0, rc.RTC_SENSOR_SIGMA, win.shape)
    heard = []
    for nb in neighbours:
        dx = ((int(nb.x) - int(body.x) + world.grid // 2) % world.grid) - world.grid // 2
        dy = ((int(nb.y) - int(body.y) + world.grid // 2) % world.grid) - world.grid // 2
        dist = max(abs(dx), abs(dy))
        if 0 < dist <= rc.RTC_RADIUS:
            heard.append((_bearing(dx, dy), float(dist) / rc.RTC_RADIUS, tuple(nb.last_symbol)))
    return {
        "body": np.asarray([
            body.energy / max(1.0, rc.RTC_ENERGY_INIT),
            body.age / max(1, rc.RTC_G0_STEPS),
            np.sin(body.heading * np.pi / 2),
            np.cos(body.heading * np.pi / 2),
        ], dtype=np.float32),
        "sensors": noisy.astype(np.float32),
        "heard": tuple(heard),
    }
