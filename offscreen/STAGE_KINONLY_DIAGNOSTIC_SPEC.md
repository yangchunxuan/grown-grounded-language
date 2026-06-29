# STAGE: WHY IS g1f KIN-ONLY? — DIAGNOSTIC pre-registration (runs BEFORE any intervention)

**Type: DIAGNOSTIC, not intervention.** We do NOT add C1/C2 or any mechanism. We instrument the *existing* g1f dynamics and measure WHY the co-evolved channel stays kin-lineage-only. The result tells us which barrier is real, so the later public-language intervention is one targeted change, not a confounded two-knob shotgun. This stage answers the owner's question directly: *why only within kin?*

**Three candidate causes (pre-stated):**
- **(a) DEMOGRAPHIC** — the population collapses to ~1 founder, so "kin-only" is largely a tautology (no non-kin pairs remain to align).
- **(b) SELECTION-RULE** — kin-only listening means cross-lineage decoding is never under selection; lineages COULD align (codes partially compatible) but were never pushed to.
- **(c) REPRESENTATIONAL-INCOMPATIBLE** — even when lineages coexist they grow arbitrary private codes with no shared anchor; they CANNOT align without a shared-grounding signal. (If true, neither C1 nor C2 suffices.)

> Carry the reviewers' lesson: cross-founder MII has a large **non-language floor** (g1f comm-blind 0.127 vs frozen 0.0016 — shared architecture/world/init alone). Every "cross-founder MII > 0" below is measured **above** the non-language baselines, never raw.

## 0. Instrumentation-only verification (no mechanism change; code-verify before run)
- Dynamics identical to g1f formal (`rtc_g1f_coevolve.py`); the ONLY additions are logging. Confirm no selection/listener/repro change.
- Implement & log **per generation**: founder composition (alive founders + shares + inverse-Simpson N_eff); **cross-founder MII** (true non-kin pairs, V0b-style); **within-founder MII**.
- Implement the **static cross-decode probe** (M2, §2): listener of lineage A decoding speaker of lineage B.
- Record full config (env/seeds/formal) in the JSON.

## 1. Measurements
- **M1 — cross-founder MII trajectory, conditioned on coexistence.** For each seed, over gens, log cross-founder MII restricted to gens that satisfy the **coexistence criterion** (§3). Also log within-founder MII and N_eff trajectories alongside.
- **M2 — static cross-decode probe.** At the **last coexisting gen** (latest pre-collapse point with ≥2 lineages), measure: cross-lineage decode accuracy `CD` (A's listener on B's speaker, both directions, averaged) vs within-lineage decode `WD` vs chance.

## 2. Non-language baselines (same env/seeds/formal; reused from the reviewers' fix)
- **lineage-shuffle**: relabel founder-ids before computing cross-founder MII → the non-language floor for M1.
- **frozen-mixed**: multi-lineage frozen-random population → the non-language floor for cross-decode `CD`.
- A signal counts only if it clears `max{shuffle, frozen-mixed}`.

## 3. FROZEN values (LOCKED — anti-post-hoc)
- mode = **formal**; n = **16 seeds** (diagnostic of a *pattern*, not a powered margin test; enough to see the trajectory shape + the probe).
- **coexistence criterion**: a gen counts as "coexisting" iff **≥2 founders each hold ≥15% of the living population**.
- **M2 checkpoint** = the last gen (per seed) meeting the coexistence criterion.
- **chance** = the g1f MII metric's random-decode rate (read from the harness `chance` field, e.g. 1/|referents|).
- **CF_MII(coexist)** = mean over coexisting gens of (cross-founder MII − `max{shuffle, frozen-mixed}`), with a bootstrap 95% CI over seeds.

## 4. PRE-REGISTERED decision rule (numerical; trajectory + probe → cause)
Let CF = CF_MII(coexist) [baseline-subtracted], with its 95% CI; CD = cross-decode accuracy with CI; ρ = within-seed correlation of cross-founder MII vs N_eff over gens.
- **CAUSE_(a)_DEMOGRAPHIC** iff CF CI **excludes 0 AND ≥ 0.04** (real cross-founder alignment exists while lineages coexist) **AND** it **declines with collapse** (ρ > 0 i.e. MII tracks N_eff down, or final-coexist CF < 0.5 × peak CF). → kin-only ≈ collapse; **C1 (diversity) is the targeted fix.**
- **CAUSE_(c)_INCOMPATIBLE** iff CF CI **includes 0 / < 0.04** (no cross-founder alignment even at coexistence) **AND** CD CI **includes chance** (codes don't cross-decode). → arbitrary private codes; **C1/C2 insufficient — needs a shared-grounding mechanism.**
- **CAUSE_(b)_SELECTION-RULE (latent-compatible)** iff CF CI includes 0 / < 0.04 **BUT** CD CI **excludes chance** (codes are partially cross-decodable but alignment was never selected). → **C2 (cross-lineage selection pressure) is the targeted lever**; a minimal C2-only probe would confirm.
- **INCONCLUSIVE_NO_WINDOW** iff **< 3 gens across seeds meet the coexistence criterion** (collapse too fast to observe coexisting lineages). → we cannot diagnose (b)/(c) without first maintaining diversity; **then C1 is a diagnostic ENABLER (open the window), not the intervention** — re-run this diagnostic with C1 on, still NO C2.

(If signals are mixed across seeds, report the per-seed distribution; do NOT force a single label.)

## 5. Outcomes → what each implies for the (shelved) intervention spec
- **(a)** → the public-language intervention reduces to **C1 only** (maintain diversity); C2 may be unnecessary. Big simplification.
- **(b)** → intervention is **C2 only** (cross-lineage selection); C1 only needed to keep a window.
- **(c)** → the intervention spec as written (C1+C2) **cannot work**; the real frontier is a shared-grounding signal — re-scope before building anything.
- **INCONCLUSIVE_NO_WINDOW** → C1-as-enabler first, then re-diagnose.

## 6. Steps
1. Pass §0 (instrument g1f, no mechanism change; implement cross-founder MII + cross-decode probe + baselines; record config).
2. Run formal n=16 (instrumented g1f) + the lineage-shuffle / frozen-mixed baselines at the SAME config.
3. Apply §4 decision rule; report trajectory plots + the probe + the per-seed distribution + a written read of which cause.
4. Only THEN pick/trim the intervention (the shelved `STAGE_PUBLIC_LANGUAGE_SPEC.md`) to target the diagnosed cause.

## 7. Why this is the right order (for the record)
Diagnose the barrier before engineering around it: an intervention-first run is confounded (two knobs; a (c)-cause failure is unattributable) and uninformative even on success (you'd make it happen without knowing why it was blocked). This diagnostic is cheaper (instrumented re-run, no new mechanism) and de-risks every downstream choice.
