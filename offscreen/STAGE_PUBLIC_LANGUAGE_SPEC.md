# STAGE: PUBLIC (cross-lineage) LANGUAGE — pre-registration spec

**Question.** g1f showed survival selection co-evolves a decodable channel, but **kin-lineage only** (population collapses to ~1 founder; cross-agent MII is decoding among near-clones). This stage asks the next question directly:

> **Does a PUBLIC, cross-lineage shared language co-evolve — i.e. can agents whose lineages never shared an ancestor come to decode each other above a comm-blind control, while lineage diversity is maintained?**

Pre-registered BEFORE running. Frozen choices below are locked; we run once at the locked config and report whatever comes out (positive, scoped-null, or design-failure).

---

## 1. Base + the two load-bearing changes
Extend the g1f RTC co-evolution harness (`rtc_g1f_coevolve.py`). Exactly two mechanism changes vs g1f, each independently ablatable:

**C1 — maintain lineage diversity (kill founder collapse).** g1f uses 50%-truncation + clone-refill in a small pop → fixation to ~1 lineage. Replace with:
- **soft selection** (fitness-proportional or tournament-k=2 instead of hard top-50% truncation), AND
- **larger population** (locked **pop=96**), AND
- **fitness sharing / niching** by lineage (penalize over-represented lineages) — the primary diversity lever.
Ablation arm: g1f-style hard-truncation + pop=16 (should collapse — the negative control for C1).

**C2 — put CROSS-lineage intelligibility under selection (the decisive change).** g1f's listener rule lets agents only ever hear **same-lineage** speakers → cross-lineage decoding was never selected for, so a private kin code suffices. Change `_speaker_for` so a listener is paired with speakers from **other** lineages (mixed-lineage interaction), so survival depends on decoding non-kin.
Ablation arm: kin-only listening (= g1f rule) under C1's diversity (isolates whether C2 is the load-bearing change).

## 2. Primary metric (and why it differs from g1f)
- **PRIMARY: cross-founder MII** = mutual intelligibility restricted to agent pairs whose lineages **never shared an ancestor** (`min_offdiag` / off-block of the MII matrix — already computed in g1f but ignored in its headline). g1f's bug was reporting population-average MII, which rises mechanically with fixation.
- **GUARD: effective-lineage-count** over generations (report the trajectory). If it falls to ~1, diversity maintenance failed and the public-language question is untestable in that run.

## 3. Controls (attack-machine, SAME-CONFIG discipline — the g1f lesson)
Every control runs at the **identical env/seeds/formal block** as the treatment (enforced + recorded in the JSON):
- **paired comm-blind control** (survival-fitness vs random-fitness reproduction, same init/seed) — the decisive null isolating selection-for-communication from descent-convergence.
- **architecture-matched frozen-random null** (no reproduction) — the floor.
- **scramble** (decode a permuted message) — content vs presence.

## 4. Pre-registered thresholds (FROZEN)
- Mode: **formal** (`RTC_G1F_FORMAL=1`), **gens=40** (g1f plateaued ~gen12–14 at pop16; allow headroom at pop96; report the plateau gen).
- pop=96; lineages tracked by frozen founder id.
- **seeds: n=48** (power: g1f paired-diff sd≈0.10 → MDE≈0.04 at n=48, 80%+ power; matches the g1f canonical).
- **VERDICT GATE tests the ACTUAL claim** (not a proxy): PUBLIC_LANGUAGE_COEVOLVES iff **(a)** cross-founder MII − comm-blind cross-founder MII has a bootstrap 95% CI **excluding 0**, AND **(b)** effective-lineage-count stays **> 1** (median over seeds ≥ 2 at the final gen). Both must hold.
- no-oracle redline unchanged (decisions read only decoded messages / own body); no borrowed weights.

## 5. Pre-registered outcomes (all honest)
- **PUBLIC_LANGUAGE_COEVOLVES** — both gates pass → the project's first cross-lineage shared-language positive. (Then: red-team it — bottleneck/diversity confounds, MII-semantics, same-config — before banking.)
- **NO_PUBLIC_LANGUAGE (scoped null)** — diversity maintained (eff-lineage>1) but cross-founder MII does NOT beat comm-blind → public language does not co-evolve here; g1f's positive stays kin-scoped. A clean, real negative.
- **DESIGN_FAILURE (untestable)** — diversity still collapses despite C1 → cannot test C2; iterate C1, do not report a language verdict.

## 6. Implementation steps (then run)
1. Add C1 diversity knobs to `_select_next` (soft selection + lineage fitness-sharing) behind env flags; keep g1f hard-truncation as the ablation default-off.
2. Add C2 cross-lineage listener option to `_speaker_for` (env flag).
3. Promote **cross-founder MII** (`min_offdiag`) + **effective-lineage-count** to first-class outputs in the verdict JSON; record full config (env/seeds/formal) in the JSON.
4. Wire the paired comm-blind + frozen + scramble controls at the SAME config.
5. Smoke-test at pilot scale (just to confirm it runs — NOT for any verdict), then run the locked formal n=48.
6. Power/reconcile + a written confound red-team before any claim.

## 7. Config-provenance discipline (carried from CLAIM_LEDGER.md)
- The treatment and every control MUST be the same env/seed/formal block; the JSON records it; a mismatch invalidates the run (this is the exact bug that produced the g1f false negative).
