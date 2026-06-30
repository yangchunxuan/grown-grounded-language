"""Harness invariants for the g1f / C1 / C2X* line — the anti-drift safety net.

These are the equivalence / byte-stability / no-oracle checks that previously lived inside each runner's
startup `equivalence_test()`. Migrated here so they run in `pytest` + CI on every change. If an AI (or a
human) edits the harness and silently changes behavior, these go red.

Run: python -m pytest tests/test_g1f_invariants.py -q
"""
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

os.environ.setdefault("RTC_G1F_FORMAL", "0")  # small/fast config; invariants are scale-independent
os.environ.setdefault("RTC_TOXIC_DEATH", "-0.9")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from offscreen import rtc_g1f_coevolve as g1f  # noqa: E402

ARM = "shared_weights_kin"


def _unified_pop(seed=123, pop=8):
    g1f.G1F_POP = pop
    return g1f._initial_pop_for(seed, ARM)


def test_mii_fast_equals_loop():
    """Vectorized MII must be byte-identical to the reference loop (pure argmax, no float arithmetic)."""
    pop = _unified_pop()
    assert g1f._mii(pop, return_matrix=True)["matrix"] == g1f._mii_matrix_fast(pop)[0]


def test_mii_fast_equals_loop_on_tie():
    """Deliberate argmax tie (flat table slice) -> both paths pick the lowest index, still identical."""
    pop = _unified_pop()
    pop[0].speaker.table[0, :, :] = 1.0
    pop[3].speaker.table[2, :, :] = -0.5
    assert g1f._mii(pop, return_matrix=True)["matrix"] == g1f._mii_matrix_fast(pop)[0]


def test_quota_K0_equals_soft():
    """_select_next_quota(K=0) is the no-reservation degenerate case == _select_next_soft (lineages+tables)."""
    pop = _unified_pop(seed=55)
    fit = np.random.default_rng(1).random(len(pop))
    a = g1f._select_next_soft(55, 3, pop, fit, np.random.default_rng(99))
    b = g1f._select_next_quota(55, 3, pop, fit, np.random.default_rng(99), K=0, m=0)
    assert [int(x.lineage) for x in a] == [int(x.lineage) for x in b]
    assert all(np.array_equal(x.speaker.table, y.speaker.table) for x, y in zip(a, b))


def test_quota_protects_top_lineages():
    """Each of the top-K largest lineages must receive >= m offspring (the niching guarantee)."""
    pop = _unified_pop(seed=7)
    for i in range(len(pop)):
        pop[i].lineage = i % 4  # 4 lineages of 2 each on pop=8
    counts = Counter(int(a.lineage) for a in pop)
    q = g1f._select_next_quota(7, 1, pop, np.random.default_rng(2).random(len(pop)),
                               np.random.default_rng(3), K=2, m=2)
    qc = Counter(int(x.lineage) for x in q)
    top2 = sorted(counts, key=lambda L: (-counts[L], L))[:2]
    assert all(qc[L] >= 2 for L in top2), (qc, top2)


def test_run_episode_speaker_rule_none_byte_stable():
    """Adding speaker_rule= must leave the default (None) path byte-stable vs not passing it."""
    pop = _unified_pop(seed=55)
    a1 = g1f._run_episode(777, pop, "open", ARM)["alive"]
    a2 = g1f._run_episode(777, pop, "open", ARM, speaker_rule=None)["alive"]
    assert a1 == a2


def test_cross_lineage_balanced_is_never_kin():
    """No-oracle-adjacent invariant: forced non-kin routing returns a DIFFERENT-lineage speaker (or None),
    never the listener's own lineage."""
    pop = _unified_pop(seed=7)
    for i in range(len(pop)):
        pop[i].lineage = i % 3  # ensure multiple lineages present
    for li in range(len(pop)):
        for pj in range(4):
            for gr in range(3):
                sp = g1f._speaker_for(pop, li, pj, gr, ARM, "cross_lineage_balanced")
                if sp is not None:
                    assert int(sp.lineage) != int(pop[li].lineage)


def test_run_episode_returns_per_agent_alive():
    """The instrument-only addition: per-agent alive list, length == pop."""
    pop = _unified_pop(seed=55)
    ep = g1f._run_episode(777, pop, "open", ARM)
    assert "alive_per_agent" in ep and len(ep["alive_per_agent"]) == len(pop)
