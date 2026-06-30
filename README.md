# Grown Grounded Language

**A from-scratch ALife study of whether a *decodable* signalling code can grow under survival
selection alone — and whether what grows is a public language or a private kin code.**

This repository backs the paper **"A Decodable Signalling Code Co-evolves but Stays Private to
Kin: Survival Selection, Clonal Descent, and Why No Public Code Bootstrapped in a Minimal
World"** (submitted to *Artificial Life*, MIT Press), and its 2-page compression as an
**ALIFE 2026 Late-Breaking Abstract** ("Survival Selection Grows a Private Kin Code, Not a
Public Language").

- Journal manuscript: `paper/ggl.tex` → `paper/ggl.pdf`
- ALIFE-2026 late-breaking abstract: `paper/lba_g1f.tex` → `paper/lba_g1f.pdf`
- Archived snapshot (cite this): Zenodo concept DOI **10.5281/zenodo.21074235** (tag `v2.0-g1f`)

> The earlier "Five Walls" late-breaking abstract (`paper/lba.tex`, frozen at tag
> `v1.0-alife2026`) is **superseded** by the g1f arc above and is kept only as a historical
> artifact. Do not read it as the current result.

---

## The headline result (honest, scoped)

In a minimal hand-coded 2-D lethal-vent world, tiny tied code-table agents (initialised from
`N(0,1)`, no gradient on communication, no oracle, no borrowed weights) evolve a **decodable**
communication channel under survival selection. The result **decomposes**:

- The architecture-matched **random-fitness control** — identical in every way except the
  reproduction-fitness signal (survival vs uniform-random, reproduction RNG byte-matched) —
  also fixates to ~one lineage and already reaches mutual intelligibility (MII) **0.1174**
  (~73× the 1/625 ≈ 0.0016 chance floor). This is the clonal-descent baseline, not zero.
- At the pre-registered gen-28 fixation point, survival selection adds a **paired win-margin of
  +0.0548 (95% CI [0.0234, 0.0849], n=48)**: survival-arm MII **0.17219** vs control **0.1174**.
  Selection therefore *sharpens* a largely descent-determined channel rather than originating it.
- A secondary, post-hoc transient probe (n=24) shows this margin is a **transient acceleration**
  that decays to a CI including zero by ~gen 100 as the control's own clonal fixation catches up.
- The code stays **private to kin**: the survival arm fixates to a single founder lineage
  (dominant-lineage share **99.1%**, N_eff **1.02**), so within-founder MII runs ≈0.16 (~100×
  chance) while cross-founder MII sits at the floor.
- **No public cross-lineage code bootstraps.** Even when diversity is actively sustained
  (niching at pop=96, soft96: N_eff 4.10 over 20+ coexisting generations) and even when survival
  is made to depend on decoding non-kin (three heterogeneous interventions C2X/C2X2/C2X3),
  cross-founder MII never leaves the floor; where the pressure bites, survival crashes. We name
  this a **pressure-vs-survival tension**. (Cross-lineage probes are n=8: positive-or-inconclusive
  tier — reported as "did not bootstrap under the regimes tested," not a formal negative.)

### The attack-machine (methodology contribution)

Every claim must survive an **architecture-matched control**, a **fair baseline**, **≥6-seed
bootstrap-CI win-margins**, **frozen pre-registration**, a **no-oracle redline**, and
**code-grounded adversarial review**. The single methodological claim is **bidirectionality**:
the audit is built to catch *deflation* as readily as inflation. It demonstrably did, twice, on
this project's own headline: (1) a pilot/formal false *negative* that had buried a real effect,
and (2) an RNG-offset bug in the headline control whose fix *strengthened* the margin
(+0.045 → +0.0548).

---

## Setup

Python ≥ 3.10. Mirrors `.github/workflows/ci.yml` (CPU-only Torch):

```bash
python3 -m venv .venv && . .venv/bin/activate          # use `python3`; `python` may be unset
pip install --index-url https://download.pytorch.org/whl/cpu torch   # CPU wheel (avoids the large CUDA download)
pip install -r requirements.txt
python -m pytest tests/ -q                              # expected: 24 passed
```

## Reproducing the headline numbers

Python, CPU/GPU, deterministic per seed. Run as **modules from the repository root**. The
heavy runs cannot be CI-automated; the exact per-stage commands, env vars, and expected
verdicts are in **`offscreen/RUNBOOK.md`** (paired with `ARCHITECTURE.md` and the claim ledger
`offscreen/CLAIM_LEDGER.md`). The g1f headline:

```bash
# headline: RNG-fixed random-fitness control, n=48 (the SOLE source of every headline number)
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_COMMBLIND_SEEDS=48 \
  python -m offscreen.rtc_g1f_commblind_control
#   -> offscreen/rtc_g1f_commblind_verdict.json (banked as ..._formal48_rngfix.json):
#      survival MII 0.17219 vs random-fitness 0.1174, paired margin +0.0548 [0.0234, 0.0849]

# lineage composition (kin-privacy)
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_LINEAGE_SEEDS=48 \
  python -m offscreen.rtc_g1f_lineage_share
#   -> rtc_g1f_lineage_share_verdict.json: dominant-share 99.1%, N_eff 1.02

# transient probe (margin decays to gen 150)
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_TRANSIENT_SEEDS=24 \
  RTC_G1F_TRANSIENT_CKPTS=28,56,100,150 python -m offscreen.rtc_g1f_transient_probe
```

The kin-only diagnostic and the C1 / C2X / C2X2 / C2X3 cross-lineage probes (and the
parallel-equivalence gate) are documented stage-by-stage in `offscreen/RUNBOOK.md`. Paper
figures regenerate from the committed verdict JSONs via `python paper/make_figs.py`.

```bash
# fast invariant tests (these ARE in CI) — includes the no-oracle redline scan
python -m pytest tests/ -q          # expected: 24 passed
```

> Companion probes `g1d` (world-state grounding) and `g1e` (use-emerges-under-selection) are
> retained in `offscreen/` and cited once in the paper as supporting / out-of-scope.

---

## Repository structure

```
rtc_*.py        RTC substrate at repo root: rtc_world, rtc_language, rtc_metabolism,
                rtc_perception, rtc_fusion.
config/         frozen pre-registration: prereg_rtc.py (RTC world constants + env knobs).
systems/        from-scratch machinery (emergent channel, Kirby iterated learning, CTM cell).
offscreen/      experiment runners (rtc_g1f_* : coevolve, commblind_control, lineage_share,
                transient_probe, kinonly_diagnostic, c1/c2x/c2x2/c2x3) + the committed
                *_verdict.json behind every number, plus the canonical paper markdown
                (PAPER.md), the claim ledger (CLAIM_LEDGER.md), the runbook (RUNBOOK.md),
                the arc write-up (G1F_ARC_WRITEUP.md), and REFERENCES_VERIFIED.md.
tests/          test_rtc_smoke.py — import smoke + the no-oracle redline assertion.
paper/          ggl.tex/ggl.pdf (journal submission), lba_g1f.tex/.pdf (ALIFE-2026 LBA),
                figs/ + make_figs.py; lba.tex/fig_rtc/make_fig_rtc.py = frozen old "Five Walls" LBA.
ARCHITECTURE.md file-by-file map of the substrate.
```

---

## Honest limits

- The co-evolution headline is well powered (n=48) but the margin is **modest** and is a
  **transient acceleration** of a clonal-descent channel, not a sustained equilibrium
  difference; it is scoped to **this world, this architecture, and a 28-generation timescale**.
- The cross-lineage "no public code bootstrapped" outcome is **n=8 (positive-or-inconclusive
  tier), not a formal negative** (a formal negative would want n=16); we claim it *did not*
  bootstrap under the regimes tested, never that it *cannot*.
- **No-oracle redline:** the automated static scan (`_redline_scan`) covers the core
  co-evolution runner `rtc_g1f_coevolve.py` only; the cross-lineage runners
  (C2X/C2X2/C2X3) are enforced by construction and checked by code-grounded review, not by the
  automated scan.
- **Hard constraints (enforced by tests):** no oracle / ground-truth leakage into agent
  decisions; no borrowed pretrained weights (architectures may be borrowed, weights are grown
  from `N(0,1)`); frozen pre-registration thresholds (no goalpost-moving).

---

## AI-assisted methodology disclosure

AI-based tools assisted with code implementation and manuscript drafting/editing. All
scientific claims, data, analyses, and conclusions are the author's own and were verified by
the author, who takes full responsibility for the content. The discipline that makes the
results trustworthy is the bidirectional self-audit described above: no claimed "win" was
banked without surviving an architecture-matched control, a fair baseline, ≥6-seed bootstrap-CI
win-margins, frozen pre-registration, a no-oracle redline, and code-grounded adversarial review.

---

## License and how to cite

**Code & artifacts:** MIT License (see `LICENSE`).  **Paper text & figures:** © 2026 Chunxuan
Yang, CC BY 4.0.

Please cite the *Artificial Life* paper (and the archived code via the Zenodo concept DOI
**10.5281/zenodo.21074235**). A BibTeX entry will be finalized on acceptance; until then cite as:

```
Chunxuan Yang (2026). A Decodable Signalling Code Co-evolves but Stays Private to Kin:
Survival Selection, Clonal Descent, and Why No Public Code Bootstrapped in a Minimal World.
Submitted to Artificial Life (MIT Press). Code: https://github.com/yangchunxuan/grown-grounded-language
(Zenodo DOI 10.5281/zenodo.21074235).
```
