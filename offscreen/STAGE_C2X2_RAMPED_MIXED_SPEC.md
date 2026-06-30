# STAGE: C2X2 — RAMPED MIXED NON-KIN SCAFFOLD — pre-registration **LOCKED**

**LOCK note.** Three independent code-grounded reviews of this merged double-PRIMARY spec (Opus 4.7,
Gemini, DeepSeek) all returned LOCK, no blocker — including Gemini (which had proposed stationary) and on
the version that put both scaffolds head-to-head. All confirmed: no-oracle clean (routing reads only
(seed,gen,round,i,j)+lineage labels), the 4-condition viability guard provably catches the C2X mislabel
(checked against C2X's real numbers), the non-kin-only final eval closes the kin-survival loophole, and
the inherited discipline (same-config, dual gate, SESOI-before-CF, vectorized MII + byte-stability) is
carried. Applied polish (all non-blocking): pinned p_nonkin to a deterministic hash (§2); wrote the
STAT025 viability guard explicitly (§5); added the CF≥0.25·WF rationale (§6); added the matched-exposure
STAT037 follow-up note (§9); added shared-baselines + byte-stability(p=0==kin) + satellite-teacher
red-team notes (§8). LOCKED for implementation.

**Provenance.** C2X (forced 100% non-kin listening, cold) suffered a **viability crash** (mean alive
0.0455 vs C1_KIN_ONLY 0.2718) — confirmed by 3 independent code-grounded investigations (Codex, Gemini,
DeepSeek): not a clean negative, convergence UNANSWERED. Two scaffold designs were proposed: stationary
mixed (Gemini, fixed 75/25) and ramped mixed (Codex, p_nonkin 0→0.75). **Claude adjudicated → ramped**,
because (1) a fixed low non-kin fraction risks an UNDER-POWERED false negative (agents survive on the kin
channel and ignore the weak non-kin penalty — the project's recurring failure mode; a viability guard
catches crashes but not under-powering); (2) the ramp gives BOTH a viable start (warm-up at 0% non-kin)
AND strong final pressure (0.75); (3) Codex's **non-kin-only final evaluation** (test the evolved pop under
100% non-kin) is the decisive feature that proves any emergent code is genuinely cross-lineage, not
kin-survival in disguise — closing the exact loophole stationary mix is most exposed to. This file is
Claude's canonical version of Codex's ramped design + Gemini's absolute viability floor, AND it keeps
Gemini's stationary-25% as a matched PRIMARY comparison arm (§3) so the run settles ramp-vs-stationary
with DATA, not adjudication. To be reviewed code-grounded before lock.

## 0. Question
After C1 (kin-only = private codes, A refuted) and C2X (cold-start forced non-kin = non-viable), the
narrow unresolved question: **if kin communication keeps the population alive while non-kin listening
pressure is gradually turned on, can survival selection move the tied UnifiedIO tables toward a shared
cross-founder code?** Success ≠ survival; success = cross-founder MII above matched baselines + content-
load-bearing under PURE non-kin evaluation + diversity/anti-painted guards.

## 1. Frozen configuration
- random UnifiedIO weights, NO pretrained/borrowed weights; same C1 soft96 selection + mutation.
- `POP=96`; `GENS=48`; `N=16` formal seeds for a NEGATIVE verdict; **if only N=8 is run, verdict may be
  POSITIVE or INCONCLUSIVE only** (never a scoped negative).
- vectorized full pop×pop MII (`_mii_matrix_fast`) + the numpy-equivalence test (incl. deliberate tie) retained.
- toxic-death + RTC/G1F constants inherited unchanged from g1f/C1.
- ALL arms share seeds / pop / gens / mutation / selection / message schedule unless listed in §3–§4.

## 2. Ramped mixed speaker rule (FROZEN schedule)
For each listener decision, a deterministic schedule (independent of reward / decode success / content /
field truth / lineage fitness) decides whether the speaker must be kin or non-kin. `p_nonkin(gen)`:
- gens 0–11: **0.00** (warm-up: kin keeps the population viable, like C1);
- gens 12–36: linear ramp **0.00 → 0.75** inclusive;
- gens 37–47: **0.75** (strong, non-ignorable final pressure).

For `(seed, gen, round, listener_i, post_i)`, draw non-kin with prob `p_nonkin(gen)` via a **deterministic
hash** (DeepSeek: pin ONE mechanism — chosen = hash, fully reproducible, consumes NO RNG so it cannot
perturb the evolution stream): `frac = ((seed*2654435761 + gen*40503 + round*12345 + listener_i*777 +
post_i*31) % 1000003) / 1000003.0`; non-kin iff `frac < p_nonkin(gen)`. If non-kin: balanced round-robin over eligible
non-self lineages then members (= the locked `cross_lineage_balanced`). If kin: original same-lineage rule.
If the requested category is empty: fall back to the other category and **record the fallback count**; if
both empty: mute. The rule may read only `(seed,gen,round,i,j)` + current lineage labels for routing —
never reward, decode success, true edibility, world patches, target codes, or founder-id-as-policy-input.

## 3. Arms
**Primary:** `C2X2_RAMP_OPEN` (ramped rule, real msgs, survival fitness) · `C2X2_STAT025_OPEN`
(**stationary mixed: fixed 25% non-kin / 75% kin throughout**, real msgs, survival fitness — Gemini's
design, included as a matched comparison so the run SETTLES ramp-vs-stationary empirically instead of by
adjudication) · `C1_KIN_ONLY` (kin, real, survival) · `C2X2_RAMP_COMMBLIND` (ramped, real, RANDOM fitness)
· `C2X2_RAMP_RANDOM_TOK` (ramped, iid tokens) · `C2X2_RAMP_SCRAMBLE` (ramped, permuted-real) ·
`C2X2_RAMP_MUTE` (ramped, mute).
The viability guard, non-kin-only final eval, success gate, and labels (§5–§6) are evaluated SEPARATELY
for each treatment (`C2X2_RAMP_OPEN` and `C2X2_STAT025_OPEN`), against the SAME shared baselines; report
both. Comparison readout: does either reach `C2X2_PUBLIC_CODE_EMERGES`? does ramp beat stationary on
CF_margin / viability / final-eval (i.e., is the schedule load-bearing)?
**Diagnostic (not subtracted from CF):** `C2X_COLD100_OPEN` (100% non-kin from gen0 — reproduces the C2X
crash as a contrast) · `FROZEN_MIXED_FLOOR` (frozen unrelated pop96 = CF floor) · `LINEAGE_SHUFFLE` (CF
lineage-invariance diagnostic).

## 4. Metrics (per seed)
mean alive (across gens + final-gen); paired open−mute / open−scramble / open−random-token survival via
`_run_episode(rng=)`; CF, WF, CF/WF, CF_margin vs baseline_max; full lineage×lineage MII matrix; dual
coexistence windows (≥2 lineages each ≥3 living AND inverse-Simpson `N_eff≥2.0`); final living-lineage
N_eff, max share, speaker-source concentration; table-L2 ratio vs gen0; kin/non-kin fallback counts;
**non-kin-only final evaluation** (final pop under 100% non-kin routing: open/mute/scramble/random-token
paired episodes). `baseline_max = max(FROZEN_MIXED_FLOOR, C1_KIN_ONLY_CF, C2X2_RAMP_COMMBLIND_CF,
C2X2_RAMP_RANDOM_TOK_CF, C2X2_RAMP_SCRAMBLE_CF)`. SESOI=0.04, FLOOR + SESOI computed before CF.

## 5. Viability guard (BEFORE interpreting any CF failure)
A CF failure counts as "private codes persist" ONLY if the scaffold actually avoided the C2X crash:
- `C2X2_RAMP_OPEN` mean alive ≥ **0.5 ×** `C1_KIN_ONLY` mean alive; **AND** ≥ **0.15 absolute** (Gemini
  belt-and-suspenders, in case C1 itself is low); **AND**
- paired `C2X2_RAMP_OPEN − C2X_COLD100_OPEN` mean-alive CI lower > 0.05; **AND**
- `C2X2_RAMP_OPEN` beats `C2X2_RAMP_MUTE` and `C2X2_RAMP_SCRAMBLE` on survival, paired CI lower > 0.
**The same 4-condition viability guard is applied IDENTICALLY to `C2X2_STAT025_OPEN`** (substitute
STAT025 for RAMP throughout, against the SAME baselines). If these fail (for a given treatment) →
`C2X2_DESIGN_FAILURE_VIABILITY_CRASH` for that treatment (NOT a public-language negative).

## 6. Success gate (FROZEN) — `C2X2_PUBLIC_CODE_EMERGES` iff ALL:
- viability guard passes;
- dual coexistence window in ≥6/8 seeds (n=8) or ≥12/16 (n=16);
- `CF_margin_vs_baseline_max` bootstrap 95% CI lower > 0 AND point ≥ 0.04;
- `CF_OPEN ≥ 0.25·WF_OPEN` (relaxed from C1/C2X's 0.5·WF: C2X2 is the first test of whether CF can rise
  AT ALL above C2X's ~0.014 floor; substantial partial closure toward the kin ceiling is already
  meaningful and worth banking — not a goalpost move, set a priori here);
- **non-kin-only final eval**: open survival beats mute, scramble, random-token (paired CI lower > 0) —
  the evolved code must be load-bearing under PURE non-kin listening;
- painted-collapse guards: final living N_eff median ≥ 3.0 AND p25 ≥ 2.0; no speaker-source lineage > 40%
  of non-kin messages AND speaker-source N_eff ≥ 2.5; final table-L2 ratio ≥ 0.5× gen0.

Other labels: CF rises but painted guards fail → `C2X2_PAINTED_ALIGNMENT`. Viability+content pass but CF
fails → `C2X2_PRIVATE_CODES_PERSIST` (the bulletproof negative: even a viable, fairly-pressured cross-
lineage regime can't grow a public code here → grounding / rich-world is needed = next paper). Viability
passes but open ≯ mute/scramble/random-token → `C2X2_CONTENT_FREE_SHORTCUT`. n=8 non-positive →
`C2X2_INCONCLUSIVE_N8`.

## 7. No-oracle redline + why it is NOT manufactured alignment
Agents read only own body state, own legal sensors, decoded messages, recurrent state. Routing reads
lineage labels only for partner choice; founder-id NEVER an input to emit/predict tables or policy. World
patches / true edibility / oracle stay fenced in eat-consequence or explicit oracle diagnostics. NO
gradients, truth labels, target codebooks, supervised CE, pretrained weights, LLMs, or public teacher.
The scaffold changes only WHO is heard over developmental time — not WHAT the answer is; the non-kin-only
final eval is run UNSCAFFOLDED (100% non-kin), so the verdict is on unscaffolded cross-lineage decoding.
Anti-painted guards reject single-teacher dominance, diversity collapse, and CF-without-load-bearing.

## 8. Implementation notes
- New runner `offscreen/rtc_g1f_c2x2_ramped.py`, reusing `rtc_g1f_c2x_crosslineage.py` + the harness.
- Add the ramped/mixed routing as a NEW `speaker_rule` variant (e.g. `mixed_ramped`) behind a parameter;
  default `_speaker_for` / g1f / C1 / C2X paths stay byte-stable (keep the byte-stability + MII-equivalence tests).
- p_nonkin uses the §2 deterministic HASH (no RNG consumed → evolution stream untouched). Record all
  fallback counts (kin-empty / nonkin-empty / both-empty-mute) + full config/env/git-commit in the JSON.
- **Byte-stability test (extend C2X's equivalence_test):** `speaker_rule="mixed_ramped"` at `p_nonkin=0.0`
  must be byte-identical to the kin-only path (gen-0 warm-up == C1), alongside the MII numpy-equivalence test.
- **Shared baselines (Opus-4.7 / compute):** the 4 CF baselines (`FROZEN_MIXED_FLOOR`, `C2X2_RAMP_COMMBLIND`,
  `C2X2_RAMP_RANDOM_TOK`, `C2X2_RAMP_SCRAMBLE`) + `C1_KIN_ONLY` are run ONCE and reused as `baseline_max`
  for BOTH `C2X2_RAMP_OPEN` and `C2X2_STAT025_OPEN` (don't run them per-treatment).
- **Post-run red-team note (Opus-4.7):** add a "satellite-teacher" diagnostic to the painted output (a
  teacher lineage that is a table-L2 outlier yet stays ≤40% of speaker-source can slip the median-L2 guard);
  flag for inspection, not a gate.
- Do NOT modify any LOCKED spec or verdict JSON. New files only.

## 9. Alternatives considered
- **Seeding from C1-evolved pops**: rejected as primary (they hold diverged private kin codes → switching
  to non-kin reproduces the C2X crash). Keep as a later diagnostic.
- **Stationary fixed mix (Gemini)**: cleaner (no schedule params); "25% gives a continuous gradient" is a
  legitimate hypothesis, not obviously wrong. Whether fixed-25% is enough pressure vs under-powered is
  EMPIRICAL — so rather than adjudicate it, `C2X2_STAT025_OPEN` is now a matched PRIMARY arm (§3) and the
  run decides ramp-vs-stationary with data. Claude's prior on ramp: it gives convergence its strongest
  fair shot (reaches 0.75) so a ramp-negative is more bulletproof, and the ramp is a built-in dose-response
  in time (covers 0→0.75) where stationary samples one point — but the data settles it. NB the two arms are
  not exposure-matched (ramp mean p_nonkin≈0.37 vs STAT025's 0.25), so this is two scaffolds head-to-head,
  not a clean schedule-shape factorial; **future follow-up: a matched-exposure STAT037 arm if ramp wins**,
  to isolate schedule shape from total non-kin exposure.
- **Rich-world grounding**: the larger next program (next paper); C2X2 is the cheap test of whether the
  current g1f optimizer can bridge private kin dialects under a fair, viable cross-lineage regime first.
