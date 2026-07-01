# PAPER PLAN — foundational paper (g1f arc + attack-machine methodology)

> **SUPERSEDED (2026-06-30) — historical blueprint.** Any `@<hash>` citations below are pre-normalization and **NOT reachable** in the public repo — anchor by verdict filename (see `RUNBOOK.md` / Zenodo DOI `10.5281/zenodo.21074235`). The live paper is `offscreen/PAPER.md` (v4) +
> `paper/ggl.tex`. Numbers below are PRE-rngfix draft values; the live headline is **MII 0.172 vs random-fitness
> control 0.1174, paired margin +0.0548 [0.0234, 0.0849]**, lineage **99.1% / N_eff 1.02 / 47-of-48**,
> diagnostic **5/5** windowed seeds, and the **+0.057 separate-RNG figure is retracted**. Kept only for the
> section structure and evidence-map rationale.

**Status: PLAN (awaiting user approval before drafting). Not a draft.** Truth sources this plan compiles
from: `offscreen/G1F_ARC_WRITEUP.md` (the calibrated spine) + `offscreen/CLAIM_LEDGER.md` (per-claim
evidence). Venue (user-confirmed): a **specialized journal** — primary target **_Artificial Life_** (MIT
Press); fallbacks _Adaptive Behavior_ (SAGE), then the ALIFE conference (short form). Scope (user-confirmed):
**the g1f arc as the science, the attack-machine as the co-equal methodological contribution.**

---

## 1. Thesis (one sentence each)

- **Scientific:** In a minimal hand-coded 2-D survival world, a *decodable, grounded* communication channel
  **co-evolves from random weights under survival selection alone** — no gradient on the task, no oracle/truth
  labels, no borrowed/pretrained weights — **but it remains a private kin dialect; a *public* cross-lineage
  code does not bootstrap across a swept cross-lineage-pressure range**, because non-kin codes are mutually
  undecodable and forcing non-kin listening kills foraging (a *pressure-vs-survival tension*).
- **Methodological:** A reusable **attack-machine** — bidirectional adversarial self-audit (architecture-matched
  null + fair baseline + ≥6-seed bootstrap-CI win-margins + frozen pre-registration + a no-oracle redline +
  adversarial *code-grounded* multi-agent review) — that, in this very project, caught **6 banked-then-killed
  false positives, one false *negative* (g1f itself), and an over-heated internal re-audit narrative.**

**The two are one story:** the science is only believable *because* of the machine, and the machine is only
demonstrated *because* the science kept trying to fool us. That coupling is the paper's identity and its fit
for an ALife audience (a field with a recognized over-claimed-emergence / weak-baseline problem).

## 2. Title candidates (calibrated — "Growing", never "Grown"; scoped, never "theorem")
1. *Growing a Grounded Language under Survival Selection: Co-evolution, Privacy, and the Limits of a Public Code in a Minimal World*
2. *A Kin-Scoped Grounded Channel Co-evolves from Scratch — and Why a Public Code Does Not Bootstrap*
3. *Attack-Machine Artificial Life: Honest Emergence of a Grounded Channel and the Wall to Shared Language*

(Recommend #1 as title, #3's "attack-machine" as a keyword/subtitle hook.)

## 3. Why this fits the venue (positioning)
- _Artificial Life_ values **minimal, mechanistic, reproducible** emergence studies over scale. Our world is
  hand-coded and tiny by design; the result is a *mechanism* (pressure-vs-survival tension), not a benchmark.
- The field's pain points we directly answer: (a) emergent-communication claims with **no matched comm-blind
  null**; (b) "language evolved!" from **gradient/oracle leakage**; (c) **underpowered** single-seed positives.
  Our methodology section is a contribution *to the field's hygiene*, not just our appendix.
- Distinct from MARL emergent-communication (Lazaridou, Foerster et al.): **no gradient on the channel, no
  centralized critic, no oracle** — selection only. Distinct from iterated-learning / Kirby: we **do not impose
  a transmission bottleneck**; we ask whether one is *needed* (our answer leans yes → "richer world").

## 4. Section outline (journal length ~12–18 pp) with content + evidence

| § | Title | Content | Evidence anchors |
|---|---|---|---|
| 1 | Introduction | The question: can grounded language *grow* (not be designed/trained-in) under survival selection, and is it public? Dual contribution stated. Honest framing up front: this is a **scoped** result in one world. | — |
| 2 | Related work | Emergent comm in MARL (gradient/oracle) · signaling games (Skyrms, Lewis) · iterated learning & compositionality (Kirby, Steels) · ALife language evolution · the replication/over-claim critique (why a methodology contribution is warranted). | — |
| 3 | World & agents (the substrate) | RTC lethal-vent 2-D world (4-channel field, advection/diffusion/vents, metabolism/death) — **hand-coded, not learned**. Agent = `UnifiedIO` tied code-table K×B×V = 4×5×6, N(0,1) init; emit=argmax symbols, predict=argmax bands. Evolution = mutation+truncation/tournament; **the only gradient anywhere (Kirby imitation) is unused in load-bearing arms**. | `ARCHITECTURE.md`; `config/prereg_rtc.py` |
| 4 | Methods: the attack-machine | The 6 disciplines as a method. MII metric (referent→emit→decode→exact-tuple; chance=1/625). Matched comm-blind null. ≥6-seed bootstrap-CI win-margin. Frozen pre-registration. No-oracle redline (what agents may read). Tier rule (n≤8 ⇒ POS/INCONCLUSIVE only; bank a negative only at n=16). Code-grounded adversarial review loop. **Provenance triple** (verdict@commit + ledger + RUNBOOK). | `RUNBOOK.md`; `tests/`; `rtc_g1f_common.make_provenance` |
| 5.1 | Result: co-evolution is real, kin-scoped | g1f: survival 0.172 vs comm-blind 0.127, **margin +0.045, 95% CI [0.020, 0.070]**, n=48. Semantic MII (survives separate-fitness-RNG control +0.057 [0.029,0.085]); no-oracle passes. **Scope: ~98% single founder lineage → kin dialect, not public.** | `rtc_g1f_commblind_verdict_formal48.json`, `rtc_g1f_reconciled_verdict.json`, `rtc_g1f_power_analysis.json` |
| 5.2 | Why kin-only? (diagnostic) | Within- vs cross-founder MII at coexisting gens. Verdict `INCONCLUSIVE_NO_WINDOW` (frozen gate held — honest), **direction C (private codes), unanimous**: WF 0.159 (~100× chance) vs CF 0.00086 (≈chance). Sentinels pass (lineage-shuffle; gate-0 open≫mute/scramble). | `rtc_g1f_kinonly_diagnostic_verdict.json` @6aaefe2 |
| 5.3 | Maintaining diversity is necessary but not sufficient (C1) | 2×2 {hard,soft}×{16,96}. **Mechanism:** pop opens windows, niching *sustains* (soft96 N_eff 4.10, 8/8). **A refuted, C supported:** even with 20+ gens sustained coexistence, CF≈floor (0.0015≈0.0016) while WF≈0.16. Kin-only = genuine private-code divergence, not collapse artifact. | `rtc_g1f_c1_collapse_probe_verdict.json` @21dc0f3 |
| 5.4 | The wall: no public code bootstraps (C2X / C2X2 / C2X3 = a de-facto pressure sweep) | Force survival to depend on decoding non-kin. **0.25** (C2X2-stat: viable, CF floor) / **0.5** (C2X3: boom-bust, CF floor) / **0.75–1.0** (C2X, C2X2-ramp: crash, CF floor). CF never rises above chance at any pressure; higher pressure only crashes survival harder. Per-gen trajectories show viable+diverse coexistence is *transient*. **Pressure-vs-survival tension.** | `rtc_g1f_c2x_crosslineage_verdict.json` @1c1a27d, `rtc_g1f_c2x2_ramped_verdict.json` @07624b4, `rtc_g1f_c2x3_forced_verdict.json` @c9c749e (+provenance, reproduced) |
| 6 | The methodology, demonstrated | Narrate the machine working *bidirectionally*: caught a false NEGATIVE (5.1 pilot/formal mismatch), held a frozen gate to honest INCONCLUSIVE (5.2), adjudicated two reviewer contradictions (5.3), corrected an over-coarse auto-label via a pre-logged continuous metric (5.4). The 6-killed-positives history (from CTM line) cited as prior bidirectional evidence. | `CLAIM_LEDGER.md` methodology row |
| 7 | Discussion | What "grounded but private" means for language-origin theory. Why a public code needs *shared referents worth naming + sustainable diversity under comm pressure* → richer world. Relation to iterated-learning bottleneck (we did not impose one; the tension suggests why one — or an ecological analogue — may be required). Honest limits (one world, one architecture, 28-gen timescale, n=8 on the cross-lineage tier). | — |
| 8 | Conclusion + future work | Scoped claim restated. Future = richer world (next program), explicitly *motivated-not-required* by this self-contained arc. | — |
| App. | Reproducibility | RUNBOOK commands, provenance triple, CI invariants, exact configs/seeds. | `RUNBOOK.md`, `.github/workflows/ci.yml` |

## 5. Figures & tables (plan)
- **F1** World schematic + agent (UnifiedIO table) + evolution loop — one diagram of the whole substrate.
- **F2** g1f survival vs comm-blind, per-seed dots + bootstrap-CI of the margin (the headline +0.045 [0.020,0.070]).
- **F3** WF vs CF MII bar (diagnostic + C1 soft96), with the chance floor line — the "private not public" picture.
- **F4** The pressure sweep: x = non-kin fraction {0,0.25,0.5,0.75,1.0}, twin y-axes = survival (crashes) and CF MII (flat at floor). **This is the money figure** — the tension in one image.
- **F5** C1 N_eff trajectories (hard96 collapses to 1.44, soft96 sustains 4.10) — niching mechanism.
- **T1** Evidence map = §6 below (every claim → verdict@commit → stat). **T2** Method checklist (the 6 disciplines as a reusable table reviewers can adopt).

## 6. Evidence map (claim → artifact@commit → statistic) — the spine of T1
| claim | verdict @ commit | key statistic |
|---|---|---|
| channel co-evolves, kin-scoped | `rtc_g1f_commblind_verdict_formal48.json` (g1f predates session commit-tracking; see git log) | +0.045, 95% CI [0.020,0.070], n=48; ~98% single lineage |
| MII semantic not weight-sim | `rtc_g1f_reconciled_verdict.json` | sep-fitness-RNG +0.057 [0.029,0.085]; gate-0 open≫mute/scramble |
| private codes (direction) | `rtc_g1f_kinonly_diagnostic_verdict.json` @6aaefe2 | WF 0.159 vs CF 0.00086; CF/WF 0.5%; 10/10 seeds |
| diversity necessary-not-sufficient | `rtc_g1f_c1_collapse_probe_verdict.json` @21dc0f3 | soft96 N_eff 4.10, CF 0.0015≈floor 0.0016, n=8 |
| viability crash @ 1.0 non-kin | `rtc_g1f_c2x_crosslineage_verdict.json` @1c1a27d | alive 0.045 vs 0.272 |
| scaffold viable, CF still floor | `rtc_g1f_c2x2_ramped_verdict.json` @07624b4 | alive ~0.15, CF margin negative |
| boom-bust @ 0.5, CF floor, per-gen | `rtc_g1f_c2x3_forced_verdict.json` @c9c749e (provenance-stamped @254f3d7, reproduced byte-identical) | alive mean 0.10, CF max 0.0058 vs 0.0016 |
| attack-machine bidirectional | `CLAIM_LEDGER.md` | 6 killed positives + 1 killed negative + 1 corrected re-audit |

## 7. Calibration guardrails (non-negotiable — enforced at draft + a final calibration pass)
1. Title/verbs: **"Growing/co-evolves", never "Grown/solved/closed/theorem."**
2. Every negative carries its **power tier**: the cross-lineage null is "no detectable cross-lineage code at
   n=8, unanimous across seeds AND pressure, with a mechanism" — *not* a FORMAL negative (that wants n=16). Say so.
3. **No "bottleneck rather than model/optimizer" without a positive control** — we never claim the architecture
   *can't*, only that under these regimes it *didn't*.
4. Scope every claim to **this world / this architecture / this timescale** in the same sentence.
5. The methodology section must **own our own mistakes** (the false negative, the mislabels) as the *evidence
   the machine works* — framed as strength, not confession. (See §9 decision.)
6. Cross-check every number against the verdict JSON before it enters prose; cite verdict@commit, not chat.

## 8. Scope boundaries
- **IN:** the g1f arc (Steps 1→4, i.e. g1f / diagnostic / C1 / C2X-C2X2-C2X3) + the attack-machine.
- **OUT (explicit non-goals, one line each in the paper):** the CTM walls W1–W5 (different substrate, a
  *separate* line); DreamerV3/world-model work; the "user-gated window to the human world" north-star.
- **DEFERRED → future work, not this paper:** the richer world (more niches/referents/spatial structure to
  sustain diversity under comm pressure). The arc is self-contained: it *motivates* the rich world, not requires it.
- **DECISION POINT (g1d/g1e):** the ledger has two adjacent scoped-positives in the *same world* — g1d
  (content→location binding is load-bearing, McNemar p<5e-4) and g1e (a heritable trust-gene for *using* a
  channel is selected up). They reinforce "the channel is genuinely grounded content, not an artifact." Options:
  (A) a short subsection "the channel carries grounded content (corroborating constructions)"; (B) one citation
  sentence + defer; (C) omit. **Recommend (B)** — gate-0 (open≫mute/scramble) already defends groundedness
  *inside* g1f, so g1d/g1e are reinforcement, not load-bearing; folding them in risks scope-creep. *User call.*

## 9. Anticipated reviewer objections → pre-emptive answers (write these into the text)
- *"MII is just weight similarity."* → It's referent→emit→decode→exact-tuple recovery; lineage-shuffle sentinel
  spikes CF 15–23×, gate-0 open≫mute/scramble. Semantic, keyed on lineage.
- *"Negative is just underpowered."* → Unanimous across seeds **and** across 4 pressure levels, with a stated
  mechanism (per-gen trajectories) — and we explicitly **decline to bank it as a FORMAL negative** (tier rule).
- *"Hand-coded world is a toy."* → That's the point: minimality is what makes the mechanism legible and the
  null fair. We claim a mechanism, not generality.
- *"You're just rediscovering kin selection / the bottleneck."* → We *quantify* it as a pressure-vs-survival
  tension with a swept curve, and show diversity-maintenance alone doesn't cross it.
- *"Authors made errors (false negative, mislabels)."* → Reframed: the audit *catching its authors* is the
  empirical demonstration of bidirectionality — the contribution.

## 10. Drafting plan (order of operations, after approval)
1. Lock §3+§4 (substrate + method) first — they're the most stable (sourced from ARCHITECTURE/RUNBOOK).
2. §5.1→5.4 results, each pinned to its verdict@commit; build F2/F3/F4/F5 from the JSONs (a small plotting
   script reading the banked verdicts — reproducible, lives in `offscreen/`).
3. §6 methodology narrative + §7 discussion.
4. §1 intro + §2 related work last (write the claims before the framing).
5. **Final calibration pass** against §7 guardrails + a fresh CLAIM_LEDGER cross-check.
6. Adversarial review round (the same code-grounded multi-agent loop) on the *manuscript* before any submission.
7. (Optional) check for an `academic-paper`/`academic-pipeline` skill at draft time; otherwise draft directly.

## 11. Open user decisions (only these — everything else has a default above)
- **D1 — venue precision:** _Artificial Life_ journal (primary, full length) vs _Adaptive Behavior_ vs ALIFE
  conference short paper. Default: **_Artificial Life_ journal.**
- **D2 — g1d/g1e:** include as subsection (A) / one-line cite (B) / omit (C). Default: **(B).**
- **D3 — own-mistakes framing (§9 last bullet):** front-and-center as the methodology's headline demonstration
  vs a quieter methods-sidebar. Default: **front-and-center as strength** (it's the paper's most novel angle).
