# CLAIM LEDGER — per-claim epistemic re-labeling (post g1f-flip + Codex audit)

**Purpose.** Every headline claim is decomposed into: corrected claim · evidence category · provenance (artifact / command+env / seeds / pilot-or-formal / is the control the SAME config as the treatment) · priority. Built after the g1f pilot/formal false-negative was caught, the 7-agent re-audit, and an independent Codex audit that (correctly) reined in two over-reaches in the re-audit.

**The systematic problem is NOT "all negatives are false."** It is two things:
1. **Provenance / config loss** — scripts, JSONs, README/paper do not guarantee the same env / seed / formal-block across a treatment and its control. (This caused the g1f false negative: a FORMAL coevolve compared against a PILOT comm-blind.)
2. **Scope overclaim** — local/in-this-world failures written one level too strong.
Small sample size is only ONE cause among several. Each wall has a different root.

**Four categories (do not conflate):**
- **(1) PILOT/CONFIG FALSE-NEGATIVE** — negative is a measurement/config artifact; flips under correct scale/config.
- **(2) SCOPED NULL** — adequately-powered negative that holds only in the impoverished/dead world tested.
- **(3) METHOD-NOT-FULLY-TRIED / DESIGN GAP** — the move that could break it was never built; undertested.
- **(4) LOCAL-FAILURE-AS-THEOREM** — a real local failure over-generalized to impossibility.

---

## RTC constructive results (the "does it grow" layer)

| id | CORRECTED claim (calibrated) | category | artifact | command / env | seeds | pilot/formal | control == treatment config? | priority |
|---|---|---|---|---|---|---|---|---|
| **g1f** | Survival selection **co-evolves a decodable channel** above a matched comm-blind control (margin **+0.045, 95% CI [0.020,0.070]**). **SCOPE: kin-lineage** (population collapses to ~1 founder lineage) — NOT yet a public cross-lineage language. | was (1), now a **scoped POSITIVE** | `rtc_g1f_commblind_verdict_formal48.json`, `rtc_g1f_reconciled_verdict.json`, `rtc_g1f_power_analysis.json` | `RTC_G1F_FORMAL=1 RTC_G1F_COMMBLIND_SEEDS=48 python -m offscreen.rtc_g1f_commblind_control` | 48 | **formal** | **YES (now)** — both formal, paired same-init; the OLD `_s12` had treatment=formal vs control=pilot (the bug) | **P0 done** |
| **g1d** | Grown-channel content (content→location **binding**) is **load-bearing RELATIVE to degraded controls** (exact paired McNemar p<5e-4; 12:0/13:0/13:0, zero wrong-direction). | scoped POSITIVE (relative); **gate tests the wrong question** (machine verdict INCONCLUSIVE only because it gates absolute >50% survival) | `rtc_g1d_lethal_verdict_sig0.3.json`, `rtc_g1d_paired_stats.json` | `RTC_SENSOR_SIGMA=0.3 RTC_TOXIC_DEATH=-0.9 RTC_LE_SEEDS=24 python -m offscreen.rtc_g1d_lethal` | 24 | formal | YES | **P1** (re-score on the relative gate; do NOT call it absolute) |
| **g1e** | A heritable trust gene gating **USE** of a separately-trained channel is **selected up** under real content (0.957) vs scramble (0.30)/drift (0.41). = **adoption / use-selection**, NOT de-novo language emergence. | scoped POSITIVE (adoption) | `rtc_g1e_emerge_verdict_tox-0.9.json` | `RTC_SENSOR_SIGMA=0.3 RTC_TOXIC_DEATH=-0.9 RTC_EM_SEEDS=8 python -m offscreen.rtc_g1e_emerge` | 8 (pop40/gen30) | formal | YES | **P1** (narrative: do NOT inflate to de-novo emergence) |

## The five walls (the "why it fails" diagnosis layer)

| wall | CORRECTED label | category | basis / provenance | priority |
|---|---|---|---|---|
| **W1 within-life optimization** | NOT "optimizer wall toppled." **Coverage wall / scoped break**: a self-generated (non-truth) reward + EM-relabel rebinds the frozen readout to the oracle ceiling **WHEN coverage suffices**; arch-null (explore-only-no-reward) stays at floor ~0.085. The committed `NO_WITHIN_LIFE_RECOVERY` was a **PILOT false negative** (n=2, temp=1 exploration starvation). | (1) for the old negative + the corrected result is a **scoped/coverage break** | `ctm_wll_rebind_pilot.json` (n=2/temp1 = the false neg) vs `ctm_wll_attack_summary.json` (powered n=6/temp8 flip) | **P0** (retract the pilot negative; write as coverage wall, NOT "optimizer wall broken") |
| **W2 compositional generalization** | Held-out JOINT stays at 0 across V1–V8 arms; root-caused to **speaker-side OOD**. Most solid of the five. Residual risk is **world/architecture scope** (only tested at 3–4 attributes where holistic coding is the shortcut), not sample size. | (2) SCOPED NULL (world-too-small / architecture-bias) | `ctm_compwall_verdict.json` (+ V1–V8), `ctm_brainaxis_verdict.json` | low — do NOT rush to overturn |
| **W3 spatial communication** | **UNDERTESTED / DESIGN GAP — NOT a false negative.** `rtc_g1c` is still inconclusive even at n=16/sig0.5 (fusion does NOT beat scramble — confirmed this run). g1d/g1e show content CAN be load-bearing in OTHER constructions but do NOT refute the original W3. The dissolving move (distributed *complementary* perception) was never built. | (3) METHOD-NOT-FULLY-TRIED | `rtc_g1c_spatial_verdict_sig0.5_n16.json` (inconclusive, powered) | **P1** (label `UNDERTESTED / DESIGN GAP`, not "near-flipped") |
| **W4 cooperation beyond communication** | Content sub-claim = clean positive. **Selection / "beyond-communication" leg NOT firmed**: open>>drift only at one frozen defector-heavy init (basin lottery at pop=24), and a prereg gate was renamed blocking→`diagnostic_` in a frozen commit (governance breach). | (3)+(4) undertested selection leg (basin/init) + a governance/overclaim issue | `pcgr_wall4_firm_verdict.json` (incomplete), init-band sweep `pcgr_wall4_initsweep.py` (running, `PCGR_W4_SEEDS=16`) | **P1** (await sweep; do NOT declare false-negative) |
| **W5 self-supervised prediction** | As-specified: untrained reservoir ties/beats the trained world-model (clean, **powered** negative, MDE≈0.10, observed −0.13). But it is a **dead-world artifact** (0% capture, no learnable dynamics). | (2) SCOPED NULL / **PARKED** (world-regime) — NOT a pilot/seed false-negative, NOT CLOSED | `wall5_reservoir_control_verdict.json` (the `+0.383` `wm_smoke2` was the underpowered pilot counterexample) | low — mark PARKED/SCOPED, do not overturn |

## Methodology claim (the contribution)

| claim | status |
|---|---|
| The attack-machine (architecture-matched null + fair baseline + ≥6-seed win-margin bootstrap CI + adversarial red-team) is a transferable, **bidirectional** self-audit. | **Stronger than before.** It has now caught false POSITIVES (6 banked-then-killed), a false NEGATIVE (g1f, via mode-mismatch), AND an over-heated re-audit narrative (this ledger's own correction, via the Codex pass). Bidirectionality is demonstrated three ways. |

---

## Discipline going forward (the real fix)
1. **Every committed verdict must record its full config** (env vars incl. formal/pilot, seeds) in the JSON, so a treatment and its control are provably the same regime.
2. **A control is only valid if it is the SAME config as the treatment** (the g1f lesson).
3. **Verdict gates must test the scientific claim** (g1d's absolute-gate vs the relative claim is a calibration bug, not a result).
4. **No "CLOSED"/"THEOREM"** as a result label; use the four categories above.
5. Re-label the LBA / paper claim-by-claim against this ledger BEFORE writing prose.

## Order of work (Codex-endorsed)
- **P0:** g1f (done — retracted negative, now formal scoped-positive) · W1 (re-label as coverage wall).
- **P1:** g1d (relative-gate re-score) · g1e (adoption, not de-novo) · W3 (UNDERTESTED/DESIGN-GAP) · W4 (await init-band sweep).
- **Not urgent:** W2 (scoped null) · W5 (parked scoped null).
- **Then, and only then:** the (a) public-language experiment spec (maintain lineage diversity + put cross-lineage intelligibility under selection + cross-founder MII metric).
