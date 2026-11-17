"""Benchmark-anchored regression: what does it cost the model to have plausible effect sizes?

The final model (decays and curve scales fixed) is re-estimated with a normal prior on each of the
five media coefficients, centred on the value that would give the channel the literature's average
long-term advertising elasticity (0.24, Sethuraman, Tellis & Briesch 2011). The other coefficients
have flat priors. With the residual variance taken from the unrestricted fit the posterior mean is
available in closed form (a ridge penalty towards a target instead of towards zero):

    beta = (X'X + s2 * P)^-1 (X'z + s2 * P * b0),      P = diag(1 / sd_c^2) for media, 0 otherwise

The prior's strength is one number k: sd_c = k x the benchmark-sized coefficient. k = 1 says "the true
effect is within +-100% of the benchmark (one sd)", k = 0.1 "within +-10%"; k = None is no prior
(the final model), k = 0 fixes the media coefficients at benchmark size."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import CHANNELS
from .engine import LAG_COL, design, simulate
from .final import FinalModel
from .insights import BENCHMARK, LABEL, elasticities
from .scenarios import standard_scenarios
from .spec import ModelSpec

STRENGTHS = (None, 2.0, 1.0, 0.5, 0.25, 0.1, 0.05, 0.02, 0.0)
HOLDOUT = 26


def strength_label(k: float | None) -> str:
    if k is None:
        return "no prior (final model)"
    if k == 0:
        return "fixed at benchmark"
    return f"±{k * 100:.0f}%"


def benchmark_coefficients(m: FinalModel) -> pd.Series:
    """Media coefficients that would give every channel a long-term elasticity of 0.24, holding the
    rest of the model fixed (elasticity is proportional to the coefficient). The anchored fits
    re-estimate the rest, so their elasticities are recomputed, not assumed."""
    lt = elasticities(m)["long-term"]
    return pd.Series({ch: m.fit.params[ch] * BENCHMARK["long"] / lt[LABEL[ch]] for ch in CHANNELS})


@dataclass
class AnchoredFit:
    strength: float | None
    params: pd.Series
    cov: np.ndarray              # posterior covariance (media rows are zero when the coefficients are fixed)
    sigma: float                 # residual standard deviation of this fit (log sales)
    ssr: float
    resid: np.ndarray


def fit_anchored(spec: ModelSpec, data: pd.DataFrame, target: pd.Series, strength: float | None,
                 rows: np.ndarray, s2: float | None = None) -> AnchoredFit:
    """Posterior mean of the coefficients on `rows` for one prior strength."""
    X, z = design(spec, data)
    cols = list(X.columns)
    Xa, za = X.to_numpy()[rows], z.to_numpy()[rows]
    k = len(cols)
    media = [cols.index(ch) for ch in CHANNELS]
    free = [i for i in range(k) if i not in media]
    b0 = np.zeros(k)
    b0[media] = target[CHANNELS].to_numpy()
    ols = np.linalg.lstsq(Xa, za, rcond=None)[0]
    if s2 is None:
        s2 = float(((za - Xa @ ols) ** 2).sum() / (len(rows) - k))
    cov = np.zeros((k, k))
    if strength is None:
        beta = ols
        cov = s2 * np.linalg.inv(Xa.T @ Xa)
    elif strength == 0:
        beta = b0.copy()
        Xf = Xa[:, free]
        beta[free] = np.linalg.lstsq(Xf, za - Xa[:, media] @ b0[media], rcond=None)[0]
        cov[np.ix_(free, free)] = s2 * np.linalg.inv(Xf.T @ Xf)
    else:
        P = np.zeros((k, k))
        P[media, media] = 1.0 / (strength * b0[media]) ** 2
        A = np.linalg.inv(Xa.T @ Xa + s2 * P)
        beta = A @ (Xa.T @ za + s2 * P @ b0)
        cov = s2 * A
    resid = za - Xa @ beta
    n_free = len(free) if strength == 0 else k
    return AnchoredFit(strength, pd.Series(beta, index=cols), cov, float(np.sqrt((resid ** 2).sum() / (len(rows) - n_free))),
                       float((resid ** 2).sum()), resid)


def _bump(m: FinalModel, a: AnchoredFit, channels: list[str], bump: float) -> np.ndarray:
    up = m.data.copy()
    up[channels] = up[channels] * (1 + bump)
    return simulate(m.spec, a.params, up, m.rows, a.resid)


def sweep(m: FinalModel, strengths=STRENGTHS) -> pd.DataFrame:
    """One row per prior strength: fit, forecast error on unseen weeks, effect sizes, returns, and the
    gain the model then credits to the first-step plan (TV -10%, digital +10%, replay of 2024).

    Hold-out: coefficients re-estimated on the weeks before the last 26 with the same prior, then a
    26-week forecast. Decays, scales and the prior's centre are those of the full sample in every row."""
    d = m.data
    target = benchmark_coefficients(m)
    sales, price = d["sales_units"].to_numpy(dtype=float)[m.rows], d["avg_price"].to_numpy()[m.rows]
    replay, plans = standard_scenarios(m)
    cf = d.copy()
    cf.loc[cf.index[replay.rows], CHANNELS] = plans["B10"].spend.to_numpy()
    pos = np.searchsorted(m.rows, replay.rows)
    origin = len(d) - HOLDOUT
    train, test = m.rows[m.rows < origin], np.arange(origin, len(d))
    s2 = float(m.fit.res.mse_resid)
    n = len(m.rows)
    ssr0 = None
    out = {}
    for k in strengths:
        a = fit_anchored(m.spec, d, target, k, m.rows, s2)
        ssr0 = a.ssr if ssr0 is None else ssr0
        h = fit_anchored(m.spec, d, target, k, train)
        pred = simulate(m.spec, h.params, d, test)
        row = {
            "prior sd, % of benchmark": np.nan if k is None else k * 100,
            "R²": 1 - a.ssr / float(((np.log(sales) - np.log(sales).mean()) ** 2).sum()),
            "residual sd %": a.sigma * 100,
            "Δ AIC vs final model": n * np.log(a.ssr / ssr0) - (2 * len(CHANNELS) if k == 0 else 0),
            "hold-out error %": float(np.mean(np.abs(pred / d["sales_units"].to_numpy()[test] - 1)) * 100),
            "lagged sales": a.params[LAG_COL],
        }
        for ch in CHANNELS:
            row[f"elasticity {LABEL[ch]}"] = float((_bump(m, a, [ch], 0.01).sum() / sales.sum() - 1) / 0.01)
        for ch in CHANNELS:
            gain = _bump(m, a, [ch], 0.10) - sales
            row[f"mROI {LABEL[ch]}"] = float((gain * price).sum() / (0.10 * d[ch].to_numpy()[m.rows].sum()))
        r = replay.rows
        base_rev = float((sales[pos] * price[pos]).sum())
        plan_units = simulate(m.spec, a.params, cf, r, a.resid[pos])
        row["first-step plan, Δ revenue %"] = float(((plan_units * price[pos]).sum() / base_rev - 1) * 100)
        order = sorted(CHANNELS, key=lambda c: -row[f"mROI {LABEL[c]}"])
        row["ranking by return on the next £"] = " > ".join(LABEL[c] for c in order)
        out[strength_label(k)] = row
    return pd.DataFrame.from_dict(out, orient="index")
