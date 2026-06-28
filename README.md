# Grown Grounded Language

**From-scratch agents that try to GROW a shared, decodable, grounded language — and an
adversarial self-audit that keeps catching us when we think we've succeeded.**

Grown Grounded Language is a research codebase for **emergent grounded communication and cooperation** in
small multi-agent worlds. The standing goal of the field — and of this project — is a
population of *from-scratch* creatures that **grows** a language which is

- **shared** (one agent can decode another's symbols),
- **decodable / grounded** (symbols carry world content we can read with probes), and
- **load-bearing** (the language causally helps the agents survive and cooperate, not
  merely present).

This repository backs an **ALIFE 2026 Late-Breaking Abstract** that reports, honestly, that
we did **not** reach that goal — and argues that the *methodology we used to keep ourselves
honest* is the more useful contribution. The headline is a negative result with a precise
diagnosis, plus a small set of scoped, audited positives.

> **This project is a standalone language + cooperation + world-model research program**, factored
> out of a larger internal ALife sandbox so the communication research stands on its own with
> no external dependency.

---

## The headline result (honest)

Across five distinct attempts to make a *grown* channel become load-bearing, we banked
**zero clean wall-breaks**. Every apparent success, when stress-tested, turned out to be a
**cheap shortcut the world allowed** rather than real grown language. The convergent
diagnosis:

> **The bottleneck is the world, not the brain or the optimizer.** Structure does not grow
> in worlds too small to require it; *installed* structure works, but it does not *emerge*.

To check this, we built a shortcut-proof world (a **Relay-Tide Commons (RTC)**: a 2D living
micro-society on a torus where survival depends on decoding and relaying messages about a
hidden tidal nutrient field that no single body can sense). Inside it, with the same audit
rig applied, we get:

| Result | What it shows | Status |
|---|---|---|
| **g1d — lethal signaling** | A *separately trained* grown channel's content (specifically its content-to-location **binding**) is **relatively** load-bearing for survival vs. degraded controls. | Scoped positive |
| **g1e — use emerges under selection** | A heritable "trust" gene that gates *using* the channel is **selected up** under real content but not under scrambled content or no selection. | Scoped positive (adoption, not de-novo emergence) |
| **g1f — does the channel co-evolve?** | Starting from **random** speaker/listener weights under survival selection alone, the channel does **not** grow into a load-bearing one. An apparent intelligibility rise was exposed as **clonal descent-convergence** by a communication-blind control. | **Clean negative** |

So: a grown channel can be *adopted* and can be *relatively* useful when handed to the
agents, but it **does not grow from scratch under selection** — the signaling-bootstrap
deadlock holds. The core goal remains unreached.

### The attack-machine (methodology)

A result counts **only if it survives all four checks simultaneously**:

1. an **architecture-matched null** (same parameters/recurrence, mechanism ablated — e.g. an
   untrained random reservoir, a frozen-random channel);
2. a **fair baseline** the mechanism must beat by design;
3. **≥6 seeds with a bootstrap CI on the win-margin** (treatment − null), not on the
   treatment alone; and
4. an **adversarial red-team** that actively tries to construct a confound.

As an executable protocol — a result is banked only if **every** row passes:

| Step | Required artifact | Pass criterion |
|---|---|---|
| Null | matched-architecture ablation | win-margin CI > 0 vs. null |
| Baseline | fair non-mechanistic baseline | treatment beats baseline |
| Seeds | ≥6 seeds | bootstrap CI on the margin |
| Red-team | written confound report | no surviving shortcut |
| Verdict | committed JSON / log | reproducible from seeds |
| Replication | separate machine / model | same headline verdict |

This rig caught **six** of our own apparent wins as artifacts (e.g. a "+0.10" world-model
denoising gain that an untrained reservoir beat by 3–4×; a channel "intelligibility rise"
that did not separate from a communication-blind random-fitness control). The negatives in
this repo are *earned* — the rig was in the room when the most attractive numbers landed.

---

## The paper

> **Chunxuan Yang.** *Five Walls to a Grown Grounded Language: An Adversarial Self-Audit of
> Emergent Communication.* ALIFE 2026, Late-Breaking Abstract. Sogang University, Seoul,
> Republic of Korea.

Source: `paper/lba.tex` (with `paper/fig_rtc.pdf` and the compiled `paper/lba.pdf`). The figure
`fig_rtc` is regenerated directly from the committed verdict JSONs by `make_fig_rtc.py`, as described
below.

---

## Reproducing the headline numbers

All experiments are pure NumPy + Python, CPU-only, and deterministic per seed. Run them as
**modules from the repository root** (they import `config.prereg_rtc` and `offscreen.*`).
Tunable knobs are environment variables; verdict filenames embed the prereg values
(`RTC_SENSOR_SIGMA`, `RTC_TOXIC_DEATH`) so each run is self-labeling.

```bash
# from the repo root
export PYTHONUTF8=1
```

### g1d — lethal signaling (24 seeds): content binding is load-bearing vs. controls

```bash
RTC_SENSOR_SIGMA=0.3 RTC_TOXIC_DEATH=-0.9 RTC_LE_SEEDS=24 \
  python -m offscreen.rtc_g1d_lethal
# writes offscreen/rtc_g1d_lethal_verdict_sig0.3.json
```

Expected (from `offscreen/rtc_g1d_lethal_verdict_sig0.3.json`): survival —
**fusion 0.58**, scramble 0.08, **misroute 0.04**, mute 0.04, oracle 1.00 (fenced
reference). The decisive **misroute** control (correct content, broken
content-to-location binding) dies, isolating that the *binding*, not mere signal presence,
carries survival.

### g1e — content-use emerges under selection (8 seeds)

```bash
RTC_SENSOR_SIGMA=0.3 RTC_TOXIC_DEATH=-0.9 RTC_EM_SEEDS=8 \
  python -m offscreen.rtc_g1e_emerge
# writes offscreen/rtc_g1e_emerge_verdict_tox-0.9.json
```

Expected (from `offscreen/rtc_g1e_emerge_verdict_tox-0.9.json`): the trust gene rises from
~0.17 to **0.96** under real content, but stays at the mutation floor (~0.30 scramble,
~0.41 drift). Verdict `RTC_G1E_CONTENT_USE_EMERGES`.

### g1f — does the channel co-evolve from random init? (clean negative, 6 seeds)

Run the g1f **formal** block
(not the cheap pilot) with `RTC_G1F_FORMAL=1`:

```bash
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_SEEDS=6 \
  python -m offscreen.rtc_g1f_coevolve
# writes offscreen/rtc_g1f_coevolve_verdict.json

# communication-blind control (the one that exposes the artifact):
python -m offscreen.rtc_g1f_commblind_control
```

Expected (from `offscreen/rtc_g1f_coevolve_verdict.json`): the only arm whose cross-agent
mutual intelligibility (MII) moves off the bootstrap floor is `shared_weights_kin`
(final MII ≈ **0.124** vs. its architecture-matched null `shared_frozen_random` ≈ 0.002) —
but that rise is **not** load-bearing: survival does **not** co-rise with MII, and a
communication-blind random-fitness control reaches the same MII level (clonal
descent-convergence). Verdict `RTC_G1F_MII_MOVES_NOT_LOAD_BEARING` — i.e. the channel does
not co-evolve.

### Tests

```bash
PYTHONUTF8=1 python -m pytest tests/ -q
```

`tests/test_rtc_smoke.py` import-checks every RTC module and asserts the **no-oracle redline**:
each RTC harness ships a static scan (`_redline_scan()` in `offscreen/rtc_g1f_coevolve.py`) that
rejects forbidden ground-truth access, so an agent's decision reads only its decoded channel, its
own body, and heard messages — never the true field. (The true field is read only by `eat()`
resolution and the clearly-fenced `oracle` reference arm.)

---

## Repository structure

This is a **minimal companion repository** trimmed to exactly what backs the paper.

```
rtc_*.py        RTC substrate at repo root: rtc_world, rtc_language, rtc_metabolism,
                rtc_perception, rtc_fusion.
make_fig_rtc.py regenerates paper/fig_rtc.pdf from the committed verdict JSONs.
reproduce.sh    re-runs g1d / g1e / g1f + tests + figure.
systems/        the from-scratch machinery the RTC experiments need: the emergent
                channel (mortal_channel), Kirby iterated learning (mortal_generations),
                mortal_death, mortal_metrics, and the CTM continuous-thought cell (ctm_cell).
config/         frozen pre-registration: prereg_rtc.py (RTC world constants + env knobs)
                and prereg_mortal.py.
offscreen/      the RTC experiment runners (rtc_g0/g1/g1b/g1c/g1d/g1e/g1f_coevolve +
                rtc_g1f_commblind_control) + the committed *verdict.json that back every
                number in the paper, plus WALLS_VERDICT.md, CTM_ARC_WRITEUP.md, and
                STAGE_RICH_WORLD_RTC_SPEC.md.
tests/          test_rtc_smoke.py — import smoke + the no-oracle redline assertion.
paper/          lba.tex, fig_rtc.pdf, the compiled lba.pdf, and the ALIFE style file.
```

---

## Honest status and limitations

- **The core goal is not achieved.** A load-bearing grounded language that *grows* from
  scratch under selection has not been demonstrated. The positives live *inside constructed
  worlds*; g1d is *relative* (vs. degraded controls), not absolute, and inside a narrow
  stakes window in a world built to make content matter; g1e is *adoption* of a
  separately-trained channel, not de-novo emergence; g1f is a clean negative on co-evolution.
- **Recurring obstacle: world design + a grounding/fidelity ceiling.** A grown channel can
  carry information yet remain too imprecise, or too easily bypassed, to be load-bearing.
- **Internal disagreement is documented, not hidden.** `offscreen/WALLS_VERDICT.md` is an
  adversarial internal audit (in Chinese) arguing that several "walls" were closed
  *prematurely* — that some failures were a handful of tried architectures plus a failure
  mechanism, packaged as impossibility, rather than proven dead ends. The published abstract
  uses the calibrated, defensible framing ("each wall fell to a cheap shortcut"); the raw
  machine verdicts (which never write "CLOSED" or "THEOREM") are the source of truth, and
  they are all included so readers can judge for themselves.
- **Hard constraints (non-negotiable, enforced by tests):** no oracle / ground-truth leakage
  into agent decisions; **no borrowed pretrained weights** (no LLM/Qwen — architectures and
  methods may be borrowed, weights are trained from scratch on this world); frozen
  pre-registration thresholds (no goalpost-moving).
- **Scope:** small CPU experiments (single-digit-to-low-dozens of seeds, populations of
  ~12–40). Compute was never the bottleneck; method and task design were.

---

## AI-assisted methodology disclosure

This work used **multiple AI coding agents** for implementation and an **adversarial
multi-agent red-team** for verification — and this protocol is itself part of the
contribution, not an incidental tool. The discipline that makes the results trustworthy is
that no agent's claimed "win" was accepted without surviving the four-check attack-machine
(architecture-matched null, fair baseline, ≥6 seeds with a bootstrap CI on the win-margin,
adversarial red-team). Headline results were **independently reproduced on a separate
machine by a different model** and audited for oracle leakage. The human author (Chunxuan
Yang) set the goals, the frozen pre-registration thresholds, and the redlines, and made the
final claims.

---

## License and how to cite

**Code & artifacts:** released under the **MIT License** (see `LICENSE`).
**Paper text & figures:** © 2026 Chunxuan Yang, **CC BY 4.0**.

```bibtex
@inproceedings{yang2026fivewalls,
  title     = {Five Walls to a Grown Grounded Language:
               An Adversarial Self-Audit of Emergent Communication},
  author    = {Yang, Chunxuan},
  booktitle = {Proceedings of the 2026 Conference on Artificial Life (ALIFE)},
  series    = {Late-Breaking Abstracts},
  year      = {2026},
  address   = {Sogang University, Seoul, Republic of Korea}
}
```

If you use the **self-audit protocol** (architecture-matched nulls + communication-blind
controls + win-margin CIs + adversarial red-team), please cite the abstract above. We
suggest emergent-communication claims be reported against architecture-matched nulls and
communication-blind controls as standard.
