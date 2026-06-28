"""RTC MVP-1 relay channel.

This module adapts the validated factored Mortal channel to RTC's four
channel-band referents: each utterance is a 4-symbol message over V=6, decoded
as four 5-way channel bands. Training targets are caller-provided forecast
tuples, so the channel never needs the hidden world state.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

import numpy as np

import config.prereg_rtc as rc

os.environ.setdefault("MORTAL_ATTRIBUTES", ",".join(f"c{i}:{rc.RTC_BANDS}" for i in range(rc.RTC_K)))
os.environ.setdefault("MORTAL_MSG_LEN", str(rc.RTC_MSG_LEN))
os.environ.setdefault("MORTAL_VOCAB", str(rc.RTC_VOCAB))

from systems import mortal_channel as mc  # noqa: E402

BandTuple = tuple[int, int, int, int]
Message = tuple[int, int, int, int]

_BAND_EDGES = np.asarray([-1.35, -0.35, 0.35, 1.35], dtype=np.float32)
_BAND_CENTERS = np.asarray([-2.0, -0.75, 0.0, 0.75, 2.0], dtype=np.float32)

if tuple(mc.ATTR_CARDS) != (rc.RTC_BANDS,) * rc.RTC_K:
    raise RuntimeError("mortal_channel geometry was imported before RTC set its band product")
if mc.MSG_LEN != rc.RTC_MSG_LEN or mc.VOCAB != rc.RTC_VOCAB:
    raise RuntimeError("mortal_channel message geometry disagrees with RTC prereg")


def values_to_bands(values: Iterable[float]) -> BandTuple:
    vals = np.asarray(tuple(values), dtype=np.float32)
    return tuple(int(x) for x in np.digitize(vals, _BAND_EDGES).tolist())


def bands_to_values(bands: Iterable[int]) -> np.ndarray:
    idx = np.asarray(tuple(bands), dtype=int).clip(0, rc.RTC_BANDS - 1)
    return _BAND_CENTERS[idx].astype(np.float32)


def neutral_bands() -> BandTuple:
    return (rc.RTC_BANDS // 2,) * rc.RTC_K


def referent_id(bands: BandTuple) -> int:
    return int(mc.referent_index(tuple(int(x) for x in bands)))


def all_band_tuples() -> list[BandTuple]:
    return [tuple(int(x) for x in r) for r in mc.REFERENTS]


@dataclass
class RelayChannel:
    speaker: object
    listener: object
    train_accuracy: float
    seen_count: int

    def emit(self, bands: BandTuple) -> Message:
        return tuple(int(x) for x in self.speaker.emit(tuple(bands)))

    def decode(self, message: Iterable[int]) -> BandTuple:
        msg = tuple(int(x) for x in message)
        if len(msg) != rc.RTC_MSG_LEN:
            return neutral_bands()
        return tuple(int(x) for x in self.listener.predict(msg))


def train_relay_channel(seed: int, forecast_refs: Iterable[BandTuple], *, epochs: int | None = None) -> RelayChannel:
    """Train by gradient on self/fused forecast tuples supplied by the caller."""
    refs = {referent_id(tuple(int(x) for x in r)) for r in forecast_refs}
    if not refs:
        refs = {referent_id(neutral_bands())}
    speaker = mc.FactoredSpeaker(seed=int(seed), hidden=rc.RTC_G1_LANG_HIDDEN)
    listener = mc.FactoredListener(seed=int(seed) + 31, hidden=rc.RTC_G1_LANG_HIDDEN)
    acc = mc.cotrain_factored(
        speaker,
        listener,
        int(rc.RTC_G1_LANG_EPOCHS if epochs is None else epochs),
        lr=rc.RTC_G1_LANG_LR,
        tau=rc.RTC_G1_LANG_TAU,
        seed=int(seed) + 73,
        seen_idx=sorted(refs),
    )
    return RelayChannel(speaker, listener, float(acc), len(refs))


def scramble_message(rng: np.random.Generator) -> Message:
    return tuple(int(x) for x in rng.integers(0, rc.RTC_VOCAB, rc.RTC_MSG_LEN))


def mute_message() -> Message:
    return (0,) * rc.RTC_MSG_LEN


class HolisticCodebook:
    """Seen-tuple lookup null; unseen tuples decode to a seed-stable default."""

    def __init__(self, seed: int, seen_refs: Iterable[BandTuple]):
        rng = np.random.default_rng(int(seed) + 5100)
        self.default = neutral_bands()
        self.encode = {}
        self.decode_table = {}
        used = set()
        for ref in sorted({tuple(r) for r in seen_refs}):
            for _ in range(1000):
                msg = tuple(int(x) for x in rng.integers(0, rc.RTC_VOCAB, rc.RTC_MSG_LEN))
                if msg not in used:
                    break
            used.add(msg)
            self.encode[ref] = msg
            self.decode_table[msg] = ref

    def emit(self, bands: BandTuple) -> Message:
        return self.encode.get(tuple(bands), mute_message())

    def decode(self, message: Iterable[int]) -> BandTuple:
        return self.decode_table.get(tuple(int(x) for x in message), self.default)
