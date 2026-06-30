# STAGE: C2X3 — FORCED-DIVERSITY × CROSS-LINEAGE PRESSURE — pre-registration **DRAFT (not locked)**

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
   by the C1 tournament-k2 on shared fitness), so **N_eff ≥ ~K is GUARANTEED throughout** while constant
   **0.5** non-kin pressure is applied. This isolates the variable: diversity is held → the ONLY question
   left is "does CF rise?". (Quota = a standard niching / island-model device; it does NOT leak referent
   truth and does NOT teach language — within each protected niche, decode-to-forage survival selection is
   intact; we only prevent global fixation. Painted-collapse guards still apply.)

## 2. Frozen config
- `POP=96`, `GENS=48`, `N=8` tier (POSITIVE-or-INCONCLUSIVE only) → `N=16` to bank a negative.
- non-kin fraction = **constant 0.5** (stronger than C2X2's 0.25, below the 1.0 cold-crash; failing it costs
  ~half the food signal → a real selection gradient, WITHOUT changing the world's fitness function).
- quota: protect **K=4** lineages, **m=4** each (16 reserved of 96; N_eff ≥ ~4 guaranteed). [flag K,m for review]
- deterministic-hash routing (C2X2 §2 formula), no RNG consumed; same C1 soft mutation; vectorized MII +
  byte-stability + numpy-equivalence tests retained; same config/seeds across arms.

## 3. Arms
- **C2X3_FORCED** (primary): quota + constant 0.5 non-kin, real msgs, survival fitness. → the decisive test.
- **C2X3_NOQUOTA** (tension diagnostic): constant 0.5 non-kin, NO quota. → does pressure collapse diversity
  without the prop? (confirms/quantifies the hypothesis-(b) tension; also shows whether the quota is what
  enables any CF rise.)
- **C1_KIN_ONLY** (baseline + viability ceiling). **C2X3_COMMBLIND** (quota+0.5, random fitness),
  **C2X3_RANDOM_TOK** (quota+0.5, iid tokens), **C2X3_SCRAMBLE** (quota+0.5, permuted-real), **FROZEN_MIXED**
  (CF floor). Shared baselines run once → `baseline_max` for the treatment.

## 4. Metrics (per seed) + the per-gen trajectory (§1.1)
CF, WF, CF/WF, CF_margin vs `baseline_max=max(FROZEN, C1, COMMBLIND, RANDOM_TOK, SCRAMBLE)`; mean+final
alive; final + per-gen N_eff; table-L2 ratio; speaker-source N_eff + max-share; fallback counts; **non-kin-only
final eval** (open/mute/scramble/permute at 100% non-kin) — **treated as confounded-corroborating, the
PRIMARY convergence evidence is CF (direct) + `cf_during_high_pressure_coexist`** (de-confounds the C2X2
mislabel where a 100%-non-kin eval re-crashed the pop). SESOI=0.04, FLOOR+SESOI before CF.

## 5. Viability + diversity-held checks
- viability (per C2X2): FORCED alive ≥ 0.5×C1 AND ≥0.15 abs AND beats COLD-equivalent AND beats its own
  mute/scramble (paired). If fails → `C2X3_DESIGN_FAILURE_VIABILITY_CRASH`.
- diversity-held (NEW): FORCED must actually maintain `median final N_eff ≥ 0.75·K` (the quota is working);
  AND `max_p_nonkin_during_coexist ≥ 0.5` in ≥6/8 seeds (the overlap we engineered actually happened). If
  the quota fails to hold diversity under 0.5 pressure → that itself is evidence for hypothesis-(b)
  (`C2X3_PRESSURE_COLLAPSES_DIVERSITY` — pressure beats even the quota).

## 6. Decision rule (FROZEN)
- `C2X3_PUBLIC_CODE_EMERGES` (scoped: "given maintained diversity") iff viability + diversity-held +
  `CF_margin` CI lower>0 AND ≥SESOI AND CF≥0.25·WF AND non-kin-only-eval open beats mute/scramble (CI>0)
  AND painted guards pass. → cross-lineage code CAN form under survival selection when diversity is held;
  the remaining blocker is diversity-maintenance (→ richer world to sustain it naturally).
- `C2X3_PRIVATE_CODES_PERSIST_UNDER_FORCED_DIVERSITY` (bulletproof negative; n≥16) iff viability +
  diversity-held + kin-content load-bearing BUT CF stays at floor (margin CI incl 0 / <SESOI) AND
  `cf_during_high_pressure_coexist` ≈ floor. → even with diversity guaranteed + strong pressure, no public
  code → grounding / rich-world needed (→ next paper). **This is the clean, interpretable negative C2X2
  could not deliver.**
- `C2X3_PRESSURE_COLLAPSES_DIVERSITY` iff the quota cannot hold N_eff under 0.5 pressure (diversity-held
  fails) → hypothesis-(b) confirmed mechanistically (the tension is real) → also a paper-worthy finding +
  rich-world bridge.
- `C2X3_CONTENT_FREE_SHORTCUT` iff KIN content is also NOT load-bearing (distinct from above — fixes the
  C2X2 mislabel: only call content-free when even kin content is dead). `C2X3_PAINTED_ALIGNMENT` if CF rises
  but painted guards fail. `C2X3_INCONCLUSIVE_N8` for any non-positive at n=8.

## 7. No-oracle + not-manufactured-alignment
Routing + quota read only population DEMOGRAPHICS (lineage labels, lineage sizes/N_eff) — never referent
truth, edibility, world patches, decode success, or founder-id-as-policy-input. The quota maintains niches;
it does NOT pick a teacher, hand out a target code, or reward imitation. Decode-to-forage survival selection
inside each niche is intact. Painted guards (table-L2 ≥0.5×gen0, speaker-source N_eff ≥2.5 + ≤40% share)
reject single-teacher / clonal fake convergence. The non-kin-only final eval is run UNSCAFFOLDED (100%
non-kin, no quota) so a positive verdict is on unscaffolded cross-lineage decoding.

## 8. Implementation notes
- New runner `offscreen/rtc_g1f_c2x3_forced.py` reusing the C2X2 runner + harness.
- Add a `_select_next_quota(...)` (additive; reserves K×m slots for the largest lineages, rest tournament-
  k2-on-shared-fitness) behind a flag; default C1/C2X/C2X2 selection byte-stable. Constant-0.5 routing reuses
  C2X2's mixed-route closure with fixed p=0.5. **Store the per-gen trajectory arrays in the JSON** (the C2X2
  gap). Keep MII byte-stability + numpy-equivalence tests.
- Do NOT modify any LOCKED spec or verdict JSON. New files only.

## 9. Why this is decisive, not a treadmill
C2X2 left two indistinguishable hypotheses (timing-accident vs fundamental-tension) because pressure and
diversity never overlapped and per-gen data wasn't saved. C2X3 (a) makes the dynamics visible (per-gen log)
and (b) FORCES the overlap (quota), so the outcome is interpretable EITHER way: code emerges given diversity
(positive, blocker = diversity-maintenance), or no code even with diversity held (bulletproof negative →
rich world), or pressure beats the quota (tension confirmed → rich world). All three are bankable and
paper-worthy. After C2X3 → consolidate & write; rich-world = next paper.
