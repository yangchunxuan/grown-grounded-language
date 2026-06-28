"""RTC MVP-1 multi-partner fusion utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

import config.prereg_rtc as rc
from rtc_language import BandTuple, bands_to_values, neutral_bands, values_to_bands
from systems.ctm_cell import SmallCTMCell


@dataclass(frozen=True)
class BandPacket:
    bands: BandTuple
    confidence: tuple[float, float, float, float]


def private_packet(values: Iterable[float], channels: Iterable[int]) -> BandPacket:
    bands = list(neutral_bands())
    conf = [0.0] * rc.RTC_K
    for ch, val in zip(tuple(channels), tuple(values)):
        bands[int(ch)] = values_to_bands([float(val)] * rc.RTC_K)[0]
        conf[int(ch)] = 1.0
    return BandPacket(tuple(bands), tuple(conf))


def decoded_packet(bands: Iterable[int], *, strength: float = 0.72, single_factor: int | None = None) -> BandPacket:
    vals = list(tuple(int(x) for x in bands))
    conf = [0.0] * rc.RTC_K
    for ch in range(rc.RTC_K):
        keep = single_factor is None or ch == int(single_factor)
        if keep and vals[ch] != rc.RTC_BANDS // 2:
            conf[ch] = float(strength)
        elif keep:
            conf[ch] = float(strength) * 0.45
        elif not keep:
            vals[ch] = rc.RTC_BANDS // 2
    return BandPacket(tuple(vals), tuple(conf))


def aggregate(self_packet: BandPacket, messages: Iterable[BandPacket]) -> BandPacket:
    packets = [self_packet, *list(messages)]
    out_bands = []
    out_conf = []
    for ch in range(rc.RTC_K):
        votes = {}
        total = 0.0
        for pkt in packets:
            c = float(pkt.confidence[ch])
            if c <= 0:
                continue
            votes[pkt.bands[ch]] = votes.get(pkt.bands[ch], 0.0) + c
            total += c
        if not votes:
            out_bands.append(rc.RTC_BANDS // 2)
            out_conf.append(0.0)
        else:
            band, wt = max(votes.items(), key=lambda kv: (kv[1], -abs(kv[0] - rc.RTC_BANDS // 2)))
            out_bands.append(int(band))
            out_conf.append(min(1.0, float(wt / max(0.1, total)) + 0.25 * (len(votes) == 1)))
    return BandPacket(tuple(out_bands), tuple(out_conf))


class CTMFilter:
    """Small recurrent filter over decoded bands and confidence."""

    def __init__(self, seed: int):
        self.core = SmallCTMCell(
            input_dim=rc.RTC_K * rc.RTC_BANDS + rc.RTC_K + 2,
            d_model=32,
            ticks=3,
            memory_length=4,
            nlm_hidden=8,
            sync_pairs=12,
            seed=int(seed) + 901,
        )
        self.state = None

    def latent(self, packet: BandPacket, body_energy: float, age: int) -> np.ndarray:
        import torch
        import torch.nn.functional as F

        bands = torch.tensor([packet.bands], dtype=torch.long)
        onehot = F.one_hot(bands, num_classes=rc.RTC_BANDS).float().reshape(1, -1)
        conf = torch.tensor([packet.confidence], dtype=torch.float32)
        body = torch.tensor([[body_energy / max(1.0, rc.RTC_ENERGY_INIT), age / max(1, rc.RTC_G1_STEPS)]])
        x = torch.cat([onehot, conf, body], dim=1)
        with torch.no_grad():
            z, self.state = self.core(x, self.state)
        return z.detach().cpu().numpy()[0]


def packet_score(packet: BandPacket, weights: np.ndarray) -> float:
    vals = bands_to_values(packet.bands)
    conf = np.asarray(packet.confidence, dtype=np.float32)
    if np.min(conf) < 0.32:
        return -1000.0 + float(np.dot(weights, vals * conf))
    return float(np.dot(weights, vals))
