"""The A2 DEATH arm + A5 selection-ablated arm for the Mortal-Bottleneck (T5).

This module makes the iterated-learning bottleneck ENDOGENOUS: an agent's survival
depends on DECODING the emergent channel into the correct survival action; agents
die; offspring learn from SURVIVING parents (fitness-weighted). It plugs into the
T4 ``transmission(state) -> teacher`` seam (``systems/mortal_generations.py``)
WITHOUT rewriting the engine -- A2/A5 are just custom ``transmission`` callables.

The survival-coupling design (honesty-first)
--------------------------------------------
Survival is a SINGLE shared, FIXED foraging policy over the validated
type×bearing×distance referent grid (``mortal_channel.REFERENTS``):

  * :func:`survival_action` maps each referent to the ONE correct survival action.
    It is identical for every agent -- so foraging skill is NOT a heritable
    confound (the killer-confound #2 in the design spec §5): the ONLY thing that
    varies between agents, and the ONLY thing inherited, is the COMMUNICATION
    CHANNEL. (The fuller frozen-foraging + channel-lesion controls are T7; this
    module is built so they remain possible -- the policy is already frozen and
    channel-independent here.)
  * A "channel" decodes a heard message back to a referent. An agent, BLIND,
    survives by hearing the speaker's message for the true referent and taking
    ``survival_action(decoded)``. :func:`channel_fitness` = the fraction of the
    referent grid where the agent's decoded action MATCHES the correct action. So
    a GARBLED channel decodes to wrong referents -> wrong actions -> LOW fitness;
    an ORACLE (perfectly compositional) channel decodes correctly -> HIGH fitness.
    Survival is therefore GENUINELY channel-gated (tested), which is the only thing
    that makes "selection-on-language" real rather than a sham.

The two survival-gated arms (matched turnover; selection-on-meaning vs blind turnover)
--------------------------------------------------------------------------------------
Both arms keep a fixed-size population, evaluate each agent's channel fitness, and
each generation kill the SAME NUMBER of agents (``round(death_frac * pop)``) -- so
turnover RATE, population size, and the bottleneck are MATCHED. What differs is
whether fitness gates survival/reproduction at all:

  * :func:`a2_death_transmission` -- selection-on-meaning ON: lowest-fitness agents
    DIE (selective mortality) AND the next teacher is FITNESS-WEIGHTED among
    survivors (selective reproduction).
  * :func:`a5_selection_ablated_transmission` -- selection-on-meaning OFF: a RANDOM
    subset of the same size dies AND the teacher is UNIFORM among survivors;
    neither death nor birth depends on decode accuracy.

CLAIM PRECISION (independent-review fix #2): A2 − A5 isolates "selection-on-meaning
acting through BOTH differential mortality AND differential reproduction" vs
"fitness-blind turnover at the same rate" -- NOT "the choice of teacher alone" (an
earlier draft overclaimed that). The two gates are COUPLED here, so a positive
A2 − A5 delta attributes to selection-on-meaning in the AGGREGATE. To attribute it
to mortality vs reproduction separately, a later task can split the single
``select`` knob (see :class:`_DeathTransmission`) into independent ``death_select``
/ ``teacher_select`` knobs and add the two intermediate 2×2-factorial cells
(``[fitness-death+uniform-teacher]``, ``[random-death+fitness-teacher]``) as extra
arms -- no change to the survival model or the engine seam.

Each arm records WHEN deaths happen as a canonical schedule of
``(generation, n_deaths)`` events (:meth:`_DeathTransmission.death_schedule`) and
derives ALL freq-match views from it consistently (fix #3): inter-GENERATION timing
(:meth:`death_intervals`) AND per-generation death COUNT (:meth:`death_counts`). A3
in T8 must match BOTH (timing alone is insufficient when several agents die in one
generation) via ``mg.matched_count_schedule`` / ``mg.freq_match_counts_valid``,
which also flags a no-death / single-event history INVALID (not trivially
matchable). The timing-only ``mg.matched_reset_schedule`` / ``mg.freq_match_valid``
stays available.

Honest scope (what T5 does and does NOT claim)
----------------------------------------------
T5 supplies the survival-coupling MODEL + A2/A5 selection logic + the death-
schedule exposure, and proves on a real multi-agent population (the fixed-population
tests) that survival is channel-gated, A2 selects fitness while A5 does not at
matched turnover, and the A2 schedule is freq-matchable on timing AND counts. The
T4 engine's ``run_generations`` currently passes a ONE-element ``state.population``,
so driving A2/A5 THROUGH the engine degenerates to plain iterated learning (1 agent
-> nobody dies): the engine tests verify SEAM WIRING only and assert that limitation
explicitly. Growing the engine's population (and the frozen-foraging + channel-
lesion hitchhiking controls of design §5 #2) is the separate engine-population /
T7 work; this module is a drop-in for it -- pass a real multi-member ``population``
of ``(speaker, listener)`` pairs / :class:`Channel`\\ s and the death/selection/
turnover/freq-match logic already consumes it. Survival is channel-DECODE-gated
only (no foraging-skill term) -- the frozen-foraging premise T7 will exploit.

Conventions mirror the sibling modules: ``from __future__ import annotations``,
frozen geometry from ``config/prereg_mortal`` via ``mortal_channel`` (nothing
hardcoded), torch imported LAZILY only where the learnable channel is touched (the
hand-built channels + selection/turnover/freq-match logic run with no torch), and
``random.Random`` seeded from the run seed for determinism.
"""

from __future__ import annotations

import random
from typing import Optional

from systems import mortal_channel as mc
from systems import mortal_generations as mg

__all__ = [
    "survival_action",
    "Channel",
    "oracle_channel",
    "garbled_channel",
    "partial_channel",
    "channel_fitness",
    "channel_fitness_on",
    "fit_readout_decoder",
    "readout_fitness",
    "evaluate_population",
    "count_deaths",
    "weighted_choice",
    "population_turnover",
    "a2_death_transmission",
    "a5_selection_ablated_transmission",
]


# ──────────────────────────────────────────────────────────────────────────────
# The FIXED / standardized foraging policy (the only heritable variation is the
# channel -- foraging skill is NOT a hidden heritable confound; design §5 #2)
# ──────────────────────────────────────────────────────────────────────────────


def survival_action(referent: mc.Referent) -> str:
    """The ONE correct survival action for a referent -- a SINGLE shared, fixed map.

    A deterministic, total, INJECTIVE function of the ``(type, bearing, distance)``
    referent, IDENTICAL for every agent: a correct decode -> correct action; a
    mis-decode -> wrong action -> starves. The policy being shared, the ONLY
    heritable variation (and the only thing selection acts on) is the COMMUNICATION
    CHANNEL -- foraging skill cannot hitchhike (the frozen-foraging premise of the
    T7 hitchhiking control, enforced here by construction). The action string
    encodes all three attributes (e.g. ``"go_bearing2_dist1_t0"``) so it is correct
    iff the WHOLE referent is decoded; decode accuracy maps faithfully to survival.
    """
    t, b, d = (int(x) for x in referent)
    return f"go_bearing{b}_dist{d}_t{t}"


# ──────────────────────────────────────────────────────────────────────────────
# Channels: the decode map an agent uses to turn a heard message into an action
# ──────────────────────────────────────────────────────────────────────────────


class Channel:
    """An agent's communication channel: heard-referent -> decoded-referent map.

    Abstracts what a blind agent recovers when the lookout speaks about the true
    referent. A real grown channel is a (speaker, listener) pair (see
    :func:`speaker_listener_channel`); the hand-built oracle / garbled / partial
    channels here exercise the survival-coupling + selection + turnover logic
    deterministically WITHOUT training. ``decode(r)`` = the referent believed heard.
    """

    def __init__(self, decode_map: dict) -> None:
        # decode_map[true_referent] = decoded_referent (what the agent recovers)
        self._decode = {tuple(k): tuple(v) for k, v in decode_map.items()}

    def decode(self, referent: mc.Referent) -> mc.Referent:
        return self._decode.get(tuple(referent), tuple(referent))


def oracle_channel() -> Channel:
    """A PERFECT (compositional) channel: decodes every referent correctly.

    The positive control for the channel-gating check -- an oracle agent always
    takes the correct survival action, so its fitness is ~1.0.
    """
    return Channel({r: r for r in mc.REFERENTS})


def garbled_channel(seed: int = 0) -> Channel:
    """A HOLISTIC / garbled channel: decodes referents to a random permutation.

    The negative control: a derangement-like random remapping of referents, so the
    agent's decoded action is almost always WRONG and its survival fitness is poor.
    Deterministic in ``seed``.
    """
    rng = random.Random(int(seed) * 7919 + 13)
    targets = list(mc.REFERENTS)
    rng.shuffle(targets)
    return Channel({r: t for r, t in zip(mc.REFERENTS, targets)})


def partial_channel(correct_frac: float, seed: int = 0) -> Channel:
    """A channel that decodes a known FRACTION of referents correctly.

    Lets fitness be tested as a smooth, monotone function of decode accuracy. A
    ``correct_frac`` of the referents map to themselves (correct); the rest are
    shuffled among themselves (wrong, like a garbled sub-channel). Deterministic in
    ``seed``.
    """
    frac = max(0.0, min(1.0, float(correct_frac)))
    rng = random.Random(int(seed) * 104_729 + 7)
    refs = list(mc.REFERENTS)
    n_correct = int(round(frac * len(refs)))
    perm = refs[:]
    rng.shuffle(perm)
    correct_set = set(perm[:n_correct])
    wrong = [r for r in refs if r not in correct_set]
    wrong_targets = wrong[:]
    if len(wrong_targets) > 1:
        # rotate so wrong referents decode to a DIFFERENT (wrong) referent
        wrong_targets = wrong_targets[1:] + wrong_targets[:1]
    decode_map = {}
    for r in refs:
        decode_map[r] = r if r in correct_set else wrong_targets[wrong.index(r)]
    return Channel(decode_map)


def speaker_listener_channel(speaker: "mc.FactoredSpeaker", listener: "mc.Listener") -> Channel:
    """Build a :class:`Channel` from a GROWN (speaker, listener) pair.

    Blind decode = ``listener.predict(speaker.emit(referent))`` -- the round-trip
    the survival episode runs. Touches torch lazily; used by the grown engine path.
    """
    decode_map = {}
    msgs = speaker.emit_all()
    for i, msg in enumerate(msgs):
        true_ref = mc.index_to_referent(i)
        decode_map[true_ref] = tuple(listener.predict(msg))
    return Channel(decode_map)


# ──────────────────────────────────────────────────────────────────────────────
# Channel-gated fitness + population survival
# ──────────────────────────────────────────────────────────────────────────────


def channel_fitness(channel: Channel) -> float:
    """Fitness = fraction of the referent grid the agent acts correctly on, BLIND.

    For each referent the agent hears the message, decodes it, and takes
    ``survival_action(decoded)``; it survives that referent iff the action MATCHES
    the correct ``survival_action(true)``. Fitness is the mean over all referents
    -- a clean [0, 1] scalar that is GENUINELY channel-gated: a better-decoding
    channel scores higher, a garbled one scores at the random-decode floor. The
    survival policy being identical for all agents, this fitness reflects ONLY the
    channel (no foraging-skill confound).
    """
    correct = 0
    for r in mc.REFERENTS:
        decoded = channel.decode(r)
        if survival_action(decoded) == survival_action(r):
            correct += 1
    return correct / mc.N_REFERENTS


def channel_fitness_on(channel: Channel, idxs) -> float:
    """Channel fitness restricted to a SUBSET of referent indices.

    Like :func:`channel_fitness` but the mean survival-action match is taken only
    over the referents at ``idxs`` (e.g. the HELD-OUT complement of a seen subset),
    so a held-out-only generalization score can be read off the same channel. An
    empty ``idxs`` returns 0.0. The full-grid :func:`channel_fitness` is the special
    case ``idxs == range(N_REFERENTS)``.
    """
    idxs = [int(i) for i in idxs]
    if not idxs:
        return 0.0
    correct = 0
    for i in idxs:
        r = mc.index_to_referent(i)
        if survival_action(channel.decode(r)) == survival_action(r):
            correct += 1
    return correct / len(idxs)


def evaluate_population(population) -> list[float]:
    """Per-agent channel fitness for a population of :class:`Channel`\\ s."""
    return [channel_fitness(c) for c in population]


def count_deaths(population, *, survive_threshold: float) -> int:
    """How many agents would DIE: those whose channel fitness is below threshold.

    A purely channel-gated mortality rule (no foraging term); the channel-gating
    honesty check uses it to show a garbled-channel population dies more.
    """
    fits = evaluate_population(population)
    return sum(1 for f in fits if f < survive_threshold)


# ──────────────────────────────────────────────────────────────────────────────
# SHARED experimenter-side readout-decoder selection fitness (confound removal)
# ──────────────────────────────────────────────────────────────────────────────
#
# An adversarial review found the reproducing-population selection (above) SOUND but
# carrying removable per-generation NOISE: fitness flowed through each agent's OWN
# trained listener, so it picked up (a) listener init-seed luck and (b) a
# newborn(interaction_epochs)-vs-survivor(gen0_epochs) listener TRAINING-BUDGET
# asymmetry that did NOT symmetrically affect the A3-reset arm, biasing the headline
# A2-vs-A3 contrast. The approved fix: score selection fitness with a SHARED
# experimenter-side FACTORED readout decoder -- a FRESH decoder trained each
# generation on the SEEN subset, applied identically to EVERY agent's speaker, the
# SPEAKER FROZEN. Fitness then measures ONLY the heritable speaker's held-out
# decodability (the M2 endpoint), is symmetric across all arms, and removes both
# nuisances. It also yields a held-out-ONLY fitness number for free.
#
# This is a SUPERVISED readout (speaker frozen -> pure decode), NOT a Lewis game:
# the decoder learns message->attributes from the speaker's hard argmax messages on
# the SEEN indices, with per-attribute cross-entropy. Held-out indices are NEVER
# shown. Determinism + symmetry: SAME decoder_epochs and SAME decoder seed for every
# agent in a generation, so any decoder-init/budget effect is CONSTANT across agents
# and cannot differentiate them -- the only thing that varies is the heritable speaker.


def fit_readout_decoder(speaker, seen_idx, *, epochs: int, seed: int,
                        hidden: int = mc._HIDDEN) -> "mc.FactoredListener":
    """Train a FRESH factored decoder on the SEEN subset, the SPEAKER FROZEN.

    Builds a fresh :class:`mc.FactoredListener` (deterministic init via
    ``torch.manual_seed(seed)``) and trains ONLY the decoder -- the speaker's
    parameters are NOT in the optimizer, so the speaker is FROZEN (pure decode, NOT a
    Lewis game). The decoder learns the speaker's HARD (argmax) ``emit_all()``
    messages on the SEEN indices -> the TRUE per-attribute values of those referents
    via per-attribute cross-entropy, ``epochs`` Adam steps. HELD-OUT referents are
    NEVER shown (no-leak; the sorted training index set is recorded on the returned
    decoder as ``_readout_train_idx`` so the no-leak invariant is checkable).

    The honesty guarantees an independent reviewer hunts:
      * speaker FROZEN -- only ``decoder.parameters()`` are optimised;
      * decoder trained on SEEN ONLY -- held-out indices never enter training;
      * deterministic in ``seed`` (decoder init AND the manual_seed before training);
      * same ``epochs`` + ``seed`` for every agent in a generation -> a CONSTANT
        decoder-init/budget effect, so it cannot differentiate agents (symmetry).

    Torch is imported LAZILY (the module imports on a box with no torch).
    """
    import torch
    import torch.nn.functional as F

    torch.manual_seed(int(seed))
    decoder = mc.FactoredListener(int(seed), hidden)
    decoder._build()

    seen = sorted(int(i) for i in seen_idx)
    # speaker FROZEN: its discrete argmax messages on the SEEN indices are the inputs.
    all_msgs = speaker.emit_all()
    syms = torch.tensor([list(all_msgs[i]) for i in seen], dtype=torch.long)  # (S, MSG_LEN)
    soft = F.one_hot(syms, num_classes=mc.VOCAB).float()  # (S, MSG_LEN, VOCAB) one-hot

    # per-attribute supervised targets = the TRUE attribute values of the seen refs.
    ref_table = torch.tensor([list(r) for r in mc.REFERENTS], dtype=torch.long)
    seen_t = torch.tensor(seen, dtype=torch.long)
    attr_targets = [ref_table[seen_t, k] for k in range(mc.N_ATTRS)]

    # optimise ONLY the decoder -- the speaker is NOT in the parameter list (frozen).
    opt = torch.optim.Adam(decoder.parameters(), lr=1e-2)
    for _epoch in range(int(epochs)):
        opt.zero_grad()
        attr_logits = decoder.attr_logits_soft(soft)  # list of (S, card_k)
        loss = sum(
            F.cross_entropy(attr_logits[k], attr_targets[k]) for k in range(mc.N_ATTRS)
        )
        loss.backward()
        opt.step()

    # record the training index set (no-leak audit hook): SEEN only, by construction.
    decoder._readout_train_idx = seen
    return decoder


def readout_fitness(speaker, seen_idx, *, decoder_epochs: int, seed: int,
                    hidden: int = mc._HIDDEN) -> dict:
    """Selection fitness of a FROZEN speaker via a shared experimenter readout decoder.

    Fits a fresh decoder on the SEEN subset (:func:`fit_readout_decoder`, speaker
    frozen), builds the round-trip :class:`Channel` ``speaker_listener_channel(speaker,
    decoder)``, and returns::

        {"full":    <channel_fitness over the FULL referent grid>,
         "heldout": <channel_fitness over the HELD-OUT complement of seen_idx>}

    ``full`` is the headline scalar A2 selection acts on (a seen+held blend);
    ``heldout`` is the pure M2 signal -- the survival-action match fraction over the
    referents NOT in ``seen_idx`` (the indices the decoder NEVER saw), so it measures
    genuine compositional generalization. Same ``decoder_epochs`` and SAME ``seed``
    for every agent in a generation makes any decoder-init/budget effect CONSTANT
    across agents (symmetry): fitness then depends ONLY on the heritable speaker, not
    on a per-agent listener -- the confound removal. Deterministic in ``seed``.
    """
    decoder = fit_readout_decoder(speaker, seen_idx, epochs=decoder_epochs, seed=seed,
                                  hidden=hidden)
    ch = speaker_listener_channel(speaker, decoder)
    seen = set(int(i) for i in seen_idx)
    heldout_idx = [i for i in range(mc.N_REFERENTS) if i not in seen]
    return {
        "full": channel_fitness(ch),
        "heldout": channel_fitness_on(ch, heldout_idx),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Pure turnover-selection primitives (no torch) -- the ONE shared policy the seam
# adapter (:class:`_DeathTransmission`) AND the reproducing-population engine
# (``mortal_generations.run_population_generations``) both consume, so death and
# reproduction obey IDENTICAL rules in the degenerate-seam path and the real engine
# ──────────────────────────────────────────────────────────────────────────────


def weighted_choice(indices: list[int], weights: list[float], rng: random.Random) -> int:
    """Deterministic fitness-weighted draw over ``indices``; uniform if all-zero.

    Extracted to module level (was ``_DeathTransmission._weighted_choice``) so the
    seam adapter and the reproducing-population engine share ONE fitness-weighted
    reproduction policy -- a fitter survivor parents more offspring, identically in
    both. ``weights`` aligns with ``indices``; a non-positive total (e.g. all
    survivors at zero fitness) falls back to a UNIFORM draw so reproduction never
    stalls. Deterministic in the passed ``rng``.
    """
    total = sum(weights)
    if total <= 0:
        return indices[rng.randrange(len(indices))]
    r = rng.random() * total
    acc = 0.0
    for i, w in zip(indices, weights):
        acc += w
        if r <= acc:
            return i
    return indices[-1]


def population_turnover(fits: list[float], n_dead: int, select: str,
                        rng: random.Random) -> tuple[set[int], list[int]]:
    """Decide who DIES (or is RESET) and who PARENTS / TEACHES each chosen slot.

    The pure (no-torch) core of one generation of turnover, consistent with
    :class:`_DeathTransmission`'s policy and usable by the reproducing-population
    engine. Returns ``(chosen_idx, sources)`` where ``chosen_idx`` is the set of
    ``n_dead`` indices that die (A2/A5) or are reset (A3) and ``sources`` is a
    length-``n_dead`` list giving ONE source index per chosen slot:

      * ``select="fitness"`` (A2 -- selection-on-meaning, irreversible DEATH): the
        ``n_dead`` LOWEST-fitness indices die (ties broken by index, deterministic);
        each dead slot's parent is a FITNESS-WEIGHTED draw among the SURVIVORS
        (:func:`weighted_choice`) -- selective mortality AND selective reproduction,
        coupled.
      * ``select="random"`` (A5 -- fitness-blind turnover, irreversible DEATH): a
        RANDOM ``n_dead`` subset dies (INDEPENDENT of decode accuracy) and each dead
        slot's parent is a UNIFORM draw among the SURVIVORS -- the same turnover RATE
        with neither gate.
      * ``select="reset"`` (A3 -- frequency-matched COHERENT-TEACHER population RESET,
        NO death, NO selection): a RANDOM ``n_dead`` subset (``rng.sample`` over ALL
        indices) is RESET IN PLACE, and each reset slot's TEACHER is drawn UNIFORMLY
        over the NON-RESET (STABLE) indices ONLY -- ``range(pop)`` minus ``reset_idx``,
        NOT the full pool. Fitness is NEVER read (the draw is uniform among non-reset
        agents -- FITNESS-BLIND; picking the best/highest-quality teacher would smuggle
        in SELECTION, the confound). This makes A3 a FAIR reset: a reset agent always
        re-imitates a STABLE (not-just-reset) agent, so the transmission bottleneck has
        a COHERENT lineage to ratchet -- the population analog of how A5 draws its
        teacher from SURVIVORS only (NOT a churning straw-man where ~half the teachers
        are themselves just-reset). This models "re-learn from the standing (stable)
        language field": the reset agent's individual PERSISTS (the caller keeps its
        lineage id; only its mind is wiped + re-learned from the teacher's PRE-reset
        speaker -- the caller must capture all speakers BEFORE mutating any slot, the
        build-before-commit ordering A2/A5 use). It stays distinct from A5's "offspring
        of a SURVIVOR": A3 keeps the lineage (no death) and is fitness-blind in BOTH
        who-resets AND who-teaches. EDGE CASE: if EVERY agent is reset (``n_dead ==
        pop`` -- impossible for ``death_frac < 1`` since ``n_dead = round(death_frac*
        pop) < pop``, but guarded) there is no stable teacher, so the draw falls back
        gracefully to the FULL pre-reset pool.

    ``n_dead`` is expected pre-clamped by the caller to ``[0, pop-1]`` (A2/A5 never
    kill everyone -- there must be a survivor to parent; A3's reset count matches that
    same bound by construction so the turnover RATE is freq-matched to A2/A5).
    ``n_dead == 0`` -> ``(set(), [])``. Deterministic in ``rng``: same fitness + same
    rng seed reproduces both outputs.
    """
    if select not in ("fitness", "random", "reset"):
        raise ValueError("select must be 'fitness' (A2), 'random' (A5), or 'reset' (A3)")
    pop = len(fits)
    if n_dead <= 0:
        return set(), []

    if select == "reset":
        # A3: a fitness-BLIND random subset is RESET in place (NOT killed). Each reset
        # agent's TEACHER is drawn UNIFORMLY from the NON-RESET (STABLE) agents ONLY --
        # so a reset agent always re-imitates a not-just-reset (coherent) speaker, the
        # population analog of A5 drawing from SURVIVORS. Fitness is IGNORED (uniform
        # among non-reset; NOT by quality -- that would be selection, the confound).
        reset_idx = set(rng.sample(range(pop), n_dead))
        non_reset = [i for i in range(pop) if i not in reset_idx]
        # EDGE CASE: all agents reset (n_dead == pop; impossible for death_frac < 1 but
        # guarded) -> no stable teacher, fall back to the FULL pre-reset pool.
        teacher_pool = non_reset if non_reset else list(range(pop))
        teachers = [teacher_pool[rng.randrange(len(teacher_pool))] for _ in range(n_dead)]
        return reset_idx, teachers

    if select == "fitness":
        # A2: the lowest-fitness lineages die (ties broken by index).
        order = sorted(range(pop), key=lambda i: (fits[i], i))
        dead_idx = set(order[:n_dead])
    else:
        # A5: a random subset of the SAME size dies -- fitness-blind mortality.
        dead_idx = set(rng.sample(range(pop), n_dead))
    survivors = [i for i in range(pop) if i not in dead_idx]

    parents: list[int] = []
    if select == "fitness":
        # selective reproduction: a fitter survivor parents more offspring.
        weights = [fits[i] for i in survivors]
        for _slot in range(n_dead):
            parents.append(weighted_choice(survivors, weights, rng))
    else:
        # reproduction independent of meaning: uniform among survivors.
        for _slot in range(n_dead):
            parents.append(survivors[rng.randrange(len(survivors))])
    return dead_idx, parents


# ──────────────────────────────────────────────────────────────────────────────
# The A2 / A5 transmission callables (the T4 seam) -- matched turnover; A2 gates
# death+reproduction on fitness, A5 is fitness-blind in both
# ──────────────────────────────────────────────────────────────────────────────


def _coerce_channel(member) -> Channel:
    """Turn a population member into a :class:`Channel` for fitness evaluation.

    Accepts ONLY a ready :class:`Channel` or an explicit ``(speaker, listener)``
    pair: channel fitness is the round-trip ``listener.predict(speaker.emit(r))``,
    meaningful ONLY when the listener is the agent's TRAINED survival-decoding one.
    A BARE :class:`mc.FactoredSpeaker` is REJECTED on purpose (independent-review
    fix #1): pairing it with a fresh untrained listener would make fitness a
    listener-SEED artifact, not survival-relevant communication -- so A2 could
    "select" for decode artifacts. The grown engine population (T7) must supply each
    agent as a ``(speaker, listener)`` pair or a precomputed :class:`Channel`.
    """
    if isinstance(member, Channel):
        return member
    if isinstance(member, tuple) and len(member) == 2:
        return speaker_listener_channel(member[0], member[1])
    if isinstance(member, mc.FactoredSpeaker):
        raise TypeError(
            "a bare FactoredSpeaker has no survival-decoding listener: fitness over "
            "a fresh untrained listener would be a seed artifact, not survival-"
            "relevant communication. Supply a (speaker, listener) pair or a Channel."
        )
    raise TypeError(f"cannot interpret population member as a channel: {type(member)!r}")


def _member_speaker(member):
    """Extract the teachable SPEAKER from a population member (what the engine wants).

    A ``(speaker, listener)`` pair -> the speaker; a :class:`Channel` -> itself (the
    pure-selection tests teach by Channel identity). A bare :class:`mc.FactoredSpeaker`
    is never a valid member here (see :func:`_coerce_channel`), but is returned
    as-is for the degenerate 1-element ENGINE path where ``state.population ==
    [teacher]`` and no fitness evaluation / death occurs (plain iterated learning).
    """
    if isinstance(member, tuple) and len(member) == 2:
        return member[0]
    return member  # a Channel (pure-selection tests) / the lone engine teacher


class _DeathTransmission:
    """A survival-gated ``transmission(state) -> teacher`` callable (A2 or A5).

    Each call (once per generation, by the T4 engine): evaluate the population's
    channel fitness, kill ``round(death_frac * pop)`` agents, then choose the next
    teacher among survivors. ``select`` drives BOTH gates (module docstring has the
    full claim): ``"fitness"`` (A2) = lowest-fitness die + fitness-weighted teacher;
    ``"random"`` (A5) = random subset of the SAME size dies + uniform teacher.

    A5 is made fully fitness-BLIND in BOTH death and birth on purpose: if A5 killed
    the lowest-fitness agents, differential MORTALITY would still be selection-on-
    meaning and the A2 − A5 contrast would be confounded. Population size, the
    per-generation death COUNT, and the bottleneck are MATCHED across the arms; the
    isolated effect is selection-on-meaning (mortality + reproduction, coupled) vs
    fitness-blind turnover -- NOT teacher-choice alone (split ``select`` into
    ``death_select`` / ``teacher_select`` later for the finer factorial cells).

    Recorded for the honesty tests + the freq-matcher: ``last_chosen_fitness``,
    ``deaths_per_gen`` (every processed gen, incl 0s), ``population_size``, and the
    canonical ``death_events`` exposed via :meth:`death_schedule` /
    :meth:`death_intervals` (inter-generation timing) / :meth:`death_counts`
    (per-generation multiplicity) / their histograms -- all derived from the SAME
    structure so the freq-match views agree.
    """

    def __init__(self, *, select: str, population=None, death_frac: float = 0.5,
                 seed: int = 0) -> None:
        if select not in ("fitness", "random"):
            raise ValueError("select must be 'fitness' (A2) or 'random' (A5)")
        self.select = select
        self.death_frac = float(death_frac)
        self.seed = int(seed)
        self._fixed_population = list(population) if population is not None else None
        self._rng = random.Random(self.seed)
        self.last_chosen_fitness: Optional[float] = None
        self.deaths_per_gen: list[int] = []  # death count for EVERY processed gen (incl 0s)
        # canonical death-event structure: one (gen_index, n_deaths) per
        # death-generation. ALL freq-match views derive from THIS (consistent; fix #3).
        self.death_events: list[tuple[int, int]] = []
        self.population_size: int = 0

    # ---- the transmission seam entry point ----
    def __call__(self, state: "mg.TransmissionState"):
        # population source: the fixed one (pure-selection tests) or the engine's
        # state.population (the live reproducing population the engine grows).
        population = (
            self._fixed_population
            if self._fixed_population is not None
            else list(state.population)
        )
        self.population_size = len(population)
        if not population:
            self.last_chosen_fitness = None
            return state.teacher

        # DEGENERATE engine path: T4's run_generations currently supplies a
        # ONE-element population (the lone current teacher, a bare FactoredSpeaker).
        # With a single agent nobody can die (we never kill everyone) and there is
        # no selection to make, so we short-circuit to plain iterated learning
        # WITHOUT coercing the bare speaker into a channel (which is rejected). The
        # real multi-agent death dynamics activate once the engine is grown to pass
        # a multi-member (speaker, listener)/Channel population (T7).
        if len(population) == 1:
            self.deaths_per_gen.append(0)
            self.last_chosen_fitness = None
            return _member_speaker(population[0])

        fits = [channel_fitness(_coerce_channel(m)) for m in population]

        # the per-generation death COUNT is MATCHED across A2/A5 (same turnover):
        # round(death_frac * pop), never killing everyone.
        n_dead = int(round(self.death_frac * len(population)))
        n_dead = max(0, min(n_dead, len(population) - 1))

        if self.select == "fitness":
            # A2: mortality is FITNESS-GATED -- the lowest-fitness agents die
            # (irreversible removal of the failed lineages).
            order = sorted(range(len(population)), key=lambda i: (fits[i], i))
            dead_idx = set(order[:n_dead])
        else:
            # A5: mortality is RANDOM -- a random subset of the SAME SIZE dies, so
            # who dies is INDEPENDENT of decode accuracy (no selection-on-meaning
            # via differential mortality either).
            dead_idx = set(self._rng.sample(range(len(population)), n_dead)) if n_dead else set()
        survivors = [i for i in range(len(population)) if i not in dead_idx]

        # record turnover. The canonical structure is a (gen_index, n_deaths) event
        # PER death-generation (preserving BOTH inter-generation timing AND the
        # per-generation death COUNT, so the three freq-match consumers agree).
        self.deaths_per_gen.append(n_dead)
        if n_dead > 0:
            self.death_events.append((int(state.gen), int(n_dead)))

        # choose the teacher among survivors.
        if self.select == "fitness":
            # A2: fitness-weighted draw among survivors (selection FOR the channel).
            weights = [fits[i] for i in survivors]
            chosen = self._weighted_choice(survivors, weights)
        else:
            # A5: uniform draw among survivors (reproduction independent of meaning).
            chosen = survivors[self._rng.randrange(len(survivors))]

        self.last_chosen_fitness = fits[chosen]
        return _member_speaker(population[chosen])

    def _weighted_choice(self, indices: list[int], weights: list[float]) -> int:
        """Deterministic fitness-weighted draw; falls back to uniform if all-zero.

        Delegates to the module-level :func:`weighted_choice` (Part 2 extraction) so
        the seam adapter and the reproducing-population engine share ONE reproduction
        policy; behaviour (and the draw on a given rng state) is unchanged.
        """
        return weighted_choice(indices, weights, self._rng)

    # ---- death-schedule exposure for the T4 frequency-matcher (fix #3) ----
    # All three views derive from the SAME canonical ``death_events`` (a list of
    # (gen_index, n_deaths) for each death-generation), so the raw stream, the
    # histogram, and the matcher AGREE about same-generation multiple deaths.

    def death_gens(self) -> list[int]:
        """The (sorted, distinct) generation indices that had >= 1 death."""
        return sorted(g for g, _c in self.death_events)

    def death_counts(self) -> list[int]:
        """Per-death-generation death COUNTS (one >= 1 per death-generation).

        The event-count structure A3 must ALSO match -- not just inter-generation
        timing. Aligned by death-generation order with :meth:`death_intervals`.
        """
        return [c for _g, c in sorted(self.death_events)]

    def death_intervals(self) -> list[int]:
        """Positive gaps between consecutive death GENERATIONS (inter-generation timing).

        Inter-event gaps over the DISTINCT death generations (NOT per-death ticks),
        so within-generation multiplicity lives in :meth:`death_counts`, never as a
        dropped zero-gap. Consumed by ``mg.matched_reset_schedule`` /
        ``mg.matched_count_schedule`` as the TARGET interval distribution.
        """
        gens = self.death_gens()
        return [gens[i] - gens[i - 1] for i in range(1, len(gens))]

    def death_interval_histogram(self) -> dict[int, float]:
        """Normalised histogram of the inter-generation death intervals (sums to 1.0).

        Consistent with :meth:`death_intervals` (over DISTINCT death generations;
        no zero-gaps). ``{}`` when < 2 death generations.
        """
        return mg.interval_histogram(self.death_intervals(), intervals=True)

    def death_count_histogram(self) -> dict[int, float]:
        """Normalised histogram of the per-generation death COUNTS (sums to 1.0)."""
        return mg.count_histogram(self.death_counts())

    def death_schedule(self) -> list[tuple[int, int]]:
        """The full canonical death schedule: ``[(gen_index, n_deaths), ...]``.

        The single source of truth for both the inter-generation timing
        (:meth:`death_intervals`) and the per-generation multiplicity
        (:meth:`death_counts`); the form ``mg.freq_match_counts_valid`` consumes to
        check A3 matches A2 on BOTH (a no-death / single-event history is flagged
        INVALID, not trivially matchable).
        """
        return sorted(self.death_events)


def a2_death_transmission(*, population=None, death_frac: float = 0.5, seed: int = 0
                          ) -> _DeathTransmission:
    """A2 DEATH arm transmission: survivors teach, FITNESS-WEIGHTED (selection FOR).

    A ``transmission(state) -> teacher`` callable for the T4 seam. Each generation
    the lowest-fitness ``round(death_frac * pop)`` agents die; the next teacher is
    drawn fitness-weighted among the survivors -- a better-decoding lineage teaches
    more. Pass ``population`` to drive a fixed population (selection/turnover/
    freq-match tests); omit it to read the engine's live ``state.population``.
    """
    return _DeathTransmission(select="fitness", population=population,
                              death_frac=death_frac, seed=seed)


def a5_selection_ablated_transmission(*, population=None, death_frac: float = 0.5,
                                      seed: int = 0) -> _DeathTransmission:
    """A5 selection-ablated transmission: SAME turnover, NEITHER death nor birth gated.

    Identical to A2 in population size, death COUNT per generation, and bottleneck.
    The ONLY difference: in A5 a RANDOM subset of the same size dies (mortality is
    fitness-blind) and the teacher is drawn UNIFORMLY among survivors -- so
    reproduction success is INDEPENDENT of decode accuracy. (Making A5 also kill
    randomly, not just teach randomly, is deliberate: if A5 killed the lowest-
    fitness agents, differential MORTALITY would still be selection-on-meaning and
    the A2 − A5 contrast would be confounded.) Isolates pure turnover from
    selection-on-meaning -- the A2 − A5 contrast.
    """
    return _DeathTransmission(select="random", population=population,
                              death_frac=death_frac, seed=seed)
