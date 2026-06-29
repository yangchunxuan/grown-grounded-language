# STAGE: WHY IS g1f KIN-ONLY? — DIAGNOSTIC pre-registration **v4**

**v4 changelog.** v3 got a THIRD pair of code-grounded reviews (Codex + Gemini), independently converging on one blocker: the **comm-blind (random-fitness) cross-founder null is the WRONG null** — it removes BOTH communication-selection AND world-survival-selection, so "survival beats comm-blind-CF" would falsely label shared-world convergence (e) as (a); and comm-blind drift-collapses/dies under the toxic world, NaN-ing the baseline. Deeper: in g1f, cross-lineage communication is **never selected** (kin-only `_speaker_for`) and survival is communication-mediated, so **no "world-selected but communication-free" null exists** → "communication-selection vs world-convergence" is **ill-posed in g1f** and cannot be settled by this diagnostic; it is deferred to the C2 intervention. v4 therefore DROPS the comm-blind null and the comm-selection claim, and asks the narrower, well-posed, C1-actionable question below.

**Narrowed question (v4):**
> At generations where ≥2 founder lineages coexist, are non-kin lineages **mutually intelligible** (cross-founder MII near the within-founder ceiling, well above the architecture floor) — so kin-only is a **collapse/demographic** artifact that maintaining diversity (C1) would lift — OR have lineages diverged into **private incompatible codes** (cross-founder MII at the floor) — so a shared-grounding mechanism is needed?

**Causes (reframed, honest):**
- **(A) COLLAPSE-LIMITED INTELLIGIBILITY** — coexisting non-kin lineages ARE mutually intelligible above the floor, and it declines with collapse. → C1 (maintain diversity) preserves cross-lineage intelligibility. *Covers both "byproduct of within-kin comm selection" and "shared-world convergence"; the diagnostic does NOT claim cross-lineage communication SELECTION (g1f never selects it) — that is the C2 intervention's question.*
- **(C) PRIVATE CODES** — cross-founder MII ≈ architecture floor ≪ within-founder MII. → shared grounding needed; C1/C2 insufficient.
- **(D) FITNESS-IRRELEVANCE** (gate-0) — message content not load-bearing at all → (A)/(C) moot.
- **(B) SELECTION-RULE** is EXPLICITLY NOT decidable by this diagnostic (kin-only listening never selects cross-lineage). Deferred to a C2-only probe. (Acknowledged, not tested here.)

## 0. SCOPE LOCK + instrumentation-only (code-verify before run)
- **Arm = `shared_weights_kin`** — only arm with inherited founder-lineage reproduction (`:247`; others reset `child.lineage=seed` `:96`; survivors deepcopy-keep lineage `:240`).
- **Per gen log (no dynamics/RNG change):** MII **matrix** + per-agent **`.lineage`** + per-agent **ALIVE** (`[st.alive for st in states]`; `_run_episode` returns only aggregate today, `:202`).
- cross-founder MII keys on `.lineage` (blind-test all-`lineage=0` → NaN/skip). within-founder MII = same-lineage off-diagonal.
- **Separate RNG streams, all recorded in JSON** (Codex+Gemini): evolution/reproduction RNG; lineage-shuffle RNG (snapshot-local); gate-0 message-mode RNG. No stream may shift another.

## 1. Measurements (shared_weights_kin)
- **M1 — cross-founder MII vs within-founder MII trajectory** over coexisting gens (+ inverse-Simpson N_eff).
- **M2 — cross-decode `CD` trajectory** (lineage-A listener on lineage-B speaker, both directions) over coexisting gens.
- **M3 — gate-0 PAIRED content test** 🔴v4: open vs mute vs random-token survival, run on the **SAME population, SAME world/post/metabolic seed, varying ONLY message generation** (do NOT reuse the mode-name-length seed scheme at `:269`, which would confound). random-token = `scramble` (already iid symbols, `rtc_language.py:94`) — documented as the alias, no new mode-name seed.

## 2. Baselines (same arm/env/seeds/formal; NO comm-blind null 🔴v4)
- **within-founder MII** = the CEILING (how well kin decode kin — the g1f kin-language strength).
- **frozen-mixed** = the architecture FLOOR: frozen-random agents from deterministically disjoint init seeds (genuinely unrelated, no evolution).
- **lineage-shuffle** (separate RNG) = sanity that the metric keys on lineage structure.
- (comm-blind dropped: it strips world-selection and NaNs out — wrong null for this question.)

## 3. FROZEN RULES (magnitudes calibrated from the floor, not pre-frozen)
- arm=shared_weights_kin; mode=formal; n=16 seeds.
- coexistence: a gen counts iff **≥2 founders each have ≥3 LIVING agents** (per-agent alive log).
- **CF** = mean over coexisting gens of cross-founder MII; **WF** = within-founder MII; **FLOOR** = frozen-mixed MII; bootstrap 95% CIs over seeds.
- SESOI = **1 seed-SD of FLOOR** (frozen-mixed), computed from the floor BEFORE looking at CF. Report raw + standardized margins.
- peak = max CF over a seed's coexisting gens, mean across seeds.
- INCONCLUSIVE_NO_WINDOW iff **< 8 of 16 seeds have ≥2 coexisting gens**.

## 4. PRE-REGISTERED decision rule
**Gate-0 (cause D):** if open-survival ≤ mute-survival OR open-survival CI overlaps random-token-survival → **FITNESS_IRRELEVANCE_WARNING**; stop.

Else (CF, WF, FLOOR over coexisting gens):
- **(A) COLLAPSE-LIMITED** iff **CF − FLOOR** CI excludes 0 and ≥ SESOI **AND** CF is "near" WF (CF ≥ 0.5·WF) **AND** CF declines with collapse (final-coexist CF < 0.5·peak). → coexisting non-kin are mutually intelligible; kin-only is demographic → **C1**.
- **(C) PRIVATE CODES** iff **CF − FLOOR** CI includes 0 / < SESOI (cross-founder at the architecture floor) while WF ≫ FLOOR. → lineages diverged into private codes → **shared grounding**.
- **PARTIAL** iff CF is between FLOOR+SESOI and 0.5·WF → report as partial intelligibility; lean (C) for intervention scoping (conservative).
- **INCONCLUSIVE_NO_WINDOW** → C1 as a window-opening enabler, re-diagnose.
- Per-seed: report the distribution; split default = conservative (C ≻ partial ≻ A) unless ≥12/16 agree.

## 5. Outcomes → intervention implication
- (A) → C1-only (maintain diversity); cross-lineage intelligibility is already latent, just collapse-truncated. **Caveat: this does NOT establish cross-lineage communication SELECTION — only that coexisting lineages are mutually intelligible; whether selection can sharpen/sustain it is the C2 question.**
- (C) → C1/C2 insufficient; need shared grounding — re-scope before building.
- (D) → world doesn't require content; question ill-posed here.
- (B, deferred) → not decidable by this diagnostic; a minimal C2-only probe is the only way.
- INCONCLUSIVE → C1-enabler then re-diagnose.

## 6. Steps — NO retrospective (code-refuted); a new instrumented run is required
1. Pass §0: instrument shared_weights_kin (matrix + lineage + per-agent alive; `.lineage`-keyed CF/WF; separate RNG streams; random-token=scramble paired gate-0); blind-tests; config recorded.
2. Run formal n=16 + frozen-mixed + lineage-shuffle at the SAME config; calibrate SESOI from FLOOR's seed-SD BEFORE looking at CF.
3. Report per-seed coexistence-window counts (sanity) → gate-0 → §4 classification + CF/WF/FLOOR trajectories + per-seed distribution + a written read.
4. Then pick/trim the intervention to the diagnosed cause.

## 7. Implementation-verify (converged "cannot tell from files")
- artifacts lack lineage/matrix/per-agent state → MUST instrument; no retrospective (Codex+Gemini confirmed).
- `.lineage`-keyed CF/WF (blind-test all-same-lineage → NaN/skip).
- gate-0 paired on identical world/post/metabolic seed, only message mode differs (NOT the `:269` mode-name seed).
- separate RNG streams (evolution / shuffle / message-mode) — none shifts another; recorded.
- per-agent ALIVE added to `_run_episode` return.
- after collapse, singleton-lineage gen → excluded from coexistence (NaN).
- MII is offline (`:219`, `speaker.emit`, not `_speaker_for`) → confirm `_speaker_for` alternation doesn't contaminate it; record.
- EMPIRICAL (only the run resolves, NOT blockers): enough coexistence windows at n=16; whether CF beats FLOOR; whether CF approaches WF; which cause wins.
