"""The final model (M14) fitted on the full history, and fast simulation under parameter uncertainty."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd

from .candidates import Config, make_spec
from .contributions import reference_levels
from .data import CHANNELS, load_data
from .engine import LAG_COL, Fit, design, fit
from .features import promo_depth, regular_price
from .ladder import final_config
from .spec import ModelSpec
from .tune import tune

N_DRAWS = 2000
SEED = 20261116


@dataclass
class FinalModel:
    config: Config
    spec: ModelSpec
    fit: Fit
    data: pd.DataFrame
    draws: np.ndarray            # (N_DRAWS, k) coefficient vectors; row 0 is the point estimate

    @property
    def columns(self) -> list[str]:
        return list(self.fit.X.columns)

    @property
    def rows(self) -> np.ndarray:
        return self.fit.rows

    @property
    def _observed(self):
        if not hasattr(self, "_obs_cache"):
            self._obs_cache = design(self.spec, self.data)
        return self._obs_cache

    def coef(self, name: str) -> np.ndarray:
        """All draws of one coefficient."""
        return self.draws[:, self.columns.index(name)]

    def paths(self, data_cf: pd.DataFrame, rows: np.ndarray | None = None, point_only: bool = False) -> np.ndarray:
        """Sales paths (draws x weeks) for counterfactual inputs, one per coefficient draw.

        Same-shocks counterfactual: for every draw the weekly shocks are the residuals that draw
        leaves on the observed data, so each draw reproduces observed sales when `data_cf` is the
        observed data. Differences between two calls are therefore pure model effects, and their
        spread across draws is parameter uncertainty."""
        rows = self.rows if rows is None else rows
        draws = self.draws[:1] if point_only else self.draws
        cols = self.columns
        exog = [c for c in cols if c != LAG_COL]
        ie = [cols.index(c) for c in exog]
        lam = draws[:, cols.index(LAG_COL)]
        X_obs, z_obs = self._observed
        shocks = z_obs.to_numpy()[rows][None, :] - draws @ X_obs.to_numpy()[rows].T      # draws x T
        lin = draws[:, ie] @ self.spec.build(data_cf)[exog].to_numpy(dtype=float)[rows].T + shocks
        z_prev = np.full(len(draws), z_obs.to_numpy()[rows[0] - 1])
        out = np.empty_like(lin)
        for t in range(lin.shape[1]):
            z_prev = lin[:, t] + lam * z_prev
            out[:, t] = z_prev
        return np.exp(out)


@lru_cache(maxsize=1)
def final_model() -> FinalModel:
    """Tune decays/TV scale on the full history, fit, and draw coefficients from the
    Newey-West covariance (decays and scales held at their estimates)."""
    data = load_data()
    cfg, search = final_config(data)
    cfg = tune(cfg, search, data)[0]
    spec = make_spec(cfg)
    f = fit(spec, data)
    rng = np.random.default_rng(SEED)
    draws = rng.multivariate_normal(f.params.to_numpy(), f.res_hac.cov_params().to_numpy(), size=N_DRAWS)
    draws[0] = f.params.to_numpy()
    return FinalModel(cfg, spec, f, data, draws)


# ------------------------------------------------------------------ decomposition with intervals

def with_reference(data: pd.DataFrame, off: tuple[str, ...], ref: dict[str, float]) -> pd.DataFrame:
    """Observed data with the drivers in `off` set to their reference.

    Channels -> reference spend; "promotions" -> no price promotion (shelf price paid every week);
    "growth" -> underlying trend frozen at the first week."""
    cf = data.copy()
    for g in off:
        if g == "promotions":
            cf["regular_price"] = regular_price(data)
            cf["promo_depth"] = 0.0
        elif g == "growth":
            cf["trend_override"] = 0.0
        else:
            cf[g] = ref[g]
    return cf


def shapley_paths(m: FinalModel, players: tuple[str, ...], reference: str = "floor") -> dict[str, np.ndarray]:
    """Shapley decomposition of sales for every coefficient draw.

    Returns {"base": (draws x weeks), player: (draws x weeks), ...}; the arrays sum to observed sales."""
    ref = reference_levels(m.data, reference)
    n = len(players)
    value = {}
    for k in range(n + 1):
        for S in combinations(players, k):
            off = tuple(p for p in players if p not in S)
            value[frozenset(S)] = m.paths(with_reference(m.data, off, ref))
    out = {"base": value[frozenset()]}
    for p in players:
        others = [q for q in players if q != p]
        phi = 0.0
        for k in range(n):
            w = factorial(k) * factorial(n - k - 1) / factorial(n)
            for S in combinations(others, k):
                phi = phi + w * (value[frozenset(S) | {p}] - value[frozenset(S)])
        out[p] = phi
    return out


def quantiles(x: np.ndarray, axis: int = 0) -> dict[str, np.ndarray]:
    """Point estimate (draw 0) and the 5% / 50% / 95% quantiles across draws."""
    q = np.quantile(x, [0.05, 0.5, 0.95], axis=axis)
    return {"estimate": np.take(x, 0, axis=axis), "p5": q[0], "p50": q[1], "p95": q[2]}
