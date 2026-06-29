# STAGE: WHY IS g1f KIN-ONLY? — DIAGNOSTIC pre-registration **v2**

**v2 changelog.** v1 got a code-grounded red-team (read `rtc_g1f_coevolve.py`): verdict DO_NOT_LOCK. v2 closes all converged fixes: lock the arm, add cause (d), fix the (c) null, operationalize every threshold, and do a FREE retrospective first. Type unchanged: **DIAGNOSTIC, no mechanism change** — instrument g1f to learn WHY its co-evolved channel is kin-lineage-only, so the later intervention targets the real cause.

**Candidate causes (now FOUR):**
- **(a) DEMOGRAPHIC** — population collapses to ~1 founder; "kin-only" is largely a tautology (no non-kin pairs left).
- **(b) SELECTION-RULE** — kin-only listening means cross-lineage decoding is never selected; codes are partially compatible but unaligned.
- **(c) REPRESENTATIONAL-INCOMPATIBLE** — coexisting lineages grow arbitrary private codes with no shared anchor; cannot align without shared grounding.
- **(d) FITNESS-IRRELEVANCE** 🔴v2 — the world may not REQUIRE cross-lineage decoding to survive at all (self-foraging suffices); then (a)/(b)/(c) are all moot and the diagnostic must NOT fabricate a "barrier". Tested first (§4 gate-0).

> Non-language floor (from g1f data): comm-blind MII = 0.127 vs frozen = 0.0016 (≈80× chance) — shared architecture/world/init alone. Every "cross-founder signal" below is measured ABOVE the right empirical baseline, never above chance.

## 0. SCOPE LOCK + instrumentation-only (code-verify before run) 🔴v2
- **ARM IS LOCKED to `shared_weights_kin`.** Reason: it is the ONLY arm with cross-generation lineage propagation (`rtc_g1f_coevolve.py:247` `preserve_lineage=True`); all other arms reset `lineage` to `child_seed` each reproduction (`:100`), so "founder" is undefined for them. All measurements, baselines, and the probe run ONLY on this arm; record the scope limit in the JSON.
- **Cross-founder MII filter must key on `.lineage`, not agent index.** Blind-test: feed a pop with all `lineage=0` → the function must return NaN/skip (not 0, not all-pairs mean).
- **lineage-shuffle timing**: randomly permute `pop[i].lineage` labels BEFORE computing the MII matrix (NOT a post-hoc reindex of (i,j) pairs).
- **reward-chain sanity (V0a-lite)**: confirm in code + at run that open-mode survival > mute-mode survival on this arm (messages are load-bearing at all); `_decoded_score`→`pick`→`eat` (`:192-198`). If open ≈ mute → see cause (d).
- Dynamics, selection, listener, repro UNCHANGED; only logging added (no RNG-order change). Record full config (env/seeds/formal) in the JSON.

## 1. Measurements
- **M1 — cross-founder MII trajectory** over gens, restricted to coexisting gens (§3), on `shared_weights_kin`; log within-founder MII + inverse-Simpson N_eff alongside.
- **M2 — cross-decode `CD` TRAJECTORY** (not just final gen 🔴v2): over coexisting gens, lineage-A listener decoding lineage-B speaker (both directions), vs within-lineage `WD`.
- **M3 — stratified survival (cause d) 🔴v2**: per coexisting gen, survival rate of agents whose `pick` follows decoded messages vs agents that effectively self-forage (argmax not tracking the decoded score). Also the open-vs-mute survival gap.

## 2. Non-language baselines (same arm/env/seeds/formal)
- **lineage-shuffle** → non-language floor for M1 (cross-founder MII).
- **frozen-mixed** = frozen-random agents drawn from **DIFFERENT seeds** (genuinely unrelated) 🔴v2 → non-language floor for **CD** (this is the null cause-(c) uses, NOT chance).
- A signal counts only if it clears its baseline by the stated SESOI.

## 3. FROZEN values (LOCKED)
- arm = **shared_weights_kin**; mode = **formal**; n = **16 seeds**.
- **coexistence criterion**: a gen counts iff **≥2 founders each have ≥3 living agents** (absolute count, pop=16) 🔴v2.
- **peak** = max cross-founder MII over a seed's coexisting gens, then mean across seeds 🔴v2.
- **CF** = mean over coexisting gens of (cross-founder MII − max{lineage-shuffle, frozen-mixed}), bootstrap 95% CI over seeds.
- chance = 1/625 = 0.0016 (verified). **CD null = frozen-mixed CD** (not chance) 🔴v2.
- Δ_min = 0.04 for CF; **CD SESOI = 0.02 over frozen-mixed** 🔴v2. (Both first calibrated by the §6 retrospective; if unchanged, flagged "untested anchor, g1f within-arm scale".)
- **INCONCLUSIVE_NO_WINDOW** iff **fewer than 8 of 16 seeds have ≥2 coexisting gens** 🔴v2.

## 4. PRE-REGISTERED decision rule (numerical)
**Gate 0 (cause d, runs first):** if open-mode survival ≤ mute-mode survival on this arm, OR self-forage survival ≥ message-following survival in coexisting gens → **FITNESS_IRRELEVANCE_WARNING**: the world does not require message content; (a)/(b)/(c) are not interpretable. Stop and report.

Else classify (CF baseline-subtracted; CD vs frozen-mixed):
- **(a) DEMOGRAPHIC** iff CF CI excludes 0 AND CF ≥ 0.04 AND it declines with collapse (final-coexist CF < 0.5 × peak). → kin-only ≈ collapse; intervention reduces toward **C1-only**. *Interpretation caveat 🔴v2: a positive (a) means C1 ENABLES cross-founder alignment under coexistence; it does NOT distinguish "alignment driven by cross-lineage communication selection" from "alignment driven by shared world-pressure on independently-evolving lineages." The latter is still C1-fixable here but may not transfer to worlds with different grounding.*
- **(b) SELECTION-RULE** iff CF CI includes 0 / < 0.04 BUT CD exceeds frozen-mixed by ≥ 0.02 (codes partially compatible, never selected to align). → **C2-only** lever; a minimal C2-only probe confirms.
- **(c) INCOMPATIBLE** iff CF < 0.04 AND CD does NOT exceed frozen-mixed by ≥0.02 (no cross-decodability above the non-language floor). → C1/C2 insufficient; needs **shared-grounding** — re-scope before building.
- **INCONCLUSIVE_NO_WINDOW** (per §3): C1 as a diagnostic ENABLER (open a window), re-diagnose with C1 on, still NO C2.
- **Per-seed aggregation 🔴v2**: report the per-seed label distribution; the project default for a split is the more conservative cause (c ≻ b ≻ a; demand the stronger intervention) unless a clear majority (≥12/16) favors one.

## 5. Outcomes → implication for the shelved intervention
- (a) → C1-only; (b) → C2-only; (c) → C1/C2 insufficient, need grounding (re-scope); (d) → the world itself doesn't require cross-lineage content (deepest finding — the public-language question is ill-posed in this world); INCONCLUSIVE → C1-enabler then re-diagnose.

## 6. Steps — RETROSPECTIVE FIRST 💡v2 (may avoid a new run entirely)
0. **Free retrospective**: the committed g1f `shared_weights_kin` runs already store row-level data (`rtc_g1f_coevolve.py:432`). FIRST extract per-agent `.lineage` + the MII matrix from the existing formal-48 artifact and compute cross-founder MII + the coexistence-window distribution + a calibration estimate of CF's natural scale (sets Δ_min). If the existing data suffices, the diagnostic may be answerable with NO new run.
1. If a new run is needed: pass §0 (lock arm, implement `.lineage`-keyed cross-founder MII + CD trajectory + M3 + baselines; blind-tests; config recorded).
2. Run formal n=16 on `shared_weights_kin` + lineage-shuffle + frozen-mixed at the SAME config.
3. Report: per-seed coexistence-window count (sanity) FIRST; then Gate 0; then the §4 classification + trajectory plots + the probe + per-seed distribution + a written read.
4. Only THEN pick/trim the intervention to target the diagnosed cause.

## 7. Implementation-verify (the red-team's "cannot tell from files" list — confirm in code before claiming)
- cross-founder MII keys on `.lineage` (blind-test all-same-lineage → NaN/skip).
- lineage-shuffle permutes `.lineage` before MII (not post-hoc pair reindex).
- `_speaker_for` after collapse (`:161-165`): singleton lineage → listens to self → that gen excluded from coexistence (NaN, not counted).
- MII is an offline metric (`:219`, uses `speaker.emit` directly, NOT `_speaker_for`) → confirm the alternation in `_speaker_for` does not contaminate the measurement; record this independence in the JSON.
- report each seed's coexistence-window length.
- same-config / formal-not-pilot enforced and recorded.
