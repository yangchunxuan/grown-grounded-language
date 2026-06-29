# STAGE: C1 COLLAPSE PROBE — intervention + collapse-cause diagnosis (Path B), pre-registration **v5.1 — LOCKED**

**LOCK note.** v5.1 passed a confirm pass (LOCK, no blocker under the STOP-RULE) that independently re-verified both adjudications (gen-start divisor; dual N_eff≥2.0 window gate) and the vectorization fix. Locked for implementation. Mandatory pre-run implementation checks (not design blockers): (i) vectorized `_mii` numpy-equivalence test INCLUDING a deliberate-tie case; (ii) soft branch must not consume evo_rng before the branch decision; (iii) paired gate-0 must NOT reuse `_run_arm`'s mode-name-length control seed; (iv) log per-lineage living-count + raw/shared fitness (gen-start-divisor caveat).

**v5.1 changelog (two independent code-grounded reviews, Gemini 3.1 Pro + Opus 4.7, both DO_NOT_LOCK; fixes applied + 2 reviewer CONTRADICTIONS adjudicated).** (1) **Fitness-sharing divisor** — Gemini caught a fatal perverse incentive: `raw/living-same-lineage-count` rewards high-mortality lineages (survivor of a near-extinct lineage gets inflated shared fitness). Opus said use post-episode alive (timestamp match w/ window gate). **Adjudicated → Gemini: divisor = GEN-START same-lineage count** (standard fitness-sharing = niche occupancy in the selection pool; window-gate timestamp and sharing divisor serve different purposes, must not share a timestamp). (2) **Window gate** — Opus: absolute ≥3-living is pop-scale-confounded (dominant+stragglers passes at pop96, fails at pop16 by share); Gemini: gate sound (hard truncation kills stragglers). **Adjudicated → Opus correct for the MODERATELY-FIT minor lineage (Gemini's counter only covers unfit stragglers) → DUAL gate: keep ≥3-living (measurability, Gemini) AND add N_eff≥2.0 (pop-normalized genuine diversity, Opus); decomposition readout on N_eff, not raw count.** (3) **MII subsample WF=NaN** (both flagged) → dissolved by **vectorizing MII to the full pop×pop matrix (drop the subsample)** + a numpy-equivalence test; fallback = pair-sampling. (4) wording + RNG/divisor implementation notes. Still DRAFT; recommend one confirm pass before lock.

**Lineage.** Descends from the kin-only DIAGNOSTIC (`STAGE_KINONLY_DIAGNOSTIC_SPEC.md` v4.1, verdict `INCONCLUSIVE_NO_WINDOW`, 5/16 windows, strong directional **(C) private codes**). Carves the **C1 half** out of the shelved `STAGE_PUBLIC_LANGUAGE_SPEC.md` (v2.1); **C2 (cross-lineage listening) stays DEFERRED**. This is an INTERVENTION (changes the selection mechanism), not instrument-only.

**Why now (not a standalone "collapse diagnostic").** After the kin-only run, founder collapse is no longer one nuisance among many — it is THE bottleneck: too few multi-lineage coexistence windows (5/16) to formally decide A-vs-C. So "why does the population collapse to one lineage" is welded INTO the C1 probe: one run answers three things at once, instead of a redundant standalone X-ray followed by the same C1 run anyway.

**The three questions this ONE run answers:**
1. **Does C1 open coexistence windows?** (≥8/16 seeds with ≥2 coexisting gens — the gate the diagnostic missed.)
2. **If windows open → A or C?** cross-founder MII rises toward the within-founder ceiling (**A: collapse-limited**, C1 suffices) vs stays at the architecture floor (**C: private codes**, C2/grounding needed).
3. **Which collapse mechanism dominates?** hard-truncation harshness vs small-pop drift vs a deeper cause (lucky-start founder / winner-take-all world / kin-only self-reinforcement).

---

## 0. SCOPE + REDLINES
- arm = `shared_weights_kin` (same as the diagnostic; preserve_lineage reproduction). **C2 deferred.**
- **NO borrowed weights** (grow from random init). **NO ORACLE LEAK** — see Instrument I2 (the "distance-to-optimal-code" idea is REJECTED: there is no canonical optimal code in this world — any self-consistent speaker↔listener code is equally fit — so defining one would inject ground truth).
- Beyond the new selection arms (which ARE dynamics changes by construction), all OTHER additions are **logging only**. Treatment and every control share env/seed/formal/instrumentation; the JSON records it (the g1f same-config lesson).

## 1. The 2×2 factorial (intervention + its own controls)
**selection ∈ {hard, soft} × pop ∈ {16, 96}** → 4 cells, ALL re-run at the SAME config/seeds/instrumentation (do NOT reuse the old hard+16 g1f verdict — different code path, no instrumentation).

| cell | selection | pop | role |
|---|---|---|---|
| **hard16** | top-50% truncation | 16 | baseline = the collapsing g1f regime (re-run instrumented) |
| **hard96** | top-50% truncation | 96 | isolates **POP/DRIFT** (hard16→hard96) |
| **soft16** | tournament-k2 + lineage fitness-sharing | 16 | isolates **SELECTION/NICHING at small pop** (hard16→soft16); interaction check |
| **soft96** | tournament-k2 + lineage fitness-sharing | 96 | the full **C1** condition |

- **C1 knob is named honestly = lineage fitness-sharing (niching):** `shared_fitness_i = raw_fitness_i / (count of same-lineage agents in the GEN-START pop)`, exponent 1.0, selected by tournament k=2. 🔴v5.1 **The divisor is the gen-start lineage count (niche occupancy in the selection pool), NOT post-episode living count** — using living count rewards high-mortality lineages (a near-extinct lineage's lone survivor would get inflated shared fitness), the opposite of an anti-collapse mechanism (Gemini). This bundles "gentler selection" + "explicit anti-collapse niching"; **"soft helps" is interpreted as "niching helps,"** not "gentler selection alone helps." (Optional follow-up cell `tournament-no-sharing` only if soft96 opens windows and the decomposition matters — NOT in the frozen battery, to bound cost.)
- **Founder structure pinned per pop = 1 agent per founder** (pop16 → 16 founders; pop96 → 96 founders), so pop changes ONLY size/drift, not founder granularity. (Deviates from v2.1's K=12×8 — chosen for clean pop-isolation; flagged for review.)

## 2. Instruments (logging only — these are the "why collapse" probes)
- **I1 — per-lineage trajectories (per gen):** (a) mean fitness per lineage, (b) living count (SHARE) per lineage = the collapse curve, (c) inverse-Simpson N_eff. → distinguishes **lucky-start** (winner high from gen-0) vs **winner-take-all** (gradual single-lineage fitness climb) vs **drift** (random share walk, arbitrary winner).
- **I2 — gen-0 founder quality (oracle-free):** per-lineage **self-consistency** (round-trip emit→predict exact-recovery accuracy = self-MII at gen 0) + **gen-0 initial fitness**; correlate (Spearman) each against **final lineage share**. High correlation ⇒ **lucky-start** dominates. Also log the gen-0 pairwise code **L2 distance matrix** (descriptive — confirm founders start distinct). *(Replaces the rejected "distance to optimal code".)*
- **I3 — the hard96 control cell IS instrument #3** (the factorial leg that isolates pop vs selection).
- **Carried from the diagnostic, per cell:** CF (cross-founder MII), WF (within-founder ceiling), FLOOR (frozen-mixed, **recomputed at each pop**), lineage-shuffle sanity, paired gate-0 (open/mute/scramble, :169+:269 paired), separate recorded RNG streams.

## 3. Baselines + SESOI (per cell)
- FLOOR = frozen-mixed cross-founder MII **at that cell's pop**; SESOI = 1 seed-SD of that FLOOR, **computed before CF**, written to JSON with `computed_before_CF: true`.
- within-founder MII = ceiling; lineage-shuffle = metric-keys-on-lineage sanity (must rise above true CF).

## 4. Compute (pre-registered) — VECTORIZE MII, no subsample 🔴v5.1
- pop=96 MII ≈ (96/16)² ≈ 36× per-gen cost. The earlier v5 "fixed agent subsample (≤24)" is **REJECTED** — both reviewers showed it breaks the verdict: small lineages get <2 sampled members → no within-lineage pairs → **WF = NaN** in high-diversity gens → the `CF ≥ 0.5·WF` test errors/false-negatives (Gemini, Opus).
- **Fix = vectorize `_mii` to compute the FULL pop×pop matrix as batched tensor ops** (emit = argmax over the symbol axis; predict = argmax over the band axis; exact-match = batched compare). Because emit/predict are pure argmax over stored float32 table values (no float arithmetic), the batched version should be **byte-identical** to the current numpy reference — **REQUIRED: a unit test asserting the vectorized `_mii` matches the loop `_mii` exactly** on a fixed pop before any cell is trusted. Full-matrix MII removes the subsample → no WF=NaN, no unit-set misalignment. GPU (torch, the 5070) is an OPTIONAL further multiplier once vectorized — gated behind the same equivalence test (no nondeterminism).
- Fallback if full-matrix MII is still infeasible at pop=96: sample MII over **pairs** (N intra-lineage + N inter-lineage pairs), guaranteeing ≥2 members per measured lineage — NOT individual subsampling.
- If wall-time still forces it, pop=96 cells may run **n=8** (pop=16 cells n=16); the per-cell seed count is recorded (a logged cap, not a hidden truncation).

## 5. PRE-REGISTERED decision rule
**Per cell — DUAL window gate 🔴v5.1** (de-confounds pop scale; Opus blocker). A gen counts as a coexistence window iff BOTH:
- **(a) MII-measurability (absolute, Gemini):** ≥2 lineages each with ≥3 LIVING agents (post-episode) — guarantees enough living units per lineage to estimate CF/WF.
- **(b) genuine diversity (pop-normalized, Opus):** inverse-Simpson **N_eff ≥ 2.0** over living-lineage shares — rules out "1 dominant lineage + stragglers" passing by absolute count alone (e.g. (82,10,5)→N_eff 1.37 FAILS; (50,40,10)→2.3 PASSES). Without (b), "hard96 opens windows" could be a pure scale artifact (3 agents = 3.1% of 96 vs 18.8% of 16).

A cell "opens windows" iff ≥8/16 (or ≥4/8 if n=8) seeds have ≥2 gens passing (a)+(b). **The collapse-decomposition readout below is judged on this dual-gated count (i.e. on N_eff-normalized diversity), NOT on raw absolute counts.** (Separately, v2.1's stricter median-N_eff≥3 / 25th-pctile≥2.5 remains the bar for declaring C1 a diversity SUCCESS, distinct from the coexistence-window floor here.)

**A vs C (only in cells that open windows):**
- **A (collapse-limited)** iff CF−FLOOR CI excludes 0 AND ≥ SESOI AND CF ≥ 0.5·WF.
- **C (private codes)** iff CF−FLOOR CI includes 0 / < SESOI while WF ≫ FLOOR.
- **PARTIAL** between; lean C (conservative).

**Collapse-mechanism decomposition (window-opening as the readout):**
- hard16 ≈ diagnostic (≈5/16, expected). 
- **hard16→hard96 opens windows ⇒ POP/DRIFT is a main cause.**
- **hard96→soft96 opens further ⇒ SELECTION-HARSHNESS / NICHING is a cause.**
- soft16 vs hard16 ⇒ selection effect at small pop (interaction).
- **No pop96/soft cell opens windows ⇒ deeper cause** → adjudicate with I1/I2:
  - **lucky-start** if I2 gen-0 self-MII / init-fitness predicts the winner (Spearman CI excludes 0);
  - **winner-take-all** if I1 shows a gradual single-lineage fitness climb without a gen-0 head-start;
  - **kin-only self-reinforcement** (residual) if neither and the winner's edge tracks kin-assortment.

## 6. Outcome labels (FROZEN)
`C1_OPENS_WINDOW_A` · `C1_OPENS_WINDOW_C` · `C1_OPENS_WINDOW_PARTIAL` · `NO_WINDOW_POP_DRIFT` · `NO_WINDOW_SELECTION_HARSHNESS` · `NO_WINDOW_DEEPER_{LUCKY|WTA|KIN}` · `INCONCLUSIVE` (power/σ insufficient — report, don't call a negative).

## 7. Fail-forward map (pre-registered — what each outcome unlocks)
- `C1_OPENS_WINDOW_A` → C1 suffices for public language; lock C1, write up, no C2 needed yet.
- `C1_OPENS_WINDOW_C` → C1 maintains diversity but lineages stay private → **C2 / shared grounding** is the next stage (re-scope from the diagnosed cause).
- `NO_WINDOW_POP_DRIFT` → scale pop further / demes; selection wasn't the issue.
- `NO_WINDOW_SELECTION_HARSHNESS` → niching is necessary; tune the sharing operator.
- `NO_WINDOW_DEEPER_*` → the named deeper cause becomes the next probe (changing the listener rule / world structure).

## 8. Implementation steps (then run)
1. **Code-verify:** soft selection (tournament-k2 + `raw / gen-start same_lineage_count`) implemented behind an env/arm flag; g1f hard-truncation is the default-off baseline. 🔴v5.1 implementation invariants: (i) the soft branch must **NOT consume the evolution RNG before the branch decision** (put the env-flag if/elif at the top; draw rng only inside the branch) or the hard cells' RNG stream shifts (Opus); (ii) the sharing divisor uses the **gen-start** lineage count, the window gate uses **post-episode living** — different timestamps by design; (iii) **vectorized `_mii` passes the numpy-equivalence unit test** before any cell runs. Plus: pop-scaled 1-per-founder init; full-matrix MII (no subsample); per-lineage fitness+share+N_eff logging; I2 gen-0 self-MII + init-fitness + Spearman; **no-oracle test passes** (decisions never see truth, esp. I2).
2. Run the 4 cells at the SAME config/seeds; recompute FLOOR + SESOI per cell before CF.
3. Report per-cell window counts → A/C (where decidable) → collapse decomposition → I1/I2 read → fail-forward label.

## 9. Naming discipline (carried)
This is the **C1 INTERVENTION + COLLAPSE-CAUSE probe**, distinct from the finished kin-only DIAGNOSTIC and from the deferred C2. Frozen pre-registration applies once locked; renaming/redefining a gate later = protocol violation (the W4 governance lesson).
