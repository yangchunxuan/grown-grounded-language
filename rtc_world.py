"""RTC MVP-0 hidden tidal nutrient field."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import config.prereg_rtc as rc


def _bilinear_torus(a: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    h, w = a.shape
    x0 = np.floor(x).astype(int) % w
    y0 = np.floor(y).astype(int) % h
    x1, y1 = (x0 + 1) % w, (y0 + 1) % h
    fx, fy = x - np.floor(x), y - np.floor(y)
    return ((1 - fx) * (1 - fy) * a[y0, x0] + fx * (1 - fy) * a[y0, x1]
            + (1 - fx) * fy * a[y1, x0] + fx * fy * a[y1, x1])


def _diffuse(a: np.ndarray, alpha: float) -> np.ndarray:
    nbr = (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1)
           + np.roll(a, -1, 1)) * 0.25
    return (1 - alpha) * a + alpha * nbr


@dataclass
class RTCWorld:
    seed: int
    grid: int = rc.RTC_GRID
    k: int = rc.RTC_K

    def __post_init__(self):
        self.rng = np.random.default_rng(int(self.seed))
        self.t = 0
        self.field = self.rng.normal(0, 0.12, (self.k, self.grid, self.grid)).astype(np.float32)
        self.vents = self.rng.uniform(0, self.grid, (self.k, rc.RTC_VENTS_PER_CHANNEL, 2))
        self.vent_phase = self.rng.uniform(0, 2 * np.pi, (self.k, rc.RTC_VENTS_PER_CHANNEL))
        self._history = [self.field.copy() for _ in range(rc.RTC_SENSOR_LAG + 1)]
        yy, xx = np.mgrid[0:self.grid, 0:self.grid]
        self.xx, self.yy = xx.astype(np.float32), yy.astype(np.float32)
        self.cx = (self.xx - self.grid * 0.5) / self.grid
        self.cy = (self.yy - self.grid * 0.5) / self.grid

    @property
    def tide_phase(self) -> float:
        return 2 * np.pi * ((self.t % rc.RTC_TIDE_PERIOD) / rc.RTC_TIDE_PERIOD)

    def _velocity(self, ch: int) -> tuple[np.ndarray, np.ndarray]:
        a = self.tide_phase + ch * 1.73
        rot = 0.55 + 0.25 * np.sin(0.013 * self.t + ch)
        vx = rc.RTC_ADVECT_SPEED * (np.cos(a) - rot * self.cy)
        vy = rc.RTC_ADVECT_SPEED * (np.sin(a + 0.7) + rot * self.cx)
        return vx, vy

    def _inject(self, ch: int) -> np.ndarray:
        out = np.zeros((self.grid, self.grid), dtype=np.float32)
        for j in range(rc.RTC_VENTS_PER_CHANNEL):
            self.vents[ch, j] += self.rng.normal(0, 0.18, 2)
            self.vents[ch, j] %= self.grid
            x, y = self.vents[ch, j]
            dx = ((self.xx - x + self.grid / 2) % self.grid) - self.grid / 2
            dy = ((self.yy - y + self.grid / 2) % self.grid) - self.grid / 2
            amp = rc.RTC_INNOVATION * self.rng.normal()
            amp += rc.RTC_TIDE_LOCK * np.sin(self.tide_phase + self.vent_phase[ch, j])
            out += amp * np.exp(-(dx * dx + dy * dy) / (2 * rc.RTC_VENT_SIGMA ** 2))
        return out

    def step(self) -> None:
        nxt = np.empty_like(self.field)
        for ch in range(self.k):
            vx, vy = self._velocity(ch)
            back_x = (self.xx - vx) % self.grid
            back_y = (self.yy - vy) % self.grid
            adv = _bilinear_torus(self.field[ch], back_x, back_y)
            nxt[ch] = rc.RTC_DECAY * _diffuse(adv, rc.RTC_DIFFUSE_ALPHA) + self._inject(ch)
        self.field = np.clip(nxt, -4.0, 4.0).astype(np.float32)
        self.t += 1
        self._history.append(self.field.copy())
        self._history = self._history[-(rc.RTC_SENSOR_LAG + 8):]

    def lagged(self, lag: int | None = None) -> np.ndarray:
        lag = rc.RTC_SENSOR_LAG if lag is None else int(lag)
        idx = max(0, len(self._history) - 1 - lag)
        return self._history[idx]

    def patch(self, x: int, y: int, *, lag: int = 0) -> np.ndarray:
        src = self.field if lag == 0 else self.lagged(lag)
        return src[:, int(y) % self.grid, int(x) % self.grid].copy()

    def window(self, x: int, y: int, channels, *, lag: int | None = None, win: int | None = None) -> np.ndarray:
        src = self.lagged(lag)
        win = rc.RTC_SENSOR_WIN if win is None else int(win)
        r = win // 2
        xs = (np.arange(int(x) - r, int(x) + r + 1) % self.grid).astype(int)
        ys = (np.arange(int(y) - r, int(y) + r + 1) % self.grid).astype(int)
        return src[np.asarray(channels, dtype=int)][:, ys[:, None], xs[None, :]].copy()

    def candidates(self, x: int, y: int, radius: int = 2) -> list[tuple[int, int]]:
        pts = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                pts.append(((int(x) + dx) % self.grid, (int(y) + dy) % self.grid))
        return pts
