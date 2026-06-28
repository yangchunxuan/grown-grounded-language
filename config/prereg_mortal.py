"""Frozen "Mortal Bottleneck" preregistration: death-vs-reset as a compositionality engine.

Pre-registered pass/FAIL thresholds for the Mortal-Bottleneck experiment, frozen
BEFORE any real multi-generation run. Moving any of these after seeing results =
moving the goalposts = forbidden (工单 危险清单 #7). This mirrors the proven
``config/prereg_comm.py`` / ``config/prereg_dcog.py`` instruments (same
``_int_env`` / ``_float_env`` env-overridable-but-frozen pattern, the same
verbatim-prose ``*_DECISION`` dict, the same ``*_FROZEN`` echo).

The strong (ambitious) claim — genuinely post-2020, falsifiable:
  In a survival-grounded emergent channel, IRREVERSIBLE DEATH used as the
  selection operator on a transmission bottleneck (offspring learn from the
  *surviving* parent, fitness-weighted transmission) compositionalizes a channel
  that plain co-training leaves holistic — AND this is DISTINCT from a
  frequency-matched artificial parameter-reset (the death-vs-reset paired CI
  excludes 0 AND the gap >= MORTAL_DEATH_VS_RESET_DELTA_MIN). A2 (death) − A3
  (matched reset) is THE decisive paired contrast.

The honest, MOST-LIKELY-REAL outcome (we must be willing to ship it):
  the frequency-matched reset (A3) captures most of the gain -> RESET_SUFFICES_TOO
  -> a clean, publishable NEGATIVE that answers a stated-open question (Galke
  2403.14427 calls reset and mortality "functionally equivalent" without
  controlling — "death is iterated learning in a costume"). Both verdicts are a
  contribution; only one is the headline; selling "death is special" when the
  paired CI includes 0 would be the overclaim.

Validated substrate (frozen by the 2-round power-check, probes 2311f0e/def9401):
  referents = a combinatorial attribute product with N_REFERENTS > VOCAB (kills
  the single-symbol "diagonal" collapse the old 8-referent channel suffered);
  the speaker MUST use a FACTORED input (per-attribute embeddings summed) — the
  committed monolithic speaker provably stays flat under the same bottleneck.
  PRIMARY metric = PosDis (validated 0.15->0.51 under bottleneck vs flat 0.14).

All scalars below are env-overridable via ``_int_env`` / ``_float_env`` for
reproducible sweeps, but their prereg-FROZEN defaults are the registered values
and are echoed verbatim in ``MORTAL_FROZEN``. The real multi-generation runs are
PENDING-USER.
"""

from __future__ import annotations

import math
import os


def _int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return int(default)
    return int(value)


def _float_env(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or value == "":
        return float(default)
    return float(value)


MORTAL_VERSION: str = os.environ.get("MORTAL_VERSION", "Mortal-Bottleneck-death-vs-reset-v1")
MORTAL_FREEZE_DATE: str = os.environ.get("MORTAL_FREEZE_DATE", "2026-06-18")

# ── Validated substrate geometry (frozen by the power-check) ──
# A combinatorial attribute product. Frozen default: type(3) × bearing(4) ×
# distance(3) = 36 referents. VOCAB < N_REFERENTS forces multi-symbol codes
# (kills the diagonal collapse a single-symbol bijection would allow); VOCAB
# >= max attribute cardinality (4) so each attribute is individually expressible.
# A 64-referent (4×4×4, VOCAB=8) variant is the documented headroom option.
MORTAL_ATTRIBUTES: tuple[tuple[str, int], ...] = (
    tuple((p.split(":")[0].strip(), int(p.split(":")[1])) for p in os.environ["MORTAL_ATTRIBUTES"].split(","))
    if os.environ.get("MORTAL_ATTRIBUTES") else (("type", 3), ("bearing", 4), ("distance", 3)))
"""Per-attribute (name, cardinality). The cross of these is the referent grid;
the away/toward/near distance + bearing are the experimenter-side scoring key
for the factored M2 decode (never shown to a decoder)."""

# = 3 * 4 * 3 = 36, computed from MORTAL_ATTRIBUTES (product of cardinalities)
MORTAL_N_REFERENTS: int = math.prod(card for _name, card in MORTAL_ATTRIBUTES)

MORTAL_MSG_LEN: int = _int_env("MORTAL_MSG_LEN", 3)
"""Symbols per message. VOCAB ** MSG_LEN = 216 expressible messages, ample slack
over the 36 referents for a non-trivial compositional code to emerge."""

MORTAL_VOCAB: int = _int_env("MORTAL_VOCAB", 6)
"""Discrete alphabet size. Frozen 6: VOCAB < N_REFERENTS (36) forces multi-symbol
codes (the anti-diagonal invariant); VOCAB >= max attribute cardinality (4) so
every attribute value is expressible."""

MORTAL_FACTORED_INPUT: bool = (os.environ.get("MORTAL_FACTORED_INPUT", "1") not in ("0", "", "false", "False"))
"""Speaker MUST consume a FACTORED input (per-attribute embeddings summed), NOT a
monolithic per-referent embedding — proven necessary by the power-check: the
monolithic speaker stays flat under the same bottleneck. Output head stays
free-form."""

# ── Bottleneck / training schedule (frozen) ──
MORTAL_BOTTLENECK_HOLD_FRAC: float = _float_env("MORTAL_BOTTLENECK_HOLD_FRAC", 0.5)
"""Fraction of whole attribute-combinations held out per generation (forces
compositional generalization across the transmission bottleneck)."""

MORTAL_IMITATION_EPOCHS: int = _int_env("MORTAL_IMITATION_EPOCHS", 150)
"""Imitation (learn-from-parent) epochs per generation."""

MORTAL_INTERACTION_EPOCHS: int = _int_env("MORTAL_INTERACTION_EPOCHS", 60)
"""Interaction (Lewis-game) epochs per generation."""

MORTAL_N_GENERATIONS: int = _int_env("MORTAL_N_GENERATIONS", 20)
"""Generations per run (start-vs-end comp rise measured across these)."""

MORTAL_N_SEEDS: int = _int_env("MORTAL_N_SEEDS", 6)
"""Distinct world seeds, paired across arms. Exactly ONE delta per seed (no
pseudo-replication); any dropped seed -> UNDERPOWERED (no back-fill)."""

# ── Reproducing-population / turnover knobs (matched CONFOUND-CONTROL, frozen) ──
# These size the REAL multi-agent reproducing population (the engine's
# ``run_population_generations``): pop size + per-generation death fraction. They
# are matched-turnover CONFOUND-CONTROL knobs (A3 reset and A5 selection-ablated
# must match A2 death on BOTH population size AND death count), NOT verdict
# thresholds -- freezing them completes the prereg substrate, it does not move any
# goalpost. With irreversible death implemented on a population of these sizes, the
# A2/A5 arms genuinely exercise differential mortality (the degenerate 1-element
# engine path was plain iterated learning -- nobody could die).
MORTAL_POP_SIZE: int = _int_env("MORTAL_POP_SIZE", 12)
"""Fixed live-population size, matched across A2/A3/A5 so turnover RATE, population,
and the bottleneck are identical and the only difference is fitness-gating."""

MORTAL_DEATH_FRAC: float = _float_env("MORTAL_DEATH_FRAC", 0.5)
"""Fraction of the population dying each generation, matched across the arms
(consistent with the ``_DeathTransmission`` default death_frac=0.5):
round(0.5 * 12) = 6 deaths/gen, clamped to never kill everyone."""

MORTAL_READOUT_EPOCHS: int = _int_env("MORTAL_READOUT_EPOCHS", 300)
"""Training steps for the SHARED experimenter-side readout decoder that scores
SELECTION fitness (``mortal_death.readout_fitness``). The readout decoder is a
fresh FactoredListener trained each generation on the SEEN subset ONLY (speaker
FROZEN; pure decode, NOT a Lewis game), applied identically to EVERY agent's
speaker -- so selection fitness measures ONLY the heritable speaker's held-out
decodability (the M2 endpoint), removing the per-agent-listener confound
(init-seed luck + a newborn-vs-survivor listener training-budget asymmetry). It
fits an EASY 18-pair seen mapping (hold_frac=0.5). Validated (offscreen sweep,
decoder seeds 1/7/13/21/42): at 300 the decoder fits SEEN cleanly at 1.000 for
BOTH a perfectly-compositional and a holistic-injective reference speaker, with
held-out 0.889-1.000 (compositional) vs 0.000 (holistic) -- a clean >> spread.
300 cleanly fits seen and is ample; raising it only sharpens the perfect-
compositional held-out toward 1.000 at proportionally more compute (not a
constraint), with no change to the compositional-vs-holistic separation."""

# ── The five arms (death-vs-reset is the decisive cut) ──
MORTAL_ARMS: tuple[str, ...] = ("A1_baseline", "A2_death", "A3_reset", "A4_intero", "A5_selection_ablated")
"""A1_baseline: co-trained channel, no bottleneck — the null (does ANY bottleneck compositionalize?).
A2_death: death-bottleneck native ecology — irreversible death + offspring-learn-from-SURVIVING-parent (fitness-weighted transmission); isolates mortality + selection.
A3_reset: frequency-matched fitness-blind COHERENT-TEACHER POPULATION reset — same substrate as A2 (a population of pop_size agents), reset matched to A2's death-count/turnover + data-budget + pop size, timing decoupled from survival; a random subset is reset IN PLACE each generation (lineage ids PRESERVED, no death) and each reset agent re-imitates a teacher drawn UNIFORMLY from the NON-RESET (stable) agents — a coherent teacher, the population analog of the single-lineage Ren/Zheng artificial-reset mechanism (NOT a survival arm). Isolates the bare learning-schedule / bottleneck WITHOUT selection or death.
A4_intero: A2 with ± interoceptive least-effort — per-symbol message cost gated by i_t=[hunger,thirst,pain] vs flat cost; tests body-grounded ordering.
A5_selection_ablated: death present but reproduction success made INDEPENDENT of decode accuracy — turnover WITHOUT selection-on-meaning."""

# ── Verdict thresholds (frozen UP FRONT, never calibrated from the same run) ──
MORTAL_COMP_RISE_MIN: float = _float_env("MORTAL_COMP_RISE_MIN", 0.15)
"""Minimum start-vs-end PosDis rise for a channel to count as compositionalizing.
The power-check saw 0.15 -> 0.51 under bottleneck vs a flat 0.14 control."""

MORTAL_HELDOUT_ABOVE_CHANCE_MIN: float = _float_env("MORTAL_HELDOUT_ABOVE_CHANCE_MIN", 0.2)
"""M2: held-out FACTORED decode (type AND bearing AND distance recovered
INDEPENDENTLY) must beat its chance floor by at least this margin. Factored is
mandatory — a holistic lookup hits high JOINT accuracy with zero systematicity."""

MORTAL_DEATH_VS_RESET_DELTA_MIN: float = _float_env("MORTAL_DEATH_VS_RESET_DELTA_MIN", 0.1)
"""M3 (the headline): minimum A2-minus-A3 paired PosDis gap for the strong claim.
PASS to MORTAL_COMPOSITIONALIZES requires BOTH the paired bootstrap 95% CI to
exclude 0 AND Δ >= this floor; below it, the death-vs-reset claim is not made."""

MORTAL_FREQ_MATCH_KS_MAX: float = _float_env("MORTAL_FREQ_MATCH_KS_MAX", 0.15)
"""Max KS distance between A2's death-interval histogram and A3's reset-interval
histogram. Above this the frequency match is broken (A3 is not a fair matched
control) -> FREQ_MATCH_INVALID (the analog of the comm NEG_CONTROL_INVALID)."""

MORTAL_ROSETTA_DROP_MIN: float = _float_env("MORTAL_ROSETTA_DROP_MIN", 0.2)
"""Minimum GROWN-minus-MUTED channel-fitness margin for the channel to count as
Removability-Rosetta LOAD-BEARING each generation -- the analog of the comm
``COMM_SURVIVAL_DROP_MIN``. The MORTAL_COMPOSITIONALIZES decision rule requires (as
an AND conjunct) that MUTING the grown channel drops survival, i.e. the grown
channel does REAL survival work and is not epiphenomenal. Operationally the engine
records, per generation, the population's channel fitness measured through a MUTED /
garbled channel (``mortal_death.garbled_channel`` -> ~chance, 1/N_REFERENTS) and the
GROWN per-gen fitness it already records; the gate is load-bearing iff
(grown - muted) >= this margin, sustained EACH generation.

HONESTY CAVEAT (surfaced, never hidden): in THIS fused-survival substrate survival
IS channel decode (``mortal_death.survival_action`` is injective on the decoded
referent), so this Rosetta gate CLOSELY TRACKS M2 (held-out above chance) -- it is
NOT a fully independent check here. It is wired anyway because the prereg literally
requires it as an AND conjunct (we do NOT silently skip a required gate); the
verdict payload echoes a ``rosetta_note`` documenting the M2-tracking redundancy so
a reviewer is not misled into treating it as independent evidence."""

MORTAL_PRIMARY_METRIC: str = os.environ.get("MORTAL_PRIMARY_METRIC", "posdis")
"""PRIMARY compositionality metric = PosDis (positional disentanglement; robust +
well-defined). topsim is SECONDARY (brittle: returns None on zero
message-distance variance — guard + report the undefined-rate)."""

MORTAL_COMP_METRICS: tuple[str, ...] = ("posdis", "bosdis", "topsim")
"""M1 metric set. The comp-rise gate requires >= 2 of these 3 to rise start-vs-end
with non-overlapping bootstrap CIs (defeats the Conklin & Smith 2022 topsim
metric artifact)."""

MORTAL_DECISION: dict[str, str] = {
    "MORTAL_COMPOSITIONALIZES": (
        "the ambitious headline: M1 >= 2/3 of (posdis, bosdis, topsim) rise start-vs-end with "
        "non-overlapping bootstrap CIs AND M2 held-out factored generalization rises above its "
        "chance floor by >= MORTAL_HELDOUT_ABOVE_CHANCE_MIN AND M3 death-vs-reset paired CI > 0 "
        "AND Δ >= MORTAL_DEATH_VS_RESET_DELTA_MIN AND the frequency match is valid "
        "(KS <= MORTAL_FREQ_MATCH_KS_MAX) AND the channel stays Rosetta-load-bearing "
        "(mute->survival drop) each generation: death-as-the-bottleneck adds a bounded "
        "compositionality delta OVER the matched reset"
    ),
    "RESET_SUFFICES_TOO": (
        "the honest negative (most likely): A2 (death) AND A3 (matched reset) BOTH "
        "compositionalize, but the M3 death-vs-reset paired CI INCLUDES 0 — death is not "
        "distinguishable from a frequency-matched learning-schedule reset (iterated learning in "
        "a costume). A clean, publishable answer to the stated-open question; we ship it"
    ),
    "LOAD_BEARING_NOT_SUSTAINED": (
        "death-selection DID compositionalize the channel and beat the frequency-matched reset "
        "(M1 >= 2/3 rise for A2 AND M2 held-out generalization above floor AND M3 death-vs-reset "
        "paired CI > 0 & Δ >= MORTAL_DEATH_VS_RESET_DELTA_MIN & sign-consistent & freq-match "
        "valid) — the underlying compositionality + death-vs-reset RESULT holds — BUT the channel "
        "is NOT Rosetta-load-bearing in EVERY generation (the grown-minus-muted margin falls below "
        "MORTAL_ROSETTA_DROP_MIN in an early/developing generation before the channel matures, "
        "though it is strongly load-bearing once mature). The prereg requires load-bearing EACH "
        "generation for the headline, so the strict MORTAL_COMPOSITIONALIZES is WITHHELD (not "
        "relaxed); the result is reported with this honest qualifier. This is NOT BOTTLENECK_NULL "
        "(which means nothing compositionalized) — A2 demonstrably did."
    ),
    "BOTTLENECK_NULL": (
        "neither A2 nor A3 beats the A1 no-bottleneck baseline: no bottleneck of either kind "
        "compositionalizes this channel (the null result on the prior question)"
    ),
    "FREQ_MATCH_INVALID": (
        "the A2 death-interval histogram and the A3 reset-interval histogram differ by KS > "
        "MORTAL_FREQ_MATCH_KS_MAX: A3 is not a fair frequency-matched control, so the decisive "
        "death-vs-reset contrast is uninterpretable -> rejected before any death-vs-reset claim "
        "(the analog of the comm NEG_CONTROL_INVALID)"
    ),
    "UNDERPOWERED": (
        "fewer than MORTAL_N_SEEDS distinct paired seeds, or any seed dropped / duplicated (no "
        "back-fill, no pseudo-replication): the paired death-vs-reset CI is not trustworthy"
    ),
    "HARD_REJECT": (
        "honesty gate failed: non-green substrate, loaded-from-pretrained / scripted-replay, the "
        "factored-input flag off, a garbled/un-parseable channel, or a redline-contaminated "
        "config -> rejected before any verdict is computed"
    ),
}

MORTAL_STATUS: str = os.environ.get("MORTAL_STATUS", "PENDING-USER (real multi-generation runs)")

MORTAL_FROZEN: dict[str, object] = {
    "MORTAL_VERSION": MORTAL_VERSION,
    "MORTAL_FREEZE_DATE": MORTAL_FREEZE_DATE,
    "MORTAL_STATUS": MORTAL_STATUS,
    "MORTAL_ATTRIBUTES": MORTAL_ATTRIBUTES,
    "MORTAL_N_REFERENTS": MORTAL_N_REFERENTS,
    "MORTAL_MSG_LEN": MORTAL_MSG_LEN,
    "MORTAL_VOCAB": MORTAL_VOCAB,
    "MORTAL_FACTORED_INPUT": MORTAL_FACTORED_INPUT,
    "MORTAL_BOTTLENECK_HOLD_FRAC": MORTAL_BOTTLENECK_HOLD_FRAC,
    "MORTAL_IMITATION_EPOCHS": MORTAL_IMITATION_EPOCHS,
    "MORTAL_INTERACTION_EPOCHS": MORTAL_INTERACTION_EPOCHS,
    "MORTAL_N_GENERATIONS": MORTAL_N_GENERATIONS,
    "MORTAL_N_SEEDS": MORTAL_N_SEEDS,
    "MORTAL_POP_SIZE": MORTAL_POP_SIZE,
    "MORTAL_DEATH_FRAC": MORTAL_DEATH_FRAC,
    "MORTAL_READOUT_EPOCHS": MORTAL_READOUT_EPOCHS,
    "MORTAL_ARMS": MORTAL_ARMS,
    "MORTAL_COMP_RISE_MIN": MORTAL_COMP_RISE_MIN,
    "MORTAL_HELDOUT_ABOVE_CHANCE_MIN": MORTAL_HELDOUT_ABOVE_CHANCE_MIN,
    "MORTAL_DEATH_VS_RESET_DELTA_MIN": MORTAL_DEATH_VS_RESET_DELTA_MIN,
    "MORTAL_FREQ_MATCH_KS_MAX": MORTAL_FREQ_MATCH_KS_MAX,
    "MORTAL_ROSETTA_DROP_MIN": MORTAL_ROSETTA_DROP_MIN,
    "MORTAL_PRIMARY_METRIC": MORTAL_PRIMARY_METRIC,
    "MORTAL_COMP_METRICS": MORTAL_COMP_METRICS,
    "MORTAL_DECISION": MORTAL_DECISION,
}
