# RUNBOOK — how to run each experiment (reproducibility for a fresh agent / future-you)

These heavy runs CANNOT be CI-automated (GPU/CPU, minutes–hours). This is the version-controlled recipe
so the commands are never lost. Pair with: `ARCHITECTURE.md` (what each file is), `CLAIM_LEDGER.md` (what
was concluded + which verdict@commit is the evidence), and each verdict JSON's `provenance` block (how
THAT result was produced). Run all commands from the repo root.

## Conventions
- `RTC_G1F_FORMAL=1` = formal config (pop/gens/MII-sample per `config`); `=0` = fast PILOT (smoke only).
- `RTC_TOXIC_DEATH=-0.9` is the lethal-world default (set automatically by the harness).
- **Tier rule (frozen):** a run at **n≤8 may only conclude POSITIVE or INCONCLUSIVE — never a scoped
  negative**; bank a negative only at **n=16**.
- **Determinism:** every run is seeded; same command+commit → byte-identical verdict. Re-running OVERWRITES
  the working verdict JSON — the banked version is preserved in git at the commit the ledger cites.
- **Provenance anchors (READ THIS):** the public git history was normalized to a single author, so any
  historical commit hash (`@…`) shown in these docs is **NOT reachable** in the current public repository.
  Anchor each result by its **verdict filename**, which is present in (a) the current repo, (b) the archived
  **`v2.0-g1f`** release, and (c) the Zenodo deposit (DOI `10.5281/zenodo.21074235`); regenerate via the
  commands below. A verdict's embedded `provenance.git_commit` likewise refers to the pre-normalization
  history (and may record a `git_dirty` base commit), so the durable identifier is the **filename + JSON
  contents**, never a commit hash.
- **Seed-parallelism (C2X3+):** `C2X3_WORKERS=N` parallelizes seeds; default `1` (serial, byte-stable).
  Cap workers (do NOT saturate): ~6 on a 16-core box. Verified byte-identical to serial (see Gate below).

## Stages (the g1f arc, in order)

### g1f — survival-selected channel (5 arms) [PREDATES this RUNBOOK; multi-step — verify vs git history]
```
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_COMMBLIND_SEEDS=48 python -m offscreen.rtc_g1f_commblind_control
```
→ writes `rtc_g1f_commblind_verdict.json`, banked as **`rtc_g1f_commblind_verdict_formal48_rngfix.json`** — the
RNG-FIXED random-fitness control (fake fitness drawn from an independent generator so the reproduction RNG is
byte-matched between arms). **This rngfix verdict is the SOLE headline source:** survival-arm MII 0.17219 vs
random-fitness 0.1174, paired margin **+0.0548, 95% CI [0.0234, 0.0849]**, n=48. The pre-rngfix
`rtc_g1f_commblind_verdict_formal48.json` and the derived `rtc_g1f_reconciled_verdict.json` /
`rtc_g1f_power_analysis.json` (via `rtc_g1f_reconcile.py` / `rtc_g1f_power_analysis.py`) hold the OLD +0.045 /
control-0.1271 and are **superseded legacy**. Result: channel co-evolves (RNG-matched control), kin-scoped.

**Lineage share (n=48):** `RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_LINEAGE_SEEDS=48 python -m offscreen.rtc_g1f_lineage_share`
→ `rtc_g1f_lineage_share_verdict.json` (dominant-share 99.1%, N_eff 1.02, 47/48 single-lineage).
**Transient probe (secondary, to gen 150, n=24):** `RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_TRANSIENT_SEEDS=24 RTC_G1F_TRANSIENT_CKPTS=28,56,100,150 python -m offscreen.rtc_g1f_transient_probe`
→ `rtc_g1f_transient_probe_verdict.json` (margin decays +0.0569 → +0.0249 across gen 28/56/100/150).

### kin-only diagnostic — why kin-only?
```
RTC_G1F_FORMAL=1 KINONLY_SEEDS=16 python -m offscreen.rtc_g1f_kinonly_diagnostic
```
→ `rtc_g1f_kinonly_diagnostic_verdict.json`. ~12 min. Result: INCONCLUSIVE_NO_WINDOW + directional (C).

### C1 — collapse probe (2×2 {hard,soft}×{16,96})
```
RTC_G1F_FORMAL=1 C1_SEEDS16=16 C1_SEEDS96=8 python -m offscreen.rtc_g1f_c1_collapse_probe
```
→ `rtc_g1f_c1_collapse_probe_verdict.json`. ~34 min. Result: A refuted, C supported (private codes).

### C2X — forced 100% non-kin listening
```
RTC_G1F_FORMAL=1 C2X_SEEDS=8 python -m offscreen.rtc_g1f_c2x_crosslineage
```
→ `rtc_g1f_c2x_crosslineage_verdict.json`. ~1 hr. Result: VIABILITY CRASH (auto-label CONTENT_FREE is a
mislabel — see ledger).

### C2X2 — ramped + stationary mixed scaffold
```
RTC_G1F_FORMAL=1 C2X2_POP=96 C2X2_GENS=48 C2X2_SEEDS=8 python -m offscreen.rtc_g1f_c2x2_ramped
```
→ `rtc_g1f_c2x2_ramped_verdict.json`. ~40 min. Result: FALSE-NEGATIVE RISK (pressure×diversity never
coincided; per-gen not logged — fixed in C2X3).

### C2X3 — forced-diversity quota + 0.5 non-kin (PARALLEL)
```
RTC_G1F_FORMAL=1 C2X3_POP=96 C2X3_GENS=48 C2X3_SEEDS=8 C2X3_K=4 C2X3_M=4 C2X3_WORKERS=6 \
  python -m offscreen.rtc_g1f_c2x3_forced
```
→ `rtc_g1f_c2x3_forced_verdict.json`. ~28 min @ 6 workers. Result: DESIGN_FAILURE_VIABILITY_CRASH (0.5
still boom-busts survival; CF never leaves floor). Knobs: `C2X3_K`/`C2X3_M` (quota), `C2X3_WORKERS`.

## Smoke test (verify a runner runs + its startup invariants pass — fast, NOT a result)
```
RTC_G1F_FORMAL=0 C2X3_POP=16 C2X3_GENS=8 C2X3_SEEDS=2 C2X3_K=2 C2X3_M=2 python -m offscreen.rtc_g1f_c2x3_forced
```
Each runner prints `[equiv] ... OK` (MII fast==loop, quota K=0==soft, etc.) before any arm.

## Parallel-equivalence GATE (before trusting a parallel run)
Run the SAME short config both ways and assert byte-identical verdict:
```
RTC_G1F_FORMAL=1 C2X3_POP=96 C2X3_GENS=4 C2X3_SEEDS=2 C2X3_WORKERS=1 python -m offscreen.rtc_g1f_c2x3_forced
cp offscreen/rtc_g1f_c2x3_forced_verdict.json /tmp/ser.json
RTC_G1F_FORMAL=1 C2X3_POP=96 C2X3_GENS=4 C2X3_SEEDS=2 C2X3_WORKERS=4 python -m offscreen.rtc_g1f_c2x3_forced
diff /tmp/ser.json offscreen/rtc_g1f_c2x3_forced_verdict.json && echo BYTE-IDENTICAL
```

## Fast checks (these ARE in CI — `.github/workflows/ci.yml`)
```
python -m pytest tests/ -q     # harness invariants + no-oracle redline + smoke
```
