"""Generational iterated-learning engine for the Mortal-Bottleneck experiment (T4).

PROMOTES the power-check-validated iterated-learning loop from
``scripts/probe_compositional_substrate.py`` into a reusable, tested engine that
drives the T2 factored channel (``systems/mortal_channel.py``) and records the T3
compositionality metrics (``systems/mortal_metrics.py``) per generation.

What lives here (the NON-survival half of the experiment):
  * ``run_generations(...)`` -- a multi-generation iterated-learning chain. Each
    generation a FRESH student imitates the current teacher's productions under a
    transmission BOTTLENECK (a held-out fraction of the referent grid is hidden so
    the student must GENERALISE the unseen attribute-combinations), then a short
    Lewis-game interaction keeps the channel communicative, then the student
    becomes the teacher. Per-generation PosDis / BosDis / guarded-topsim are
    recorded with the T3 metrics.
  * The two NON-survival arms:
      - ``A1_baseline``: NO bottleneck (the student sees ALL referents /
        continuous cotrain) -> the null; this should stay flat/holistic (the
        power-check's verified negative control -- the bottleneck, not turnover,
        is the active ingredient).
      - ``A3_reset``: a single-lineage frequency-matched ARTIFICIAL reset -- a
        fitness-BLIND bottlenecked reset on a schedule decoupled from any survival,
        the standard iterated-learning reset (the Ren/Zheng single-lineage mechanism),
        which SHOULD compositionalize (reproducing the probe's PosDis rise). NOTE: the
        HEADLINE A3_reset arm is NOT this single-lineage chain -- it is the
        COHERENT-TEACHER POPULATION reset driven by ``run_population_generations``
        (the population analog: a random subset reset IN PLACE each generation, each
        re-imitating a teacher drawn uniformly among the NON-RESET stable agents,
        lineage ids preserved), the matched control for the A2 death population. This
        ``run_generations`` chain is the simpler non-survival relative.
    A2 (death) and A5 (selection-ablated) are SURVIVAL-gated and arrive in T5;
    the engine exposes a pluggable ``transmission`` callable seam (see below) so
    T5 can inject a survival-weighted teacher-selection WITHOUT rewriting the
    loop. The arm string is otherwise just bookkeeping here.
  * The PURE frequency-matcher utilities (``interval_histogram``, ``ks_distance``,
    ``matched_reset_schedule``, ``freq_match_valid``) -- unit-testable WITHOUT the
    death arm. Their POINT: A3's reset timing must be matchable to A2's death
    timing (the death-interval histogram T8 supplies later) so the ONLY remaining
    difference between A2 and A3 is survival-gating, not schedule.

The transmission seam (T5 readiness)
------------------------------------
``run_generations`` calls ``transmission(state) -> teacher`` once per generation
to choose WHICH speaker the next student learns from. ``state`` is a
``TransmissionState`` carrying the current ``teacher``, the shared ``listener``,
the population (a 1-element list here; T5 grows it), the generation index, and a
seeded ``random.Random``. The default (``select_current_teacher``) returns the
single current teacher -- plain iterated learning. T5's A2/A5 supply a callable
that selects a teacher from a FITNESS-WEIGHTED population, and nothing else in the
engine changes.

Conventions mirror ``systems/mortal_channel.py`` / ``systems/mortal_metrics.py``:
``from __future__ import annotations``, a docstring stating the honesty role,
frozen schedule imported from ``config/prereg_mortal`` (nothing hardcoded), torch
imported LAZILY inside the methods that touch the channel (so the module + the
pure freq-matcher import on a box with no torch), and deterministic everywhere
(torch + ``random`` seeded from the run seed).
"""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Optional

from config.prereg_mortal import (
    MORTAL_BOTTLENECK_HOLD_FRAC,
    MORTAL_DEATH_FRAC,
    MORTAL_FREQ_MATCH_KS_MAX,
    MORTAL_IMITATION_EPOCHS,
    MORTAL_INTERACTION_EPOCHS,
    MORTAL_N_GENERATIONS,
    MORTAL_POP_SIZE,
    MORTAL_READOUT_EPOCHS,
)
from systems import mortal_channel as mc
from systems import mortal_metrics as metrics

__all__ = [
    "TransmissionState",
    "select_current_teacher",
    "run_generations",
    "run_population_generations",
    "interval_histogram",
    "ks_distance",
    "matched_reset_schedule",
    "freq_match_valid",
    "count_histogram",
    "matched_count_schedule",
    "freq_match_counts_valid",
    "MIN_DEATH_EVENTS",
]

# The survival-gated arms this reproducing-population engine implements. A1/A3/A4
# are NON-survival arms driven by ``run_generations`` and are REJECTED here (so a
# caller cannot silently get an iterated-learning run from the death engine).
_POPULATION_ARMS: dict[str, str] = {
    "A2_death": "fitness",            # selection-on-meaning: lowest die, fit parent
    "A5_selection_ablated": "random",  # fitness-blind: random die, uniform parent
    "A3_reset": "reset",              # fitness-blind COHERENT-TEACHER POPULATION reset:
                                      # no death, no selection; reset agents KEEP their
                                      # lineage id (mind wiped + re-learned from a teacher
                                      # drawn UNIFORMLY among the NON-RESET stable agents)
                                      # -- the matched control for A2 death; the
                                      # population analog of the Ren/Zheng single-lineage
                                      # reset.
}

# The non-survival arms implemented here. A2_death / A5_selection_ablated are
# survival-gated and supplied by T5 via a custom ``transmission`` callable; the
# engine accepts ANY arm string (it is bookkeeping) but recognises these two for
# the bottleneck on/off default.
_NO_BOTTLENECK_ARMS = ("A1_baseline",)


# ──────────────────────────────────────────────────────────────────────────────
# The transmission seam (pluggable for T5's survival-weighted teacher selection)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class TransmissionState:
    """Everything a ``transmission`` callable needs to pick the next teacher.

    The default :func:`select_current_teacher` reads only ``teacher`` (plain
    iterated learning: each student learns from the single current teacher). T5's
    survival-weighted arms (A2 death / A5 selection-ablated) read ``population``
    and ``rng`` (and, when T5 attaches them, per-speaker fitness scores) to choose
    a SURVIVING / fitness-weighted teacher -- without the engine changing.
    """

    teacher: "mc.FactoredSpeaker"
    listener: "mc.Listener"
    gen: int
    seed: int
    rng: random.Random
    # population of candidate teachers; a 1-element list here (the current
    # teacher). T5 grows this to a real reproducing population.
    population: list = field(default_factory=list)
    # optional per-population fitness scores (T5 fills these; unused by the
    # default callable). Kept here so the seam carries them without a signature
    # change.
    fitness: Optional[list] = None


# A transmission callable maps a TransmissionState to the teacher the next
# student imitates.
Transmission = Callable[[TransmissionState], "mc.FactoredSpeaker"]


def select_current_teacher(state: TransmissionState) -> "mc.FactoredSpeaker":
    """Default transmission: the next student learns from the current teacher.

    This is plain (fitness-blind) iterated learning -- correct for A1/A3. T5 swaps
    in a survival-weighted selector for A2/A5.
    """
    return state.teacher


# ──────────────────────────────────────────────────────────────────────────────
# The generational iterated-learning chain
# ──────────────────────────────────────────────────────────────────────────────


def _seen_referents(n_referents: int, hold_frac: float, seed: int, gen: int) -> list[int]:
    """Referent indices the student SEES this generation (rotates each gen).

    ``hold_frac`` of the whole attribute-combinations are held out (so the student
    must GENERALISE the unseen combos through the factored input). ``hold_frac=0``
    -> sees all (the A1 no-bottleneck control). Promoted from the probe's
    ``seen_referents`` (same disjoint-rotation construction).
    """
    import torch

    if hold_frac <= 0.0:
        return list(range(n_referents))
    g = torch.Generator().manual_seed(seed * 100_003 + gen)
    perm = torch.randperm(n_referents, generator=g).tolist()
    n_hold = int(round(hold_frac * n_referents))
    seen = sorted(perm[n_hold:])
    if not seen:  # never hide everything
        seen = sorted(perm[:1])
    return seen


def _imitate(student: "mc.FactoredSpeaker", teacher_msgs, seen_idx, epochs: int,
             lr: float, seed: int) -> None:
    """Supervise the student to reproduce teacher messages on SEEN referents only.

    Promoted from the probe's ``imitate``: cross-entropy of the student's
    per-position logits against the teacher's discrete symbols, over the
    bottlenecked (seen) subset, so the held-out combos are underdetermined and the
    student must extrapolate compositionally.
    """
    import torch
    import torch.nn.functional as F

    torch.manual_seed(int(seed))
    student._build()
    idx = torch.tensor(sorted(seen_idx), dtype=torch.long)
    targets = torch.tensor(
        [list(teacher_msgs[i]) for i in sorted(seen_idx)], dtype=torch.long
    )
    opt = torch.optim.Adam(student.parameters(), lr=lr)
    for _epoch in range(int(epochs)):
        opt.zero_grad()
        logits = student.logits_for(idx)  # (S, MSG_LEN, VOCAB)
        loss = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]), targets.reshape(-1)
        )
        loss.backward()
        opt.step()


def _measure(spk: "mc.FactoredSpeaker") -> dict:
    """PosDis / BosDis / guarded-topsim of the speaker's FULL code, via T3 metrics."""
    msgs = spk.emit_all()
    return {
        "posdis": metrics.posdis(msgs, mc.REFERENTS, mc.VOCAB),
        "bosdis": metrics.bosdis(msgs, mc.REFERENTS, mc.VOCAB),
        "topsim": metrics.topsim_guarded(msgs, mc.REFERENTS),
    }


def run_generations(
    seed: int,
    arm: str,
    *,
    n_generations: int = MORTAL_N_GENERATIONS,
    transmission: Optional[Transmission] = None,
    hold_frac: Optional[float] = None,
    gen0_epochs: int = 600,
    imitation_epochs: int = MORTAL_IMITATION_EPOCHS,
    interaction_epochs: int = MORTAL_INTERACTION_EPOCHS,
    lr: float = 1e-2,
    hidden: int = mc._HIDDEN,
) -> dict:
    """Run one multi-generation iterated-learning chain on the T2 factored channel.

    Schedule per generation (after a gen-0 cotrained teacher):
      (a) BOTTLENECK / imitation -- a fresh student imitates the
          ``transmission``-selected teacher's discrete messages, supervised on a
          BOTTLENECKED subset (``hold_frac`` of referents held out, so the student
          must generalise the unseen attribute-combinations);
      (b) INTERACTION -- a short Lewis referential game (``mc.cotrain``) over ALL
          referents keeps the code communicative without flattening structure;
      (c) the student becomes the teacher; PosDis/BosDis/guarded-topsim of its
          FULL code are recorded.

    Arms (the NON-survival ones; A2/A5 come in T5 via a custom ``transmission``):
      * ``A1_baseline`` -> hold_frac defaults to 0.0 (NO bottleneck, continuous
        cotrain) -> should stay flat/holistic;
      * ``A3_reset`` (and any other arm) -> hold_frac defaults to the frozen
        ``MORTAL_BOTTLENECK_HOLD_FRAC`` -> the standard iterated-learning reset,
        should compositionalize (reproduces the probe rise).
    Pass ``hold_frac`` explicitly to override the per-arm default.

    The ``transmission`` callable (default :func:`select_current_teacher`) chooses
    WHICH teacher the student imitates each generation -- the pluggable seam T5
    uses to inject survival-weighted selection (see module docstring).

    Returns a dict::

        {
          "per_gen_posdis":  [float, ...],            # gen-0 baseline + each gen
          "per_gen_bosdis":  [float, ...],
          "per_gen_topsim":  [(value_or_None, defined_bool), ...],
          "final_posdis":    float,                   # == per_gen_posdis[-1]
          "accuracy_curve":  [float, ...],            # round-trip acc per entry
          "arm":             arm,
          "seed":            seed,
        }

    Deterministic: torch and ``random`` are seeded from ``seed`` so the same
    (seed, arm, schedule) reproduces the curve exactly. The REAL run uses the
    frozen prereg values (``MORTAL_*`` defaults); tests use reduced gens/epochs.
    """
    import torch

    if transmission is None:
        transmission = select_current_teacher
    if hold_frac is None:
        hold_frac = 0.0 if arm in _NO_BOTTLENECK_ARMS else MORTAL_BOTTLENECK_HOLD_FRAC

    torch.manual_seed(int(seed))
    rng = random.Random(int(seed))
    n_referents = mc.N_REFERENTS

    # gen-0: a cotrained teacher + the persistent listener (kept across the chain
    # so the interaction phase has a stable comprehender, as in the probe).
    teacher = mc.FactoredSpeaker(seed=int(seed), hidden=hidden)
    listener = mc.Listener(seed=int(seed) + 991, hidden=hidden)
    gen0_acc = mc.cotrain(teacher, listener, epochs=gen0_epochs, lr=lr, seed=int(seed))

    m0 = _measure(teacher)
    per_gen_posdis = [m0["posdis"]]
    per_gen_bosdis = [m0["bosdis"]]
    per_gen_topsim = [m0["topsim"]]
    accuracy_curve = [gen0_acc]

    for gen in range(1, int(n_generations) + 1):
        # (transmission seam) choose the teacher the next student learns from.
        state = TransmissionState(
            teacher=teacher,
            listener=listener,
            gen=gen,
            seed=int(seed),
            rng=rng,
            population=[teacher],
            fitness=None,
        )
        chosen_teacher = transmission(state)

        teacher_msgs = chosen_teacher.emit_all()
        seen = _seen_referents(n_referents, hold_frac, int(seed), gen)

        # (a) bottleneck / imitation: a FRESH student
        student = mc.FactoredSpeaker(seed=int(seed) * 131 + gen, hidden=hidden)
        _imitate(
            student, teacher_msgs, seen,
            epochs=imitation_epochs, lr=lr, seed=int(seed) * 131 + gen,
        )

        # (b) interaction: short Lewis game over ALL referents keeps it communicative
        acc = mc.cotrain(
            student, listener,
            epochs=interaction_epochs, lr=lr, seed=int(seed) * 17 + gen,
        )

        # (c) student becomes teacher; record metrics of the full code
        teacher = student
        m = _measure(teacher)
        per_gen_posdis.append(m["posdis"])
        per_gen_bosdis.append(m["bosdis"])
        per_gen_topsim.append(m["topsim"])
        accuracy_curve.append(acc)

    return {
        "per_gen_posdis": per_gen_posdis,
        "per_gen_bosdis": per_gen_bosdis,
        "per_gen_topsim": per_gen_topsim,
        "final_posdis": per_gen_posdis[-1],
        "accuracy_curve": accuracy_curve,
        "arm": arm,
        "seed": int(seed),
    }


# ──────────────────────────────────────────────────────────────────────────────
# The REAL reproducing population with IRREVERSIBLE DEATH (A2 / A5)
# ──────────────────────────────────────────────────────────────────────────────
#
# ``run_generations`` above is the single-lineage iterated-learning chain (A1/A3):
# one teacher per generation, a fresh student, no population, nobody dies. Codex's
# CRITICAL #1/#2: that makes the A2/A5 *death* arms degenerate to plain iterated
# learning when driven through the engine's 1-element ``state.population`` --
# "irreversible death" is implemented NOWHERE. The function below is the FIX: a
# genuine fixed-size population of (speaker, listener) agents, each with a unique
# lineage id, where every generation the matched-turnover number of agents are
# PERMANENTLY removed (a dead lineage id never reappears) and replaced by offspring
# that learn from a SURVIVING parent (A2 fitness-weighted / A5 uniform). Survivors
# persist UNCHANGED -- the Moran-style "offspring learn from surviving parents"
# process the strong claim rests on. It is ADDITIVE: ``run_generations`` and all its
# tests are untouched; this is a new entry point the real A2/A5 runs call.


def _measure_agent(spk: "mc.FactoredSpeaker") -> dict:
    """PosDis / BosDis / guarded-topsim of one agent's full code (alias of _measure)."""
    return _measure(spk)


def _new_agent(seed: int, hidden: int):
    """A fresh (speaker, FACTORED-listener) agent pair with deterministic per-agent seeds.

    The listener is the POSITION-AWARE :class:`mc.FactoredListener` (per-position
    embeddings concatenated, per-attribute heads), NOT the joint :class:`mc.Listener`.
    This is the selection-mechanism fix: the joint listener decodes held-out
    attribute-combinations at 0.00, capping full-grid fitness at the seen fraction
    FLAT across agents -> fitness-weighted death-selection is a coin-flip uncorrelated
    with generalization. The factored listener makes held-out combos decodable, so
    fitness carries genuine held-out signal for selection to act on.
    """
    spk = mc.FactoredSpeaker(seed=int(seed), hidden=hidden)
    lis = mc.FactoredListener(seed=int(seed) + 991, hidden=hidden)
    return spk, lis


def run_population_generations(
    seed: int,
    arm: str,
    *,
    pop_size: int = MORTAL_POP_SIZE,
    death_frac: float = MORTAL_DEATH_FRAC,
    n_generations: int = MORTAL_N_GENERATIONS,
    hold_frac: float = MORTAL_BOTTLENECK_HOLD_FRAC,
    gen0_epochs: int = 600,
    imitation_epochs: int = MORTAL_IMITATION_EPOCHS,
    interaction_epochs: int = MORTAL_INTERACTION_EPOCHS,
    readout_epochs: int = MORTAL_READOUT_EPOCHS,
    lr: float = 1e-2,
    hidden: int = mc._HIDDEN,
    return_population: bool = False,
) -> dict:
    """Run the REAL reproducing population with IRREVERSIBLE DEATH (A2 or A5).

    The multi-agent engine the strong claim needs (Codex CRITICAL #1/#2). An AGENT
    is a ``(FactoredSpeaker, FactoredListener)`` pair with a UNIQUE integer lineage
    id; the live population is a mutable list of ``pop_size`` such agents. Each
    agent's OWN POSITION-AWARE :class:`mc.FactoredListener` is still used for the
    INTERACTION (Lewis-game) phase (gen-0 and offspring ``cotrain_factored``), but
    SELECTION fitness does NOT flow through it.

    SELECTION FITNESS = a SHARED experimenter-side READOUT DECODER (confound removal).
        An adversarial review found selection SOUND but carrying removable
        per-generation NOISE because fitness used to flow through each agent's OWN
        trained listener: (a) listener init-seed luck and (b) a
        newborn(interaction_epochs)-vs-survivor(gen0_epochs) listener TRAINING-BUDGET
        asymmetry that did NOT symmetrically affect the A3-reset arm, biasing the
        headline A2-vs-A3 contrast. The approved fix (here): each generation compute
        per-agent fitness with :func:`md.readout_fitness` -- a FRESH factored decoder
        trained on the SEEN subset ONLY (speaker FROZEN; pure decode, NOT a Lewis
        game), applied identically to EVERY agent's speaker, with ``readout_epochs``
        steps and the SAME per-generation decoder seed (a deterministic function of
        (run seed, gen), IDENTICAL across agents in that generation). So any
        decoder-init/budget effect is CONSTANT across agents and cannot differentiate
        them: fitness measures ONLY the heritable speaker's held-out decodability (the
        M2 endpoint), is symmetric across all arms, and removes both nuisances. (Each
        agent's speaker maps referents to DIFFERENT messages, so each speaker needs
        its own readout fit -- "shared" means same PROCEDURE+seed+budget for all, not
        one decoder instance decoding every speaker.)

    gen 0
        Create ``pop_size`` agents with distinct seeds and lineage ids ``0..pop-1``;
        ``cotrain_factored`` EACH agent's own (speaker, factored-listener) pair on
        gen-0's SEEN subset (``_seen_referents(..., gen=0)``) for ``gen0_epochs``.
        Selection fitness is the readout fitness over gen-0's SEEN subset, so held-out
        generalisation -- hence fitness -- varies by lineage (the variance selection
        acts on). A ``next_lineage_id`` counter tracks fresh ids.

    each generation g = 1 .. n_generations
        1. recompute the SEEN subset for g;
        2. score every live agent's SPEAKER via the shared readout decoder
           (``md.readout_fitness(spk, seen, decoder_epochs=readout_epochs,
           seed=<per-gen seed, same for all agents>)``) -> ``heldout`` (pure M2 = the
           SELECTION signal) + ``full`` (secondary reported blend) per agent; the
           agent's OWN listener is NOT consulted for selection;
        3. ``n_dead = clamp(round(death_frac*pop), 0, pop-1)`` (never kill everyone);
        4. ``md.population_turnover`` decides the dead set + a surviving parent per
           dead slot, consuming the ``heldout`` readout fitness vector (FIX 1, Codex
           HIGH: selection -- death AND fitness-weighted parent -- acts on the HELD-OUT
           M2 generalization, NOT the ``full`` seen+held blend, because the rotating
           seen-split leaves seen-fitness unsaturated so ``full`` is NOT rank-equivalent
           to ``heldout``; ``select`` = "fitness" for A2, "random" for A5);
        5. IRREVERSIBLE DEATH: dead agents (and their lineage ids) are PERMANENTLY
           removed. Each dead slot gets an OFFSPRING: a fresh speaker that imitates
           its assigned surviving parent's messages on the SEEN subset
           (``imitation_epochs``), paired with a fresh FactoredListener, then the
           offspring PAIR is ``cotrain_factored`` on the SEEN subset
           (``interaction_epochs``) so its factored listener stays a communicative
           comprehender. Survivors PERSIST UNCHANGED. The offspring gets a NEW
           lineage id (``next_lineage_id++``).

    Returns a dict mirroring :func:`run_generations`' keys plus population fields::

        {
          "arm", "seed",
          "per_gen_posdis":  [float, ...],   # gen0 + each gen: MEAN PosDis over pop
          "per_gen_bosdis":  [float, ...],   # population mean
          "per_gen_topsim":  [(value_or_None, defined_bool), ...],  # FITTEST agent's
          "per_gen_posdis_best": [float, ...],   # fittest agent's PosDis (secondary)
          "final_posdis":    float,          # == per_gen_posdis[-1]
          "per_gen_fitness_mean": [float, ...],   # readout FULL fitness (secondary blend)
          "per_gen_fitness_max":  [float, ...],
          "per_gen_heldout_fitness_mean": [float, ...],  # readout HELD-OUT = SELECTION signal
          "per_gen_heldout_fitness_max":  [float, ...],
          # Rosetta load-bearing gate input: per-gen MUTED (garbled-channel) fitness
          # baseline (~chance) -- the grown per-gen fitness is compared against this for
          # the headline's "mute->survival drop each generation" AND conjunct:
          "per_gen_muted_fitness_mean":   [float, ...],
          "per_gen_muted_fitness_max":    [float, ...],
          # FIX 2 fixed-readout DIAGNOSTIC (constant seen0 split + constant decoder seed;
          # NOT used for selection -- a clean persistence/lineage-plot panel):
          "per_gen_fixed_readout_full_mean":    [float, ...],
          "per_gen_fixed_readout_full_max":     [float, ...],
          "per_gen_fixed_readout_heldout_mean": [float, ...],
          "per_gen_fixed_readout_heldout_max":  [float, ...],
          "per_gen_fixed_readout_heldout_by_lineage": [{lineage_id: float, ...}, ...],
          "deaths_per_gen":  [int, ...],     # LINEAGE deaths per gen (A2/A5: n_dead>0;
                                             #   A3: 0 -- reset is NOT death, no lineage dies)
          "turnover_per_gen": [int, ...],    # agents REPLACED/RESET per gen (A2/A5/A3:
                                             #   n_dead each gen -- matched turnover RATE)
          "population_size": pop_size,       # constant across the run
          "live_lineage_ids": [[int,...], ...],  # live id set after each generation
        }

    THE DEATH-vs-RESET MARKER (A2/A5 vs A3): for the irreversible-death arms
    (A2/A5) a chosen agent's lineage DIES -- its id is RETIRED forever, ``next_lineage_id``
    advances, and ``live_lineage_ids`` GROWS (the set of distinct ids ever seen grows by
    sum(deaths_per_gen)). For the RESET arm (A3) the chosen agent's individual PERSISTS:
    only its mind is wiped + re-learned from a COHERENT teacher drawn UNIFORMLY among the
    NON-RESET (stable, not-just-reset) agents -- the standing "language field" of agents
    whose codes were NOT wiped this generation (the population analog of A5 drawing its
    parent from survivors; fitness-blind, so NOT selection) -- so it KEEPS ITS LINEAGE ID --
    ``next_lineage_id`` does NOT advance, ``deaths_per_gen`` is all 0 (no lineage dies),
    and ``live_lineage_ids`` stays CONSTANT (= the initial pop ids ``0..pop-1``) for the
    whole run. ``turnover_per_gen`` is the matched count (= n_dead each gen) for ALL
    three arms, so A2-vs-A3 is a fair freq-matched contrast where ONLY the turnover gate
    differs (selection + death vs fitness-blind in-place reset).

    topsim choice: a population MEAN of a None/value mix is ill-defined (topsim
    returns None on zero message-distance variance), so ``per_gen_topsim`` reports
    the FITTEST agent's guarded ``(value, defined)`` rather than a meaningless mean
    -- consistent with PosDis/BosDis being population means and the secondary
    ``per_gen_posdis_best`` being the fittest agent's PosDis. "Fittest" here is the
    MAX-HELD-OUT agent (the agent SELECTION favours, FIX 1), not the max-full agent.

    FIX 2 (Codex MEDIUM) fixed-readout DIAGNOSTIC: the per-generation SELECTION readout
    rotates BOTH the seen split AND the decoder seed, so an UNCHANGED surviving speaker
    is re-scored differently each generation and its recorded selection score WOBBLES
    (measurement noise, not a lineage change). Within-generation selection is still fair
    (all agents share that gen's split+seed). For clean persistence/lineage PLOTS the
    engine ALSO records a fixed-readout panel: each generation it scores every agent
    with a CONSTANT seen split (gen-0's ``seen0``) and a single CONSTANT decoder seed
    for the whole run, so an unchanged survivor's score is exactly reproducible
    gen-to-gen. This panel is DIAGNOSTIC ONLY -- selection stays on the rotating per-gen
    held-out (the ``per_gen_fixed_readout_*`` keys, incl. the per-lineage map, never
    feed turnover).

    Validation: ``arm`` must be a population arm (A2_death / A5_selection_ablated /
    A3_reset) -- A1/A4 (non-turnover iterated learning) use :func:`run_generations`
    and raise here; ``pop_size >= 2`` (else nobody can ever die/be-reset against a
    standing population) and ``0 < death_frac < 1``. A3_reset is the frequency-matched
    COHERENT-TEACHER POPULATION-RESET arm (the matched control for A2 death; the
    population analog of the Ren/Zheng single-lineage reset): it RUNS here (no
    ValueError), with a fitness-BLIND in-place reset that KEEPS lineage ids and re-learns
    each reset agent from a teacher drawn uniformly among the NON-RESET stable agents.
    Determinism: torch and a ``random.Random`` are seeded from ``seed`` so the same
    (seed, arm) reproduces ``deaths_per_gen`` and the lineage-id history exactly.
    The REAL run uses the frozen prereg values; tests use tiny gens/epochs.
    """
    import torch

    from systems import mortal_death as md  # lazy: md imports this module

    if arm not in _POPULATION_ARMS:
        raise ValueError(
            f"run_population_generations drives only the survival-gated population "
            f"arms {sorted(_POPULATION_ARMS)}; got {arm!r} (A1/A3/A4 use "
            f"run_generations -- this engine must not silently iterated-learn them)."
        )
    if int(pop_size) < 2:
        raise ValueError(
            f"pop_size must be >= 2 (with a 1-agent population nobody can die -- the "
            f"degenerate iterated-learning case); got {pop_size}"
        )
    if not (0.0 < float(death_frac) < 1.0):
        raise ValueError(f"death_frac must be in (0, 1); got {death_frac}")

    select = _POPULATION_ARMS[arm]
    pop_size = int(pop_size)
    n_generations = int(n_generations)
    n_referents = mc.N_REFERENTS

    torch.manual_seed(int(seed))
    rng = random.Random(int(seed))

    # ---- gen 0: build + cotrain pop_size agents, each on gen-0's SEEN subset ----
    seen0 = _seen_referents(n_referents, hold_frac, int(seed), 0)
    population: list = []          # live (speaker, listener) agents
    lineage_ids: list[int] = []    # lineage id per live agent (parallel to population)
    for i in range(pop_size):
        spk, lis = _new_agent(seed=int(seed) * 1009 + i, hidden=hidden)
        mc.cotrain_factored(spk, lis, epochs=gen0_epochs, lr=lr,
                            seed=int(seed) * 1009 + i, seen_idx=seen0)
        population.append((spk, lis))
        lineage_ids.append(i)
    next_lineage_id = pop_size

    def _readout_seed(gen: int) -> int:
        """The per-generation readout-decoder seed: deterministic in (run seed, gen).

        IDENTICAL across every agent in generation ``gen`` (so the decoder
        init/budget effect is a CONSTANT that cannot differentiate agents -- the
        symmetry the confound removal needs), and a function of the run seed and the
        generation index (so it is deterministic and varies generation to
        generation). The offset is distinct from the ``_seen_referents`` seed mix.
        """
        return int(seed) * 100_003 + 524_287 * int(gen) + 1

    def _readout_vectors(seen, gen: int) -> tuple[list[float], list[float]]:
        """(full, heldout) readout-fitness vectors over the live population for ``gen``.

        Each agent's SPEAKER is scored via the SHARED experimenter readout decoder
        (:func:`md.readout_fitness`): a fresh decoder trained on ``seen`` ONLY,
        speaker FROZEN, ``readout_epochs`` steps, the SAME ``_readout_seed(gen)`` for
        every agent -- so fitness measures ONLY the heritable speaker (the agent's own
        listener is NOT consulted for selection). Returns the parallel ``full`` and
        ``heldout`` vectors.
        """
        dseed = _readout_seed(gen)
        results = [
            md.readout_fitness(spk, seen, decoder_epochs=readout_epochs, seed=dseed,
                               hidden=hidden)
            for spk, _lis in population
        ]
        return [r["full"] for r in results], [r["heldout"] for r in results]

    # ---- FIX 2 (Codex MEDIUM): FIXED-readout DIAGNOSTIC (persistence/lineage plots) ----
    # The per-generation SELECTION readout above rotates BOTH the seen split AND the
    # decoder seed, so an UNCHANGED surviving speaker is re-scored by a DIFFERENT decoder
    # on a DIFFERENT split each generation -> its recorded score WOBBLES (measurement
    # noise, not lineage change). Within-generation selection is still fair (all agents
    # share that gen's split+seed), but the wobble makes the rotating MAX a noisy
    # "lineage preservation" signal. This fixed-readout panel removes the noise: every
    # generation it ALSO scores each agent with a CONSTANT split (gen-0's ``seen0``) and
    # a single CONSTANT decoder seed for the whole run, so an unchanged survivor's score
    # is DETERMINISTIC (same speaker + same split + same decoder seed -> identical). It
    # is a DIAGNOSTIC ONLY -- selection stays on the rotating per-gen held-out (FIX 1).
    _FIXED_READOUT_SEED = int(seed) * 100_003 + 7_919

    def _fixed_readout_panel():
        """Per-agent fixed-readout (full, heldout) over ``seen0`` + the constant seed.

        Scores every live agent's SPEAKER with the SAME constant seen split (gen-0's
        ``seen0``) and the SAME ``_FIXED_READOUT_SEED`` every generation. An unchanged
        survivor therefore gets a byte-identical score gen-to-gen (deterministic), so
        the lineage-preservation diagnostic carries no rotating-readout wobble. Returns
        parallel ``full`` and ``heldout`` lists (aligned with the live population).
        """
        results = [
            md.readout_fitness(spk, seen0, decoder_epochs=readout_epochs,
                               seed=_FIXED_READOUT_SEED, hidden=hidden)
            for spk, _lis in population
        ]
        return [r["full"] for r in results], [r["heldout"] for r in results]

    def _record_fixed(diag: dict) -> None:
        """Append the fixed-readout DIAGNOSTIC panels (mean/max full+heldout + by-lineage).

        NOT a selection signal -- selection uses the rotating per-gen held-out (FIX 1).
        ``by_lineage`` maps the CURRENT live lineage id -> its fixed-readout held-out
        score, so a persistence plot can follow a single lineage and an unchanged
        survivor's score is exactly constant across generations.
        """
        ffull, fheld = _fixed_readout_panel()
        diag["fixed_full_mean"].append(sum(ffull) / len(ffull))
        diag["fixed_full_max"].append(max(ffull))
        diag["fixed_held_mean"].append(sum(fheld) / len(fheld))
        diag["fixed_held_max"].append(max(fheld))
        diag["fixed_held_by_lineage"].append(
            {lineage_ids[i]: fheld[i] for i in range(len(population))}
        )

    def _muted_baseline(gen: int) -> tuple[float, float]:
        """(mean, max) MUTED channel-fitness baseline over the live population.

        The Removability-Rosetta LOAD-BEARING gate (the headline's required AND
        conjunct: muting the grown channel must drop survival each generation) needs a
        per-generation MUTED baseline to compare the GROWN per-gen fitness against. A
        MUTED / garbled channel (:func:`md.garbled_channel`) decodes referents to a
        random permutation, so its :func:`md.channel_fitness` sits at ~chance
        (1/N_REFERENTS) and is POPULATION-INDEPENDENT in value -- but we record it
        per-agent and per-gen so the gate is EXPLICIT and robust to substrate changes
        (no training; pure eval -> cheap). The garbled seed is keyed off the run seed +
        the generation (deterministic) and the per-agent index, so the baseline is
        reproducible. Returns the population (mean, max) of those muted fitnesses.

        HONESTY: because survival here IS channel decode (``md.survival_action`` is
        injective), this muted->grown drop closely tracks the M2 held-out signal in
        this fused substrate -- documented in the verdict ``rosetta_note``; we record
        it because the prereg requires the gate, not as independent evidence.
        """
        muted = [
            md.channel_fitness(md.garbled_channel(int(seed) * 31 + int(gen) * 131 + i))
            for i in range(len(population))
        ]
        return sum(muted) / len(muted), max(muted)

    def _record(diag: dict, fits: list[float], held: list[float], *, gen: int) -> None:
        """Append population-mean PosDis/BosDis + fittest-agent topsim/PosDis + fitness.

        ``fits`` is the readout FULL fitness (the secondary reported blend; drives the
        ``per_gen_fitness_*`` mean/max), ``held`` the readout HELD-OUT-only fitness --
        the M2 SELECTION signal (FIX 1). The "fittest agent" whose topsim/PosDis is
        reported as the secondary ``best`` is the agent SELECTION favours, i.e. the
        MAX-HELDOUT agent (consistent with death+parent keying off held-out), NOT the
        max-full agent. It also records the per-gen MUTED baseline (the Rosetta
        load-bearing gate input) over the current live population.
        """
        measures = [_measure_agent(spk) for spk, _lis in population]
        diag["posdis"].append(sum(m["posdis"] for m in measures) / len(measures))
        diag["bosdis"].append(sum(m["bosdis"] for m in measures) / len(measures))
        best = max(range(len(population)), key=lambda i: (held[i], i))
        diag["topsim"].append(measures[best]["topsim"])
        diag["posdis_best"].append(measures[best]["posdis"])
        diag["fitness_mean"].append(sum(fits) / len(fits))
        diag["fitness_max"].append(max(fits))
        diag["heldout_mean"].append(sum(held) / len(held))
        diag["heldout_max"].append(max(held))
        muted_mean, muted_max = _muted_baseline(gen)
        diag["muted_mean"].append(muted_mean)
        diag["muted_max"].append(muted_max)
        # Stage-3 inter-agent panel (additive diagnostics; NOT selection signals):
        #  - cross-agent mutual intelligibility = THE shared-language signal (cross
        #    rising toward self = one shared code; cross ~ chance = private idiolects);
        #  - decode_shift = survival-decoupled positive listening (Lowe 2019);
        #  - message_entropy = entropy-minimization-collapse trip-wire (Kharitonov 2020).
        speakers = [spk for spk, _lis in population]
        listeners = [lis for _spk, lis in population]
        mii = mc.mutual_intelligibility_matrix(speakers, listeners)
        diag["mii_self"].append(mii["self"])
        diag["mii_cross"].append(mii["cross"])
        diag["mii_min_offdiag"].append(mii["min_offdiag"])
        diag["decode_shift"].append(
            sum(mc.decode_shift(spk, lis) for spk, lis in population) / len(population))
        diag["msg_entropy"].append(
            sum(mc.message_entropy_bits(spk) for spk, _lis in population) / len(population))

    diag = {"posdis": [], "bosdis": [], "topsim": [], "posdis_best": [],
            "fitness_mean": [], "fitness_max": [],
            "heldout_mean": [], "heldout_max": [],
            # Rosetta load-bearing gate input: the per-gen MUTED channel-fitness
            # baseline (garbled channel -> ~chance) the grown per-gen fitness is
            # compared against (mute->survival drop each generation).
            "muted_mean": [], "muted_max": [],
            # FIX 2 fixed-readout DIAGNOSTIC panels (not selection):
            "fixed_full_mean": [], "fixed_full_max": [],
            "fixed_held_mean": [], "fixed_held_max": [],
            "fixed_held_by_lineage": [],
            # Stage-3 inter-agent panels (additive):
            "mii_self": [], "mii_cross": [], "mii_min_offdiag": [],
            "decode_shift": [], "msg_entropy": []}
    deaths_per_gen: list[int] = []     # LINEAGE deaths (A2/A5: n_dead; A3: 0)
    turnover_per_gen: list[int] = []   # agents replaced/reset (A2/A5/A3: n_dead) -- matched
    live_lineage_ids: list[list[int]] = []

    # gen-0 baseline metrics (over the live, just-cotrained population): selection
    # fitness is the shared readout decoder over gen-0's SEEN subset.
    full0, held0 = _readout_vectors(seen0, 0)
    _record(diag, full0, held0, gen=0)
    _record_fixed(diag)  # FIX 2 diagnostic panel (gen-0 baseline)

    for gen in range(1, n_generations + 1):
        seen = _seen_referents(n_referents, hold_frac, int(seed), gen)
        # SELECTION fitness = shared experimenter readout decoder (NOT the agent's own
        # listener). FIX 1 (Codex HIGH): selection acts on the HELD-OUT (M2) vector,
        # NOT the full seen+held blend. Because the bottleneck seen-split ROTATES each
        # generation, a survivor's seen-fitness is NOT saturated, so ``full`` is not
        # rank-equivalent to ``heldout`` (measured Spearman(full, heldout) ~0.74 at the
        # prereg budget) -- selecting on ``full`` would partly select for seen-set
        # readout fit, not pure held-out generalization. ``full`` is still recorded as
        # the secondary reported blend.
        fits, held = _readout_vectors(seen, gen)

        n_dead = int(round(death_frac * pop_size))
        n_dead = max(0, min(n_dead, pop_size - 1))

        if select == "reset":
            # ---- A3: frequency-matched COHERENT-TEACHER POPULATION RESET (NO death,
            # NO selection) ----
            # A fitness-BLIND random subset of size n_dead is RESET IN PLACE: each
            # chosen agent's mind is wiped (fresh speaker that RE-IMITATES a COHERENT
            # teacher drawn UNIFORMLY among the NON-RESET (stable) agents' pre-reset
            # speakers -- the standing language field of codes NOT wiped this gen --
            # then a fresh FactoredListener is cotrained), but the INDIVIDUAL PERSISTS:
            # it KEEPS ITS LINEAGE ID. Fitness is NEVER read -- pass a DUMMY zero vector
            # so turnover provably cannot consume it; the non-reset teacher pool (NOT
            # survivors, NOT the full pool) makes the reset FAIR (coherent lineage to
            # ratchet) yet still distinct from A5's "offspring of a survivor" (A3 keeps
            # the lineage, no death).
            dummy_fits = [0.0] * pop_size
            reset_idx, teachers = md.population_turnover(dummy_fits, n_dead, select, rng)

            # capture ALL pre-reset speakers' messages BEFORE mutating any slot, so a
            # reset agent may re-imitate even another to-be-reset agent's pre-reset
            # speaker (build-before-commit, matching the A2/A5 ordering).
            pre_reset_msgs = [spk.emit_all() for spk, _lis in population]
            rebuilt: list = []  # (slot, new_agent) per reset slot -- lineage id KEPT
            for slot, teacher_i in zip(sorted(reset_idx), teachers):
                teacher_msgs = pre_reset_msgs[teacher_i]
                # deterministic per-reset seed keyed off the PERSISTING lineage id +
                # the generation (the individual is re-learning, not a new lineage).
                reset_seed = int(seed) * 6151 + lineage_ids[slot] * 97 + gen
                new_spk = mc.FactoredSpeaker(seed=reset_seed, hidden=hidden)
                _imitate(new_spk, teacher_msgs, seen, epochs=imitation_epochs, lr=lr,
                         seed=reset_seed)
                new_lis = mc.FactoredListener(seed=reset_seed + 991, hidden=hidden)
                mc.cotrain_factored(new_spk, new_lis, epochs=interaction_epochs, lr=lr,
                                    seed=reset_seed, seen_idx=seen)
                rebuilt.append((slot, (new_spk, new_lis)))

            # commit: the reset slots get a fresh mind but KEEP their lineage id
            # (no id retired, next_lineage_id does NOT advance); others UNCHANGED.
            for slot, new_agent in rebuilt:
                population[slot] = new_agent
                # lineage_ids[slot] is INTENTIONALLY left as-is (the individual persists)

            deaths_per_gen.append(0)            # no lineage dies under A3
            turnover_per_gen.append(len(reset_idx))
            live_lineage_ids.append(list(lineage_ids))  # CONSTANT for A3 (= initial ids)
        else:
            # ---- A2/A5: IRREVERSIBLE DEATH + reproduction (UNCHANGED) ----
            # turnover (death + fitness-weighted parent) keys off the HELD-OUT vector.
            dead_idx, parents = md.population_turnover(held, n_dead, select, rng)

            # build each offspring from its assigned surviving parent BEFORE mutating
            # the list (parents index the CURRENT pop).
            offspring: list = []  # (dead_slot, new_agent, child_lineage_id) per dead slot
            for slot, parent_i in zip(sorted(dead_idx), parents):
                parent_spk, _parent_lis = population[parent_i]
                parent_msgs = parent_spk.emit_all()
                child_spk = mc.FactoredSpeaker(
                    seed=int(seed) * 7919 + next_lineage_id, hidden=hidden)
                _imitate(child_spk, parent_msgs, seen, epochs=imitation_epochs, lr=lr,
                         seed=int(seed) * 7919 + next_lineage_id)
                child_lis = mc.FactoredListener(
                    seed=int(seed) * 7919 + next_lineage_id + 991, hidden=hidden)
                mc.cotrain_factored(child_spk, child_lis, epochs=interaction_epochs, lr=lr,
                                    seed=int(seed) * 7919 + next_lineage_id, seen_idx=seen)
                offspring.append((slot, (child_spk, child_lis), next_lineage_id))
                next_lineage_id += 1

            # commit: dead agents PERMANENTLY removed (their lineage ids never reused),
            # each vacated slot filled by its offspring; survivors carried over UNCHANGED.
            for slot, child_agent, child_id in offspring:
                population[slot] = child_agent
                lineage_ids[slot] = child_id

            deaths_per_gen.append(n_dead)
            turnover_per_gen.append(n_dead)
            live_lineage_ids.append(list(lineage_ids))

        # record metrics over the NEW live population (post-turnover), via the shared
        # readout decoder for generation ``gen`` (same SEEN subset / decoder seed).
        post_full, post_held = _readout_vectors(seen, gen)
        _record(diag, post_full, post_held, gen=gen)
        _record_fixed(diag)  # FIX 2 diagnostic panel (post-turnover, this gen)

    result = {
        "arm": arm,
        "seed": int(seed),
        "per_gen_posdis": diag["posdis"],
        "per_gen_bosdis": diag["bosdis"],
        "per_gen_topsim": diag["topsim"],
        "per_gen_posdis_best": diag["posdis_best"],
        "final_posdis": diag["posdis"][-1],
        "per_gen_fitness_mean": diag["fitness_mean"],
        "per_gen_fitness_max": diag["fitness_max"],
        "per_gen_heldout_fitness_mean": diag["heldout_mean"],
        "per_gen_heldout_fitness_max": diag["heldout_max"],
        # Rosetta load-bearing gate input: the per-gen MUTED (garbled-channel) fitness
        # baseline (~chance) the GROWN per-gen fitness is compared against (the
        # mute->survival drop the headline requires EACH generation). Closely tracks M2
        # in this fused-survival substrate (documented in the verdict rosetta_note).
        "per_gen_muted_fitness_mean": diag["muted_mean"],
        "per_gen_muted_fitness_max": diag["muted_max"],
        # FIX 2 fixed-readout DIAGNOSTIC panels (constant split + constant seed):
        # NOT a selection signal -- a clean persistence/lineage-plot diagnostic where an
        # unchanged survivor's score is exactly reproducible gen-to-gen.
        "per_gen_fixed_readout_full_mean": diag["fixed_full_mean"],
        "per_gen_fixed_readout_full_max": diag["fixed_full_max"],
        "per_gen_fixed_readout_heldout_mean": diag["fixed_held_mean"],
        "per_gen_fixed_readout_heldout_max": diag["fixed_held_max"],
        "per_gen_fixed_readout_heldout_by_lineage": diag["fixed_held_by_lineage"],
        "deaths_per_gen": deaths_per_gen,
        "turnover_per_gen": turnover_per_gen,
        "population_size": pop_size,
        "live_lineage_ids": live_lineage_ids,
        # Stage-3 inter-agent panels (additive; cross rising toward self = a SHARED
        # grown language; decode_shift = positive listening; msg_entropy = collapse guard):
        "per_gen_mii_self": diag["mii_self"],
        "per_gen_mii_cross": diag["mii_cross"],
        "per_gen_mii_min_offdiag": diag["mii_min_offdiag"],
        "per_gen_decode_shift": diag["decode_shift"],
        "per_gen_msg_entropy": diag["msg_entropy"],
    }
    if return_population:
        # the live GROWN (speaker, listener) pairs -- in-memory only (not JSON), for the
        # Stage-1+3 bridge: re-run the type-coordination task with the grown shared code.
        result["population"] = list(population)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Frequency-matcher: PURE functions (no torch, no death arm needed)
# ──────────────────────────────────────────────────────────────────────────────
#
# These let A3's artificial-reset timing be matched to A2's death-interval timing
# so the death-vs-reset contrast isolates SURVIVAL-GATING, not schedule. They
# operate on INTER-EVENT INTERVALS (gaps between consecutive event ticks): A2's
# death intervals vs A3's reset intervals. T8 supplies A2's death-interval
# histogram as the target.


def _intervals_from_ticks(event_ticks) -> list[int]:
    """Inter-event gaps from a list of absolute (monotonic) event ticks."""
    ticks = sorted(int(t) for t in event_ticks)
    return [ticks[i] - ticks[i - 1] for i in range(1, len(ticks))]


def interval_histogram(event_ticks, *, intervals: bool = False) -> dict[int, float]:
    """Normalised histogram of inter-event intervals.

    By default ``event_ticks`` are absolute event TICKS and the histogram is over
    the inter-event GAPS (the natural "how often do events happen" distribution).
    Pass ``intervals=True`` to treat the input as already-computed intervals.

    Returns ``{interval: probability}`` summing to 1.0 (empty dict for < 2 ticks /
    no intervals). PURE: no torch, deterministic.
    """
    if intervals:
        gaps = [int(g) for g in event_ticks]
    else:
        gaps = _intervals_from_ticks(event_ticks)
    if not gaps:
        return {}
    counts = Counter(gaps)
    total = sum(counts.values())
    return {k: counts[k] / total for k in counts}


def _cdf_at(hist: dict[int, float], x: int) -> float:
    """Cumulative probability P(interval <= x) of a normalised histogram."""
    return sum(p for k, p in hist.items() if k <= x)


def ks_distance(hist_a: dict[int, float], hist_b: dict[int, float]) -> float:
    """Kolmogorov-Smirnov distance between two interval histograms.

    The KS statistic is the maximum absolute difference between the two empirical
    CDFs over the union of their support. 0.0 for identical histograms, up to 1.0
    for disjoint ones. Two empty histograms are identical -> 0.0; one empty and
    one not -> 1.0. PURE / deterministic.
    """
    if not hist_a and not hist_b:
        return 0.0
    if not hist_a or not hist_b:
        return 1.0
    support = sorted(set(hist_a) | set(hist_b))
    return max(abs(_cdf_at(hist_a, x) - _cdf_at(hist_b, x)) for x in support)


def matched_reset_schedule(target_intervals, n: int, seed: int) -> list[int]:
    """A reset schedule (absolute ticks) whose interval histogram matches a TARGET.

    Builds ``n`` reset events whose ``n-1`` inter-event GAPS REPRODUCE the
    EMPIRICAL distribution of ``target_intervals`` (A2's death intervals, supplied
    by T8) as faithfully as the gap count allows: each distinct target interval is
    allocated a share of the ``n-1`` gaps PROPORTIONAL to its target probability
    (largest-remainder rounding), so the reset interval histogram is KS-close to
    the target by construction (KS -> 0, well under
    ``MORTAL_FREQ_MATCH_KS_MAX``). The gaps are then ORDERED by a fixed seeded
    ``random.Random`` -- the seed varies the ORDER (which decouples reset timing
    from survival) WITHOUT perturbing the matched distribution.

    ``target_intervals`` is a list of inter-event gaps (NOT absolute ticks).
    Returns a sorted list of ``n`` absolute integer tick positions (so its own
    inter-event intervals reproduce the target distribution). Deterministic in
    ``seed``. PURE: no torch.
    """
    gaps_pool = [int(g) for g in target_intervals if int(g) > 0]
    if n <= 0:
        return []
    if n == 1 or not gaps_pool:
        if not gaps_pool:
            # no target structure to match -> degenerate evenly-spaced unit schedule
            return list(range(n))
        return [0]

    n_gaps = n - 1
    hist = Counter(gaps_pool)
    total = sum(hist.values())

    # Largest-remainder apportionment of n_gaps across the distinct intervals so
    # the realised proportions track the target proportions as closely as an
    # integer count permits (this is what drives KS -> 0).
    quotas = {}
    remainders = []
    assigned = 0
    for interval, count in sorted(hist.items()):
        exact = n_gaps * count / total
        base = int(exact)
        quotas[interval] = base
        assigned += base
        remainders.append((exact - base, interval))
    # distribute the leftover gaps to the largest fractional remainders
    leftover = n_gaps - assigned
    for _frac, interval in sorted(remainders, key=lambda t: (-t[0], t[1]))[:leftover]:
        quotas[interval] += 1

    gaps = []
    for interval, q in quotas.items():
        gaps.extend([interval] * q)

    rng = random.Random(int(seed))
    rng.shuffle(gaps)

    ticks = [0]
    for g in gaps:
        ticks.append(ticks[-1] + g)
    return ticks


def freq_match_valid(target_intervals, reset_schedule) -> bool:
    """True iff the reset schedule's interval histogram matches the target's.

    Matched ⇔ ``ks_distance`` between the target interval histogram and the reset
    schedule's interval histogram is ``<= MORTAL_FREQ_MATCH_KS_MAX`` (the frozen
    prereg threshold; above it A3 is not a fair frequency-matched control ->
    FREQ_MATCH_INVALID). ``target_intervals`` are inter-event gaps;
    ``reset_schedule`` are absolute reset ticks. PURE / deterministic.
    """
    target_hist = interval_histogram(target_intervals, intervals=True)
    reset_hist = interval_histogram(reset_schedule)
    return ks_distance(target_hist, reset_hist) <= MORTAL_FREQ_MATCH_KS_MAX


# ──────────────────────────────────────────────────────────────────────────────
# COUNT-aware frequency-matcher (additive) — matches BOTH the inter-generation
# timing AND the per-generation death COUNT structure
# ──────────────────────────────────────────────────────────────────────────────
#
# A2's death schedule has TWO pieces of structure that the bare interval matcher
# above conflates / drops (independent-review fix #3): (a) the inter-(death-)
# generation TIMING -- gaps between successive generations that had >= 1 death --
# and (b) the per-generation death COUNT -- how MANY die in each such generation.
# When multiple agents die in one generation the raw tick stream has zero-gaps that
# the three consumers treated inconsistently. The functions below represent the
# schedule explicitly as (counts, intervals) and make A3 reproduce BOTH, so the
# decisive A2-vs-A3 frequency-matched control is not weakened by a count mismatch.
#
# A schedule here is a "count schedule": a list of (gen_index, n_deaths) events with
# n_deaths >= 1, one entry per generation that had deaths, gen_index strictly
# increasing. ``intervals`` = the positive gaps between consecutive gen_index;
# ``counts`` = the per-event n_deaths.

# Minimum number of distinct death GENERATIONS for a death history to be a valid
# freq-match TARGET. Below this there is no interval distribution to match (an
# empty / single-event history is NOT trivially matchable -> INVALID, the analog of
# FREQ_MATCH_INVALID). Frozen here (not in prereg) as a structural floor.
MIN_DEATH_EVENTS: int = 2


def count_histogram(counts) -> dict[int, float]:
    """Normalised histogram of per-generation death COUNTS (sums to 1.0; {} if none).

    ``counts`` is the list of per-death-generation death counts (each >= 1). Used
    alongside :func:`interval_histogram` so a matched reset reproduces the death
    MULTIPLICITY per generation, not just the inter-generation timing. PURE.
    """
    vals = [int(c) for c in counts if int(c) > 0]
    if not vals:
        return {}
    counter = Counter(vals)
    total = sum(counter.values())
    return {k: counter[k] / total for k in counter}


def matched_count_schedule(target_intervals, target_counts, n_events: int, seed: int):
    """A count-schedule reproducing BOTH the interval AND the count distribution.

    Builds ``n_events`` death-like events as a list of ``(gen_index, n_deaths)``
    pairs whose ``n_events - 1`` inter-event GAPS reproduce ``target_intervals`` and
    whose per-event COUNTS reproduce ``target_counts`` -- each by the same
    largest-remainder apportionment :func:`matched_reset_schedule` uses (so both
    KS distances -> 0 by construction). The gaps and the counts are independently
    seeded-shuffled (decoupling A3's reset timing AND multiplicity from survival
    while keeping both distributions matched). Deterministic in ``seed``. PURE.

    Returns ``[(gen_index, n_deaths), ...]`` with strictly increasing gen_index
    starting at 0 and every ``n_deaths >= 1``.
    """
    if n_events <= 0:
        return []
    gap_ticks = matched_reset_schedule(target_intervals, n=n_events, seed=seed)
    # gap_ticks has n_events absolute positions; turn into gen indices.
    gen_indices = sorted(int(t) for t in gap_ticks)
    # apportion n_events counts across the target count distribution.
    counts = _apportion(target_counts, n_events, default=1)
    rng = random.Random(int(seed) * 6_700_417 + 17)
    rng.shuffle(counts)
    return list(zip(gen_indices, counts))


def _apportion(target_values, n: int, *, default: int) -> list[int]:
    """``n`` integer draws reproducing the empirical distribution of ``target_values``.

    Largest-remainder apportionment (the same construction
    :func:`matched_reset_schedule` uses for gaps). If ``target_values`` is empty,
    returns ``n`` copies of ``default``. Each returned value is one of the observed
    target values (>= 1 expected for counts). PURE / deterministic in input order.
    """
    pool = [int(v) for v in target_values if int(v) >= 1]
    if not pool or n <= 0:
        return [int(default)] * max(0, n)
    hist = Counter(pool)
    total = sum(hist.values())
    quotas = {}
    remainders = []
    assigned = 0
    for value, count in sorted(hist.items()):
        exact = n * count / total
        base = int(exact)
        quotas[value] = base
        assigned += base
        remainders.append((exact - base, value))
    leftover = n - assigned
    for _frac, value in sorted(remainders, key=lambda t: (-t[0], t[1]))[:leftover]:
        quotas[value] += 1
    out = []
    for value, q in quotas.items():
        out.extend([value] * q)
    return out


def freq_match_counts_valid(target_intervals, target_counts, count_schedule) -> bool:
    """True iff a count-schedule matches the target on BOTH timing AND counts.

    A valid frequency-matched A3 must reproduce BOTH (independent-review fix #3):
      * the inter-generation INTERVAL distribution (KS <= MORTAL_FREQ_MATCH_KS_MAX),
      * the per-generation death-COUNT distribution (KS <= MORTAL_FREQ_MATCH_KS_MAX),
    AND the target must itself be a non-degenerate death history: at least
    :data:`MIN_DEATH_EVENTS` death generations with at least one positive interval
    (an empty / no-death / single-event history is NOT trivially matchable ->
    INVALID). ``count_schedule`` is ``[(gen_index, n_deaths), ...]``. PURE.
    """
    tgt_intervals = [int(g) for g in target_intervals if int(g) > 0]
    tgt_counts = [int(c) for c in target_counts if int(c) >= 1]
    # degenerate target -> invalid (not trivially matchable).
    if len(tgt_counts) < MIN_DEATH_EVENTS or len(tgt_intervals) < 1:
        return False
    if not count_schedule:
        return False
    sched_gens = sorted(int(g) for g, _c in count_schedule)
    sched_intervals = [sched_gens[i] - sched_gens[i - 1] for i in range(1, len(sched_gens))]
    sched_counts = [int(c) for _g, c in count_schedule]

    interval_ok = ks_distance(
        interval_histogram(tgt_intervals, intervals=True),
        interval_histogram(sched_intervals, intervals=True),
    ) <= MORTAL_FREQ_MATCH_KS_MAX
    counts_ok = ks_distance(
        count_histogram(tgt_counts), count_histogram(sched_counts)
    ) <= MORTAL_FREQ_MATCH_KS_MAX
    return interval_ok and counts_ok
