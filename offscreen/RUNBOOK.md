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
- **Seed-parallelism (C2X3+):** `C2X3_WORKERS=N` parallelizes seeds; default `1` (serial, byte-stable).
  Cap workers (do NOT saturate): ~6 on a 16-core box. Verified byte-identical to serial (see Gate below).

## Stages (the g1f arc, in order)

### g1f — survival-selected channel (5 arms)
```
RTC_G1F_FORMAL=1 RTC_G1F_COMMBLIND_SEEDS=48 python -m offscreen.rtc_g1f_commblind_control
```
→ `rtc_g1f_commblind_verdict_formal48.json`, `rtc_g1f_reconciled_verdict.json`. (Canonical g1f command;
see CLAIM_LEDGER g1f row.) Result: channel co-evolves, kin-scoped.

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
