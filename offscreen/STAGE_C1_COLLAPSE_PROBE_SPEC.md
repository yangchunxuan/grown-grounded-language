# STAGE: C1 COLLAPSE PROBE — intervention + collapse-cause diagnosis (Path B), pre-registration **v5 — DRAFT (not locked)**

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
- Beyond the new selection arms, all additions are **logging only** (no dynamics change). Treatment and every control share env/seed/formal/instrumentation; the JSON records it (the g1f same-config lesson).

## 1. The 2×2 factorial (intervention + its own controls)
**selection ∈ {hard, soft} × pop ∈ {16, 96}** → 4 cells, ALL re-run at the SAME config/seeds/instrumentation (do NOT reuse the old hard+16 g1f verdict — different code path, no instrumentation).

| cell | selection | pop | role |
|---|---|---|---|
| **hard16** | top-50% truncation | 16 | baseline = the collapsing g1f regime (re-run instrumented) |
| **hard96** | top-50% truncation | 96 | isolates **POP/DRIFT** (hard16→hard96) |
| **soft16** | tournament-k2 + lineage fitness-sharing | 16 | isolates **SELECTION/NICHING at small pop** (hard16→soft16); interaction check |
| **soft96** | tournament-k2 + lineage fitness-sharing | 96 | the full **C1** condition |

- **C1 knob is named honestly = lineage fitness-sharing (niching):** `shared_fitness_i = raw_fitness_i / (count of living same-lineage agents)`, exponent 1.0, selected by tournament k=2. This bundles "gentler selection" + "explicit anti-collapse niching"; **"soft helps" is interpreted as "niching helps,"** not "gentler selection alone helps." (Optional follow-up cell `tournament-no-sharing` only if soft96 opens windows and the decomposition matters — NOT in the frozen battery, to bound cost.)
- **Founder structure pinned per pop = 1 agent per founder** (pop16 → 16 founders; pop96 → 96 founders), so pop changes ONLY size/drift, not founder granularity. (Deviates from v2.1's K=12×8 — chosen for clean pop-isolation; flagged for review.)

## 2. Instruments (logging only — these are the "why collapse" probes)
- **I1 — per-lineage trajectories (per gen):** (a) mean fitness per lineage, (b) living count (SHARE) per lineage = the collapse curve, (c) inverse-Simpson N_eff. → distinguishes **lucky-start** (winner high from gen-0) vs **winner-take-all** (gradual single-lineage fitness climb) vs **drift** (random share walk, arbitrary winner).
- **I2 — gen-0 founder quality (oracle-free):** per-lineage **self-consistency** (round-trip emit→predict exact-recovery accuracy = self-MII at gen 0) + **gen-0 initial fitness**; correlate (Spearman) each against **final lineage share**. High correlation ⇒ **lucky-start** dominates. Also log the gen-0 pairwise code **L2 distance matrix** (descriptive — confirm founders start distinct). *(Replaces the rejected "distance to optimal code".)*
- **I3 — the hard96 control cell IS instrument #3** (the factorial leg that isolates pop vs selection).
- **Carried from the diagnostic, per cell:** CF (cross-founder MII), WF (within-founder ceiling), FLOOR (frozen-mixed, **recomputed at each pop**), lineage-shuffle sanity, paired gate-0 (open/mute/scramble, :169+:269 paired), separate recorded RNG streams.

## 3. Baselines + SESOI (per cell)
- FLOOR = frozen-mixed cross-founder MII **at that cell's pop**; SESOI = 1 seed-SD of that FLOOR, **computed before CF**, written to JSON with `computed_before_CF: true`.
- within-founder MII = ceiling; lineage-shuffle = metric-keys-on-lineage sanity (must rise above true CF).

## 4. Compute cap (pre-registered, logged — NOT silent)
- pop=96 MII ≈ (96/16)² ≈ 36× per-gen cost. **Mitigation: MII computed on a deterministic fixed agent SUBSAMPLE** — up to `S=24` agents, sampled to cover all living lineages proportionally (seeded, recorded) — matrix stays ~24×24; MII_SAMPLE referents unchanged. The subsample size + selection rule are recorded in the JSON. If still too slow, pop=96 cells may run **n=8** (pop=16 cells n=16); the per-cell seed count is recorded (a logged cap, not a hidden truncation).

## 5. PRE-REGISTERED decision rule
**Per cell — window gate:** coexistence gen = ≥2 lineages each with ≥3 LIVING agents (post-episode); a cell "opens windows" iff ≥8/16 (or ≥4/8 if n=8) seeds have ≥2 coexisting gens.

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
1. **Code-verify:** soft selection (tournament-k2 + `raw/same_lineage_count`) implemented behind an env/arm flag; g1f hard-truncation is the default-off baseline; pop-scaled 1-per-founder init; deterministic MII subsample; per-lineage fitness+share logging; I2 gen-0 self-MII + init-fitness + correlation; **no-oracle test passes** (decisions never see truth, esp. I2).
2. Run the 4 cells at the SAME config/seeds; recompute FLOOR + SESOI per cell before CF.
3. Report per-cell window counts → A/C (where decidable) → collapse decomposition → I1/I2 read → fail-forward label.

## 9. Naming discipline (carried)
This is the **C1 INTERVENTION + COLLAPSE-CAUSE probe**, distinct from the finished kin-only DIAGNOSTIC and from the deferred C2. Frozen pre-registration applies once locked; renaming/redefining a gate later = protocol violation (the W4 governance lesson).
