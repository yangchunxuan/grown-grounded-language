#!/usr/bin/env bash
# Reproduce the g1f-arc headline behind "A Decodable Signalling Code Co-evolves but Stays
# Private to Kin" (Artificial Life submission) + the ALIFE 2026 late-breaking abstract.
# Papers: paper/ggl.tex (journal) and paper/lba_g1f.tex (ALIFE-2026 LBA).
#   NOTE: paper/lba.tex is the FROZEN, superseded "Five Walls" LBA (tag v1.0-alife2026) — not current.
# Run from the repo root. Deterministic per seed. Heavy stages are documented in
# offscreen/RUNBOOK.md; this script runs the headline g1f arc + the invariant tests.
set -e
export PYTHONUTF8=1

echo "== g1f headline: RNG-fixed random-fitness control, n=48 (SOLE source of headline numbers) =="
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_COMMBLIND_SEEDS=48 \
  python -m offscreen.rtc_g1f_commblind_control
#   -> offscreen/rtc_g1f_commblind_verdict.json (banked as ..._formal48_rngfix.json):
#      survival MII 0.17219 vs random-fitness 0.1174, paired margin +0.0548 [0.0234, 0.0849]

echo "== g1f lineage composition (kin-privacy: dominant-share 99.1%, N_eff 1.02) =="
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_LINEAGE_SEEDS=48 \
  python -m offscreen.rtc_g1f_lineage_share

echo "== g1f transient probe (margin decays to a CI including zero by ~gen 100) =="
RTC_G1F_FORMAL=1 RTC_TOXIC_DEATH=-0.9 RTC_G1F_TRANSIENT_SEEDS=24 \
  RTC_G1F_TRANSIENT_CKPTS=28,56,100,150 python -m offscreen.rtc_g1f_transient_probe

echo "== regenerate the paper figures from the verdict JSONs =="
python paper/make_figs.py

echo "== invariant tests (the no-oracle redline scan is the load-bearing guard) =="
python -m pytest tests/ -q

echo "Done. The kin-only diagnostic and the C1/C2X/C2X2/C2X3 cross-lineage probes are heavier;"
echo "see offscreen/RUNBOOK.md for their exact commands. Verdicts: offscreen/*_verdict.json."
