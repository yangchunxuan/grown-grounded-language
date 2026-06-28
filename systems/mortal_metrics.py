"""Compositionality metrics for the Mortal-Bottleneck experiment (T3).

PROMOTES the power-check-validated metric implementations from
``scripts/probe_compositional_substrate.py`` into a clean, tested, dependency-light
instrument. The frozen preregistration (``config/prereg_mortal.py``) names
``MORTAL_PRIMARY_METRIC = "posdis"`` and ``MORTAL_COMP_METRICS =
("posdis", "bosdis", "topsim")``; this module is the single source of truth for
those three numbers.

Why PosDis is PRIMARY (and topsim only secondary):
  PosDis (positional disentanglement, Chaabouni et al. 2020 / Korbak et al. 2020)
  is well-defined whenever ANY message position varies, and directly measures
  whether each position specialises to ONE attribute. topsim (Spearman rho between
  pairwise message-distance and referent-distance) is brittle: it is UNDEFINED
  when the message-distance vector has zero variance -- the exact "diagonal
  collapse" pathology the bigger geometry was chosen to avoid, and which the
  committed ``scripts/rosetta_stats.topsim`` silently returns ``None`` for. Here
  that undefined-ness is made FIRST-CLASS: ``topsim_guarded`` returns
  ``(value_or_None, defined: bool)`` and ``topsim_undefined_rate`` aggregates the
  undefined fraction across a run so the harness can REPORT it (a high
  undefined-rate is itself a finding, not a silently-dropped row).

Conventions mirror ``systems/mortal_channel.py``: ``from __future__ import
annotations``, a docstring stating the honesty role, numpy-optional / no torch
(the metrics are pure discrete information theory over symbol/attribute labels).
Everything here is deterministic.

A ``message`` is a tuple of symbol indices (length MSG_LEN); a ``referent`` is a
tuple of attribute-value indices (length n_attrs). ``messages`` and ``referents``
are equal-length, same-order lists (``messages[i]`` is the code for
``referents[i]``).
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Optional, Sequence

Message = Sequence[int]
Referent = Sequence[int]

__all__ = [
    "posdis",
    "bosdis",
    "topsim_guarded",
    "topsim_undefined_rate",
]


# ──────────────────────────────────────────────────────────────────────────────
# Discrete information-theory primitives (bits) — promoted verbatim from the probe
# ──────────────────────────────────────────────────────────────────────────────


def _entropy(counts: Sequence[float]) -> float:
    """Shannon entropy (bits) of a list of category counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * math.log(p, 2)
    return h


def _entropy_of_labels(labels: Sequence) -> float:
    """Entropy (bits) of the empirical distribution of a label sequence."""
    return _entropy(list(Counter(labels).values()))


def _mutual_information(xs: Sequence, ys: Sequence) -> float:
    """MI(X; Y) in bits for two equal-length lists of discrete labels (>= 0)."""
    n = len(xs)
    if n == 0:
        return 0.0
    cx = Counter(xs)
    cy = Counter(ys)
    cxy = Counter(zip(xs, ys))
    mi = 0.0
    for (x, y), nxy in cxy.items():
        pxy = nxy / n
        px = cx[x] / n
        py = cy[y] / n
        mi += pxy * math.log(pxy / (px * py), 2)
    return max(mi, 0.0)


def _attr_columns(referents: Sequence[Referent]) -> list[list]:
    """Transpose referents into one label-column per attribute."""
    n_attrs = len(referents[0])
    return [[r[k] for r in referents] for k in range(n_attrs)]


def _top_two(values: Sequence[float]) -> tuple[float, float]:
    """Largest and second-largest of a sequence (second is 0.0 if length < 2)."""
    ordered = sorted(values, reverse=True)
    top = ordered[0]
    second = ordered[1] if len(ordered) > 1 else 0.0
    return top, second


# ──────────────────────────────────────────────────────────────────────────────
# PosDis — POSITIONAL disentanglement (PRIMARY metric)
# ──────────────────────────────────────────────────────────────────────────────


def posdis(
    messages: Sequence[Message],
    referents: Sequence[Referent],
    vocab: Optional[int] = None,
) -> float:
    """Positional disentanglement (Chaabouni 2020 / Korbak 2020). PRIMARY metric.

    For each message position ``j``: compute MI(symbol_j ; attribute_k) for every
    attribute ``k``. The position's contribution is the GAP between its top and
    second mutual-information attribute, normalised by the position's symbol
    entropy ``H(symbol_j)``: ``(top_MI - second_MI) / H(symbol_j)``. PosDis is the
    mean of this over positions that actually VARY (``H(symbol_j) > 0``); a
    constant position carries no information and is skipped.

    A position that specialises to exactly one attribute has a large top-vs-second
    gap relative to its entropy -> contribution near 1; a position that mixes
    attributes (holistic) has a small gap -> contribution near 0. PROMOTED
    verbatim (behaviour-identical) from
    ``scripts/probe_compositional_substrate.py``.

    Returns a float in ``[0, 1]``. Well-defined even when topsim is not. Returns
    ``0.0`` (a valid floor, NOT ``None``) when no position varies (e.g. all
    messages identical) so callers can treat PosDis as an always-numeric primary;
    the probe returned ``None`` for that degenerate case, but a fully-collapsed
    code is correctly the minimum-compositionality floor.

    ``vocab`` is accepted for signature compatibility with the probe but is NOT
    needed (PosDis is computed from the observed symbols); pass it or omit it.
    """
    del vocab  # not needed; observed symbols drive the computation
    if not messages:
        return 0.0
    msg_len = len(messages[0])
    attr_cols = _attr_columns(referents)
    n_attrs = len(attr_cols)
    per_pos: list[float] = []
    for j in range(msg_len):
        sym_col = [m[j] for m in messages]
        h_pos = _entropy_of_labels(sym_col)
        if h_pos <= 0:  # this position carries no information -> skip
            continue
        mis = [_mutual_information(sym_col, attr_cols[k]) for k in range(n_attrs)]
        top, second = _top_two(mis)
        per_pos.append((top - second) / h_pos)
    if not per_pos:
        return 0.0
    return sum(per_pos) / len(per_pos)


# ──────────────────────────────────────────────────────────────────────────────
# BosDis — BAG-OF-SYMBOLS disentanglement
# ──────────────────────────────────────────────────────────────────────────────


def bosdis(
    messages: Sequence[Message],
    referents: Sequence[Referent],
    vocab: Optional[int] = None,
) -> float:
    """Bag-of-symbols disentanglement (Chaabouni et al. 2020).

    Like PosDis but POSITION-INDEPENDENT: instead of a per-position symbol, the
    informative variable for each vocab symbol ``s`` is its COUNT in the message
    (the histogram of symbols). For each symbol ``s`` compute
    MI(count_s ; attribute_k) for every attribute, take the top-vs-second gap, and
    average the gaps WEIGHTED by the count's entropy ``H(count_s)`` (symbols whose
    count never varies carry no information and are skipped). PROMOTED verbatim
    (behaviour-identical) from ``scripts/probe_compositional_substrate.py``.

    Returns a float (>= 0). Returns ``0.0`` when no symbol-count varies (the
    degenerate floor; the probe returned ``None`` there).

    ``vocab`` sets the symbol range to histogram over. When omitted it is inferred
    as ``max(symbol) + 1`` over the observed messages (symbols never observed have
    a constant zero count -> zero entropy -> skipped anyway, so the result is
    identical whether or not a larger vocab is passed).
    """
    if not messages:
        return 0.0
    if vocab is None:
        max_sym = -1
        for m in messages:
            for s in m:
                if s > max_sym:
                    max_sym = s
        vocab = max_sym + 1
    attr_cols = _attr_columns(referents)
    n_attrs = len(attr_cols)
    gaps: list[float] = []
    weights: list[float] = []
    for s in range(vocab):
        count_col = [sum(1 for sym in m if sym == s) for m in messages]
        h_s = _entropy_of_labels(count_col)
        if h_s <= 0:
            continue
        mis = [_mutual_information(count_col, attr_cols[k]) for k in range(n_attrs)]
        top, second = _top_two(mis)
        gaps.append(top - second)
        weights.append(h_s)
    if not weights:
        return 0.0
    return sum(g * w for g, w in zip(gaps, weights)) / sum(weights)


# ──────────────────────────────────────────────────────────────────────────────
# topsim — topographic similarity (SECONDARY; undefined-ness made FIRST-CLASS)
# ──────────────────────────────────────────────────────────────────────────────


def _hamming(a: Message, b: Message) -> float:
    return float(sum(1 for x, y in zip(a, b) if x != y))


def _rank(values: Sequence[float]) -> list[float]:
    """Average (tie-corrected) 1-based ranks — promoted from the probe / rosetta."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def topsim_guarded(
    messages: Sequence[Message],
    referents: Sequence[Referent],
) -> tuple[Optional[float], bool]:
    """Guarded topographic similarity = Spearman rho between pairwise message
    Hamming-distance and pairwise referent Hamming-distance.

    UNDEFINED-NESS IS FIRST-CLASS. The committed ``scripts/rosetta_stats.topsim``
    silently returns ``None`` when a distance vector has zero variance (the
    "diagonal collapse": every message ``(s, s, s)`` distinct s -> every pair
    differs in all positions -> the message-distance vector is the constant
    MSG_LEN). Here the caller is told EXPLICITLY:

    Returns ``(value, defined)``:
      * ``(rho, True)``  -- a real Spearman rho in ``[-1, 1]`` when BOTH the
        message-distance and referent-distance vectors vary;
      * ``(None, False)`` -- UNDEFINED, when either distance vector has ~zero
        variance (diagonal collapse / a degenerate referent set) or there are
        fewer than 3 items (no informative pair structure).

    Never crashes and never returns a misleading number on the degenerate case;
    ``topsim_undefined_rate`` aggregates the ``defined`` flag across a run.
    """
    n = min(len(messages), len(referents))
    if n < 3:
        return None, False

    md: list[float] = []
    rd: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            md.append(_hamming(messages[i], messages[j]))
            rd.append(_hamming(referents[i], referents[j]))

    rx, ry = _rank(md), _rank(rd)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx <= 0 or vy <= 0:  # zero-variance -> topsim is genuinely undefined
        return None, False
    rho = cov / math.sqrt(vx * vy)
    return rho, True


def topsim_undefined_rate(
    messages_per_run: Sequence[Sequence[Message]],
    referents_per_run: Sequence[Sequence[Referent]],
) -> float:
    """Fraction of runs whose guarded topsim is UNDEFINED.

    Companion to :func:`topsim_guarded` so the harness can REPORT the undefined
    rate (a high rate = the diagonal pathology is recurring, itself a finding)
    rather than silently dropping undefined rows. ``messages_per_run[r]`` pairs
    with ``referents_per_run[r]``.

    Returns a float in ``[0, 1]`` (``0.0`` for an empty input — nothing
    undefined). Raises ``ValueError`` on mismatched run counts.
    """
    if len(messages_per_run) != len(referents_per_run):
        raise ValueError(
            "messages_per_run and referents_per_run must have the same length "
            f"({len(messages_per_run)} != {len(referents_per_run)})"
        )
    if not messages_per_run:
        return 0.0
    undefined = 0
    for msgs, refs in zip(messages_per_run, referents_per_run):
        _value, defined = topsim_guarded(msgs, refs)
        if not defined:
            undefined += 1
    return undefined / len(messages_per_run)
