# STAGE: CROSS-LINEAGE MUTUAL INTELLIGIBILITY — pre-registration spec **v2**

**v2 changelog.** v1 was reviewed by three independent red-teams (Gemini full A–J + two others); unanimous verdict **DO_NOT_LOCK**. Direction endorsed; the spec had a fatal hole (no non-language baseline for cross-founder MII) plus unfrozen degrees of freedom. v2 closes every converged fix below. **Claim wording downgraded**: this stage tests CROSS-LINEAGE mutual intelligibility, NOT "public language" (that label is reserved for a later, higher-diversity stage).

**Question (v2, calibrated).** g1f showed survival selection co-evolves a decodable channel but **kin-lineage only** (~1 founder fixes; cross-agent MII is decoding among near-clones). This stage asks:

> **Does survival selection raise mutual intelligibility between agents from DIFFERENT founder lineages, ABOVE all non-language baselines, while genuine lineage diversity is maintained?**

Pre-registered before running. All FROZEN values are locked; we run once and report whatever comes out.

> **The load-bearing fact that shapes this spec (from g1f data):** comm-blind MII = **0.127** vs frozen = **0.0016** — i.e. shared architecture + shared world + shared init produce ~75× the floor MII **with no communication selection at all**. Therefore cross-founder MII is presumed contaminated by a large non-language baseline until proven otherwise. The whole control design exists to subtract that baseline.

---

## 0. IMPLEMENTATION-VERIFICATION GATES (must pass in code BEFORE the run — the reviews could not check these from files)
- **V0a — reward→message strict chain (FM-γ).** Read `rtc_g1f_coevolve.py` reward/fitness path and CONFIRM that an agent which does not decode cross-lineage message content cannot exceed chance survival. If the world does NOT enforce this, the world must be changed (or the run is invalid — it would re-run the W3 "content-free shortcut"). The `random-token` control (§3) is the empirical test; V0a is the code-level confirmation.
- **V0b — true cross-FOUNDER MII.** Current code computes an all-pairs off-diagonal (`min_offdiag`). Implement a metric restricted to pairs whose founders **never shared an ancestor**. Record the exact MII definition (probing-decode of sampled referents → exact-tuple recovery; NOT raw weight similarity) in the verdict JSON.
- **V0c — config recorded.** Every run's JSON records full env (incl. formal flag, C1-state, selection operator, all frozen params) + seeds, so treatment and every control are provably the SAME config.

## 1. The two mechanism changes (each independently ablatable)
- **C1 — maintain lineage diversity.** Replace g1f's hard top-50% truncation with **tournament selection, k=2, on SHARED fitness** where `shared_fitness_i = raw_fitness_i / (count of living same-lineage agents)` (standard lineage fitness-sharing). Larger pop. (Ablation: g1f hard-truncation + pop=16 — the negative control that should collapse.)
- **C2 — put cross-lineage intelligibility under selection.** `_speaker_for` pairs each listener with speakers from **other** founder lineages (mixed-lineage interaction), so survival depends on decoding non-kin. (Ablation = C2-only / kin-only listening, see §3.)

## 2. Metrics
- **PRIMARY: cross-founder MII** (V0b) — non-kin pairs only.
- **DIVERSITY (gate + guard): effective lineage count = inverse-Simpson index** of founder shares, reported as a trajectory over gens.
- **FM-β guard: lineage functional distance** — mean pairwise distance between lineages' speaker weight-vectors AND message-set (symbol-distribution) distance. **Report BOTH; gate (c) requires BOTH > 0 (either one alone is insufficient).** Share-based N_eff alone does NOT prove the maintained lineages are functionally different ("painted collapse").

## 3. Controls — ALL at the SAME env/seeds/formal block, C1 ON unless noted (the g1f same-config lesson)
1. **paired comm-blind** (survival vs random fitness, same init/seed, **C1 ON**) — descent/selection discriminator.
2. **frozen-mixed** (multi-lineage population, frozen-random weights, no reproduction) — **the true non-language zero-baseline for cross-founder MII** (single-lineage frozen 0.0016 does NOT represent the mixed case). 🔴 new in v2.
3. **lineage-shuffle** (same run; founder-ids randomly relabeled BEFORE computing cross-founder MII) — proves the metric measures lineage structure, not artifact. Predicted margin → ~0. 🔴 new in v2.
4. **random-token** (each frame an i.i.d. random message; ≠ scramble) — tests whether a content-free token suffices. Predicted = chance. 🔴 new in v2.
5. **scramble** (decode a permuted real message) — content vs presence.
6. **C1-only ablation** (C1 on, kin-only listening) and **C2-only ablation** (cross-lineage listening, g1f hard-truncation + pop=16) — isolate each mechanism. 🔴 C2-only new in v2.
7. **within-lineage MII** — **apparatus sanity**: must be significantly > frozen; **seeds that fail this are excluded from the main analysis** (instrument not in place).

## 4. FROZEN values (LOCKED — no post-hoc tuning; renaming/redefining a gate later = protocol violation, per the W4 governance lesson)
- mode = **formal**; gens = **40** (g1f plateaued ~gen12–14 at pop16; report the plateau gen; if not plateaued, see §5 INCONCLUSIVE).
- pop = **96**; initial founder count **K = 12** (8 agents/founder at start).
- selection = **tournament k=2 on shared fitness** (the ONE chosen operator — NOT an either/or); fitness-sharing form = `raw / same_lineage_count` (exponent 1.0).
- seeds = **n = 48** (g1f paired-diff σ≈0.10 → MDE≈0.04 at 80%+ power). **If observed cross-founder σ > 0.20 (= 2×0.10), report it and treat n=48 as INCONCLUSIVE rather than a negative — do not falsely report NO_CROSS_LINEAGE.** 🔴 v2.
- no-oracle redline unchanged; no borrowed weights.

## 5. SUCCESS GATE (FROZEN) — verdict `CROSS_LINEAGE_MII_COEVOLVES` iff ALL hold:
- **(a) effect**: `cross_founder_MII(survival)` minus **the MAX of {comm-blind, frozen-mixed, lineage-shuffle}** has a bootstrap 95% CI **excluding 0 AND a point estimate ≥ Δ_min = 0.04** (SESOI anchored to g1f's +0.045). Subtracting the strongest non-language baseline is the FM-α fix. 🔴
- **(b) diversity**: effective-lineage-count (inverse-Simpson) **median over seeds ≥ 3 AND 25th-percentile ≥ 2.5** at the final gen. 🔴 (raised from >1)
- **(c) functional**: lineage functional distance does NOT collapse — **final-gen functional distance ≥ 0.5 × gen-0 functional distance** (FM-β guard); maintained lineages stay genuinely different, not relabeled clones.

### Outcomes (FROZEN, incl. corner cases)
- **CROSS_LINEAGE_MII_COEVOLVES** — (a)+(b)+(c) all pass → then run §6 lesions before banking.
- **NO_CROSS_LINEAGE_MII (scoped null)** — (b) holds (diversity maintained) but (a) fails. AND (b) passes but (a) fails ⇒ this bucket. 🔴
- **DESIGN_FAILURE (untestable)** — (b) fails (diversity collapsed despite C1), regardless of (a). AND (a) passes but (b) fails ⇒ this bucket (a "positive" among collapsed lineages is just g1f again). 🔴
- **INCONCLUSIVE** — observed σ ≫ planned, power insufficient; report, do not call it a negative. 🔴

## 5b. RED-TEAM LESIONS — PRE-DECLARED, predictions FROZEN (🔴 new in v2; "thought of but not in the spec = not thought of")
Run on any (a)+(b)+(c)-passing result BEFORE banking; each prediction + the failure-mode it would trigger is locked now:
- **L1 lineage-shuffle** → predict cross-founder margin collapses < Δ_min. If it does NOT collapse ⇒ **FM-α** (metric measuring non-language convergence) — REJECT.
- **L2 random-token** → predict margin = chance. If treatment ≈ random-token ⇒ **FM-γ** (content-free shortcut) — REJECT.
- **L3 targeted message edit** (swap founder-A's symbol for founder-B's) → predict cross-lineage behavior changes in the edit's direction. If no change ⇒ messages not causal — REJECT.
- **L4 comm-lesion @ gen40** (cut the cross-lineage message channel) → predict survival/MII falls toward comm-blind **within 5 ticks** of the cut. If unchanged ⇒ channel not load-bearing — REJECT.
- **L5 frozen-listener @ gen30** → predict cross-founder MII plateaus from gen30; if it keeps rising ⇒ speaker-side shortcut. **L5 is DIAGNOSTIC-ONLY (does NOT reject by itself); a failing L5 triggers a follow-up speaker-side audit.**

## 6. Implementation steps (then run)
1. Pass V0a/V0b/V0c (§0) — code-verify the reward→message chain, implement true cross-founder MII + functional-distance + inverse-Simpson, record config.
2. Add C1 (tournament-k2 + lineage fitness-sharing) and C2 (cross-lineage `_speaker_for`) behind env flags; g1f behavior is the ablation default-off.
3. Wire ALL §3 controls at the same config; implement the §5b lesions.
4. Pilot smoke-test (runs-without-crashing ONLY, no verdict), then the locked formal n=48.
5. Power/reconcile + the §5b pre-declared lesion battery + a written confound report before any claim.

## 7. Provenance discipline (carried from CLAIM_LEDGER.md)
Treatment and every control MUST share env/seed/formal/C1-state; the JSON records it; a mismatch invalidates the run. This is the exact class of bug (formal-vs-pilot) that produced the g1f false negative — never again.
