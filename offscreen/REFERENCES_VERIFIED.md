# Verified references (for PAPER.md — replaces the [CITE?] placeholders)

All seven verified against live sources on 2026-06-30 (web search). Use these to remove every `[CITE?]`
marker in PAPER.md and to fix the body attributions. Formatted roughly APA; reformat to the *Artificial Life*
(MIT Press) house style at submission.

1. **Foerster, J. N., Assael, Y. M., de Freitas, N., & Whiteson, S. (2016).** Learning to Communicate with
   Deep Multi-Agent Reinforcement Learning. *Advances in Neural Information Processing Systems 29 (NeurIPS
   2016)*, 2137–2145. — DIAL/RIAL; gradient through the channel. Supports the §2 "trained-in by gradient,
   differentiable inter-agent channel" contrast. ✓ attribution correct.

2. **Lazaridou, A., Peysakhovich, A., & Baroni, M. (2017).** Multi-Agent Cooperation and the Emergence of
   (Natural) Language. *International Conference on Learning Representations (ICLR 2017)*. arXiv:1612.07182.
   — referential games with reward/task pressure. Supports the §2 "reward/oracle-driven referential game"
   contrast. ✓ attribution correct (it is reward/task-driven, not literally a centralized critic — phrase §2
   as "reward on a referential task", not "centralized critic", to be precise).

3. **Kirby, S., Cornish, H., & Smith, K. (2008).** Cumulative cultural evolution in the laboratory: An
   experimental approach to the origins of structure in human language. *Proceedings of the National Academy
   of Sciences, 105*(31), 10681–10686. https://doi.org/10.1073/pnas.0707835105 — iterated learning;
   transmission bottleneck induces structure. Supports §2 + §7.3 "bottleneck imposed by design" contrast.
   ✓ (note: this is the *human iterated-learning* experiment; if citing the computational model, also/instead
   cite Kirby 2001/2002 — but 2008 PNAS is correct for "structure from a transmission bottleneck").

4. **Cangelosi, A., & Parisi, D. (Eds.) (2002).** *Simulating the Evolution of Language.* London:
   Springer-Verlag. https://doi.org/10.1007/978-1-4471-0663-0 — edited volume; computational ALife approaches
   to language evolution. Supports the §2 ALife-language-evolution paragraph. ✓ (edited volume — cite a
   specific chapter if a specific claim is attributed; otherwise the volume is fine for the survey sentence).

5. **Steels, L. (2003).** Evolving grounded communication for robots. *Trends in Cognitive Sciences, 7*(7),
   308–312. https://doi.org/10.1016/S1364-6613(03)00129-3 — grounded/embodied communication, Talking-Heads
   lineage. Supports the §2 embodied-evolved-communication paragraph the novelty reviewer asked for. ✓.

6. **Lewis, D. K. (1969).** *Convention: A Philosophical Study.* Cambridge, MA: Harvard University Press. —
   signalling/coordination conventions, game-theoretic. Supports the §2 signalling-game lineage. ✓.

7. **Skyrms, B. (2010).** *Signals: Evolution, Learning, and Information.* New York: Oxford University Press.
   ISBN 978-0199580828. — evolutionary/learning dynamics of signalling games; builds on Lewis. Supports §2
   signalling-game lineage. ✓.

## Newly verified (2026-06-30) — completes the bibliography (the 3 the novelty reviewer asked for)
8. **Hamilton, W. D. (1964).** The Genetical Evolution of Social Behaviour, I & II. *Journal of Theoretical
   Biology, 7*(1), 1–16 & 17–52. — kin selection / inclusive fitness; the foundational reference for the
   kin-private result and the §7.1 "what is non-obvious vs kin-selection theory" paragraph. ✓
9. **Quinn, M. (2001).** Evolving communication without dedicated communication channels. *Advances in
   Artificial Life (ECAL 2001)*, LNCS, Springer. — evolved communication in embodied agents with NO pre-given
   channel; the closest embodied-evolved-communication prior. Pair with **Marocco, D., & Nolfi, S. (2007).**
   Emergence of communication in embodied agents evolved for the ability to solve a collective navigation
   problem. *Connection Science, 19*(1), 53–74. ✓ VERIFIED 2026-06-30: Quinn = ECAL 2001, LNCS 2159, pp.
   357–366, DOI 10.1007/3-540-44811-X_38; Marocco & Nolfi = Connection Science 19(1):53–74, DOI
   10.1080/09540090601015067. (no [verify] remaining)
10. **Kottur, S., Moura, J. M. F., Lee, S., & Batra, D. (2017).** Natural Language Does Not Emerge 'Naturally'
   in Multi-Agent Dialog. *EMNLP 2017.* — negative result: agent-invented protocols are effective but not
   interpretable/compositional; supports the "emergent protocols are often degenerate" point and strengthens the
   gate-0 content sentinels + the "signalling code, not language" caution. ✓

## RECENT LAYER (2019–2024) — added 2026-06-30 to fix the "nothing after 2017" gap (a real reviewer red flag)
The foundational refs above are canon (cite regardless of age); these situate the paper in the CURRENT field.
11. **Lazaridou, A., & Baroni, M. (2020).** Emergent Multi-Agent Communication in the Deep Learning Era.
    arXiv:2006.02419. — the field review; updates the Foerster 2016 / Lazaridou 2017 line in §2. ✓
12. **Chaabouni, R., Kharitonov, E., Bouchacourt, D., Dupoux, E., & Baroni, M. (2020).** Compositionality and
    Generalization in Emergent Languages. *ACL 2020.* — finds compositionality and generalization are not tied
    in emergent languages; directly supports our "signalling code, compositionality untested" caution + Kottur. ✓
13. **Kharitonov, E., Chaabouni, R., Bouchacourt, D., & Baroni, M. (2019).** EGG: a toolkit for research on
    Emergence of lanGuage in Games. *EMNLP 2019 (System Demonstrations).* arXiv:1907.00852. — the standard
    emergent-comm toolkit; situates our methodology vs the deep-learning EmCom infrastructure. ✓
14. (survey, verify authors) "Towards More Human-like AI Communication: A Review of Emergent Communication
    Research." arXiv:2308.02541 (2023). — a recent review establishing the field is active through 2023. [verify authors]
15. (optional, recent ALife venue) cite a relevant ALIFE 2022 or 2023 proceedings paper (MIT Press / ISAL) on
    emergent communication / language evolution to show current ALife engagement. [pick + verify at integration]
Note: the related-work section (§2) currently stops at 2017; INTEGRATE 11-13 (and 14) as a "recent work" layer
so the paper is not frozen at 2017. Do this in the next related-work modernization pass (after the PDF build).

## LLM-society CONTRAST cite — VERIFIED 2026-06-30 (corrects Codex's wrong "Klein & Hilbig" guess)
16. **Flint Ashery, A., Aiello, L. M., & Baronchelli, A. (2025).** Emergent social conventions and collective
    bias in LLM populations. *Science Advances, 11*(20), eadu9368. DOI 10.1126/sciadv.adu9368 (arXiv:2410.08948).
    — cited ONLY as CONTRAST (LLM populations form conventions over a BORROWED, pre-trained language).
    ⚠️ Codex's draft guessed the authors as "Klein & Hilbig 2025" — WRONG; the verified authors are
    Flint Ashery, Aiello & Baronchelli. Fix this in PAPER.md + ggl.tex before submission.
