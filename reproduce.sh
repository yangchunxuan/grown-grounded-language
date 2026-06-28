#!/usr/bin/env bash
# Reproduce the headline results behind the ALIFE 2026 LBA.
# Run from the repo root.  Pure NumPy/Python, CPU-only, deterministic per seed.
set -e
export PYTHONUTF8=1

echo "== g1d: lethal signaling (content binding load-bearing, 24 seeds) =="
RTC_SENSOR_SIGMA=0.3 RTC_TOXIC_DEATH=-0.9 RTC_LE_SEEDS=24 python -m offscreen.rtc_g1d_lethal

echo "== g1e: content-use emerges under selection (8 seeds) =="
RTC_SENSOR_SIGMA=0.3 RTC_TOXIC_DEATH=-0.9 RTC_EM_SEEDS=8 python -m offscreen.rtc_g1e_emerge

echo "== g1f: does the channel co-evolve from random init? (clean negative, 6 seeds) =="
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_SEEDS=6 python -m offscreen.rtc_g1f_coevolve
echo "== g1f communication-blind control (exposes the descent-convergence artifact) =="
python -m offscreen.rtc_g1f_commblind_control

echo "== regenerate the paper figure from the verdict JSONs =="
python make_fig_rtc.py

echo "== test suite (the no-oracle redline is the load-bearing guard) =="
python -m pytest tests/ -q

echo "Done. See offscreen/*_verdict.json and paper/fig_rtc.pdf."
