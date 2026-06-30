# STAGE: C2X2 — RAMPED MIXED NON-KIN SCAFFOLD — pre-registration **DRAFT (not locked)**

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
Claude's canonical version of Codex's design + Gemini's absolute viability floor. To be reviewed
code-grounded (route to Gemini to defend stationary or concede) before lock.

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

For `(seed, gen, round, listener_i, post_i)`, draw non-kin with prob `p_nonkin(gen)` via an **arm-local
RNG / deterministic hash** (NOT the main evolution stream). If non-kin: balanced round-robin over eligible
non-self lineages then members (= the locked `cross_lineage_balanced`). If kin: original same-lineage rule.
If the requested category is empty: fall back to the other category and **record the fallback count**; if
both empty: mute. The rule may read only `(seed,gen,round,i,j)` + current lineage labels for routing —
never reward, decode success, true edibility, world patches, target codes, or founder-id-as-policy-input.

## 3. Arms
**Primary:** `C2X2_RAMP_OPEN` (ramped rule, real msgs, survival fitness) · `C1_KIN_ONLY` (kin, real,
survival) · `C2X2_RAMP_COMMBLIND` (ramped, real, RANDOM fitness) · `C2X2_RAMP_RANDOM_TOK` (ramped, iid
tokens) · `C2X2_RAMP_SCRAMBLE` (ramped, permuted-real) · `C2X2_RAMP_MUTE` (ramped, mute).
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
If these fail → `C2X2_DESIGN_FAILURE_VIABILITY_CRASH` (NOT a public-language negative).

## 6. Success gate (FROZEN) — `C2X2_PUBLIC_CODE_EMERGES` iff ALL:
- viability guard passes;
- dual coexistence window in ≥6/8 seeds (n=8) or ≥12/16 (n=16);
- `CF_margin_vs_baseline_max` bootstrap 95% CI lower > 0 AND point ≥ 0.04;
- `CF_OPEN ≥ 0.25·WF_OPEN`;
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
- Arm-local RNG for the p_nonkin draw — must NOT consume the evolution stream. Record its seed + all
  fallback counts + the full config/env/git-commit in the verdict JSON.
- Do NOT modify any LOCKED spec or verdict JSON. New files only.

## 9. Alternatives considered
- **Seeding from C1-evolved pops**: rejected as primary (they hold diverged private kin codes → switching
  to non-kin reproduces the C2X crash). Keep as a later diagnostic.
- **Stationary fixed mix (Gemini)**: cleaner (no schedule params) but either risks a second cold-start
  crash or applies weak cross-lineage pressure forever (under-powered false-negative). Ramp + the non-kin-
  only final eval dominate it on the convergence question. (A stationary-high arm could be added later if
  the ramp's schedule is contested.)
- **Rich-world grounding**: the larger next program (next paper); C2X2 is the cheap test of whether the
  current g1f optimizer can bridge private kin dialects under a fair, viable cross-lineage regime first.
