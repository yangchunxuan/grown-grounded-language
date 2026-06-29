# STAGE: WHY IS g1f KIN-ONLY? — DIAGNOSTIC pre-registration **v3**

**v3 changelog.** v2 got a SECOND independent code-grounded red-team (Codex), converging with the first (Gemini). Both DO_NOT_LOCK. v3 fixes: (1) the "free retrospective" was **code-refuted** (committed artifacts contain only trajectory summaries — no per-agent lineage / MII matrix) → REMOVED; a new instrumented run is required. (2) Add a 5th cause **(e) COMMON-ATTRACTOR** (both reviewers) and make the **comm-blind cross-founder MII the PRIMARY null** that separates real cross-lineage communication-selection from shared-world convergence. (3) gate-0 made non-tautological via a **random-token** baseline. (4) thresholds become **calibration outputs relative to the measured null**, not pre-frozen magnitudes. (5) reword the arm-lock; add per-agent-alive logging. Type unchanged: **DIAGNOSTIC, no mechanism change.**

**Candidate causes (FIVE):**
- **(a) DEMOGRAPHIC** — collapse to ~1 founder; cross-lineage selection-alignment exists while lineages coexist but is truncated by collapse. → intervention ~ C1.
- **(b) SELECTION-RULE** — codes partially compatible but cross-lineage decoding never selected. → C2.
- **(c) REPRESENTATIONAL-INCOMPATIBLE** — arbitrary private codes, no shared anchor. → needs shared grounding.
- **(d) FITNESS-IRRELEVANCE** — the world doesn't require (cross-lineage) message content at all; (a)–(c) moot. (gate-0)
- **(e) COMMON-ATTRACTOR / SHARED-GROUNDING CONVERGENCE** 🔴v3 — lineages converge to similar codes because the SAME world/metabolic structure favors them, NOT communication selection. The decisive discriminator vs (a) is the **comm-blind cross-founder null**.

## 0. SCOPE LOCK + instrumentation-only (code-verify before run)
- **Arm = `shared_weights_kin`** — the only arm with **inherited founder-lineage reproduction** (`:247` `preserve_lineage=True`; other arms reset `child.lineage=seed` at `:96`; copied survivors keep parent lineage via deepcopy `:240`; frozen arms trivially preserve). 🔴v3 reworded: "inherited-lineage reproduction", not "only arm where lineage propagates".
- **New logging (no dynamics/RNG-order change), per gen:** the full MII **matrix** + the **per-agent `.lineage` vector** + **per-agent ALIVE state** (Codex: `_run_episode` returns only aggregate alive `:148`/`:155` — must add per-agent alive to support the coexistence criterion + M3).
- cross-founder MII filter keys on `.lineage` (blind-test: all-`lineage=0` pop → NaN/skip).
- **lineage-shuffle uses a SEPARATE local RNG** seeded off a snapshot (must NOT consume the evolution RNG, else instrument-only is false). 🔴v3
- reward-chain present (`_decoded_score`→`pick`→`eat`, `:153/:191/:197`); load-bearing tested in gate-0.
- record full config (env/seeds/formal/arm) in the JSON.

## 1. Measurements (all on shared_weights_kin)
- **M1 — cross-founder MII trajectory** over coexisting gens (+ within-founder MII + inverse-Simpson N_eff).
- **M2 — cross-decode `CD` trajectory** over coexisting gens (lineage-A listener on lineage-B speaker, both directions).
- **M3 — gate-0 load-bearing (non-tautological)** 🔴v3: open-mode vs **mute** vs **random-token** survival (random-token = i.i.d. message each frame; it IS "followed" but carries no content, so it breaks the open-mode "argmax follows decoded score" tautology Codex flagged).

## 2. Baselines (same arm/env/seeds/formal; the linchpin is the comm-blind cross-founder null)
- **comm-blind cross-founder MII / CD** 🔴v3 (PRIMARY null) — random-fitness reproduction, same arm, multi-lineage, instrumented identically. This is cross-lineage decodability from {shared world + architecture + descent} WITHOUT communication selection. Survival must BEAT this to claim real cross-lineage selection.
- **frozen-mixed** = frozen-random agents from deterministically disjoint init seeds within each diagnostic seed (genuinely unrelated) — floor for CD's "no evolution at all".
- **lineage-shuffle** — relabel `.lineage` (separate RNG) before computing M1 — catches non-lineage structure.

## 3. FROZEN RULES (magnitudes are CALIBRATION OUTPUTS of the run's own nulls, per Codex #6)
- arm=shared_weights_kin; mode=formal; n=16 seeds.
- coexistence: a gen counts iff **≥2 founders each have ≥3 LIVING agents** (uses the new per-agent alive log).
- **SESOI is data-calibrated, not pre-frozen**: a margin counts only if its bootstrap 95% CI excludes 0 **AND** the point estimate ≥ **one seed-to-seed SD of the corresponding comm-blind null**. (Report the SD; this replaces the un-grounded 0.04/0.02.)
- peak = max cross-founder MII over a seed's coexisting gens, then mean across seeds.
- INCONCLUSIVE_NO_WINDOW iff **< 8 of 16 seeds have ≥2 coexisting gens**.

## 4. PRE-REGISTERED decision rule
**Gate-0 (cause d):** if open-survival ≤ mute-survival OR open-survival ≈ random-token-survival (CI overlaps) → **FITNESS_IRRELEVANCE_WARNING** (content not load-bearing); stop, do not label (a)–(c)/(e).

Else, using {comm-blind-CF, frozen-mixed, lineage-shuffle} nulls:
- **(a) DEMOGRAPHIC** iff cross-founder MII(survival) **beats comm-blind-CF** (CI-clean margin ≥ data-SESOI) AND it **declines with collapse** (final-coexist < 0.5×peak). → real cross-lineage selection-alignment exists at coexistence, truncated by collapse → **C1**.
- **(e) COMMON-ATTRACTOR** iff cross-founder MII(survival) is elevated above frozen-mixed/shuffle BUT **does NOT beat comm-blind-CF** (CI overlaps). → alignment is shared-world convergence, not communication selection → neither C1 nor C2-about-communication helps; the "alignment" isn't language. 🔴v3
- **(b) SELECTION-RULE** iff cross-founder MII ≈ frozen-mixed (no alignment) BUT **CD beats comm-blind-CF CD** (codes latently cross-decodable, never selected). → **C2**.
- **(c) INCOMPATIBLE** iff cross-founder MII ≈ frozen-mixed AND CD does NOT beat comm-blind-CF CD. → needs shared grounding.
- **INCONCLUSIVE_NO_WINDOW** → C1 as a window-opening enabler, re-diagnose, still no C2.
- Per-seed aggregation: report the distribution; default for a split = the more conservative cause (c ≻ e ≻ b ≻ a) unless ≥12/16 agree.

## 5. Outcomes → intervention implication
(a)→C1-only; (b)→C2-only; (c)→shared-grounding (re-scope); (d)→world doesn't require content (question ill-posed here); **(e)→the kin-only "language" is partly shared-world convergence, not communication — a deflationary finding that reframes g1f's positive itself**; INCONCLUSIVE→C1-enabler then re-diagnose.

## 6. Steps — NO free retrospective (it was code-refuted) 🔴v3
1. Pass §0: instrument shared_weights_kin (matrix + lineage vector + per-agent alive; `.lineage`-keyed cross-founder MII + CD; separate-RNG lineage-shuffle; random-token mode for gate-0); blind-tests; config recorded.
2. Run formal n=16 on shared_weights_kin + the three baselines (comm-blind-CF, frozen-mixed, lineage-shuffle) at the SAME config; calibrate SESOI from the comm-blind null's seed-SD.
3. Report per-seed coexistence-window counts (sanity) → gate-0 → §4 classification + trajectories + per-seed distribution + written read. **Pre-register the gate before looking at the survival arm's cross-founder numbers** (calibration uses the nulls only).
4. Only THEN pick/trim the intervention to the diagnosed cause.

## 7. Implementation-verify (converged "cannot tell from files")
- artifacts lack lineage/matrix/per-agent state (Codex-confirmed) → MUST instrument; no retrospective.
- `.lineage`-keyed cross-founder filter (blind-test all-same-lineage → NaN/skip).
- lineage-shuffle on a separate RNG (no evolution-RNG consumption).
- per-agent ALIVE log added (aggregate-only today, `_run_episode`).
- after collapse, singleton lineage / self-listening (`_speaker_for :160`) gen → excluded from coexistence (NaN).
- MII is offline (`:219`, uses `speaker.emit` not `_speaker_for`) → confirm `_speaker_for` alternation doesn't contaminate it; record independence.
- comm-blind-CF baseline = random-fitness, SAME arm/config; frozen-mixed = deterministically disjoint init seeds within each diagnostic seed.
- whether enough coexisting windows exist at n=16, and whether CD beats the comm-blind-CF null — only knowable after the run.
