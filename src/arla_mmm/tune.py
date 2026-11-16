"""Grid search for the nonlinear media parameters (carry-over decay, saturation scale).

For fixed decays and scales the model is an ordinary regression, so the search is a
profile likelihood: try a combination, run OLS, keep the combination with the smallest
residual sum of squares. Parameters can be shared across channels (`groups`) to save
degrees of freedom. Each tuned group counts as one parameter in AIC/BIC.
"""

from dataclasses import dataclass, field
from itertools import product

import numpy as np
import pandas as pd

from .candidates import Config, build_controls, make_spec
from .data import CHANNELS
from .engine import LAG_COL, SAMPLE_START
from .features import adstock, saturate
from .spec import ModelSpec

DECAY_GRID = tuple(round(0.1 * i, 1) for i in range(10))        # 0.0 ... 0.9
SCALE_GRID = (0.25, 0.5, 1.0, 2.0, 4.0)                           # multiples of the base scale
EXHAUSTIVE_LIMIT = 150_000


def base_scales(data: pd.DataFrame) -> dict[str, float]:
    """Mean weekly spend per channel in £ (TV: mean of on-air weeks)."""
    return {ch: float(data.loc[data[ch] > 0, ch].mean()) for ch in CHANNELS}


@dataclass(frozen=True)
class Search:
    """Which parameters are tuned. Groups are tuples of channels sharing one value."""
    decay_groups: tuple[tuple[str, ...], ...] = ()
    scale_groups: tuple[tuple[str, ...], ...] = ()
    decay_grid: tuple[float, ...] = DECAY_GRID
    scale_grid: tuple[float, ...] = SCALE_GRID
    base_scale: dict = field(default_factory=dict)

    @property
    def n_params(self) -> int:
        return len(self.decay_groups) + len(self.scale_groups)


class _Problem:
    """Fast SSR for a (decay, scale) assignment: controls are projected out once."""

    def __init__(self, cfg: Config, search: Search, data: pd.DataFrame, end: int | None):
        self.cfg, self.search, self.data = cfg, search, data
        self.rows = np.arange(SAMPLE_START, len(data) if end is None else end)
        Z = build_controls(cfg, data).astype(float)
        z = np.log(data["sales_units"].to_numpy(dtype=float))
        if cfg.lag_y:
            Z[LAG_COL] = pd.Series(z, index=data.index).shift(1)
        self.fixed_media = [ch for ch in CHANNELS if ch == "tv" and cfg.tv_two_part]
        if self.fixed_media:
            on = (data["tv"] > 0).to_numpy()
            Z["tv_on_air"] = on.astype(float)
            Z["tv_log"] = np.where(on, np.log(np.where(on, data["tv"], 1.0)), 0.0)
        self.Q, _ = np.linalg.qr(Z.to_numpy()[self.rows])
        self.y = self._resid(z[self.rows])
        self.channels = [ch for ch in CHANNELS if ch not in self.fixed_media]
        self._cache: dict = {}

    def _resid(self, v):
        return v - self.Q @ (self.Q.T @ v)

    def column(self, ch: str, decay: float, mult: float) -> np.ndarray:
        key = (ch, decay, mult)
        if key not in self._cache:
            a = adstock(self.data[ch], decay)
            col = saturate(a, self.cfg.shape, mult * self.search.base_scale[ch])
            self._cache[key] = self._resid(col[self.rows])
        return self._cache[key]

    def assignment(self, values: tuple) -> tuple[dict, dict]:
        nd = len(self.search.decay_groups)
        decay = dict(self.cfg.decay)
        mult = {ch: self.cfg.scale[ch] / self.search.base_scale[ch] for ch in CHANNELS}
        for group, v in zip(self.search.decay_groups, values[:nd]):
            decay.update({ch: v for ch in group})
        for group, v in zip(self.search.scale_groups, values[nd:]):
            mult.update({ch: v for ch in group})
        return decay, mult

    def ssr(self, values: tuple) -> float:
        decay, mult = self.assignment(values)
        M = np.column_stack([self.column(ch, decay.get(ch, 0.0), mult[ch]) for ch in self.channels])
        beta, *_ = np.linalg.lstsq(M, self.y, rcond=None)
        r = self.y - M @ beta
        return float(r @ r)


def tune(cfg: Config, search: Search, data: pd.DataFrame, end: int | None = None) -> tuple[Config, dict]:
    """Best Config on weeks < end, plus the search record (best SSR, profiles per group)."""
    prob = _Problem(cfg, search, data, end)
    grids = [search.decay_grid] * len(search.decay_groups) + [search.scale_grid] * len(search.scale_groups)
    size = int(np.prod([len(g) for g in grids])) if grids else 1

    if size <= EXHAUSTIVE_LIMIT:
        best = min(product(*grids), key=prob.ssr)
    else:
        # coordinate search from several starting points; each pass optimises one group at a time
        best, best_ssr = None, np.inf
        for start_decay, start_scale in product((0.0, 0.3, 0.6), (1.0,)):
            cur = [start_decay] * len(search.decay_groups) + [start_scale] * len(search.scale_groups)
            cur_ssr = prob.ssr(tuple(cur))
            improved = True
            while improved:
                improved = False
                for i, grid in enumerate(grids):
                    for v in grid:
                        trial = cur.copy()
                        trial[i] = v
                        s = prob.ssr(tuple(trial))
                        if s < cur_ssr - 1e-12:
                            cur, cur_ssr, improved = trial, s, True
            if cur_ssr < best_ssr:
                best, best_ssr = tuple(cur), cur_ssr

    # likelihood profile per group: change one group, hold the others at their best value
    n = len(prob.rows)
    best_ssr = prob.ssr(best)
    profiles = {}
    labels = ["decay " + "+".join(g) for g in search.decay_groups] + ["scale " + "+".join(g) for g in search.scale_groups]
    for i, (label, grid) in enumerate(zip(labels, grids)):
        prof = {}
        for v in grid:
            trial = list(best)
            trial[i] = v
            prof[v] = n * np.log(prob.ssr(tuple(trial)) / best_ssr)     # = AIC difference to the best
        profiles[label] = prof

    decay, mult = prob.assignment(best)
    tuned = cfg.with_(
        decay=decay,
        scale={ch: mult[ch] * search.base_scale[ch] for ch in CHANNELS},
        n_extra_params=search.n_params,
    )
    return tuned, {"best": dict(zip(labels, best)), "profiles": profiles, "ssr": best_ssr}


def tuned_spec(cfg: Config, search: Search, data: pd.DataFrame) -> ModelSpec:
    """Spec tuned on the full sample; its `refit` re-tunes on a training window (for hold-outs)."""
    best, record = tune(cfg, search, data)
    spec = make_spec(best)
    object.__setattr__(spec, "refit", lambda d, end: make_spec(tune(cfg, search, d, end)[0]))
    object.__setattr__(spec, "search_record", record)
    return spec
