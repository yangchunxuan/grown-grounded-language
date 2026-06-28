# The CTM Arc — an honest consolidation (grown readable grounded language, from scratch)

*Working record / preprint-shaped. Purpose: bank what is solid, map the walls precisely, and point the next
push. Not polished for submission; every claim is scoped to what the committed artifacts support.*

## One line
We set out to grow a shared, decodable, GROUNDED language (and a readable mind) in from-scratch creatures. This
arc upgraded the brain to a CTM (Continuous Thought Machine) and precisely localized WHY grounded language is
hard to grow — turning a vague "the substrate is the wall" into three specific, separable walls, while banking
several real partial positives. No false wins; we repeatedly caught and retracted our own confounds, and
red-teamed our own specs to kill two would-be-meaningless "wins" before spending compute.

## Background
Prior work grew a decodable, compositional, grounded language in a from-scratch population under an
iterated-learning bottleneck + death/selection (tiny numpy/torch nets), but composition of multiple mechanisms
kept failing and "the tiny substrate is the binding constraint" was the recurring, fuzzy verdict. This arc asked:
does a CTM — a brain with internal "thinking" ticks and a synchronization representation that is meant to be
READABLE — change the picture, and can we pin down the real wall?

## What is solid (committed, multi-seed, controlled)
1. **CTM readability (DELIB).** On a depth-extrapolation algorithmic task with hard validity firewalls
   (depth-cropped MLP fails held-out deep-k = 0.000; freeze-input accumulation = 0.000), a from-scratch CTM's
   synchronization decodes the latent (current hop) MORE readably than a dimension-matched GRU hidden state:
   0.348 vs 0.276, Δ +0.055 [+0.035,+0.080], Holm-corrected, 6/6 seeds. Honest scope: modest effect, toy task.
   → CTM earns its complexity on the one axis it was chosen for — readability.
2. **The communication wall is the OPTIMIZER, not the architecture (comm-bootstrap).** In a gradient-trained
   referential game, a CTM speaker+listener with ZERO scaffold already learns grounded causal communication:
   message→referent decode +0.60 [.47,.73] (chance .25), foraging open−mute +0.63 [.51,.75]; RANDOM_TEACHER
   control clean. Under evolution / sparse REINFORCE the same agents never bootstrap (the joint speaker↔listener
   discovery is too sparse). → grounded language CAN grow from scratch in CTM agents — just not under pure
   evolution. Gradient through a differentiable channel dissolves the wall with no scaffold.
3. **A genuinely alive, ADAPTIVE micro-society (CTM-ALIVE).** A 2D world (energy/typed food/hazards/obstacles/
   agent markers/local perception/reproduction=mutated-clone) where CTM agents live, die, reproduce, modify the
   world, and EVOLVE foraging from scratch (EAT 0.14→0.21, energy 28→49, lineages collapse 24→4-6 = strong
   selection). No-oracle redline 9/9. Honest: communication never becomes causal here (open≈mute; signal→world
   decode 0.0) — consistent with (2), since the world uses evolution.
4. **Single-attribute compositional generalization emerges in a CTM (GCRL).** With Gumbel-temperature annealing,
   a CTM speaker+listener over combinatorial referents reaches CLEAN held-out compositional generalization for a
   SINGLE attribute (held-out attr → 1.0). Honest: see wall (c) — never BOTH attributes at once.
5. **CULTURAL (social) transmission of a grounded language — a training wheel removed (2026-06-27, 6-seed,
   red-teamed HOLDS_WITH_CAVEATS).** In a content-pressure life loop, a scaffolded grounded scout/forager language
   (gen-0 only) is transmitted across a post-gen-0 chain (gens 13–15) purely by SOCIAL IMITATION of fallible,
   reproduced elders' OBSERVED behaviour — the forager's target is the elder's possibly-wrong ACTION, never truth,
   never the elder's internal state — and is MAINTAINED, removing the genetic-weight-copy + parent-distillation
   wheels. clean-chain success 0.852 [0.800,0.909] vs three controls dead at chance (world_only 0.068 — *with* a
   genuine self-RL signal — / no_teaching 0.071 / random_teacher 0.072); within 2.5% of a truth-supervised
   distillation ceiling (ratio 0.975, doesn't exceed it); eff_label 0.857 (<0.98 = lossy, not laundered); SURVIVES
   43% elder-action corruption (ε0.3 → 0.754, where the young's success exceeds its own label accuracy — a
   truth-memorizer cannot); same gen-0 codebook carried (cross_gen0 0.672); content-bearing (lesions → chance);
   population-robust (drop top-decile teachers → 0.825); deep gens 10–15 no decay. Internal sync readable
   PER-AGENT (0.51 on the live run; pooled-across-heterogeneous-agents 0.09 is a measurement artifact, not a loss).
   Honest scope: NOT spontaneous emergence (grammar pre-exists in gen-0); the SCOUT re-perceives true content each
   birth (firewall #1 — it is the perceiver), so this is re-convergence to a truth-anchored attractor, not fragile
   preservation of a degrading signal; per-agent sync (0.51) is below the clean-dyad 0.70 (tight life-loop budget
   partially degrades it). [ctm_cultural_transmission_run, ctm_cultural_verdict.json]

**Brain-axis update (2026-06-27): the CTM brain is NOT the demonstrated bottleneck.** A grounded, premise-attacked
study + a 6-seed capacity-controlled CTM-vs-MLP ablation (CTM sits ON the MLP capacity→readability curve — a 6k-param
MLP matches its 0.68 internal readability at half the params) → no CTM capacity or readability edge over a plain MLP
on the gen-0 task (caveat: a basic decode metric, not the full DELIB battery, so it does NOT refute item 1's
CTM-vs-GRU edge). Every wall that ever flipped did so on a non-brain knob (optimizer/world/budget). → do NOT build a
bigger "organ-stacked" brain on faith; the leverage is world-design / selection-structure. The readable-brain bet
(item 1) holds; readable sync survives social transmission per-agent (4 falsified collapse-hypotheses). [ctm_brain_ablation, ctm_sync_survival]

**Two more boundaries (2026-06-27 follow-ups):**
- **Cultural transmission is partly truth-anchor-dependent (noise sweep, 6-seed).** Degrading the scout's PERCEPTION
  (gen-0 clean; truth scores only) degrades the maintained language. A CLEAN code-map probe (true content, no runtime
  misperception) de-confounds it: `clean_decode` 0.63→0.34 as ε rises and `clean_cross_founder` tracks it →
  `MAP_PARTIALLY_DEGRADES` — the learned code gradually DEGRADES, it does NOT drift to a new functional code. So the
  clean per-birth re-perception is load-bearing for code INTEGRITY (not just runtime acuity); there is NO "cultural
  language evolution under noise." [ctm_cultural_transmission_run --noise-sweep]
- **The within-life learning time-scale does NOT break a wall (brain/learning lever, MIDLIFE-PAYOFF-PERMUTE).** Mid-life
  the (dir,type)→payoff permutes (scoring only; language+scout intact; π invisible from content → a FROZEN agent
  provably →chance). Re-binding is achievable (DISTILL dense-gradient-on-true-π → 0.91; precheck unlimited-supervised
  → 0.93), but within-life SELF-driven learning can't: reward-gated self-imitation plateaus 0.16, REINFORCE 0.25 —
  both far below the 0.45 floor and the 0.91 ceiling, in an ample budget, readability preserved (heads-only). → **the
  OPTIMIZER WALL extends to within-life ADAPTATION, not just bootstrap: a sparse self-generated signal can't even
  re-bind a frozen linear readout; only dense gradient on truth (unavailable within life) can. The binding constraint
  is the learning SIGNAL, not the brain.** [ctm_wll_run]

## The three walls, precisely mapped (the arc's main contribution)
- **(a) Communication = the learning signal.** Not CTM, not scaffolding. Evolution/sparse-RL can't bootstrap
  joint sender↔listener discovery; gradient can (no scaffold). [comm-bootstrap]
- **(b) The living-loop integration = stacked, structural.** (i) the world rewards FLOCKING/aggregation, only
  weakly grounded comm CONTENT (ideal-communicator open−scramble +0.17, borderline); (ii) gradient-trained comm
  has SPLIT IO (speaker in=9, blind listener in=16) with no defined map into the UNIFIED alive agent (in=136,
  shared feat → both heads) — "inject as population init" is undefined; (iii) selection collapses content back
  to solo-foraging. Three panels + 8 dead spatial designs against the same flocking shortcut. [alive, affordance,
  hybrid red-team]
- **(c) Compositionality = a ROBUST wall surviving BOTH the learning-pressure AND brain-architecture axes — NOT
  a "weak CTM" problem.** Does a from-scratch brain GROW a multi-attribute compositional code (held-out JOINT
  generalization to unseen attribute combinations), or only memorize holistically?
  - *First sign (GCRL):* a CTM masters TRAIN but the compositional "slot" flips between attributes — either
    attribute alone generalizes (held-out → 1.0), never BOTH; held-out JOINT = 0. The Kirby iterated-learning
    bottleneck did not fix it.
  - *Learning-pressure axis (compwall v3, 4.77h, convergence-gated, multi-scale):* 7 converged attribute-SYMMETRIC
    arms (entropy-balance, population, curriculum, slot-swap, token-dropout) across 3×3 & 4×4 all mastered TRAIN
    (joint=1.000) yet got held-out JOINT = 0.000 on BOTH the recombination and the harder structured split;
    emergent topsim only 0.20–0.44 (holistic). 5×5 wouldn't even fit TRAIN at 10k steps (the competition caps
    training capacity as the referent space grows). Diverse symmetric learning pressures do NOT grow it.
  - *Brain-architecture axis (brainaxis, prior-ablation-gated):* swapping the CTM for a plain MLP, slot-attention
    (permissive K3_SEP0 + prior K3_SEP02), or VQ (commitment on/off) — all converged train=1.000 but held-out
    JOINT near chance (4×4 chance .0625; best MLP .125, CI-lower below chance). The disentangling PRIORS did NOT
    beat a plain MLP; ablations show the architectures don't EXOGENOUSLY factorize (random-task held-out ~0) and
    there's no prior-knob dose-response. (Formally INCONCLUSIVE — one strong-VQ cell never converged — but clearly
    NULL-leaning.)
  - The ONLY thing that ever produced held-out JOINT generalization was HAND-IMPOSING the factorization (a
    partitioned per-attribute readout) — which we banned as built-not-grown. **Conclusion: full multi-attribute
    compositional language does NOT grow from scratch in this referential-game family (gradient + a flat discrete
    channel) across EITHER axis; it appears only when structure is imposed.** Echoes Chaabouni et al.
    ("compositionality doesn't emerge for free"). [GCRL, compwall v3, brainaxis]

## Method / discipline (the methodological contribution)
- NO-ORACLE redline (policy reads only local obs + own state + decoded messages; truth only in scorers/probes),
  random-init only (no borrowed learned content), frozen pre-registration, ≥6 seeds, bootstrap CIs, ship nulls.
- Adversarial red-team BEFORE compute: ~10 candidate designs killed for smuggled-impossible tasks, broken/
  circular discriminators, oracle leaks, kitchen-sink unattributability, or detours that don't de-risk.
- Caught our OWN confounds and retracted: a step-count confound that faked CAUSAL_COMMUNICATION; a flocking
  confound (followed signal PRESENCE not CONTENT) that faked a comm-affordance; a Gumbel training instability
  (fixed via temperature annealing); and a convergence confound (held-out=0 is meaningless until TRAIN is
  mastered — fixed by a train_joint≥0.95 gate + multi-scale).
- Red-teamed our OWN SPECS before the system spent compute, catching two would-be MEANINGLESS "wins": a
  factored-readout fake-win in the composition-wall spec, and a TAUTOLOGY trap in the brain-axis spec
  (off-the-shelf disentanglers pass naive "grown" tests by construction). The latter forced the key reframe —
  GROWN-vs-BUILT = ENDOGENEITY: a real grown win must FAIL on a non-compositional control task AND collapse when
  the architecture's factorization knob is off. Lineage: Lowe et al., "Pitfalls of Measuring Emergent
  Communication" — extended to a from-scratch, readable, evolution-vs-gradient, grown-vs-imposed setting.

## Honest limitations
- DELIB readability is modest and on a toy task. comm-bootstrap is a referential game, not a living world.
  ALIVE communication is a null. Single-attribute compositionality grows but full multi-attribute does not
  across two axes. None of these is "a grown readable society."
- The headline negatives (b),(c) are genuine RESEARCH FRONTIERS, not a few-hours fix. The (c) result is scoped:
  it shows compositional language doesn't grow *in this referential-game family under gradient + a flat discrete
  channel across the pressure & architecture axes* — not that it can never grow (the channel/game axis is untested,
  and one strong-prior cell left the brain-axis verdict formally INCONCLUSIVE though clearly null-leaning).

## What's next (open frontiers, in priority)
- **(c) compositionality is now CLOSED across ALL THREE axes (2026-06-27).** Learning-pressure (compwall),
  brain-architecture (brainaxis), AND the channel/GAME axis all fail to grow held-out multi-attribute
  compositional generalization. The channel/game lead candidate (a PRODUCTIVE/open referent space where holistic
  memorization should be impossible) turned out to be ALREADY built = `ctm_openref_run.py` → `DISCRIMINATOR_BROKEN`
  (the apparatus can't even certify a hand-coded compositional ORACLE on the open space; held-out joint 0.048), and
  `openref_suff` shows held-out generalization tracks EXPOSURE (K), not composition (K=32 fails even the analytic
  linear ceiling; K≥128 a flat holistic coder interpolates unseen combos WITHOUT composition) → there is no regime
  where composition is BOTH necessary AND learnable. A constructed query-conditioned-listener mechanism (move the
  two-attribute demand across trials instead of within one readout) just re-encodes `loss(a1)+loss(a2)` over the
  same bounded shared code → confirms the closure. **SCOPED THEOREM: in the from-scratch referential-game family
  (gradient + flat discrete channel + bounded shared readout), full multi-attribute compositional language does NOT
  grow; held-out JOINT generalization appears ONLY when the factorization is hand-imposed. The binding constraint is
  that independent, generalizable per-factor information must coexist in one bounded shared code, and no
  attribute-symmetric pressure supplies that separation — only a static (Firewall-0-banned) partition does.**
- **CONSTRUCTIVE NEXT MOVE (not consolidate, not a closed re-attempt): INSTALL the partition, GROW the meanings.**
  Stop trying to GROW the factorization; install it as scaffolding — legitimate under the refined constraint
  (borrow structure/capacity, grow CONTENT) and consistent with cultural transmission (gen-0 grammar pre-exists;
  what grows is its grounded, transmissible USE). Then build the productive frontier = the **(a→living) UNIFIED-IO
  BRIDGE**: one CTM playing BOTH speaker+listener roles, gradient-trained, which ALSO resolves the split-IO
  injection-map blocker that stopped gradient-grown comm from entering the living/cultural loop — with composition
  installed. This combines every banked positive (gradient-comm grows; cultural transmission; single-attr
  composition) and de-risks the actual north star (a grown, decodable, grounded society) far more than chasing
  free composition. (Cheap residual bookkeeping: converge the lone strong-VQ cell to formalize `BRAIN_AXIS_NULL`.)
- **(a→living) bridge** — a UNIFIED-IO speaker-listener (one CTM, both roles) trained by gradient, which also
  resolves the (b)(ii) injection map; only then is the decouple-then-select / content-pressure world meaningful.
- Each specified with validity firewalls + falsifiers up front, attempted aggressively (incl. latest methods),
  and the RESULT adversarially red-teamed before belief.
