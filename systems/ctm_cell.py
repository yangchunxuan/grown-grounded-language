"""Small from-scratch CTM cell for Phase-1 behavior-brain viability.

Adapted at the architecture level from SakanaAI/continuous-thought-machines
(Apache-2.0): internal ticks, private neuron-level models over FIFO traces, and
synchronisation as the policy representation. No pretrained weights are loaded.
"""
from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
import torch.nn.functional as F


@dataclass
class CTMState:
    activated: torch.Tensor
    trace: torch.Tensor
    sync_alpha: torch.Tensor
    sync_beta: torch.Tensor


class PrivateNeuronMLP(nn.Module):
    """Per-neuron MLP mapping each neuron's pre-activation trace to activation."""

    def __init__(self, d_model: int, memory_length: int, hidden_dim: int) -> None:
        super().__init__()
        d, m, h = int(d_model), int(memory_length), int(hidden_dim)
        self.w1 = nn.Parameter(torch.empty(d, m, h))
        self.b1 = nn.Parameter(torch.zeros(d, h))
        self.w2 = nn.Parameter(torch.empty(d, h))
        self.b2 = nn.Parameter(torch.zeros(d))
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.xavier_uniform_(self.w1)
        nn.init.xavier_uniform_(self.w2)

    def forward(self, trace: torch.Tensor) -> torch.Tensor:
        h = torch.einsum("bdm,dmh->bdh", trace, self.w1) + self.b1
        h = F.gelu(h)
        return torch.tanh(torch.einsum("bdh,dh->bd", h, self.w2) + self.b2)


class SmallCTMCell(nn.Module):
    """Compact CTM core with random pair synchronisation for action/value heads."""

    init_source = "rng_random_init"
    upstream_license = "Apache-2.0"

    def __init__(
        self,
        input_dim: int,
        d_model: int = 64,
        ticks: int = 12,
        memory_length: int = 8,
        nlm_hidden: int = 16,
        sync_pairs: int = 32,
        bottleneck_dim: int | None = None,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        if seed is not None:
            torch.manual_seed(int(seed))
        self.input_dim = int(input_dim)
        self.d_model = int(d_model)
        self.ticks = int(ticks)
        self.memory_length = int(memory_length)
        self.sync_pairs = int(sync_pairs)
        self.bottleneck_dim = None if bottleneck_dim is None else int(bottleneck_dim)
        if self.bottleneck_dim and self.bottleneck_dim < self.input_dim:
            self.input_proj = nn.Sequential(
                nn.Linear(self.input_dim, self.bottleneck_dim),
                nn.Tanh(),
                nn.Linear(self.bottleneck_dim, self.d_model),
            )
        else:
            self.input_proj = nn.Linear(self.input_dim, self.d_model)
        self.synapses = nn.Sequential(
            nn.Linear(self.d_model * 2, self.d_model * 2),
            nn.GLU(dim=-1),
            nn.LayerNorm(self.d_model),
        )
        self.trace_processor = PrivateNeuronMLP(self.d_model, self.memory_length, int(nlm_hidden))
        bound_state = (1.0 / max(1, self.d_model)) ** 0.5
        bound_trace = (1.0 / max(1, self.d_model + self.memory_length)) ** 0.5
        self.start_activated = nn.Parameter(torch.empty(self.d_model).uniform_(-bound_state, bound_state))
        self.start_trace = nn.Parameter(
            torch.empty(self.d_model, self.memory_length).uniform_(-bound_trace, bound_trace)
        )
        gen = torch.Generator()
        gen.manual_seed(0 if seed is None else int(seed) + 991)
        left = torch.randint(0, self.d_model, (self.sync_pairs,), generator=gen)
        right = torch.randint(0, self.d_model, (self.sync_pairs,), generator=gen)
        self.register_buffer("sync_left", left)
        self.register_buffer("sync_right", right)
        self.decay_params = nn.Parameter(torch.zeros(self.sync_pairs))
        self.sync_norm = nn.LayerNorm(self.sync_pairs)

    @property
    def feature_dim(self) -> int:
        return self.sync_pairs

    def zero_state(self, batch_size: int = 1, device: torch.device | str | None = None) -> CTMState:
        dev = torch.device(device) if device is not None else self.start_activated.device
        b = int(batch_size)
        activated = self.start_activated.to(dev).unsqueeze(0).expand(b, -1).clone()
        trace = self.start_trace.to(dev).unsqueeze(0).expand(b, -1, -1).clone()
        alpha = torch.zeros(b, self.sync_pairs, device=dev)
        beta = torch.zeros(b, self.sync_pairs, device=dev)
        return CTMState(activated=activated, trace=trace, sync_alpha=alpha, sync_beta=beta)

    def detach_state(self, state: CTMState | None) -> CTMState | None:
        if state is None:
            return None
        return CTMState(
            activated=state.activated.detach(),
            trace=state.trace.detach(),
            sync_alpha=state.sync_alpha.detach(),
            sync_beta=state.sync_beta.detach(),
        )

    def _sync(self, activated: torch.Tensor, alpha: torch.Tensor, beta: torch.Tensor):
        prod = activated[:, self.sync_left] * activated[:, self.sync_right]
        decay = torch.sigmoid(self.decay_params).unsqueeze(0)
        alpha = decay * alpha + prod
        beta = decay * beta + 1.0
        return alpha / torch.sqrt(beta.clamp_min(1e-6)), alpha, beta

    def tick(self, x: torch.Tensor, state: CTMState | None = None):
        if x.dim() == 1:
            x = x.unsqueeze(0)
        if state is None:
            state = self.zero_state(x.shape[0], x.device)
        drive = self.input_proj(x)
        activated, trace = state.activated, state.trace
        alpha, beta = state.sync_alpha, state.sync_beta
        pre = self.synapses(torch.cat([activated, drive], dim=-1))
        trace = torch.cat([trace[:, :, 1:], pre.unsqueeze(-1)], dim=-1)
        activated = self.trace_processor(trace)
        sync, alpha, beta = self._sync(activated, alpha, beta)
        new_state = CTMState(activated=activated, trace=trace, sync_alpha=alpha, sync_beta=beta)
        return self.sync_norm(sync), new_state

    def forward(self, x: torch.Tensor, state: CTMState | None = None, *, return_all_ticks: bool = False):
        if x.dim() == 1:
            x = x.unsqueeze(0)
        if state is None:
            state = self.zero_state(x.shape[0], x.device)
        sync = torch.zeros(x.shape[0], self.sync_pairs, device=x.device)
        ticks = []
        for _ in range(self.ticks):
            sync, state = self.tick(x, state)
            ticks.append(sync)
        new_state = state
        if return_all_ticks:
            return torch.stack(ticks, dim=1), new_state
        return sync, new_state

    def rollout(self, x_seq: torch.Tensor, *, freeze_after: int | None = None):
        """Run one continuous rollout and return synchronization at every tick.

        ``freeze_after`` keeps the input drive fixed after that 1-based tick; it is
        used by the DELIB accumulation gate without retraining or re-running
        truncated networks.
        """
        if x_seq.dim() != 3:
            raise ValueError("x_seq must have shape (batch, ticks, input_dim)")
        state = self.zero_state(x_seq.shape[0], x_seq.device)
        outs = []
        frozen = None
        for t in range(x_seq.shape[1]):
            if freeze_after is not None and t >= int(freeze_after):
                frozen = x_seq[:, int(freeze_after) - 1, :] if frozen is None else frozen
                x_t = frozen
            else:
                x_t = x_seq[:, t, :]
            sync, state = self.tick(x_t, state)
            outs.append(sync)
        return torch.stack(outs, dim=1), state


def flat_parameter_vector(module: nn.Module) -> torch.Tensor:
    return torch.cat([p.detach().reshape(-1).cpu() for p in module.parameters()])
