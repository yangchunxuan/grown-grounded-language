"""RTC G1F: can a relay channel co-evolve from survival selection alone?

Cheap pilot first, by design. Speakers/listeners start random; no
cotrain_factored truth pretraining is used. The only scalar selection signal is
survival in the G1D lethal vent world. A Kirby-linked arm may imitate a parent's
utterances, but those utterances are not truth labels.
"""
from __future__ import annotations

import copy
import ast
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

os.environ.setdefault("RTC_TOXIC_DEATH", "-0.9")
import config.prereg_rtc as rc
from rtc_language import bands_to_values, scramble_message, values_to_bands
from rtc_metabolism import MetabolicState, eat, metabolic_vector
from rtc_world import RTCWorld
from offscreen.rtc_g1_run import _ci, _sensor_values
from systems import mortal_channel as mc
from systems.mortal_generations import _imitate, _seen_referents

ROOT = Path(__file__).resolve().parents[1]
FULL_BASIS = (0, 1, 2, 3)
G = rc.RTC_GRID

PILOT = os.environ.get("RTC_G1F_FORMAL", "0") in ("0", "", "false", "False")
G1F_SEEDS = list(range(int(os.environ.get("RTC_G1F_SEEDS", "3" if PILOT else "6"))))
G1F_POP = int(os.environ.get("RTC_G1F_POP", "8" if PILOT else "16"))
G1F_GENS = int(os.environ.get("RTC_G1F_GENS", "7" if PILOT else "28"))
G1F_ROUNDS = int(os.environ.get("RTC_G1F_ROUNDS", "22" if PILOT else "55"))
G1F_VENTS = int(os.environ.get("RTC_G1F_VENTS", "8" if PILOT else "12"))
G1F_STEP = int(os.environ.get("RTC_G1F_STEP", "3"))
G1F_HIDDEN = int(os.environ.get("RTC_G1F_HIDDEN", "24"))
G1F_MUT = float(os.environ.get("RTC_G1F_MUT", "0.035"))
G1F_KIRBY_EPOCHS = int(os.environ.get("RTC_G1F_KIRBY_EPOCHS", "10" if PILOT else "45"))
G1F_HOLD_FRAC = float(os.environ.get("RTC_G1F_HOLD_FRAC", "0.55"))
G1F_MII_MOVE_MIN = float(os.environ.get("RTC_G1F_MII_MOVE_MIN", "0.02"))
G1F_MII_SAMPLE = int(os.environ.get("RTC_G1F_MII_SAMPLE", "96" if PILOT else "625"))
ARMS = ("pure_selection", "kirby_linked", "shared_weights_kin", "frozen_random", "shared_frozen_random")
CTRL = ("open", "scramble", "mute", "oracle")


@dataclass
class Agent:
    speaker: object
    listener: object
    lineage: int


class UnifiedIO:
    """One tied code table used for both sending and receiving.

    For each channel, ``table[channel, band, symbol]`` chooses the emitted
    symbol by argmax over symbols and decodes a received symbol by argmax over
    bands. A mutation therefore changes encoder and decoder together.
    """

    def __init__(self, seed: int):
        rng = np.random.default_rng(int(seed))
        self.table = rng.normal(0, 1, (rc.RTC_K, rc.RTC_BANDS, rc.RTC_VOCAB)).astype(np.float32)

    def emit(self, referent):
        ref = tuple(int(x) for x in referent)
        return tuple(int(np.argmax(self.table[ch, ref[ch]])) for ch in range(rc.RTC_K))

    def predict(self, message):
        msg = tuple(int(x) % rc.RTC_VOCAB for x in message)
        return tuple(int(np.argmax(self.table[ch, :, msg[ch]])) for ch in range(rc.RTC_K))

    def predict_all(self, messages):
        return [self.predict(m) for m in messages]

    def mutate(self, rng: np.random.Generator, sigma: float):
        self.table += rng.normal(0, sigma, self.table.shape).astype(np.float32)


def _new_agent(seed: int, lineage: int) -> Agent:
    spk = mc.FactoredSpeaker(seed=int(seed), hidden=G1F_HIDDEN)
    lis = mc.FactoredListener(seed=int(seed) + 991, hidden=G1F_HIDDEN)
    spk._build(); lis._build()
    return Agent(spk, lis, int(lineage))


def _new_unified_agent(seed: int, lineage: int) -> Agent:
    io = UnifiedIO(seed)
    return Agent(io, io, int(lineage))


def _mutate(agent: Agent, seed: int, rng: np.random.Generator, *, preserve_lineage: bool = False) -> Agent:
    import torch

    child = copy.deepcopy(agent)
    child.lineage = int(agent.lineage if preserve_lineage else seed)
    if isinstance(child.speaker, UnifiedIO):
        child.speaker.mutate(rng, G1F_MUT)
        child.listener = child.speaker
        return child
    mods = []
    for module in (child.speaker, child.listener):
        if id(module) not in [id(m) for m in mods]:
            mods.append(module)
    with torch.no_grad():
        for module in mods:
            for p in module.parameters():
                p.add_(torch.randn_like(p) * G1F_MUT)
    if rng.random() < 0.15 and not preserve_lineage:
        child.speaker = mc.FactoredSpeaker(seed=int(seed) + 17, hidden=G1F_HIDDEN)
        child.speaker._build()
    return child


def _kirby_child(parent: Agent, seed: int, gen: int, rng: np.random.Generator) -> Agent:
    child = _mutate(parent, seed, rng)
    seen = _seen_referents(mc.N_REFERENTS, G1F_HOLD_FRAC, int(seed), int(gen))
    # Legitimate cultural bottleneck: imitate parent utterances, not vent safety.
    _imitate(child.speaker, parent.speaker.emit_all(), seen, G1F_KIRBY_EPOCHS, 1e-2, int(seed))
    return child


def _initial_pop(seed: int) -> list[Agent]:
    return [_new_agent(seed * 1009 + i * 17, i) for i in range(G1F_POP)]


def _initial_pop_for(seed: int, arm: str) -> list[Agent]:
    if arm in ("shared_weights_kin", "shared_frozen_random"):
        return [_new_unified_agent(seed * 1009 + i * 17, i) for i in range(G1F_POP)]
    return _initial_pop(seed)


def _posts(world: RTCWorld, seed: int):
    prng = np.random.default_rng(seed + 7001)
    vflat = np.asarray(world.vents).reshape(-1, 2)
    idx = prng.choice(len(vflat), min(G1F_VENTS, len(vflat)), replace=False)
    return [(int(vflat[i][0]) % G, int(vflat[i][1]) % G) for i in idx]


def _message_for(agent: Agent, world: RTCWorld, post, rng, mode: str):
    if mode == "mute":
        return None
    if mode == "scramble":
        return scramble_message(rng)
    vals = _sensor_values(world, post[0], post[1], FULL_BASIS, rng)
    return agent.speaker.emit(values_to_bands(vals))


def _decoded_score(agent: Agent, msg, w) -> float:
    if msg is None:
        return 0.0
    dec = agent.listener.predict(msg)
    return float(np.dot(w, bands_to_values(dec)))


def _speaker_for(pop: list[Agent], listener_i: int, post_i: int, gen_round: int, arm: str):
    if arm == "shared_weights_kin":
        same = [j for j, a in enumerate(pop) if a.lineage == pop[listener_i].lineage]
        if same:
            return pop[same[(post_i + gen_round) % len(same)]]
    return pop[(listener_i + post_i + gen_round + 1) % len(pop)]


def _run_episode(seed: int, pop: list[Agent], mode: str = "open", arm: str = "", rng=None):
    # rng kept optional for instrument-only paired gate-0 (kin-only diagnostic): passing the
    # SAME rng across open/mute/scramble removes the len(mode) drift below. Default = unchanged.
    if rng is None:
        rng = np.random.default_rng(seed * 41 + len(mode))
    world = RTCWorld(seed)
    for _ in range(40):
        world.step()
    posts = _posts(world, seed)
    weights = metabolic_vector(seed)
    states = [MetabolicState(rc.RTC_ENERGY_INIT) for _ in pop]
    food = np.zeros(len(pop), dtype=float)
    rounds = np.zeros(len(pop), dtype=float)
    for gen_round in range(G1F_ROUNDS):
        live = [i for i, st in enumerate(states) if st.alive]
        if not live:
            break
        for _ in range(G1F_STEP):
            world.step()
        true_edib = np.asarray([float(np.dot(weights, world.patch(px, py))) for px, py in posts])
        for i in live:
            if mode == "oracle":
                pick = int(np.argmax(true_edib))
            elif mode == "mute":
                pick = int(rng.integers(0, len(posts)))
            else:
                scores = []
                for j, post in enumerate(posts):
                    # Per-agent message; shared_weights_kin assimilates by lineage.
                    speaker = _speaker_for(pop, i, j, gen_round, arm)
                    msg = _message_for(speaker, world, post, rng, mode)
                    scores.append(_decoded_score(pop[i], msg, weights))
                pick = int(np.argmax(scores))
            out = eat(states[i], world.patch(*posts[pick]), weights)
            food[i] += int(out["outcome"] == "eat")
            rounds[i] += 1
    fitness = rounds + 0.25 * food + np.asarray([st.energy for st in states]) * 0.01
    return {
        "fitness": fitness,
        "alive": float(np.mean([st.alive for st in states])),
        "alive_per_agent": [bool(st.alive) for st in states],  # instrument-only: kin-only diagnostic coexistence gate
        "rounds": float(np.mean(rounds)),
        "food_pick_rate": float(np.mean(food / np.maximum(1.0, rounds))),
    }


def _mii(pop: list[Agent], return_matrix: bool = False) -> dict:
    rng = np.random.default_rng(12345)
    if G1F_MII_SAMPLE >= mc.N_REFERENTS:
        idx = list(range(mc.N_REFERENTS))
    else:
        idx = sorted(rng.choice(mc.N_REFERENTS, G1F_MII_SAMPLE, replace=False).tolist())
    refs = [mc.index_to_referent(i) for i in idx]
    matrix = []
    for sp_agent in pop:
        msgs = [sp_agent.speaker.emit(r) for r in refs]
        row = []
        for li_agent in pop:
            preds = li_agent.listener.predict_all(msgs)
            row.append(float(np.mean([tuple(p) == tuple(r) for p, r in zip(preds, refs)])))
        matrix.append(row)
    diag = [matrix[i][i] for i in range(len(pop))]
    off = [matrix[i][j] for i in range(len(pop)) for j in range(len(pop)) if i != j]
    out = {
        "self": round(float(np.mean(diag)), 5),
        "cross": round(float(np.mean(off)), 5),
        "min_offdiag": round(float(np.min(off)), 5),
        "chance": round(float(1.0 / mc.N_REFERENTS), 5),
    }
    if return_matrix:  # instrument-only: kin-only diagnostic CF/WF (off-diagonal keyed on .lineage)
        out["matrix"] = matrix
        out["lineages"] = [int(a.lineage) for a in pop]
    return out


def _select_next(seed: int, gen: int, pop: list[Agent], fitness, arm: str, rng):
    if arm in ("frozen_random", "shared_frozen_random"):
        return pop
    order = np.argsort(-np.asarray(fitness, float))
    parents = [pop[int(i)] for i in order[: max(2, len(pop) // 2)]]
    new_pop = [copy.deepcopy(p) for p in parents]
    while len(new_pop) < len(pop):
        p = parents[int(rng.integers(0, len(parents)))]
        child_seed = seed * 100_003 + gen * 1009 + len(new_pop)
        if arm == "kirby_linked":
            new_pop.append(_kirby_child(p, child_seed, gen, rng))
        elif arm == "shared_weights_kin":
            new_pop.append(_mutate(p, child_seed, rng, preserve_lineage=True))
        else:
            new_pop.append(_mutate(p, child_seed, rng))
    return new_pop[: len(pop)]


def _run_arm(seed: int, arm: str):
    rng = np.random.default_rng(seed * 17 + len(arm))
    pop = _initial_pop_for(seed * 11 + len(arm), arm)
    traj = []
    for gen in range(G1F_GENS + 1):
        mii = _mii(pop)
        ep = _run_episode(seed * 1000 + gen * 13 + len(arm), pop, "open", arm)
        traj.append({
            "gen": gen, "mii_cross": mii["cross"], "mii_self": mii["self"],
            "mii_chance": mii["chance"], "survival": round(ep["alive"], 4),
            "rounds": round(ep["rounds"], 4), "food_pick_rate": round(ep["food_pick_rate"], 4),
        })
        if gen < G1F_GENS:
            pop = _select_next(seed, gen, pop, ep["fitness"], arm, rng)
    controls = {}
    for mode in CTRL:
        ep = _run_episode(seed * 2000 + len(mode) + len(arm), pop, mode, arm)
        controls[mode] = {k: round(float(ep[k]), 4) for k in ("alive", "rounds", "food_pick_rate")}
    return {
        "seed": seed, "arm": arm, "traj": traj,
        "init_mii": traj[0]["mii_cross"], "final_mii": traj[-1]["mii_cross"],
        "mii_rise": round(traj[-1]["mii_cross"] - traj[0]["mii_cross"], 5),
        "init_survival": traj[0]["survival"], "final_survival": traj[-1]["survival"],
        "survival_rise": round(traj[-1]["survival"] - traj[0]["survival"], 5),
        "controls": controls,
    }


def _redline_scan():
    hits = {}
    src = (ROOT / "offscreen" / "rtc_g1f_coevolve.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def func_name(node):
        cur = node
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, ast.FunctionDef):
                return cur.name
        return "<module>"

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
        if name in ("cotrain_factored", "train_relay_channel", "find_nearest"):
            hits.setdefault(str(node.lineno), []).append(name)
        if isinstance(f, ast.Attribute) and f.attr == "patch":
            owner = f.value.id if isinstance(f.value, ast.Name) else ""
            if owner == "world" and func_name(node) != "_run_episode":
                hits.setdefault(str(node.lineno), []).append("world.patch")
    return hits


def _summ(rows):
    out = {}
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        out[arm] = {
            "final_mii_mean": round(float(np.mean([r["final_mii"] for r in rs])), 5),
            "final_mii_ci": _ci([r["final_mii"] for r in rs], len(arm) + 1),
            "mii_rise_mean": round(float(np.mean([r["mii_rise"] for r in rs])), 5),
            "mii_rise_ci": _ci([r["mii_rise"] for r in rs], len(arm) + 2),
            "final_survival_mean": round(float(np.mean([r["final_survival"] for r in rs])), 4),
            "survival_rise_mean": round(float(np.mean([r["survival_rise"] for r in rs])), 4),
            "control_alive": {
                mode: round(float(np.mean([r["controls"][mode]["alive"] for r in rs])), 4)
                for mode in CTRL
            },
        }
    return out


def _by_seed(rows, arm: str):
    return {int(r["seed"]): r for r in rows if r["arm"] == arm}


def _paired(rows, arm_a: str, arm_b: str, key: str):
    a, b = _by_seed(rows, arm_a), _by_seed(rows, arm_b)
    seeds = sorted(set(a) & set(b))
    return [float(a[s][key]) - float(b[s][key]) for s in seeds]


def _control_delta(rows, arm: str, left: str, right: str):
    return [float(r["controls"][left]["alive"]) - float(r["controls"][right]["alive"])
            for r in rows if r["arm"] == arm]


def _traj_corr(row):
    xs = np.asarray([p["mii_cross"] for p in row["traj"]], float)
    ys = np.asarray([p["survival"] for p in row["traj"]], float)
    if np.std(xs) < 1e-9 or np.std(ys) < 1e-9:
        return 0.0
    return float(np.corrcoef(xs, ys)[0, 1])


def main():
    t0 = time.time()
    rows = []
    for sd in G1F_SEEDS:
        line = [f"[seed {sd}]"]
        for arm in ARMS:
            r = _run_arm(sd, arm)
            rows.append(r)
            line.append(f"{arm}:mii {r['init_mii']:.4f}->{r['final_mii']:.4f} "
                        f"surv {r['init_survival']:.2f}->{r['final_survival']:.2f}")
        print(" | ".join(line), flush=True)
    summary = _summ(rows)
    redline_hits = _redline_scan()
    candidate_arms = ("pure_selection", "kirby_linked", "shared_weights_kin")
    best_arm = max(candidate_arms,
                   key=lambda a: summary[a]["mii_rise_mean"])
    best = summary[best_arm]
    null_arm = "shared_frozen_random" if best_arm == "shared_weights_kin" else "frozen_random"
    mii_delta = _paired(rows, best_arm, null_arm, "final_mii")
    survival_rise = [r["survival_rise"] for r in rows if r["arm"] == best_arm]
    open_scramble = _control_delta(rows, best_arm, "open", "scramble")
    open_mute = _control_delta(rows, best_arm, "open", "mute")
    traj_corr = [_traj_corr(r) for r in rows if r["arm"] == best_arm]
    moved = best["mii_rise_ci"][0] > G1F_MII_MOVE_MIN and _ci(mii_delta, 31)[0] > G1F_MII_MOVE_MIN
    gates = {
        "redline_scan_clean": not redline_hits,
        "pilot_mii_moves_off_floor": moved,
        "evolved_beats_arch_null_mii": _ci(mii_delta, 31)[0] > G1F_MII_MOVE_MIN,
        "open_beats_scramble_survival": _ci(open_scramble, 32)[0] > 0.0,
        "open_beats_mute_survival": _ci(open_mute, 33)[0] > 0.0,
        "survival_co_rises_with_mii": _ci(survival_rise, 34)[0] > 0.0 and _ci(traj_corr, 35)[0] > 0.0,
    }
    if PILOT:
        verdict = "RTC_G1F_PILOT_MOVED_PENDING_FORMAL" if moved and not redline_hits else "RTC_G1F_NO_CHANNEL_EMERGES"
    elif all(gates.values()):
        verdict = "RTC_G1F_CHANNEL_COEVOLVES"
    elif moved:
        verdict = "RTC_G1F_MII_MOVES_NOT_LOAD_BEARING"
    else:
        verdict = "RTC_G1F_NO_CHANNEL_EMERGES"
    if verdict == "RTC_G1F_PILOT_MOVED_PENDING_FORMAL":
        verdict = "RTC_G1F_PILOT_MOVED_PENDING_REVIEW"
    out = {
        "kind": "rtc_g1f_coevolve_v1",
        "block": "cheap_pilot" if PILOT else "formal",
        "seeds": G1F_SEEDS,
        "prereg": {
            "arms": ARMS, "controls": CTRL, "G1F_POP": G1F_POP, "G1F_GENS": G1F_GENS,
            "G1F_ROUNDS": G1F_ROUNDS, "G1F_VENTS": G1F_VENTS, "G1F_STEP": G1F_STEP,
            "G1F_HIDDEN": G1F_HIDDEN, "G1F_MUT": G1F_MUT,
            "G1F_KIRBY_EPOCHS": G1F_KIRBY_EPOCHS, "G1F_HOLD_FRAC": G1F_HOLD_FRAC,
            "G1F_MII_MOVE_MIN": G1F_MII_MOVE_MIN, "G1F_MII_SAMPLE": G1F_MII_SAMPLE,
            "RTC_TOXIC_DEATH_g1f_taskdesign": rc.RTC_TOXIC_DEATH,
            "no_truth_gradient": True, "channel_init": "random FactoredSpeaker/FactoredListener",
            "decision_reads": "decoded per-agent messages only; true field only in eat/oracle resolution",
            "cultural_mechanism": "kirby_linked imitates parent utterances via mortal_generations._imitate",
            "shared_weights_kin": (
                "UnifiedIO ties encode/decode table; lineage id is inherited; listener "
                "prefers same-lineage speakers; shared_frozen_random is the architecture null"
            ),
        },
        "summary": summary,
        "paired_tests": {
            "best_minus_arch_null_final_mii": {"mean": round(float(np.mean(mii_delta)), 5), "ci": _ci(mii_delta, 31)},
            "open_minus_scramble_alive": {"mean": round(float(np.mean(open_scramble)), 5), "ci": _ci(open_scramble, 32)},
            "open_minus_mute_alive": {"mean": round(float(np.mean(open_mute)), 5), "ci": _ci(open_mute, 33)},
            "survival_rise": {"mean": round(float(np.mean(survival_rise)), 5), "ci": _ci(survival_rise, 34)},
            "mii_survival_corr": {"mean": round(float(np.mean(traj_corr)), 5), "ci": _ci(traj_corr, 35)},
        },
        "best_arm": best_arm,
        "arch_null_for_best": null_arm,
        "redline_hits": redline_hits,
        "gates": gates,
        "verdict": verdict,
        "honest_claim": (
            "Cheap G1F pilot. If null, survival selection plus the tested legitimate "
            "Kirby linkage did not move cross-agent intelligibility off the bootstrap floor."
        ),
        "rows": rows,
        "wall_seconds": round(time.time() - t0, 1),
    }
    path = ROOT / "offscreen" / "rtc_g1f_coevolve_verdict.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"VERDICT={verdict} best={best_arm} gates={gates} -> {path}", flush=True)
    ok = {
        "RTC_G1F_NO_CHANNEL_EMERGES",
        "RTC_G1F_PILOT_MOVED_PENDING_REVIEW",
        "RTC_G1F_CHANNEL_COEVOLVES",
        "RTC_G1F_MII_MOVES_NOT_LOAD_BEARING",
    }
    return 0 if verdict in ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
