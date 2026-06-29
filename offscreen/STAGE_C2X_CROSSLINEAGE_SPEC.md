# STAGE: C2X — CROSS-LINEAGE SELECTION MICRO-PROBE — pre-registration **DRAFT (not locked)**

**Lineage.** Descends from g1f (channel co-evolves, kin-scoped) → kin-only DIAGNOSTIC (directional C) →
C1 COLLAPSE PROBE (`C1_OPENS_WINDOW_C`: A refuted, C supported — even with sustained multi-lineage
diversity, cross-founder MII stays at the floor). The C1 code located the exact causal path: in
`shared_weights_kin`, listening explicitly prefers **same-lineage** speakers (`rtc_g1f_coevolve.py:160`
`_speaker_for`). So the next clean, cheap, decisive variable is: **change ONLY that path** — make
survival depend on decoding NON-kin — while keeping the C1 soft96 diversity regime. This is a C2
mechanism micro-probe in the existing G1D/G1F world; **NOT** the rich-world build, **NOT** a claim of
full public language. Builds on a Codex strategy draft + the Claude adjudication of the Codex-vs-Gemini
strategy split (see §1.1). Authored by Claude; to be reviewed code-grounded by Gemini + Codex before lock.

## 0. Evidence this spec may use (anchored to verdict JSONs)
- g1f formal: decodable channel co-evolves under survival selection, kin-scoped. Survival beats
  comm-blind MII +0.045, 95% CI [0.020, 0.070], n=48.
- kin-only diagnostic: cross-founder MII floor-level in the few coexistence windows; gate-0 = content
  load-bearing.
- C1 probe (`rtc_g1f_c1_collapse_probe_verdict.json`): soft96 maintains diversity (final N_eff ≈ 4.1,
  8/8 seeds, 15–25 coexisting gens) yet cross-founder MII stays at floor (CF 0.00153 ≈ FLOOR 0.00159;
  CF−FLOOR CI [−0.00031, +0.00021]; WF 0.160; CF/WF ≈ 1%). → A (collapse-limited) REFUTED, C (private
  codes) SUPPORTED, within g1f / soft96 / n=8 / 28 gens.

## 1. Question
On top of the C1 soft96 diversity regime, does adding **direct cross-lineage listening pressure** raise
cross-founder mutual intelligibility above every non-language baseline, while genuine lineage diversity
is maintained? Equivalently: is the private-code result caused mainly by the **absence of cross-lineage
decoding in the fitness path**, or is the current world+UnifiedIO architecture unable to support a
shared cross-founder code **even when cross-lineage decoding is selected**?

### 1.1 Why this is NOT a priori impossible (addressing the "aliasing dead-end" objection)
A strategy review argued C2X is doomed: with diverged private codes and **no speaker-ID tag**, one
listener table cannot map the same symbol to different referents for different lineages → aliasing
collision. That collision is real **for a FIXED set of diverged codes**. But C2X does not hold codes
fixed — it applies selection, and there is a concrete convergence mechanism the objection omits:
- **UnifiedIO is a TIED table** (`rtc_g1f_coevolve.py:57-78`): emit and predict share the same weights.
  Selecting a listener to decode the non-kin code it hears therefore **drags that agent's emission
  toward the same code**. Decode-pressure couples into emit-convergence.
- With **no speaker-ID** (founder-id forbidden as input, §3), a listener that hears balanced non-kin
  speakers can only survive if those speakers share ≈one code. The unique stable attractor where all
  listeners survive is a **single shared code**. Selection thus points at convergence; the open
  question is purely whether **mutation + tournament selection (no gradient)** can REACH that attractor
  from diverged codes, over ~4 effective lineages (soft96, not 10) in the small 4×5×6 table space.
This is an **optimizer-reachability** question — empirical, not settled by theory. The project's
methodology forbids banking a theory-predicted negative (cf. the g1f false-negative). C2X tests it
cheaply; its pre-registered failure outcome (`C2X_PRIVATE_CODES_PERSIST`, §8) **is** the reviewer's
hypothesis and becomes the earned motivation for shared grounding / the rich world.

## 2. Minimal mechanism change
Reuse the `shared_weights_kin` UnifiedIO agent and the **C1 soft96 selection operator unchanged**
(tournament-k2 on lineage-shared fitness, divisor = **GEN-START** same-lineage count; preserve_lineage
reproduction; 1 agent/founder init — directly comparable to soft96). The ONLY new treatment rule is
`speaker_rule = cross_lineage_balanced`:
- For each (listener i, post j, round t), choose the speaker from a founder lineage **different** from
  listener i's, by **deterministic balanced round-robin over currently-present non-self lineages**,
  keyed by `(seed, gen, round, i, j)` — NOT by fitness, decode success, message content, or truth.
- If <2 lineages are present, the gen is no-window (cannot contribute to the primary verdict).
- Forced non-kin listening; NOT a chosen "good"/teacher speaker.
- Implement as a **new `speaker_rule` parameter**; the default `_speaker_for` stays byte-stable so g1f/C1
  remain reproducible. New runner `offscreen/rtc_g1f_c2x_crosslineage.py` reusing the C1 runner.

## 3. No-oracle redline (the sharpest C2 trap)
**Allowed in decisions:** the decoded message from the selected speaker; the listener's own UnifiedIO
table; metabolic state already in g1f; RNG for sensor noise / random-token controls.
**Forbidden in decisions or training:** true `world.patch`/edibility/best-post or any target code
(except inside the existing eat/consequence resolver + fenced oracle controls); **founder-id as an input
to any table/policy** (= no speaker-ID cheat — this is load-bearing for §1.1); any loss/gradient against
referent labels or the global field; pretrained/borrowed weights. The redline scan
(`test_rtc_smoke.py`-style) MUST be extended to the C2X runner; HARD REJECT if `world.patch` is read
outside the fence or if the partner rule reads reward/code-quality/ground-truth.

## 4. Frozen formal config
- env `RTC_G1F_FORMAL=1`, `RTC_TOXIC_DEATH=-0.9`; pop=96; gens=40 (more than C1's 28, to give
  convergence time — report the convergence/plateau gen); rounds=inherited formal (record actual).
- MII = full 625 referents, **full pop×pop vectorized `_mii_matrix_fast`**; the numpy-equivalence test
  (incl. deliberate-tie) MUST pass before any formal cell.
- seeds = **16** for every primary arm/control. **If runtime forces n=8, the verdict may only be
  POSITIVE or INCONCLUSIVE, never a scoped negative** (a negative needs the power).
- treatment and EVERY control share identical seed lists, env, pop, gens, selection, init, instrumentation.

## 5. Arms + controls (all same-config)
1. **`C2X_OPEN`** (treatment): C1 soft96 + `cross_lineage_balanced` speakers + real decoded messages.
2. **`C1_KIN_ONLY`** (the C2X-OFF control = nearest baseline): C1 soft96 with the old same-lineage rule;
   should reproduce the private-code C1 floor.
3. **`C2X_COMMBLIND`**: same init / cross-lineage rule / C1 reproduction, but **random fitness** replaces
   survival fitness — subtracts common-attractor/drift convergence.
4. **`C2X_RANDOM_TOKEN`**: C2X_OPEN but every heard message = iid random symbols.
5. **`C2X_SCRAMBLE`**: C2X_OPEN but real messages permuted before decoding (content vs presence).
6. **`C2X_MUTE`**: no usable message.
7. **`FROZEN_MIXED`**: frozen unrelated UnifiedIO at pop96 = architecture FLOOR, computed before CF;
   SESOI = 1 seed-SD of FLOOR, computed before CF, written with `computed_before_CF: true`.
8. **`LINEAGE_SHUFFLE`** (diagnostic, NOT a subtracted baseline): shuffle lineage labels before CF on
   the treatment run. A true public code is ~invariant to label-shuffle, so shuffle is a diagnostic
   plot, not a gate baseline (fixes the v2.1 trap).
- Controls 4–6 MUST use the `_run_episode(..., rng=...)` hook (not the `_run_arm` mode-name seed) so
  mode-name length cannot shift the world/message stream (paired).

## 6. Primary metrics + painted-collapse guards
- `CF` (cross-founder MII, different-lineage off-diag), `WF` (within-founder, same-lineage off-diag),
  `FLOOR` (frozen-mixed CF).
- `baseline_max = max(C1_KIN_ONLY_CF, C2X_COMMBLIND_CF, C2X_RANDOM_TOKEN_CF, FROZEN_MIXED_CF)`.
- `CF_margin = C2X_OPEN_CF − baseline_max` (subtract the strongest non-language baseline).
- survival lift: C2X_OPEN alive/rounds/food-rate minus random-token / scramble / mute, paired by seed.
- diversity: inverse-Simpson N_eff over living founder shares (final gen + across coexistence windows).
- **painted-collapse guards (reject "manufactured" alignment):** final living-founder N_eff median ≥ 3.0
  AND 25th-pctile ≥ 2.5; **no single lineage supplies >40% of actual cross-lineage speaker events**;
  median pairwise UnifiedIO table-L2 distance among living founders at final gen ≥ 0.5× gen-0; report
  reproduction-lineage N_eff AND speaker-source N_eff. (Message-set distance reported, NOT a reject
  criterion — a real shared code may legitimately reduce it.)

## 7. Coexistence window gate (C1 dual gate)
A gen is a measurement window iff (a) ≥2 founder lineages each ≥3 living agents (post-episode) AND
(b) inverse-Simpson N_eff ≥ 2.0. A formal verdict requires ≥50% of seeds with ≥2 such windows; else
`DESIGN_FAILURE_NO_WINDOW` (C1 did not survive the harsher rule — fix viability before interpreting MII).

## 8. Success / failure rules (FROZEN, pre-registered)
**`C2X_CROSS_FOUNDER_CODE_COEVOLVES`** iff ALL: window gate passes; `CF_margin` bootstrap 95% CI lower
> 0 AND point ≥ **0.04** (SESOI anchored to g1f +0.045); `C2X_OPEN_CF ≥ 0.25·WF` (a minimal cross-founder
code need not reach kin ceiling); survival lift over random-token/scramble/mute each CI-lower > 0;
painted-collapse guards pass; no-oracle scan passes. → kin-only was mainly the listener rule.

**`C2X_PRIVATE_CODES_PERSIST`** iff: window gate passes; content stays load-bearing
(open > random-token/scramble/mute); CF_margin CI includes 0 OR point < 0.04; WF > FLOOR. → direct
cross-lineage selection in this world+architecture is **not enough** to create a shared cross-founder
code; motivates shared grounding anchors / rich-world RTC. **Does NOT prove impossibility** (this is the
reviewer's hypothesis, earned empirically, and the explicit bridge to the next paper).

**`C2X_CONTENT_FREE_SHORTCUT`** iff C2X_OPEN survival or CF is matched by random-token/scramble/mute →
reward-message coupling is broken; fix before any larger run.
**`C2X_PAINTED_COLLAPSE`** iff CF rises but any painted-collapse guard fails → not public language.
**`DESIGN_FAILURE_NO_WINDOW`** iff window gate fails.
**`INCONCLUSIVE`** iff power insufficient (n=8 + wide CI, or effect below planned MDE but not rejectable).

## 9. Red-team lesions (run on the final treatment population BEFORE banking any positive)
- random-token / scramble / mute: survival AND CF must fall below the success threshold.
- cross-lineage channel cut (replace non-kin messages with mute for 5 extra ticks): survival/food-pick
  must fall toward the mute control, within those ticks.
- speaker-source shuffle (permute which non-kin lineage supplies messages): if it degrades performance →
  partner-specific decoding (scope the claim); if not → a genuine common code (cleaner).
- lineage-label shuffle: report whether CF is lineage-invariant. Large shuffle-inflation ⇒ residual
  private-code structure remains ⇒ scope the verdict accordingly.

## 10. What each outcome teaches
- POSITIVE → the missing C1→public ingredient was direct cross-lineage selection; no rich-world needed
  for a minimal cross-founder code. **Upgrades the whole arc to a positive.**
- PRIVATE_CODES_PERSIST → the world+UnifiedIO basin is insufficient even when cross-lineage decoding is
  selected; next dollar = physically shared grounding anchors or the rich-world RTC (NEXT paper). The
  g1f arc + this result = a clean, mechanism-identified bound, paper-ready.
- CONTENT_FREE_SHORTCUT → world reward-message coupling invalid; fix first.
- PAINTED_COLLAPSE → redesign partner sampling / strengthen anti-teacher constraints.
- NO_WINDOW → C1 didn't survive the harsher rule; solve viability before interpreting MII.

## 11. Implementation notes
- New runner `offscreen/rtc_g1f_c2x_crosslineage.py`; add a `speaker_rule` parameter to the speaker path
  (default = current `_speaker_for`, byte-stable). Reuse `_mii_matrix_fast`, `_select_next_soft`,
  `_run_episode(rng=...)`. Do NOT edit any LOCKED spec or verdict JSON.
- Record full config, env, seed list, git commit, RNG-stream descriptions, and all arm/control summaries
  in the verdict JSON.
- Determinism: formal + pinned seeds; the equivalence test gates the vectorized MII.
- This is the LAST planned g1f-world experiment before consolidation; after it → write the paper. The
  rich world is explicitly deferred to the next paper regardless of C2X's outcome.
