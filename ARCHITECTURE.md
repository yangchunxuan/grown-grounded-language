# ARCHITECTURE — grown-grounded-language (code map)

Purpose: a human-readable map so the codebase stays understandable (anti-"AI code-pile"). If you can't
follow a file from this map, that file is drifting — simplify it. No line numbers (they go stale); this
describes files, public functions, and the discipline. **Truth = `offscreen/CLAIM_LEDGER.md`**; README and
older paper drafts are OLD-FRAMED.

## What this project is
From-scratch (no borrowed/pretrained weights, no LLM) artificial-life study of whether a **decodable,
grounded communication channel** evolves under **survival selection** in a tiny hand-coded 2D world —
and the **attack-machine** methodology (matched nulls + fair baselines + bootstrap-CI + frozen
pre-registration + no-oracle + adversarial review) that keeps every claim honest.

## Layers
- **World + agents** (hand-coded, NOT learned): `rtc_world.py` (4-channel field, advection/diffusion/vents),
  `rtc_metabolism.py` (energy/eat/death), `rtc_language.py` (band<->value, scramble), `config/prereg_rtc.py`
  (frozen constants: RTC_K, RTC_BANDS, RTC_VOCAB, grid, etc.), `systems/mortal_channel.py`
  (FactoredSpeaker/Listener nets), `systems/mortal_generations.py` (Kirby imitation helpers).
- **Core harness**: `offscreen/rtc_g1f_coevolve.py` — agents, evolution, episodes, MII. THE shared engine.
- **Stage runners** (one per experiment; `offscreen/`): each evolves populations, logs, classifies, writes
  a `*_verdict.json`. See "Runners" below.
- **Specs** (`offscreen/STAGE_*.md`): frozen pre-registrations, one per stage.
- **Truth/record**: `offscreen/CLAIM_LEDGER.md` (per-claim epistemic ledger), `offscreen/G1F_ARC_WRITEUP.md`
  (the closed g1f arc), `offscreen/*_verdict.json` (results, with full config recorded).

## Core harness — `offscreen/rtc_g1f_coevolve.py` (public surface)
- **Config**: `PILOT` (env `RTC_G1F_FORMAL`), `G1F_POP/GENS/ROUNDS/VENTS/MII_SAMPLE/MUT/...`; `ARMS`, `CTRL`.
  Runners override `g1f.G1F_POP` / `g1f.G1F_GENS` at runtime for their scale.
- **Agents**: `Agent(speaker, listener, lineage)` dataclass. `UnifiedIO` = one TIED table
  `[K, BANDS, VOCAB]`; `emit` = argmax over symbols, `predict` = argmax over bands, `mutate` = Gaussian
  noise (emit & predict change together — load-bearing for the C2X convergence argument).
  `_new_unified_agent` (shared_weights_kin / shared_frozen_random arms) vs `_new_agent` (FactoredSpeaker/Listener).
- **Reproduction**: `_mutate(agent, seed, rng, *, preserve_lineage=False)` (kin arm keeps founder lineage);
  `_initial_pop_for(seed, arm)` (1 agent per founder lineage; `shared_*` arms use UnifiedIO).
- **Episode**: `_run_episode(seed, pop, mode="open", arm="", rng=None, speaker_rule=None)` → returns
  `{fitness, alive, alive_per_agent, rounds, food_pick_rate}`. **Additive params (default = original
  behavior, byte-stable):** `rng=` external paired-RNG hook (paired gate-0); `speaker_rule=` either a
  string (`"cross_lineage_balanced"`) OR a **callable** `(pop,i,j,gen_round)->speaker` (C2X3 mixed/ramped
  routing). `mode` ∈ {open, mute, scramble(=iid random / "random-token"), permute(=permuted real msg),
  oracle}.
- **Who speaks to whom**: `_speaker_for(pop, listener_i, post_i, gen_round, arm, speaker_rule=None)` —
  default kin (same-lineage) for `shared_weights_kin`; `"cross_lineage_balanced"` = forced non-kin
  round-robin (C2X); returns `None` if no non-kin present (caller falls back to mute).
- **Metric**: `_mii(pop, return_matrix=False)` (MII = referent→emit→decode→exact-tuple recovery; chance =
  1/N_REFERENTS). `_mii_matrix_fast(pop)` = vectorized full pop×pop MII for UnifiedIO, **byte-identical**
  to the loop (tested). Cross-founder MII (CF) / within-founder MII (WF) are computed by runners by
  filtering the matrix off-diagonal on `.lineage`.
- **Selection** (THREE variants — see DEBT #2): `_select_next` (hard top-50% truncation; original g1f),
  `_select_next_soft` (tournament-k2 on lineage-SHARED fitness `raw / gen-start-same-lineage-count`; C1
  niching), `_select_next_quota(...,K,m)` (reserve m offspring for top-K largest lineages, AUGMENT; **K=0
  == soft, byte-identical**; C2X3). All preserve_lineage for the kin arm.
- `_run_arm(seed, arm)` = the original g1f multi-arm experiment loop.

## Runners (`offscreen/`) — the g1f arc, in order
| runner | stage | mechanism | verdict json |
|---|---|---|---|
| `rtc_g1f_coevolve.py` (`_run_arm`) | g1f | survival-selected channel, 5 arms | `rtc_g1f_commblind_verdict_formal48.json` etc. |
| `rtc_g1f_kinonly_diagnostic.py` | diagnostic | why kin-only? CF vs WF vs floor | `rtc_g1f_kinonly_diagnostic_verdict.json` |
| `rtc_g1f_c1_collapse_probe.py` | C1 | 2×2 {hard,soft}×{16,96} niching | `rtc_g1f_c1_collapse_probe_verdict.json` |
| `rtc_g1f_c2x_crosslineage.py` | C2X | forced 100% non-kin listening | `rtc_g1f_c2x_crosslineage_verdict.json` |
| `rtc_g1f_c2x2_ramped.py` | C2X2 | ramped + stationary mixed scaffold | `rtc_g1f_c2x2_ramped_verdict.json` |
| `rtc_g1f_c2x3_forced.py` | C2X3 | diversity quota + 0.5 non-kin; **seed-parallel (C2X3_WORKERS)** | `rtc_g1f_c2x3_forced_verdict.json` |

**Common runner shape**: per arm → per seed (`_run_one_seed` in C2X3, parallelizable) → per gen
{`_mii_matrix_fast` → CF/WF; `_run_episode`; `_select_next_*`}; log per-gen trajectory; gate-0 paired eval;
classify against frozen pre-registered rules; write verdict JSON with full config/env/git-commit.

## Discipline (how this stays not-a-pile)
- **No-oracle redline**: agent decisions read only decoded messages + own body state + legal sensors —
  never true `world.patch`/edibility/target-code/founder-id-as-policy-input. World truth is fenced to the
  eat/consequence resolver + explicit oracle controls.
- **Frozen pre-registration**: a stage's SPEC is locked before the run; gates/labels are not moved after.
- **Verified-equivalence before trust**: any harness change ships with an equivalence/byte-stability test
  (MII fast==loop; quota K=0==soft; speaker_rule=None==original; seed-parallel==serial). This is the main
  defense against silent AI-introduced behavior drift.
- **Provenance**: every verdict JSON records env/seeds/formal/commit so treatment and controls are provably
  the same config (the g1f false-negative lesson). Reviews are code-grounded + adversarial.
- **Reproducibility system (fresh-agent-proof)**: `RUNBOOK.md` = exact command per stage (heavy runs can't
  be CI'd, but the recipes are version-controlled); new verdicts embed a `provenance` block
  (`rtc_g1f_common.make_provenance` → command + env + git_commit); `CLAIM_LEDGER.md` indexes each claim to
  `verdict-file @ commit` (git = the immutable evidence vault — re-runs overwrite the working file, the
  banked version stays frozen at its commit). Fast invariants run in CI (`.github/workflows/ci.yml`).

## KNOWN DEBT (fix in the "consolidation" pass, AFTER the active run; safety net = verdict reproduction)
1. **Helper duplication** — PARTIALLY ADDRESSED. `offscreen/rtc_g1f_common.py` is now the CANONICAL home
   for the shared metric/stats helpers (`cf_wf, neff, living_by_lineage, is_coexist, boot_ci, mean_nan,
   med_l2`) + `make_provenance`. `rtc_g1f_c2x3_forced.py` imports them (verified byte-identical: a small
   serial run pre/post-refactor diffed clean). The 4 older runners (diagnostic / c1 / c2x / c2x2) keep
   FROZEN inline copies alongside their already-banked verdicts — refactor-on-next-touch, NOT now (their
   results are git-frozen; touching them = risk without scientific reward). New runners import common.
   Still-duplicated runner-specific bits (`make_route`, `paired_eval`, `classify`) can move to common when
   a second runner needs them. **Documented divergence (not a bug):** the kin-only DIAGNOSTIC's `is_coexist`
   is the OLDER SINGLE gate (≥2 lineages each ≥3 living, NO N_eff term) — it predates the dual gate added in
   C1; common's `is_coexist` is the DUAL gate (+N_eff≥2.0). The diagnostic's gate is frozen + correct for
   its banked verdict; do NOT retrofit it (would change a banked result). So `common` matches C1/C2X/C2X2/C2X3,
   NOT the diagnostic.
2. **Three `_select_next*` variants** with overlapping logic → fold into one parameterized selector.
3. **Equivalence tests live inside each runner's `equivalence_test()` (run at startup)** → migrate to
   `tests/` + enforce in CI (see `.github/workflows/ci.yml`).
