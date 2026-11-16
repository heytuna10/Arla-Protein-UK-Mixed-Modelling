"""Fit, simulate and forecast any ModelSpec."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .spec import ModelSpec

LAG_COL = "lagged_sales"
HAC_MAXLAGS = 4
# All candidates are compared on the same weeks. Week 0 is dropped because the
# baseline needs one lag of sales; later candidates keep the same sample so that
# AIC/BIC stay comparable.
SAMPLE_START = 1


@dataclass
class Fit:
    spec: ModelSpec
    res: "sm.regression.linear_model.RegressionResultsWrapper"   # plain OLS
    res_hac: "sm.regression.linear_model.RegressionResultsWrapper"
    X: pd.DataFrame
    z: pd.Series
    rows: np.ndarray           # integer positions of the estimation rows in `data`

    @property
    def params(self) -> pd.Series:
        return self.res.params

    @property
    def n_params(self) -> int:
        """Estimated parameters incl. constant and nonlinear ones (excl. error variance)."""
        return int(self.res.df_model + 1 + self.spec.n_extra_params)

    @property
    def aic(self) -> float:
        return float(self.res.aic + 2 * self.spec.n_extra_params)

    @property
    def bic(self) -> float:
        return float(self.res.bic + np.log(self.res.nobs) * self.spec.n_extra_params)


def design(spec: ModelSpec, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Full design matrix (with the observed lagged-sales term if the spec has one) and z."""
    X = spec.build(data).astype(float)
    z = pd.Series(spec.z(data["sales_units"].to_numpy(dtype=float)), index=data.index, name="z")
    if spec.lag_y:
        X.insert(1, LAG_COL, z.shift(1))
    return X, z


def fit(spec: ModelSpec, data: pd.DataFrame, end: int | None = None, start: int = SAMPLE_START) -> Fit:
    """OLS on rows start..end-1 of `data` (default: the common sample, all weeks but the first)."""
    X, z = design(spec, data)
    rows = np.arange(start, len(data) if end is None else end)
    Xs, zs = X.iloc[rows], z.iloc[rows]
    if Xs.isna().any().any():
        raise ValueError(f"{spec.name}: NaN in design matrix on the estimation sample")
    ols = sm.OLS(zs, Xs)
    return Fit(spec, ols.fit(), ols.fit(cov_type="HAC", cov_kwds={"maxlags": HAC_MAXLAGS}), Xs, zs, rows)


def simulate(
    spec: ModelSpec,
    params: pd.Series,
    data: pd.DataFrame,
    rows: np.ndarray,
    shocks: np.ndarray | None = None,
) -> np.ndarray:
    """Sales path (units) over `rows` for the inputs in `data`.

    With a lagged-sales term the path is recursive: each week feeds the *simulated*
    previous week back in, starting from observed sales in the week before rows[0].
    `shocks` (same length as rows) are added to z each week; pass the in-sample
    residuals to get a "same shocks" counterfactual, which reproduces observed sales
    exactly when `data` is the observed data.
    """
    X = spec.build(data).astype(float)
    exog = [c for c in X.columns if c != LAG_COL]
    lin = X[exog].to_numpy()[rows] @ params[exog].to_numpy()
    if shocks is not None:
        lin = lin + np.asarray(shocks)
    if not spec.lag_y:
        return spec.z_inv(lin)
    lam = params[LAG_COL]
    z_prev = spec.z(float(data["sales_units"].iloc[rows[0] - 1]))
    out = np.empty(len(rows))
    for i, v in enumerate(lin):
        z_prev = v + lam * z_prev
        out[i] = z_prev
    return spec.z_inv(out)


def one_step(spec: ModelSpec, params: pd.Series, data: pd.DataFrame, rows: np.ndarray) -> np.ndarray:
    """One-week-ahead predictions (units) using observed lagged sales."""
    X, _ = design(spec, data)
    return spec.z_inv(X.iloc[rows].to_numpy() @ params[X.columns].to_numpy())
