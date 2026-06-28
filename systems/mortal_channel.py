"""The factored compositional channel for the Mortal-Bottleneck experiment.

This module PROMOTES the power-check-validated recipe from
``scripts/probe_compositional_substrate.py`` into a clean, tested instrument.
The probe established (probes 2311f0e/def9401, and reproduced in
``offscreen/probe2_factored_*.json``) the ONE substrate geometry where
compositionality is well-defined AND can rise under a transmission bottleneck:

  * referents are a COMBINATORIAL ATTRIBUTE PRODUCT (``MORTAL_ATTRIBUTES`` ->
    ``MORTAL_N_REFERENTS`` tuples) with ``VOCAB < N_REFERENTS`` so no single
    symbol can index a referent -- the code is structurally FORCED to combine
    positions (this kills the single-symbol "diagonal" collapse the committed
    8-referent ``comm_channel`` channel suffered); and
  * the speaker input is FACTORED -- one embedding table PER ATTRIBUTE, summed.
    This is NON-NEGOTIABLE: with a monolithic per-referent embedding a held-out
    attribute-combination's embedding is untrained, so the bottleneck cannot
    transmit compositional structure and PosDis stays flat (the power-check's
    verified negative control). The OUTPUT head stays free-form
    ``(MSG_LEN, VOCAB)`` -- no compositional output prior is baked in.

Conventions mirror ``systems/comm_channel.py``: a module docstring stating the
honesty role, ``from __future__ import annotations``, frozen geometry imported
from ``config/prereg_mortal`` (NOTHING hardcoded -- a config change flows
through), and ``torch`` imported LAZILY inside the methods that need it so this
whole module imports on a box with no torch / no GPU. Only the learnable paths
touch torch.

The geometry here is exactly the cotrain/measure substrate; the multi-generation
death-vs-reset bottleneck loop and the PosDis/BosDis/topsim metrics (T3+) live in
their own modules and are deliberately NOT built here.
"""

from __future__ import annotations

import itertools

from config.prereg_mortal import (
    MORTAL_ATTRIBUTES,
    MORTAL_MSG_LEN,
    MORTAL_N_REFERENTS,
    MORTAL_VOCAB,
)

# A referent is a tuple of per-attribute value indices, e.g. (type, bearing,
# distance) -> (1, 3, 0). A channel message is a tuple of MORTAL_MSG_LEN symbol
# indices each in 0 .. MORTAL_VOCAB - 1.
Referent = tuple[int, ...]
Message = tuple[int, ...]

# Re-export the frozen geometry under the short names the learnable nets use
# (mirrors comm_channel's MSG_LEN / VOCAB re-export).
MSG_LEN: int = MORTAL_MSG_LEN
VOCAB: int = MORTAL_VOCAB

# Per-attribute cardinalities, derived from the frozen config (NOT hardcoded).
ATTR_CARDS: tuple[int, ...] = tuple(card for _name, card in MORTAL_ATTRIBUTES)
N_ATTRS: int = len(ATTR_CARDS)

# ── stable referent ordering = the cartesian product of MORTAL_ATTRIBUTES ──
# itertools.product is first-attribute-major (last attribute varies fastest), a
# stable mixed-radix code; REFERENTS[i] is the i-th tuple, _REFERENT_IDX inverts.
REFERENTS: list[Referent] = [tuple(t) for t in itertools.product(*(range(c) for c in ATTR_CARDS))]
N_REFERENTS: int = len(REFERENTS)  # == MORTAL_N_REFERENTS by construction
_REFERENT_IDX: dict[Referent, int] = {r: i for i, r in enumerate(REFERENTS)}

assert N_REFERENTS == MORTAL_N_REFERENTS, (
    "referent product size disagrees with MORTAL_N_REFERENTS: "
    f"{N_REFERENTS} != {MORTAL_N_REFERENTS} (config drift)"
)


def referent_index(referent: Referent) -> int:
    """The stable 0..N_REFERENTS-1 index of an attribute-tuple referent."""
    return _REFERENT_IDX[tuple(referent)]


def index_to_referent(index: int) -> Referent:
    """Inverse of :func:`referent_index`: the attribute-tuple at a stable index."""
    return REFERENTS[int(index)]


# ── the GROWN (learnable) factored channel: tiny torch nets, Lewis-cotrained ──

_HIDDEN: int = 32  # net width; the power-check used 32 and it cleared the bar


class FactoredSpeaker:
    """Referent (attribute-tuple) -> per-position symbol logits, FACTORED input.

    Architecture (built lazily on first use): one ``nn.Embedding(card, H)`` PER
    attribute (``attr_embeds``), summed into a single hidden vector, then
    ``ReLU`` + ``nn.Linear(H, MSG_LEN * VOCAB)`` reshaped to ``(MSG_LEN, VOCAB)``
    logits. The per-attribute embedding tables are the load-bearing inductive
    bias: a held-out attribute-combination REUSES the per-attribute embeddings
    learned from seen combos, so the bottleneck (later tasks) can transmit
    compositional structure -- the monolithic per-referent alternative provably
    cannot (power-check negative control). The OUTPUT head is free-form (no
    compositional output prior). Deterministic init via ``torch.manual_seed``.
    """

    def __init__(self, seed: int = 0, hidden: int = _HIDDEN) -> None:
        self.seed = int(seed)
        self.hidden = int(hidden)
        self.n_referents = N_REFERENTS
        self.msg_len = MSG_LEN
        self.vocab = VOCAB
        self.attr_embeds = None  # nn.ModuleList, built lazily
        self.proj = None         # ReLU + Linear, built lazily
        self._ref_table = None   # (N_REFERENTS, N_ATTRS) long tensor of attr indices

    def _build(self):
        if self.attr_embeds is None:
            import torch
            from torch import nn

            torch.manual_seed(self.seed)
            self.attr_embeds = nn.ModuleList(
                [nn.Embedding(card, self.hidden) for card in ATTR_CARDS]
            )
            self.proj = nn.Sequential(
                nn.ReLU(), nn.Linear(self.hidden, self.msg_len * self.vocab)
            )
            self._ref_table = torch.tensor([list(r) for r in REFERENTS], dtype=torch.long)
        return self.attr_embeds, self.proj

    def parameters(self):
        embeds, proj = self._build()
        ps = []
        for e in embeds:
            ps += list(e.parameters())
        ps += list(proj.parameters())
        return ps

    def logits_for(self, referent_idx):
        """Per-position logits ``(batch, MSG_LEN, VOCAB)`` for a tensor of referent indices.

        Looks up the attribute values for each referent index, embeds each
        attribute with its own table, sums them, and projects to symbol logits.
        """
        embeds, proj = self._build()
        attrs = self._ref_table[referent_idx]  # (B, N_ATTRS)
        h = sum(embeds[k](attrs[:, k]) for k in range(attrs.shape[1]))
        flat = proj(h)  # (B, MSG_LEN * VOCAB)
        return flat.view(-1, self.msg_len, self.vocab)

    def emit(self, referent: Referent) -> Message:
        """Discrete eval-time message: argmax symbol per position -> ``tuple[int, ...]``."""
        import torch

        mods = (*self._build()[0], self._build()[1])
        # capture each module's PRIOR train/eval flag and RESTORE it afterward (FIX 3):
        # forcing .train() would flip a caller's eval() module to train -- a latent
        # footgun (e.g. fit_readout_decoder calls emit_all on a frozen speaker).
        prior = [m.training for m in mods]
        for m in mods:
            m.eval()
        idx = torch.tensor([referent_index(referent)], dtype=torch.long)
        with torch.no_grad():
            logits = self.logits_for(idx)[0]  # (MSG_LEN, VOCAB)
        msg = tuple(int(s) for s in logits.argmax(dim=-1).tolist())
        for m, was_training in zip(mods, prior):
            m.train(was_training)
        return msg

    def emit_all(self) -> list[Message]:
        """Discrete argmax message for EVERY referent, as a list of tuples."""
        import torch

        mods = (*self._build()[0], self._build()[1])
        prior = [m.training for m in mods]  # FIX 3: preserve prior train/eval mode
        for m in mods:
            m.eval()
        idx = torch.arange(self.n_referents, dtype=torch.long)
        with torch.no_grad():
            logits = self.logits_for(idx)  # (N, MSG_LEN, VOCAB)
        msgs = [tuple(int(s) for s in row) for row in logits.argmax(dim=-1).tolist()]
        for m, was_training in zip(mods, prior):
            m.train(was_training)
        return msgs


class Listener:
    """Tiny net inverting a (soft or hard) message back to a referent.

    Architecture (built lazily): a shared ``nn.Embedding(VOCAB, H)`` applied at
    each of the MSG_LEN positions, position embeddings summed, then
    ``nn.Linear(H, N_REFERENTS)`` -> JOINT referent logits (the power-check
    listener predicts the joint index; per-attribute factored decode is the
    EXPERIMENTER-side M2 metric in a later task, not the trained listener).
    ``predict`` returns the argmax referent tuple; ``forward_soft`` takes the
    speaker's Gumbel-Softmax soft message and stays differentiable end to end.
    Deterministic init via ``torch.manual_seed(seed)``.
    """

    def __init__(self, seed: int = 0, hidden: int = _HIDDEN) -> None:
        self.seed = int(seed)
        self.hidden = int(hidden)
        self.n_referents = N_REFERENTS
        self.msg_len = MSG_LEN
        self.vocab = VOCAB
        self._embed = None
        self._head = None

    def _build(self):
        if self._embed is None:
            import torch
            from torch import nn

            torch.manual_seed(self.seed)
            self._embed = nn.Embedding(self.vocab, self.hidden)
            self._head = nn.Linear(self.hidden, self.n_referents)
        return self._embed, self._head

    def parameters(self):
        embed, head = self._build()
        return list(embed.parameters()) + list(head.parameters())

    def forward_soft(self, soft_message):
        """Referent logits from a soft message ``(batch, MSG_LEN, VOCAB)`` (differentiable).

        A soft one-hot over the vocab indexes the embedding as a matmul with the
        embedding weight, so a Gumbel-Softmax (hard=True straight-through) message
        flows gradients back into the speaker.
        """
        embed, head = self._build()
        pos = soft_message @ embed.weight  # (B, MSG_LEN, H)
        return head(pos.sum(dim=1))

    def predict(self, message: Message) -> Referent:
        """Discrete eval-time decode: argmax referent tuple for a hard ``Message``."""
        import torch

        embed, head = self._build()
        # FIX 3: capture + restore prior train/eval mode (do not force .train()).
        prior = (embed.training, head.training)
        embed.eval()
        head.eval()
        syms = torch.tensor([list(message)], dtype=torch.long)  # (1, MSG_LEN)
        with torch.no_grad():
            pos = embed(syms).sum(dim=1)  # (1, H)
            logits = head(pos)
        ref = index_to_referent(int(logits.argmax(dim=-1).item()))
        embed.train(prior[0])
        head.train(prior[1])
        return ref


class FactoredListener:
    """POSITION-AWARE factored decoder: message -> per-attribute heads -> referent tuple.

    The selection instrument the death-bottleneck must flow through. The committed
    joint :class:`Listener` predicts a single ``N_REFERENTS``-way index and SUMS its
    position embeddings; it is never trained on held-out attribute-combinations, so
    held-out decode is 0.00 and full-grid fitness saturates at the seen fraction,
    FLAT across agents -> fitness-weighted death-selection degenerates to a coin-flip
    UNCORRELATED with compositionality. Even a position-aware-but-position-SUMMING
    factored listener fails: a perfectly compositional code reaches only 0.167
    held-out because summing the position embeddings destroys WHICH-symbol-was-WHERE.

    The fix, NON-NEGOTIABLE here:
      * ``self.embeds``: a ``nn.ModuleList`` of MSG_LEN DISTINCT ``nn.Embedding(VOCAB,
        H)`` tables -- ONE PER POSITION. A single shared table summed over positions
        is the verified trap (the 0.167 cap); distinct-per-position tables let each
        position learn to READ the symbol AT that position.
      * ``self.heads``: a ``nn.ModuleList`` of ``nn.Linear(MSG_LEN * H, card)`` -- ONE
        PER ATTRIBUTE, ``card`` from :data:`ATTR_CARDS`. The position embeddings are
        CONCATENATED (never summed), preserving position identity, and each attribute
        is read off the joint representation by its own head. Per-attribute decode is
        exactly what makes a held-out attribute-combination REACHABLE: position k
        learns attribute k from SEEN combos and that decode transfers to unseen ones.

    The validated power-check ceiling/floor (the acceptance bar): a perfectly
    compositional code -> ~1.000 held-out joint accuracy; holistic random codes ->
    ~chance (joint chance 1/N_REFERENTS ~ 0.028); selection spread ~0.98. Held-out
    generalization (M2) and PosDis (M1) are DECOUPLED at low compositionality
    (Chaabouni 2020), so this instrument is NOT tuned for any gen-0 PosDis
    correlation -- it is tuned only to reward held-out generalization.

    Built lazily; deterministic init via ``torch.manual_seed(seed)``; torch imported
    LAZILY inside the methods (the module imports with no torch). ``predict`` is the
    hard eval path :func:`systems.mortal_death.speaker_listener_channel` calls.
    """

    def __init__(self, seed: int = 0, hidden: int = _HIDDEN) -> None:
        self.seed = int(seed)
        self.hidden = int(hidden)
        self.n_referents = N_REFERENTS
        self.msg_len = MSG_LEN
        self.vocab = VOCAB
        self.embeds = None  # nn.ModuleList of MSG_LEN per-position embeddings, lazy
        self.heads = None   # nn.ModuleList of N_ATTRS per-attribute heads, lazy

    def _build(self):
        if self.embeds is None:
            import torch
            from torch import nn

            torch.manual_seed(self.seed)
            # ONE distinct embedding table PER message position (the crux: NOT a
            # single shared table summed over positions, which caps held-out at 0.167).
            self.embeds = nn.ModuleList(
                [nn.Embedding(self.vocab, self.hidden) for _ in range(self.msg_len)]
            )
            # ONE head PER attribute, reading the CONCATENATED position embeddings.
            self.heads = nn.ModuleList(
                [nn.Linear(self.msg_len * self.hidden, card) for card in ATTR_CARDS]
            )
        return self.embeds, self.heads

    def parameters(self):
        embeds, heads = self._build()
        ps = []
        for e in embeds:
            ps += list(e.parameters())
        for h in heads:
            ps += list(h.parameters())
        return ps

    def attr_logits_soft(self, soft_message):
        """Per-attribute logits from a soft message ``(B, MSG_LEN, VOCAB)`` (differentiable).

        Each position's soft one-hot indexes ITS OWN embedding as a matmul with that
        table's weight; the per-position vectors are CONCATENATED (never summed) into
        ``(B, MSG_LEN * H)``, preserving which-symbol-was-where, and each attribute is
        read by its own head. Returns a list of ``(B, card_k)`` logits. A
        Gumbel-Softmax straight-through soft message flows gradients to the speaker.
        """
        import torch

        embeds, heads = self._build()
        parts = [soft_message[:, k, :] @ embeds[k].weight for k in range(self.msg_len)]
        h = torch.cat(parts, dim=1)  # (B, MSG_LEN * H)
        return [head(h) for head in heads]

    def predict(self, message: Message) -> Referent:
        """Discrete eval-time decode: per-attribute argmax reassembled into a referent.

        Builds a ``(1, MSG_LEN)`` long tensor, one-hots it to ``(1, MSG_LEN, VOCAB)``
        float, runs :meth:`attr_logits_soft`, takes the per-attribute argmax, and
        REASSEMBLES the attribute tuple. This is what ``speaker_listener_channel``
        calls -- a valid attribute-tuple referent is REQUIRED (per-attribute decode is
        precisely what makes held-out combos reachable). Uses eval()/no_grad and
        RESTORES each module's PRIOR train/eval mode afterward (FIX 3: never forces
        train(), so a caller's eval() module stays in eval).
        """
        import torch
        import torch.nn.functional as F

        embeds, heads = self._build()
        mods = (*embeds, *heads)
        prior = [m.training for m in mods]  # FIX 3: preserve prior train/eval mode
        for m in mods:
            m.eval()
        syms = torch.tensor([list(message)], dtype=torch.long)  # (1, MSG_LEN)
        with torch.no_grad():
            soft = F.one_hot(syms, num_classes=self.vocab).float()  # (1, MSG_LEN, VOCAB)
            attr_logits = self.attr_logits_soft(soft)               # list of (1, card_k)
        ref = tuple(int(a.argmax(dim=-1).item()) for a in attr_logits)
        for m, was_training in zip(mods, prior):
            m.train(was_training)
        return ref

    def predict_all(self, messages) -> list[Referent]:
        """Per-attribute-argmax referent for a LIST of hard messages, in one eval pass.

        The batched speed path for :meth:`predict`: one-hot the whole ``messages``
        list to ``(B, MSG_LEN, VOCAB)``, run :meth:`attr_logits_soft` once, and take
        the per-attribute argmax for each row, reassembling each into a referent
        tuple. Uses eval()/no_grad and RESTORES each module's PRIOR train/eval mode
        afterward (FIX 3: never forces train()); semantically identical to calling
        :meth:`predict` per message.
        """
        import torch
        import torch.nn.functional as F

        embeds, heads = self._build()
        mods = (*embeds, *heads)
        prior = [m.training for m in mods]  # FIX 3: preserve prior train/eval mode
        for m in mods:
            m.eval()
        syms = torch.tensor([list(msg) for msg in messages], dtype=torch.long)  # (B, MSG_LEN)
        with torch.no_grad():
            soft = F.one_hot(syms, num_classes=self.vocab).float()  # (B, MSG_LEN, VOCAB)
            attr_logits = self.attr_logits_soft(soft)               # list of (B, card_k)
        preds = [a.argmax(dim=-1).tolist() for a in attr_logits]    # n_attrs lists of len B
        out = [tuple(int(preds[k][b]) for k in range(len(heads))) for b in range(len(messages))]
        for m, was_training in zip(mods, prior):
            m.train(was_training)
        return out


def round_trip_accuracy(spk: FactoredSpeaker, lis: Listener) -> float:
    """Fraction of referents where ``lis.predict(spk.emit(r)) == r`` (argmax path)."""
    msgs = spk.emit_all()
    correct = 0
    for i, m in enumerate(msgs):
        if lis.predict(m) == index_to_referent(i):
            correct += 1
    return correct / spk.n_referents


def round_trip_accuracy_factored(spk: FactoredSpeaker, lis: FactoredListener) -> float:
    """Full-set joint round-trip acc for a (speaker, FACTORED-listener) pair.

    Fraction of ALL referents where the listener's per-attribute decode of the
    speaker's argmax message reassembles the EXACT attribute tuple. The factored
    analogue of :func:`round_trip_accuracy`; reported by :func:`cotrain_factored` so
    a held-out cotrain SCORES held-out generalization (the M2 endpoint selection acts
    on), not just the trained subset.
    """
    msgs = spk.emit_all()
    correct = 0
    for i, m in enumerate(msgs):
        if tuple(lis.predict(m)) == index_to_referent(i):
            correct += 1
    return correct / spk.n_referents


def mutual_intelligibility_matrix(speakers, listeners):
    """Stage-3 SHARED-LANGUAGE metric: do agents understand EACH OTHER?

    M[i][j] = round-trip accuracy of speaker i's code decoded by listener j (reuses
    ``round_trip_accuracy_factored``, which already takes any spk+lis pair). Diagonal
    = self-decode; off-diagonal = cross-agent intelligibility. A population that grew
    ONE shared language has cross ~ self; private idiolects have cross ~ chance (the
    0/36-cross vs 36/36-self anchor from the positive control).
    """
    n = len(speakers)
    M = [[round_trip_accuracy_factored(speakers[i], listeners[j]) for j in range(n)]
         for i in range(n)]
    diag = [M[i][i] for i in range(n)]
    off = [M[i][j] for i in range(n) for j in range(n) if i != j]
    self_mean = sum(diag) / len(diag) if diag else 0.0
    cross_mean = sum(off) / len(off) if off else float("nan")
    return {
        "matrix": M, "self": self_mean, "cross": cross_mean,
        "mii": (cross_mean / self_mean) if self_mean > 0 else 0.0,
        "min_offdiag": (min(off) if off else float("nan")),
        "chance": (1.0 / speakers[0].n_referents) if speakers else float("nan"),
    }


def decode_shift(spk: "FactoredSpeaker", lis: "FactoredListener") -> float:
    """Survival-DECOUPLED positive-listening (Lowe et al. 2019): does the listener's
    output actually CHANGE when the message changes? Fraction of referents where the
    decode of the REAL message differs from the decode of a COUNTERFACTUAL (a
    different referent's message). A channel-IGNORING listener -> ~0; a listener that
    genuinely USES the channel -> high. Decoder-side only, independent of survival."""
    msgs = spk.emit_all()
    n = len(msgs)
    if n < 2:
        return 0.0
    shifts = sum(1 for i in range(n)
                 if tuple(lis.predict(msgs[i])) != tuple(lis.predict(msgs[(i + n // 2) % n])))
    return shifts / n


def message_entropy_bits(spk: "FactoredSpeaker") -> float:
    """Entropy-minimization-collapse trip-wire (Kharitonov et al. 2020): bits of the
    distribution over DISTINCT emitted messages. Healthy needs >= log2(n_referents)
    (log2(36)=5.17); a monotone decline => the code is collapsing to fewer messages."""
    import math
    from collections import Counter
    msgs = [tuple(m) for m in spk.emit_all()]
    n = len(msgs)
    if n == 0:
        return 0.0
    counts = Counter(msgs)
    return -sum((k / n) * math.log2(k / n) for k in counts.values())


def cotrain(
    spk: FactoredSpeaker,
    lis: Listener,
    epochs: int,
    *,
    lr: float = 1e-2,
    tau: float = 1.0,
    seed: int = 0,
    seen_idx: list[int] | None = None,
) -> float:
    """Co-train speaker/listener as a Lewis referential game; return argmax round-trip acc.

    Each epoch the speaker emits Gumbel-Softmax soft messages (``hard=True``
    straight-through, so the forward is discrete but the backward differentiable)
    for the training referents, the listener predicts the joint referent index,
    and a cross-entropy loss against the true index is minimised by Adam over
    BOTH nets jointly. Determinism is pinned by ``torch.manual_seed(seed)``.

    ``seen_idx`` optionally restricts cotrain to a SUBSET of referent indices (for
    later held-out-bottleneck tasks); the default (None) trains over ALL
    referents. The returned accuracy is ALWAYS the argmax round-trip over the full
    referent set, so a held-out cotrain reports held-out generalisation.
    """
    import torch
    import torch.nn.functional as F

    torch.manual_seed(int(seed))
    spk._build()
    lis._build()

    params = list(spk.parameters()) + list(lis.parameters())
    opt = torch.optim.Adam(params, lr=lr)

    if seen_idx is None:
        train_idx = torch.arange(spk.n_referents, dtype=torch.long)
    else:
        train_idx = torch.tensor(sorted(seen_idx), dtype=torch.long)
    targets = train_idx  # joint-index classification target == the referent index

    for _epoch in range(int(epochs)):
        opt.zero_grad()
        logits = spk.logits_for(train_idx)  # (B, MSG_LEN, VOCAB)
        soft_msg = F.gumbel_softmax(logits, tau=tau, hard=True, dim=-1)
        pred_logits = lis.forward_soft(soft_msg)  # (B, N_REFERENTS)
        loss = F.cross_entropy(pred_logits, targets)
        loss.backward()
        opt.step()

    return round_trip_accuracy(spk, lis)


def cotrain_factored(
    spk: FactoredSpeaker,
    lis: FactoredListener,
    epochs: int,
    *,
    lr: float = 1e-2,
    tau: float = 1.0,
    seed: int = 0,
    seen_idx: list[int] | None = None,
) -> float:
    """Co-train a (speaker, FACTORED-listener) pair with PER-ATTRIBUTE cross-entropy.

    The factored analogue of :func:`cotrain`, the same Lewis referential game but
    routed through the POSITION-AWARE :class:`FactoredListener`: each epoch the
    speaker emits Gumbel-Softmax soft messages (``hard=True`` straight-through, so the
    forward is discrete but the backward differentiable) for the training referents,
    :meth:`FactoredListener.attr_logits_soft` produces per-attribute logits, and the
    loss is the SUM over the :data:`N_ATTRS` attributes of the cross-entropy of each
    attribute head against the TRUE attribute value of the training referents (read
    off the speaker's ``_ref_table``-style ``(N_REFERENTS, N_ATTRS)`` attribute
    table). Adam optimises BOTH nets jointly; determinism pinned by
    ``torch.manual_seed(seed)``.

    ``seen_idx`` optionally restricts training to a SUBSET of referent indices (the
    held-out bottleneck); the default (None) trains over ALL referents. The returned
    accuracy is ALWAYS the FULL-set joint round-trip
    (:func:`round_trip_accuracy_factored`) -- train on ``seen_idx``, SCORE on the full
    set -- so a held-out cotrain REPORTS held-out generalization (the same contract as
    :func:`cotrain`, and the M2 endpoint selection acts on).
    """
    import torch
    import torch.nn.functional as F

    torch.manual_seed(int(seed))
    spk._build()
    lis._build()

    params = list(spk.parameters()) + list(lis.parameters())
    opt = torch.optim.Adam(params, lr=lr)

    if seen_idx is None:
        train_idx = torch.arange(spk.n_referents, dtype=torch.long)
    else:
        train_idx = torch.tensor(sorted(seen_idx), dtype=torch.long)

    # the (N_REFERENTS, N_ATTRS) attribute table -> per-attribute targets for the
    # TRAIN referents (the value each attribute head must predict). Built here (not
    # leaning on the speaker's private _ref_table) so the loss target is explicit.
    ref_table = torch.tensor([list(r) for r in REFERENTS], dtype=torch.long)
    attr_targets = [ref_table[train_idx, k] for k in range(N_ATTRS)]

    for _epoch in range(int(epochs)):
        opt.zero_grad()
        logits = spk.logits_for(train_idx)  # (B, MSG_LEN, VOCAB)
        soft_msg = F.gumbel_softmax(logits, tau=tau, hard=True, dim=-1)
        attr_logits = lis.attr_logits_soft(soft_msg)  # list of (B, card_k)
        loss = sum(
            F.cross_entropy(attr_logits[k], attr_targets[k]) for k in range(N_ATTRS)
        )
        loss.backward()
        opt.step()

    return round_trip_accuracy_factored(spk, lis)
