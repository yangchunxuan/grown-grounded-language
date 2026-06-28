# RELAY-TIDE COMMONS (RTC) — rich-world spec (shortcut-proof, staged, buildable)

*Produced by the rich-world design workflow (4 diverse designs → adversarial shortcut-hunt on each → synthesis adopting every patch), 2026-06-28. Verdict: **PATCH_THEN_BUILD**. Built so the 5+1 campaign shortcuts (S1 holistic / S2 brute-force / S3 basin-lottery / S4 thin-perception / S5 flocking / S6 decode-equivalence) die BY CONSTRUCTION, while the ONE unbroken wall (grown multi-attribute JOINT compositionality) is a pre-registered PROBE that may ship an honest null — never a load-bearing assumption.*

---

A from-scratch 2D living micro-society on a torus where survival = reading a hidden tidal nutrient field that NO body can sense alone, decoding+RELAYING multi-channel messages, fusing them, and choosing trustworthy relay partners by integrated gossip. Reuses the existing substrate verbatim where possible; the **differentiable channel** and the **within-life recurrent reputation reader** are the two non-negotiable, codebase-earned mechanics.

## 0. Earned constraints (non-negotiable, from the verdicts)
1. **Language grows ONLY through a differentiable channel** (CTM-COMM-BOOTSTRAP; `mortal_channel.cotrain_factored` has the `F.gumbel_softmax(hard=True)` path). Pure survival/evolution selection on EMIT = decorative channel (CTM-ALIVE open-mute −0.045). → EMIT trained by gradient against a dense self-supervised target; selection acts on WHETHER/WHEN to act on a decoded forecast, never on the code itself. = DECOUPLE-THEN-SELECT.
2. **No-oracle redline** (reuse `tests/test_coop_redline.py` forbidden-token scan): policy reads only (own body, own partial perception, decoded heard messages, own recurrent state). Ground-truth field/labels/coords readable ONLY by scorer/loss. The self-supervised target is the SPEAKER'S OWN observed reading, never the global field.
3. **Grown JOINT compositionality is the open wall** (CTM-GCRL HALF_COMPOSITIONAL; Wall-2 growth-side disentanglement 4/4 NULL). PROBED, never ASSUMED. The world kills S1 (holistic can't cover) but whether a speaker GROWS a generalizing factored code is the falsifiable headline that MAY ship a null.
4. Files <500 lines; single GPU; staged isolate-then-probe; every claim ships arch-matched null + scramble/mute + held-out + clean-CI ≥6 seeds.

## 1. World mechanics (S4 + S2 spine)
- GRID 48×48 torus (no edge oracle). HIDDEN (never observed by agents): K=4-channel spectral nutrient field s_t(x)∈R^4, each channel transported by a slowly-rotating 2D advection-diffusion current (semi-Lagrangian advect + small gaussian diffuse + 0.97 decay), injected from drifting vents.
- **Anti-clock patch (kills S2/S4-solo):** each channel's per-step innovation is LARGE + INDEPENDENT across channels, only WEAKLY phase-locked to the tide; a clock-from-phase predicts <0.03 of any channel's variance. **World-validity redline: a `clock_only` null (predicts missing channels from tidal phase + own axes, no messages) MUST stay at the solo floor; if it reaches the fusion lift the WORLD is invalid (not the agent).**
- EDIBILITY: patch value r_i = w_i · s_t(patch), w_i∈R^4 = heritable metabolic vector with **FULL support over all 4 channels** (no single 2-channel reading suffices). Eat: energy += clip(r_i) if r_i>θ else −toxin_cost (toxic kills). Optimal eat-site moves every step → a random reservoir that can't integrate its sensory history into a flow+spectrum estimate STARVES (S4 real).
- RESOURCES capped below metabolic demand at carrying capacity → real scarcity, real defection pressure (S3 substrate).

## 2. Distributed partial perception + RELAY (kills S5, rescues S1)
- PERCEPTION (the ONE no-oracle seam, reuse `live_perception`): creature i reads only (a) own energy/age/heading, (b) NOISY (σ=0.8) LAGGED (3-step) reading of ONLY its 2 genome-selected channels B_i over a 5×5 window, (c) neighbours within r=6 as (bearing, distance, last-heard symbols) — NEVER genome, NEVER s_t, NEVER patch labels.
- **S5 kill (information-theoretic):** edibility needs full-support w_i; i senses only 2 channels; a neighbour's body/position encodes only ITS own 2-axis projection (orthogonal to i's need). Missing channels exist ONLY in messages. Following a body = strict SUBSET of need, never a superset. Verify: body-follow null gets 0 of the fusion lift.
- **S1 RESCUE (RELAY-AND-AGGREGATE):** full-support w_i + any one partner supplies only 2 channels → i must AGGREGATE K≥2 diverse-basis partners to reconstruct all 4. A fused creature is a HUB and to inform others must RE-EXPRESS up to 4 channel-levels in ONE M=4 utterance. Geometry: K=4 channels × 5 bands = 625 hub-referents, V=6, M=4 → V^M=1296≥625 (factorable) but a per-meaning blob over 625 is unlearnable within a lifetime AND can't cover held-out band-combos. **The JOINT referent is now PER-MESSAGE → S1 pressure is real, held-out partition non-empty.**

## 3. The grown language (DECOUPLE-THEN-SELECT)
- Reuse `mortal_channel.FactoredSpeaker` + `FactoredListener`. Referent = the 4-channel band tuple a hub must express.
- **EMIT trained by GRADIENT** through `cotrain_factored`'s `F.gumbel_softmax(hard=True)` against a DENSE self-supervised target: listener reconstructs the SPEAKER'S OWN decoded forecast (its private + already-fused estimate), NOT the global field (no-oracle preserved).
- Survival reward shapes only WHEN/WHETHER to act (eat/avoid/move/donate), via a small CTM policy (`ctm_cell.SmallCTMCell`) over decoded+filtered latent. WM (`live_world_model` RSSM) = REPRESENTATION/MONITOR ONLY (behaviour via real-env policy, never imagination-RL).
- REPRODUCTION + Kirby bottleneck (`mortal_generations.run_population_generations`): offspring RE-LEARN speaker/listener by imitating a SAMPLED subset of parent productions — NO weight inheritance. Genes (w_i, basis B_i, give/take disposition, gossip honesty) inherit; brain/language weights do not.

## 4. Cooperation + within-life integrated reputation (kills S6)
- Survival above subsistence needs DONATION-coupled mutual relay: I name my channels for you, you name yours for me. Honest reporting is free to fake → free-riders emit noise and still eat your info (real defection niche).
- **S6 kill:** gossip = a SINGLE witnessed EVENT per message ("partner P emitted a reading that misclassified patch-type T this window"), one event/message, different witnesses/times. NEVER a pre-binned reputation scalar (no `_rep_referent(bin)`, no `_true_bin` reaching the policy). The chooser receives a STREAM of event-messages and ITSELF accumulates them into a trust estimate inside CTM recurrent state (within-life, NOT inheritable). Partner-choice/donation = a learned recurrent function of the event stream, not a genetic threshold. Trust = a temporal integral no single message supplies.
- Partners chosen BEYOND visual range so the message (not proximity) is the only reputation carrier.

## 5. Population/ecology (kills S3)
- POP 150 (MVP 60-120), continuous birth/death, niches, lineage continuity. Defection pays short-run; reputation+partner-choice make conditional cooperation invasion-resistant.
- **Anti basin-lottery:** SPATIAL viscosity — gossip + partner-choice are LOCAL (within radius), replicator structured not well-mixed. S3 endpoint = pre-registered defector-invasion BAND across init mixes, ≥20 seeds, paired RNG, basin-escape-RATE primary; open>drift CI-clean at EVERY init (NOT aggregate); gate FROZEN as blocking (the wall-4 sin was softening a frozen gate to diagnostic_).

## 6. Probes (attributable; one control per shortcut)
- (1) MESSAGE: `mortal_channel` posdis/topsim + `mutual_intelligibility_matrix` cross-vs-self + held-out JOINT on band-combos never sent. Controls: mute, scramble. **A holistic-codebook null (size-V^M lookup over decoded tuples) MUST fail held-out-JOINT while the grown code succeeds** = the S1 attribution gate.
- (2) SYNC/WM: `live_probe_tap` linear-decode hidden flow + missing-channel band from CTM sync / RSSM latent, scored ONLY vs the architecture-matched UNTRAINED-reservoir null + time-matched input baseline (the mandatory post-Wall-5 template).
- (3) BEHAVIOUR/REPUTATION: `live_social_metrics` balanced rep-decode AUC vs 0.5; pivotality knockout. Controls: history_shuffled, type_broadcast, AND the new **single_event** (give only the most recent ONE event) — if cooperation survives single_event the agent is one-shot decoding → ship NULL.

## 7. THE MINIMAL VIABLE BUILD (staged; each shortcut killed+probed before the next layer)
- **MVP-0 world+death (~1wk):** `rtc_world.py` (field+vents+advection, DECORRELATED channel innovations, <300 ln), `rtc_perception.py` (2-channel noisy/lagged read, the no-oracle seam, <120 ln), `rtc_metabolism.py` (full-support w_i, eat/toxin, <150 ln), `config/prereg_rtc.py` (K=4, bands=5, V=6, M=4, radius=6, pop, thresholds). **GATE G0 (ship-blocking world-validity):** solo/mute creature STARVES (reservoir-dies positive control) AND `clock_only` null stays at solo floor. (Run a difficulty-calibration pilot with a hand-coded near-optimal forecaster BEFORE freezing the field params — the S4 trap.)
- **MVP-1 fusion+RELAY language (~1wk):** wire `FactoredSpeaker`/`FactoredListener` via `cotrain_factored` (gradient EMIT, dense self-sup target = speaker's own fused forecast) + multi-partner aggregation (hub expresses ≥4 levels/utterance). **GATE G1:** fusion +lift over solo (body-follow null fails); held-out-JOINT grown-code vs holistic-codebook null (S1 attribution — MAY SHIP NULL per GCRL); single-factor-mute does NOT preserve eat-success (anti per-message holistic collapse).
- **MVP-2 WM monitor (~1wk):** per-creature RSSM representation-only; CTM policy over decoded+filtered latent. **GATE G2 (Wall-5 dream test):** WM latent decodes flow/missing-channel ABOVE the untrained-reservoir null + time-matched input baseline, clean CI ≥6 seeds.
- **MVP-3 reproduction+society (~1wk):** birth/death + Kirby bottleneck at pop ~120. **GATE G3:** shared compositional code grows (mii_cross self≈cross above chance).
- **MVP-4 cooperation+within-life reputation (~1-2wk):** donation + LOCAL gossip-as-single-events + within-life CTM recurrent trust reader (NO inherited trust params); reuse `pcgr_replicator` strategy-gene layer but REPLACE its reputation-scalar broadcast with the event stream; defector-invasion BAND driver. **GATE G4:** S6 battery {history_shuffled, type_broadcast, single_event} all collapse cooperation; balanced rep-AUC>0.6; S3 band basin-escape-rate open>drift CI-clean at EVERY init (≥20 seeds, paired RNG, frozen blocking gate).
- Reuse verbatim: `ctm_cell`, `mortal_channel`, `mortal_generations`, `live_world_model`, `live_probe_tap`, `live_social_metrics`, `pcgr_replicator` (replicator layer ONLY — scalar broadcast REPLACED by event stream), `spatial_referent`, verdict/CI harness, `test_coop_redline`.

## 8. Honest scope (what ships even if the hard wall holds)
If grown held-out-JOINT compositionality returns NULL (the GCRL-likely outcome), the build STILL delivers, scoped honestly: "a from-scratch living society where (S4) world-modelling is survival-critical and beats a reservoir, (S5) distributed perception makes a grown channel load-bearing for an embodied fusion act (body-follow fails), (S6) cooperation rides a within-life-integrated reputation that single_event/history_shuffle collapse, and (S3) cooperation is a viscous-population attractor across an invasion band — while the SPEAKER grows only a HALF-compositional code." A real multi-shortcut-killing contribution AND a clean break-or-falsify of the one unbroken wall.

---

## Shortcut-kill table (S1-S6 + how each is verified dead)
- **S1 HOLISTIC** — RELAY-AND-AGGREGATE (full-support w_i forces fusing ≥2 diverse-basis partners; hub re-expresses ≥4 levels/M=4 utterance over 625 referents → per-message combinatorial, holistic info-theoretically dead). VERIFY: held-out-JOINT beats a size-V^M holistic-codebook null; mute/scramble collapse fusion to solo floor.
- **S2 BRUTE-FORCE/CLOCK** — un-enumerable field + DECORRELATED innovations (clock <0.03 variance). VERIFY: frozen `clock_only` null stays at solo floor; else WORLD invalid.
- **S3 BASIN-LOTTERY** — large (150) VISCOUS (local gossip/partner-choice) population + defection pressure + lineage. VERIFY: pre-reg defector-invasion BAND, ≥20 seeds, paired RNG, basin-escape-RATE primary, open>drift CI-clean at EVERY init; gate FROZEN blocking.
- **S4 THIN-PERCEPTION** — hidden advection-diffusion PDE (2-of-4 noisy+lagged; eat-site moves every step). VERIFY: reservoir STARVES; WM latent decodes flow/missing-channel ABOVE untrained-reservoir null + time-matched baseline.
- **S5 FLOCKING** — distributed partial perception (full-support need vs 2-channel sensing; followable neighbour = strict subset). VERIFY: body-follow null 0 lift; co-location-only null collapses to lone-agent survival (ship-blocking); advection makes "where a crowd eats now" stale on arrival.
- **S6 DECODE-EQUIVALENCE** — within-life temporally-integrated reputation (single events accumulated in CTM recurrent state, not inherited, not a world-scalar). VERIFY: {history_shuffled, type_broadcast, single_event} all collapse cooperation; survive single_event → ship NULL.

## Pre-registered falsifiers
- **S1 attribution:** grown held-out-JOINT 95% CI upper ≤ holistic-codebook null → ship HALF_COMPOSITIONAL null (S1 holistic-kill survives; grown-code claim does not).
- **S1 world-validity:** eat-success survives muting all-but-one channel-message → per-message holistic indexing → WORLD INVALID, redesign.
- **S4 anti-reservoir:** (trained-WM − untrained-reservoir) value-added 95% CI upper ≤0 (selectivity control present, ≥6 seeds) → S4 not killed (world too thin).
- **S4 clock:** `clock_only` reaches fusion lift → WORLD INVALID.
- **S5:** open-vs-SCRAMBLE 95% CI lower ≤0.05 OR body-follow/co-location null reaches fusion lift → S5 not killed.
- **S6:** cooperation survives `single_event` → one-shot decoding → ship NULL (do not rebrand as gossip).
- **S3:** open-vs-drift not CI-clean at EVERY init across the band (≥20 seeds, paired RNG) → basin luck → S3 not killed; do not soften the frozen gate.
- **Integration-trap:** any combined-stage gain not decomposable by its single dedicated knockout → ship INCONCLUSIVE.
- **No-oracle:** forbidden-token scan + behavioral-invariance; self-supervised EMIT target must be the speaker's OWN observation → else HARD_REJECT.

## Honest risk (verbatim from the synthesis)
Kills S1..S6 by construction ONLY after adopting all four hunts' patches, but inherits the ONE unbroken wall: grown MULTI-ATTRIBUTE JOINT compositionality (CTM-GCRL HALF_COMPOSITIONAL; Wall-2 4/4 NULL). Making a hub NEED 4 levels/utterance makes S1 PRESSURE real but does NOT guarantee a speaker GROWS a JOINT-generalizing code. Highest-probability outcome: G1 ships a HALF_COMPOSITIONAL null while S4/S5/S6/S3 pass. Second risk: from-scratch CTM policy may not learn to ACT on fusion (imagination-RL never learned the hunt) — mitigated by WM-as-monitor + real-env policy + scripted-forage fallback that still probes whether the GROWN channel is load-bearing. Third: tuning S4 so a reservoir dies but trained-WM beats it is fragile (the Wall-5 trap) — needs a difficulty-calibration pilot with a hand-coded near-optimal forecaster BEFORE freezing. Fourth: within-life recurrent reputation at pop 120 with per-creature gradient EMIT is compute-heavy — needs a batched refactor (GPU at MVP-2+); shared-brain-per-lineage may be needed without breaking selection variance.
