# G1F ARC — does a decodable channel co-evolve from survival selection, and is it shared?

**Status: complete scoped arc (g1f → C2X3), 2026-06-30** (not "closed/theorem" — that label is banned;
scoped within-world findings). The full g1f line in one place: a survival-selected channel CO-EVOLVES from
random weights (kin scope, n=48) but is a **private kin dialect**; maintaining diversity is
necessary-but-insufficient (C1: A refuted, C supported, n=8); and direct cross-lineage selection across a
swept pressure range (C2X/C2X2/C2X3) does NOT bootstrap a public code — there is a **pressure-vs-survival
tension** (forced non-kin listening kills foraging because non-kin codes are mutually undecodable). So in
g1f, grounded language is kin-scoped and a public cross-lineage code does not bootstrap; obtaining one
plausibly needs a **richer world** (the next paper). This document is the truth-calibrated narrative/spine
for the paper; numbers are anchored to the verdict JSONs (Provenance table). CLAIM_LEDGER.md is the
per-claim ledger; RUNBOOK.md regenerates any stage; README/older drafts (incl. the frozen LBA) are OLD-FRAMED.

---

## The question
Can a decodable, grounded communication channel **grow from scratch** (random init, no borrowed
weights, no oracle/truth labels) under **survival selection alone** in the G1D lethal-vent world? And
if it does — is it a **shared/public** language across the population, or only **private** to kin?

Architecture (constant across the arc): each agent = a tiny `UnifiedIO` tied code-table
(K×BANDS×VOCAB = 4×5×6), N(0,1) init; speaker `emit` = argmax over symbols, listener `predict` =
argmax over bands. No gradient on the survival task (evolution = mutation + selection); the only
gradient anywhere is optional Kirby cultural imitation (not used in the load-bearing arms). The world
is a hand-coded fixed-rule simulator (not learned). MII (mutual intelligibility) = probe a sampled set
of referents through emit→decode and score exact-tuple recovery; chance = 1/N_REFERENTS = 1/625 ≈
0.0016.

---

## Step 1 — g1f: co-evolution is real within-kin (n=48 formal), but kin-only (a corrected false-negative)
**Claim (scoped POSITIVE):** under FORMAL settings, survival selection co-evolves a decodable channel
that beats an architecture-matched comm-blind control: the survival-fitness arm reaches MII 0.172 vs the RNG-fixed random-fitness control's 0.1174, **paired margin
+0.0548, 95% CI [0.0234, 0.0849]** at n=48 (`rtc_g1f_commblind_verdict_formal48_rngfix.json`; old formal48/reconciled are pre-rngfix legacy). MII is semantic (referent→emit→decode→exact-tuple), not weight
similarity; the matched control is the RNG-fixed random-fitness control (isolating communication-selection from clonal descent — the unsupported +0.057 separate-RNG figure is retracted); no-oracle test passes; no
borrowed weights.

**Scope (load-bearing):** the population **collapses to ~1 founder lineage** (formal n=48, measured: dominant-lineage share 99.1%, N_eff 1.02, 47/48 seeds single-lineage), so the co-evolved channel is **kin-lineage decodability, NOT a public cross-lineage
shared language**.

**Methodology note (the rig is bidirectional):** the earlier "g1f clean negative" was a FALSE
NEGATIVE the author introduced — a FORMAL coevolve compared against a PILOT comm-blind (config
mismatch). The attack-machine + the user's question ("did we kill a real effect for the paper's
sake?") caught it. Load-bearing knob = GENERATIONS (7→28; effect plateaus ~gen 12–14; the pilot
truncated mid-rise).

## Step 2 — kin-only DIAGNOSTIC: why kin-only? (window-limited, directional C)
**Question:** at generations where ≥2 founder lineages coexist, are non-kin lineages mutually
intelligible (cross-founder MII near the within-founder ceiling → **A: collapse-limited**, fixable by
maintaining diversity) or diverged into private codes (cross-founder MII at the architecture floor →
**C: private codes**, needs shared grounding)?

Design discipline: dropped a wrong comm-blind null (it strips world-survival selection too; the
"communication-selection vs world-convergence" question is ill-posed in g1f's kin-only regime, so the
diagnostic narrows to the well-posed within-vs-cross-founder + frozen-mixed-floor comparison). 4
code-grounded review rounds (spec v4.1 LOCKED, commit 67ce59b).

**Verdict (formal n=16): `INCONCLUSIVE_NO_WINDOW`** — only 5/16 seeds hit the frozen ≥2-coexisting-gens
gate (founder collapse too fast). The frozen gate held; not relabeled.
**Direction (strong, unanimous): C.** within-founder MII 0.159 (≈100× chance) vs cross-founder MII
0.00086 (≈ chance ≈ frozen-mixed floor), CF/WF = 0.5%; 5/5 measurable (windowed) seeds same form
(`rtc_g1f_kinonly_diagnostic_verdict.json`).
**Sentinels pass:** lineage-shuffle (CF 0.0009 → 0.065 on label-shuffle = the metric truly keys on
lineage); gate-0 (open 0.31 vs mute 0.03 / scramble 0.05; open−mute CI [0.20, 0.37], open−scramble CI
[0.17, 0.34] = content is load-bearing, so floor-level CF is NOT "messages don't matter").

## Step 3 — C1 collapse probe: A REFUTED, C SUPPORTED
**Design:** weld the "why collapse" diagnosis INTO a minimal C1 (maintain-diversity) intervention. 2×2
factorial {selection: hard top-50% truncation, soft: tournament-k2 + lineage fitness-sharing (divisor
= GEN-START same-lineage count)} × {pop 16, 96}, same config/seeds. DUAL coexistence gate (≥2 lineages
each ≥3 living AND inverse-Simpson N_eff ≥ 2.0, to de-confound pop scale). Full vectorized pop×pop MII
(numpy-equivalence test incl. a deliberate-tie case PASSES). Spec v5.1 LOCKED after 2 reviews
(both DO_NOT_LOCK → 2 reviewer contradictions adjudicated) + a confirm pass.
(`rtc_g1f_c1_collapse_probe_verdict.json`; pop16 n=16, pop96 n=8.)

| cell | opens windows | final N_eff | cross-founder MII (CF) | CF−FLOOR (CI) | WF | CF/WF |
|---|---|---|---|---|---|---|
| hard16 | no (3/16) | 0.94 (collapsed) | 0.00081 | −0.00068 [−.00095, −.00052] | 0.174 | 0.5% |
| hard96 | yes (8/8) | 1.44 (still collapses) | 0.00176 | +0.00017 [−.00045, +.00092] | 0.175 | 1.0% |
| soft16 | no (2/16) | 0.72 (collapsed) | 0.00072 | −0.00074 [−.00117, −.00031] | 0.096 | 0.8% |
| soft96 | yes (8/8) | 4.10 (sustained) | 0.00153 | −0.00007 [−.00031, +.00021] | 0.160 | 1.0% |

**(i) Mechanism — pop opens, niching sustains** (the binary window-label "POP_DRIFT" is too coarse;
the pre-logged N_eff trajectory refines it): in g1f, pop=16 collapses regardless of selection; pop=96 opens
windows, but only soft/niching SUSTAINS diversity (hard96 ends at N_eff 1.44 — still collapses; soft96
ends at N_eff 4.10, all 8 seeds, 15–25 coexisting gens each).
**(ii) A REFUTED, C SUPPORTED (within soft96, n=8, pop≥96, 28 gens):** soft96 maintains genuine multi-lineage diversity for 20+ generations
AND cross-founder MII STILL sits at chance/floor (CF 0.0015 ≈ FLOOR 0.0016 ≈ 1/625; CF−FLOOR CI
includes 0; CF/WF ≈ 1%) while within-founder MII ≈ 0.16 (~100× chance). Preventing collapse does NOT
produce cross-lineage intelligibility → kin-only is **genuine private-code divergence (C)**, not a
collapse artifact (A).
**(iii) Sentinels pass:** lineage-shuffle CF jumps 15–23× on label-shuffle (metric keys on lineage);
gate-0 open ≫ mute/scramble with CIs excluding 0 (content load-bearing); I2 gen-0-founder-quality →
final-share Spearman low (0.03–0.20, so collapse is NOT lucky-start — it is drift / winner-take-all).

---

## Step 4 — C2X / C2X2 / C2X3: cross-lineage selection, and the pressure-vs-survival tension
C1 left A-refuted / C-supported but raised the obvious next question: **if survival is made to depend on
decoding NON-kin, does a shared cross-founder code emerge?** Three pre-registered intervention probes
(each LOCKED only after code-grounded adversarial review) attacked it; together they form a de-facto sweep
over how hard cross-lineage listening is pushed.

- **C2X — forced 100% non-kin, cold start.** Survival crashed: mean alive **0.045** vs C1-kin 0.272 — the
  population dies before selection can act on communication. (The auto-label `CONTENT_FREE_SHORTCUT` was a
  MISLABEL: at ~0.045 survival the content gate is uninformative; the real outcome is a **viability crash**.)
  Convergence UNANSWERED.
- **C2X2 — ramped + stationary scaffold.** Kept the population alive (~0.15) but cross-founder MII stayed
  at floor; a 3-analyst review judged this a **FALSE-NEGATIVE RISK**: strong non-kin pressure and lineage
  diversity never COINCIDED (the ramp's 0.75 plateau arrives after diversity collapsed; the stationary 0.25
  pressure was sub-threshold), and per-gen dynamics weren't logged — so it could not separate "timing
  accident" from a real tension.
- **C2X3 — diversity QUOTA + constant 0.5 non-kin, per-gen logged.** Built to FORCE pressure×diversity to
  overlap and make the dynamics visible. Result (`DESIGN_FAILURE_VIABILITY_CRASH`, both arms): at 0.5
  non-kin the population is **boom-bust** (mean alive 0.10, range 0–0.76, below the viability bar) and
  **cross-founder MII never leaves the floor** (max 0.0058 across all seeds/gens vs chance ≈ 0.0016). The
  per-gen trajectories show the mechanism directly: viable+diverse coexistence is transient — the system
  cannot stay there long enough to converge.

**Holistic — the de-facto pressure sweep.** Across the cross-lineage probes — non-kin fraction 0.25
(C2X2-stationary: viable, CF floor) / 0.5 (C2X3: boom-bust, CF floor) / 0.75–1.0 (C2X, C2X2-ramp: crash,
CF floor) — **cross-founder MII never rose above chance at ANY pressure; higher pressure only crashes
survival harder.** Mechanism: non-kin codes are mutually undecodable, so forcing non-kin listening kills
foraging → a **pressure-vs-survival tension** in which a viable, diverse, converging regime is never
reached. (All n=8 = the POSITIVE-or-INCONCLUSIVE tier; the CF-at-floor null is unanimous across seeds AND
pressure levels, so it reads as a clear null with a mechanism — not a power artifact — though banking a
FORMAL negative would still want n=16.)

---

## Scoped conclusion (calibrated — NOT a universal theorem)
Within g1f (this world, 28-generation timescale): a survival-selected decodable channel co-evolves from
scratch (Step 1, n=48) but is a **private kin dialect**; and under the sustained-diversity condition
tested (soft96, n=8) the kin-only-ness is **genuine private-code divergence**, not merely
truncated-by-collapse — when diversity is actively maintained, coexisting non-kin lineages still decode
each other at chance. **In g1f, maintaining lineage diversity is necessary but NOT sufficient for
cross-lineage (public) language.** Collapse itself: in our runs, pop=16 is fatal regardless of selection
(small-population drift); niching (tournament + lineage-fitness-sharing) sustains diversity at pop=96 —
where the boundary lies, and whether this holds in other worlds/architectures, is untested beyond these
cases. **And the cross-lineage chapter (Step 4) closes the public-language question for this world:** even
when survival is made to depend on decoding non-kin — across a swept pressure range, with diversity propped
up by a quota — cross-founder MII never rises above chance, because cross-lineage pressure and survival
trade off (non-kin codes are mutually undecodable, so forced non-kin listening kills foraging). So in g1f,
**grounded language is kin-scoped, and a public cross-lineage code does not bootstrap**; obtaining one
plausibly needs a richer world (more niches/referents to sustain diversity under communication pressure) —
the next program, not this one.

## Methodology shown in this arc (the contribution)
The attack-machine operated bidirectionally and on the process itself: it caught a false NEGATIVE
(Step 1 pilot/formal mismatch), held a frozen gate to an honest INCONCLUSIVE rather than over-claiming
(Step 2), adjudicated two direct contradictions between independent reviewers (Step 3 divisor +
window-gate), and corrected an over-coarse auto-label using a pre-logged continuous metric (Step 3
mechanism). Throughout: same-config treatment/control, frozen pre-registration, no-oracle redline,
no borrowed weights, recorded provenance.

## Open / next: the rich world (the cross-lineage chapter is DONE, not open)
C2 (cross-lineage selection) was RUN — Step 4 — and answered: a public code does not bootstrap in g1f
(the pressure-vs-survival tension). So the honest next program is **a RICHER WORLD** — more niches /
referents / spatial structure, so lineage diversity can be sustained UNDER communication pressure and so
there are shared referents worth a cross-lineage code for. That is a multi-week build and a SEPARATE
paper; it is the project's real frontier bet (and the substrate the "creatures that understand they live
in a 2D world + a user-gated window to ours" north-star would need). This arc (g1f → C2X3) is a closed,
self-contained unit: it MOTIVATES the rich world rather than requiring it.

## Provenance
| step | spec / commit | verdict JSON | config |
|---|---|---|---|
| g1f | @5a6885a | `rtc_g1f_commblind_verdict_formal48_rngfix.json` (**sole headline source**) + `rtc_g1f_lineage_share_verdict.json`; legacy `..._formal48.json` / `..._reconciled_verdict.json` = **superseded** pre-rngfix | `RTC_G1F_FORMAL=1 RTC_G1F_COMMBLIND_SEEDS=48` |
| diagnostic | `STAGE_KINONLY_DIAGNOSTIC_SPEC.md` v4.1 (67ce59b) | `rtc_g1f_kinonly_diagnostic_verdict.json` @6aaefe2 | `RTC_G1F_FORMAL=1 KINONLY_SEEDS=16` |
| C1 probe | `STAGE_C1_COLLAPSE_PROBE_SPEC.md` v5.1 (f99ed6f) | `rtc_g1f_c1_collapse_probe_verdict.json` @21dc0f3 | `RTC_G1F_FORMAL=1 C1_SEEDS16=16 C1_SEEDS96=8` |
| C2X | `STAGE_C2X_CROSSLINEAGE_SPEC.md` (LOCKED) | `rtc_g1f_c2x_crosslineage_verdict.json` @1c1a27d | `RTC_G1F_FORMAL=1 C2X_SEEDS=8` |
| C2X2 | `STAGE_C2X2_RAMPED_MIXED_SPEC.md` v2.1 (LOCKED) | `rtc_g1f_c2x2_ramped_verdict.json` @07624b4 | `RTC_G1F_FORMAL=1 C2X2_POP=96 C2X2_GENS=48 C2X2_SEEDS=8` |
| C2X3 | `STAGE_C2X3_FORCED_DIVERSITY_SPEC.md` v2.1 (c91d822) | `rtc_g1f_c2x3_forced_verdict.json` @c9c749e | `RTC_G1F_FORMAL=1 C2X3_POP=96 C2X3_GENS=48 C2X3_SEEDS=8 C2X3_K=4 C2X3_M=4 C2X3_WORKERS=6` |
| — | full run recipes: `offscreen/RUNBOOK.md` · per-claim index: `offscreen/CLAIM_LEDGER.md` · code map: `ARCHITECTURE.md` | — | — |
