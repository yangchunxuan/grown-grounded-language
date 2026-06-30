# STAGE: C2X3 — FORCED-DIVERSITY × CROSS-LINEAGE PRESSURE — pre-registration **v2.1 — LOCKED**

**LOCK note (review round 2: Codex + Opus-4.7 both on v2).** Both confirmed the round-1 blocker (decision-tree
conflation) is RESOLVED, no-oracle clean, quota = legit niching (not painting), per-gen logging resolves the
timing question. Both INDEPENDENTLY caught the SAME real v2 bug — the degenerate byte-stability test
`K=POP,m=1` is impossible under AUGMENT (Codex called it DO_NOT_LOCK, Opus polish; identical fix). Applied:
degenerate test → **K=0** (+ quota-specific invariants); CF **gray-zone** verdict `C2X3_INCONCLUSIVE_GRAY_CF`
(sub-SESOI rise not forced into private/public); `CONTENT_FREE_SHORTCUT` → `CONTENT_FREE_UNDER_FORCED_ROUTING`
(+ kin-context note). No science change; these are label/test correctness. LOCKED for implementation.

**v2 changelog (review round 1: Codex DO_NOT_LOCK + Opus-4.7 LOCK → adjudicated Codex's blocker is real, applied).** Codex's blocker: the decision tree conflated alive-viability / content-load / content-free. Fixed → §5 now has FOUR independent checks (alive_viable = ALIVE only, no open-vs-mute; diversity_held; treatment_content_load = open>mute IN the forced arm; CF_success), §6 is an ordered tree. CONTENT_FREE is now judged in the treatment arm (Codex), NOT "kin dead" (my v1 error). Added `C2X3_QUOTA_KINONLY` control + `C2X3_DESIGN_FAILURE_QUOTA` to de-confound "pressure beats quota" from "quota too weak". Renamed PUBLIC_CODE_EMERGES → `C2X3_SCOPED_PUBLIC_CODE_GIVEN_FORCED_DIVERSITY` (scope in the label). Pinned quota = augment + lowest-index tiebreak; "census slots guaranteed, living N_eff measured"; degenerate byte-stability test. Both reviewers: quota is legit niching (not painting), no-oracle clean, per-gen logging resolves the timing question.

**Provenance.** C2X2 (ramped + stationary scaffold) FIXED the C2X viability crash (alive 0.15 vs 0.045)
but returned no public code (CF at floor). A 3-analyst adversarial review (all FALSE_NEGATIVE_RISK, high
confidence) found the n=8 negative is **NOT trustworthy**: strong cross-lineage pressure and lineage
diversity **never coincided** — RAMP's 0.75 plateau arrives at gen 37 but diversity had already collapsed
(final N_eff ≈1.4–1.8); STAT025 held diversity (N_eff ≈2.4–2.9) but its 0.25 pressure was likely
sub-threshold (failing non-kin costs only ~the food fraction, agents coast on kin). Routing/hash verified
CORRECT (no bug, no oracle leak) — it is a **design/timing flaw**, and per-gen trajectories were computed
but NOT saved, so we cannot even SEE the overlap. **Two live hypotheses we currently cannot separate:**
(a) FALSE negative — timing accident (fixable); (b) TRUE deeper negative — **cross-lineage pressure
inherently collapses the diversity it needs** (a real, mechanistic finding, and the bridge to rich-world).
C2X3 resolves (a) vs (b). This is the 3rd time the attack-machine caught this false-negative class
(g1f → C2X mislabel → C2X2); C2X3 is the experiment that finally gives an INTERPRETABLE answer, not a
treadmill step.

## 0. Question
**When lineage diversity is MAINTAINED and strong cross-lineage decoding pressure is applied
SIMULTANEOUSLY, does a shared cross-founder code emerge under survival selection?** Plus the diagnostic:
**does cross-lineage pressure, left unchecked, collapse the diversity it needs?**

## 1. The two fixes (vs C2X2)
1. **PER-GEN TRAJECTORY LOGGING (mandatory).** Save, per seed per arm, the full per-gen array
   `{gen, p_nonkin, cf, wf, neff, n_lineages_living, coexist, alive}` to the verdict JSON (the runner
   already computes this and discards it — store it). Plus derived diagnostics per seed:
   `last_coexist_gen`, `max_p_nonkin_during_coexist`, `cf_during_high_pressure_coexist` (mean CF over gens
   where `p_nonkin ≥ 0.5 AND coexist`), and the `(neff, p_nonkin)` trajectory. This makes pressure×diversity×CF
   VISIBLE and lets us see if/when they overlapped — the thing C2X2 could not show.
2. **FORCE pressure × diversity to COINCIDE (diversity quota).** A niche **quota** that protects the top-K
   founder lineages from extinction (reserve `K × m` offspring slots, m per protected lineage; fill the rest
   by the C1 tournament-k2 on shared fitness), so **≥K founder lineages keep gen-start census slots throughout** (living N_eff is MEASURED, not
   guaranteed — §5) while constant **0.5** non-kin pressure is applied. This isolates the variable: diversity is held → the ONLY question
   left is "does CF rise?". (Quota = a standard niching / island-model device; it does NOT leak referent
   truth and does NOT teach language — within each protected niche, decode-to-forage survival selection is
   intact; we only prevent global fixation. Painted-collapse guards still apply.)

## 2. Frozen config
- `POP=96`, `GENS=48`, `N=8` tier (POSITIVE-or-INCONCLUSIVE only) → `N=16` to bank a negative.
- non-kin fraction = **constant 0.5** (stronger than C2X2's 0.25, below the 1.0 cold-crash; failing it costs
  ~half the food signal → a real selection gradient, WITHOUT changing the world's fitness function).
- quota: protect the **K=4 LARGEST** founder lineages (ties → lowest lineage-index), **m=4** reserved
  offspring slots each (**AUGMENT, not cap**: protected lineages may ALSO win extra slots via tournament);
  16 of 96 reserved. Guarantees gen-start **census** slots for ≥K lineages; **living N_eff is MEASURED, not
  guaranteed** (§5). [K=4, m=4 flagged for review]
- deterministic-hash routing (C2X2 §2 formula), no RNG consumed; same C1 soft mutation; vectorized MII +
  byte-stability + numpy-equivalence tests retained; same config/seeds across arms.

## 3. Arms
- **C2X3_FORCED** (primary): quota + constant 0.5 non-kin, real msgs, survival fitness. → the decisive test.
- **C2X3_NOQUOTA** (tension diagnostic): constant 0.5 non-kin, NO quota. → does pressure collapse diversity
  without the prop? (confirms/quantifies the hypothesis-(b) tension; also shows whether the quota is what
  enables any CF rise.)
- **C2X3_QUOTA_KINONLY** (quota-control): quota + p_nonkin=0 (kin-only listening). → does the quota hold
  N_eff ABSENT pressure? De-confounds a diversity_held failure (pressure-beats-quota vs quota-too-weak; §6.2).
- **C1_KIN_ONLY** (baseline + viability ceiling). **C2X3_COMMBLIND** (quota+0.5, random fitness),
  **C2X3_RANDOM_TOK** (quota+0.5, iid tokens), **C2X3_SCRAMBLE** (quota+0.5, permuted-real), **FROZEN_MIXED**
  (CF floor). Shared baselines run once → `baseline_max` for the treatment.

## 4. Metrics (per seed) + the per-gen trajectory (§1.1)
CF, WF, CF/WF, CF_margin vs `baseline_max=max(FROZEN, C1, COMMBLIND, RANDOM_TOK, SCRAMBLE)`; mean+final
alive; final + per-gen N_eff; table-L2 ratio; speaker-source N_eff + max-share; fallback counts; **non-kin-only
final eval** (open/mute/scramble/permute at 100% non-kin) — **treated as confounded-corroborating, the
PRIMARY convergence evidence is CF (direct) + `cf_during_high_pressure_coexist`** (de-confounds the C2X2
mislabel where a 100%-non-kin eval re-crashed the pop). SESOI=0.04, FLOOR+SESOI before CF.

## 5. FOUR INDEPENDENT checks (Codex blocker fix: do NOT conflate alive / content-load / diversity / CF)
Each check has its OWN metric; open-vs-mute is NOT inside viability:
- **alive_viable** (ALIVE only): FORCED mean_alive ≥ 0.5×C1 AND ≥ 0.15 abs AND beats the COLD-equivalent
  (paired CI>0.05). NO content test here.
- **diversity_held**: median final LIVING N_eff ≥ 0.75·K (=3.0 at K=4; 25% tolerance because the quota
  guarantees gen-start CENSUS slots, not living post-episode N_eff — so we MEASURE it) AND
  `max_p_nonkin_during_coexist ≥ 0.5` in ≥6/8 seeds (the engineered overlap actually happened).
- **treatment_content_load** (in the FORCED arm under ITS OWN routing): open beats mute AND scramble
  (paired CI>0) = is ANY message content (kin+non-kin) load-bearing for survival? (Also report the
  kin-only-routing paired_eval as context — but the label is driven by the FORCED arm, not by kin.)
- **CF_success**: `CF_margin` CI lower>0 AND ≥ SESOI AND CF ≥ 0.25·WF AND painted guards pass;
  non-kin-only eval (open>mute/scramble) is CORROBORATING, CF + `cf_during_high_pressure_coexist` are primary.
- **quota-control** `C2X3_QUOTA_KINONLY` (quota, p_nonkin=0) de-confounds a diversity_held failure: did the
  quota hold N_eff ABSENT pressure?

## 6. Decision rule (FROZEN, ORDERED — Codex split)
1. NOT alive_viable → `C2X3_DESIGN_FAILURE_VIABILITY_CRASH`.
2. NOT diversity_held:
   - QUOTA_KINONLY held N_eff (quota works without pressure) → `C2X3_PRESSURE_COLLAPSES_DIVERSITY` (pressure
     beats the quota — hypothesis-(b) confirmed, deconfounded; paper-worthy mechanism + rich-world bridge).
   - QUOTA_KINONLY also failed → `C2X3_DESIGN_FAILURE_QUOTA` (quota too weak / mis-implemented — NOT a
     science result; fix the quota & rerun).
3. alive_viable + diversity_held + NOT treatment_content_load (open ≯ mute in FORCED) →
   `C2X3_CONTENT_FREE_UNDER_FORCED_ROUTING` (in THIS arm's 50%-non-kin routing, no message content is
   load-bearing — judged in the treatment arm, NOT via "kin dead", Codex's correct test). NB: if the
   kin-routing paired_eval (§8) shows kin content IS healthy, read this as "the forced routing dilutes
   content too much," NOT "the world doesn't reward content" (Opus).
4. + treatment_content_load + CF_success → `C2X3_SCOPED_PUBLIC_CODE_GIVEN_FORCED_DIVERSITY` (renamed so the
   label itself carries the scope — Opus/Codex: a label-only reader must not over-read it as "public code
   emerges naturally"). Scoped positive: cross-lineage code CAN form when diversity is held; remaining
   blocker = diversity-maintenance (→ richer world to sustain it).
5. + treatment_content_load + CF at floor (margin CI incl 0 / <SESOI; `cf_during_high_pressure_coexist`
   ≈ floor) → `C2X3_PRIVATE_CODES_PERSIST_UNDER_FORCED_DIVERSITY` (bulletproof negative, n≥16: alive +
   diverse + content load-bearing, yet cross-lineage stays at floor → grounding / rich-world needed = next
   paper). The clean, interpretable negative C2X2 could not deliver.
5b. CF above floor but margin < SESOI (a real-but-sub-threshold rise, `cf_during_high_pressure_coexist`
   NOT at floor) → `C2X3_INCONCLUSIVE_GRAY_CF` (report the partial rise honestly; do NOT force it into
   private-codes OR public-code — Codex gray-zone fix).
6. CF rises but painted guards fail → `C2X3_PAINTED_ALIGNMENT`. Any non-positive at n=8 → `C2X3_INCONCLUSIVE_N8`.

## 7. No-oracle + not-manufactured-alignment
Routing + quota read only population DEMOGRAPHICS (lineage labels, lineage sizes/N_eff) — never referent
truth, edibility, world patches, decode success, or founder-id-as-policy-input. The quota maintains niches;
it does NOT pick a teacher, hand out a target code, or reward imitation. Decode-to-forage survival selection
inside each niche is intact. Painted guards (table-L2 ≥0.5×gen0, speaker-source N_eff ≥2.5 + ≤40% share)
reject single-teacher / clonal fake convergence. The non-kin-only final eval is run UNSCAFFOLDED (100%
non-kin, no quota) so a positive verdict is on unscaffolded cross-lineage decoding.

## 8. Implementation notes
- New runner `offscreen/rtc_g1f_c2x3_forced.py` reusing the C2X2 runner + harness.
- Add a `_select_next_quota(...)` (additive; behind a flag; default C1/C2X/C2X2 selection byte-stable):
  compute gen-start lineage counts → pick top-K largest lineages (**ties → lowest lineage-index**) →
  reserve **m** offspring slots each (AUGMENT: they may also win more via tournament) → fill the remaining
  `n − K·m` slots by the C1 tournament-k2-on-shared-fitness; preserve_lineage=True throughout.
- **Byte-stability + quota tests** (Codex+Opus both flagged the v2 test as impossible): (i) MII
  numpy-equivalence (carried); (ii) constant-route at p=0 == kin-only (carried); (iii) **`_select_next_quota`
  at K=0 (no reservation → all slots go to tournament) must be byte-identical to `_select_next_soft`** (the
  correct degenerate case; NOT K=POP,m=1 — under AUGMENT that reserves every slot and tournament never runs,
  so it cannot equal soft). PLUS quota-specific invariants: each protected lineage receives **≥ m** offspring;
  AUGMENT lets protected lineages **also** win extra tournament slots; the top-K tiebreak (lowest
  lineage-index) is deterministic.
- Constant-0.5 routing reuses C2X2's mixed-route closure with fixed p=0.5. **kin-content-load** = reuse
  C2X2 `paired_eval` (rtc_g1f_c2x2_ramped.py:152) on KIN routing (speaker_rule=None) — reported as context.
- **Store the per-gen trajectory arrays in the JSON** (the C2X2 gap) + per-gen: protected-lineage IDs,
  fallback counts, speaker-source concentration. Keep MII vectorized.
- Do NOT modify any LOCKED spec or verdict JSON. New files only.

## 9. Why this is decisive, not a treadmill
C2X2 left two indistinguishable hypotheses (timing-accident vs fundamental-tension) because pressure and
diversity never overlapped and per-gen data wasn't saved. C2X3 (a) makes the dynamics visible (per-gen log)
and (b) FORCES the overlap (quota), so the outcome is interpretable EITHER way: code emerges given diversity
(positive, blocker = diversity-maintenance), or no code even with diversity held (bulletproof negative →
rich world), or pressure beats the quota (tension confirmed → rich world). All three are bankable and
paper-worthy. After C2X3 → consolidate & write; rich-world = next paper.
