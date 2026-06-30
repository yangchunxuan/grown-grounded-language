"""Shared helpers + provenance for the g1f / C1 / C2X* runners.

CANONICAL home for the metric/stats helpers that were copy-pasted across the stage runners (the known
duplication debt in ARCHITECTURE.md). New runners import from here; the 5 existing runners keep their
inline copies frozen alongside their already-banked verdicts (refactor-on-next-touch, with verdict
byte-reproduction as the safety net). The functions here are VERBATIM the inline versions, so importing
them is byte-identical (covered by tests/test_g1f_invariants.py::test_common_helpers_match).

Also provides make_provenance(): every NEW verdict JSON should embed this so the result self-describes how
it was produced (command + env + git commit) — paired with RUNBOOK.md (how to run) and CLAIM_LEDGER.md
(claim -> verdict@commit index).
"""
from __future__ import annotations

import os
import subprocess
from collections import Counter

import numpy as np

COEX_MIN_PER = 3
NEFF_MIN = 2.0


def cf_wf(matrix, lineages):
    """cross-founder MII = off-diagonal different-lineage mean; within-founder = same-lineage off-diag."""
    n = len(lineages)
    cross, within = [], []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            (cross if lineages[i] != lineages[j] else within).append(matrix[i][j])
    return (float(np.mean(cross)) if cross else float("nan"),
            float(np.mean(within)) if within else float("nan"))


def neff(counts):
    """inverse-Simpson effective lineage count over a list of per-lineage living counts."""
    tot = sum(counts)
    return float(1.0 / sum((c / tot) ** 2 for c in counts)) if tot else 0.0


def living_by_lineage(pop, alive):
    c = Counter()
    for a, al in zip(pop, alive):
        if al:
            c[int(a.lineage)] += 1
    return c


def is_coexist(comp, min_per=COEX_MIN_PER, neff_min=NEFF_MIN):
    """dual coexistence gate: >=2 lineages each >=min_per living AND inverse-Simpson N_eff >= neff_min."""
    return sum(1 for v in comp.values() if v >= min_per) >= 2 and neff(list(comp.values())) >= neff_min


def boot_ci(xs, reps=2000, seed=7):
    xs = [x for x in xs if x == x]
    if len(xs) < 2:
        return [float("nan"), float("nan")]
    r = np.random.default_rng(seed)
    a = np.asarray(xs, float)
    bs = [float(np.mean(r.choice(a, len(a), replace=True))) for _ in range(reps)]
    return [round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]


def mean_nan(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


def med_l2(tables):
    if len(tables) < 2:
        return float("nan")
    ds = [float(np.linalg.norm(tables[i] - tables[j]))
          for i in range(len(tables)) for j in range(i + 1, len(tables))]
    return float(np.median(ds))


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()[:12]
    except Exception:
        return "unknown"


def make_provenance(stage, command_hint, env_keys, timestamp_note=""):
    """Self-describing record for a verdict JSON: how THIS result was produced.

    stage: short stage name (e.g. 'C2X3'). command_hint: the RUNBOOK command (string, no live timestamp).
    env_keys: list of env var names to capture (their current values). timestamp_note: pass a stamp in
    from outside if wanted (the harness forbids live Date.now()-style calls in some contexts; keep it
    explicit). Returns a plain dict to embed under verdict["provenance"].
    """
    return {
        "stage": stage,
        "command": command_hint,
        "git_commit": git_commit(),
        "env": {k: os.environ.get(k) for k in env_keys},
        "runbook": "offscreen/RUNBOOK.md",
        "note": timestamp_note or "see git log of the verdict file for the exact run time",
    }
