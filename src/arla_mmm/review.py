"""Step 9: diagnostics for the critical review of the final model (results/part2/step9_*.md).

Each function answers one question about whether the large social and influencer effects could
be an artefact: of budgets following demand, of three correlated channels sharing one effect, or
of the horizon at which the effect is measured. Plus the numbers for the test design and the profit view."""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from .candidates import build_controls, media_response
from .data import CHANNELS
from .engine import HAC_MAXLAGS, fit, simulate
from .features import adstock, saturate
from .final import FinalModel
from .spec import ModelSpec

ALWAYS_ON = ["instagram", "tiktok", "influencer", "pos_promotion"]
DIGITAL = ["instagram", "tiktok", "influencer"]
HOLDOUT = 26


def _hac(y, X):
    return sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_MAXLAGS})


# ------------------------------------------------------------------ 1. does spend follow demand?

def spend_process(m: FinalModel) -> pd.DataFrame:
    """How each channel's weekly spend behaves: persistence, correlation with the other channels, and
    whether it responds to the things that move demand (season, trend, promotions, last week's sales).

    If platforms or planners spent more when demand is high, spend should rise in promotion weeks
    (demand +13%) and after strong sales weeks."""
    d = m.data
    _, z = m._observed
    ctrl = build_controls(m.config, d).drop(columns=["Intercept", "promo_depth_lag1"])
    corr = d[CHANNELS].corr()
    rows = {}
    for ch in CHANNELS:
        y = (d[ch] > 0).astype(float) if ch == "tv" else np.log(d[ch])
        X = sm.add_constant(pd.concat([ctrl, z.shift(1).rename("lag_sales")], axis=1)).iloc[1:]
        r = _hac(y.iloc[1:], X)
        season = [c for c in X.columns if c.startswith("season") or c == "january"]
        rows[ch] = {
            "autocorrelation, 1 week": d[ch].autocorr(1),
            "largest correlation with another channel": corr[ch].drop(ch).abs().max(),
            "R² on demand drivers": sm.OLS(y.iloc[1:], X).fit().rsquared,
            "season p": float(r.wald_test(np.eye(len(X.columns))[[X.columns.get_loc(c) for c in season]], scalar=True).pvalue),
            "trend p": r.pvalues["trend"],
            "promotion depth: coefficient": r.params["promo_depth"], "promotion depth p": r.pvalues["promo_depth"],
            "last week's sales: coefficient": r.params["lag_sales"], "last week's sales p": r.pvalues["lag_sales"],
        }
    return pd.DataFrame(rows).T


def lead_placebo(m: FinalModel, horizons=(1, 4, 8)) -> pd.DataFrame:
    """Placebo at longer horizons: does the *future* average spend (next h weeks) 'explain' this week's
    sales once the model is in? It should not, unless budgets are set where demand is expected."""
    X, z = m._observed
    d = m.data
    rows = {}
    for h in horizons:
        lead = pd.DataFrame({f"lead_{ch}": np.log1p(d[ch]).shift(-1).iloc[::-1].rolling(h).mean().iloc[::-1] for ch in CHANNELS})
        Z = pd.concat([X, lead], axis=1).iloc[1:len(d) - h]
        r = _hac(z.iloc[1:len(d) - h], Z)
        R = np.eye(len(Z.columns))[[Z.columns.get_loc(c) for c in lead.columns]]
        rows[f"next {h} week(s)"] = {
            "weeks used": int(r.nobs), "joint p (all five channels)": float(r.wald_test(R, scalar=True).pvalue),
            **{f"{ch} p": r.pvalues[f"lead_{ch}"] for ch in CHANNELS},
        }
    return pd.DataFrame.from_dict(rows, orient="index")


def frequency_split(m: FinalModel, window: int = 13) -> pd.DataFrame:
    """Is the effect the same for slow and fast movements of spend?

    Each always-on channel's regressor is split into its 13-week centred average (the budget level,
    which planning could align with expected demand) and the week-to-week deviation from it (which
    planning cannot). Budgets that follow demand would show up as a larger coefficient on the slow part."""
    X, z = m._observed
    Z = X.copy()
    for ch in ALWAYS_ON:
        slow = X[ch].rolling(window, center=True, min_periods=window // 2 + 1).mean()
        Z[f"{ch}_slow"], Z[f"{ch}_fast"] = slow, X[ch] - slow
        Z = Z.drop(columns=ch)
    r = _hac(z.iloc[m.rows], Z.iloc[m.rows])
    rows = {}
    for ch in ALWAYS_ON:
        R = np.zeros(len(Z.columns))
        R[Z.columns.get_loc(f"{ch}_slow")], R[Z.columns.get_loc(f"{ch}_fast")] = 1, -1
        rows[ch] = {
            "final model": m.fit.params[ch],
            "slow part (13-week level)": r.params[f"{ch}_slow"], "slow se": r.bse[f"{ch}_slow"],
            "fast part (week-to-week)": r.params[f"{ch}_fast"], "fast se": r.bse[f"{ch}_fast"],
            "share of the regressor's variance that is fast %": float(Z[f"{ch}_fast"].var() / X[ch].var() * 100),
            "p (slow = fast)": float(r.wald_test(R, scalar=True).pvalue),
        }
    out = pd.DataFrame(rows).T
    out.attrs["aic"], out.attrs["aic_final"] = float(r.aic), float(m.fit.res.aic)
    return out


# ------------------------------------------------------------------ 2. one shared digital effect?

def _holdout_mape(spec: ModelSpec, d: pd.DataFrame) -> float:
    origin = len(d) - HOLDOUT
    f = fit(spec, d, end=origin)
    rows = np.arange(origin, len(d))
    pred = simulate(spec, f.params, d, rows)
    return float(np.mean(np.abs(pred / d["sales_units"].to_numpy()[rows] - 1)) * 100)


def _bump_roi(spec: ModelSpec, f, d: pd.DataFrame, channels: list[str], bump: float = 0.10) -> float:
    up = d.copy()
    up[channels] = up[channels] * (1 + bump)
    price, sales = d["avg_price"].to_numpy()[f.rows], d["sales_units"].to_numpy()[f.rows]
    gain = simulate(spec, f.params, up, f.rows, f.res.resid.to_numpy()) - sales
    return float((gain * price).sum() / (bump * d[channels].to_numpy()[f.rows].sum()))


def digital_aggregate(m: FinalModel) -> tuple[pd.DataFrame, pd.DataFrame]:
    """M14 against the same model with Instagram + TikTok + influencer spend added up into one
    'digital' channel (one decay chosen by AIC, curve bending at mean spend). Hold-out with the
    decays fixed at their full-sample values for both models. Also the coefficient correlations."""
    d, cfg = m.data, m.config
    scale = float(d[DIGITAL].sum(axis=1).mean())

    def make(decay: float) -> ModelSpec:
        def b(data: pd.DataFrame) -> pd.DataFrame:
            X = build_controls(cfg, data)
            X["tv"] = media_response(cfg, data, "tv")
            X["digital"] = saturate(adstock(data[DIGITAL].sum(axis=1), decay), cfg.shape, scale)
            X["pos_promotion"] = media_response(cfg, data, "pos_promotion")
            return X
        return ModelSpec(f"digital_{decay}", b, lag_y=True, n_extra_params=4)       # decays for TV, digital, POS + the TV scale

    fits = {dec: fit(make(dec), d) for dec in np.round(np.arange(0, 1.0, 0.1), 1)}
    best = min(fits, key=lambda k: fits[k].res.aic)
    spec_a = make(best)
    fa = fit(spec_a, d)
    f0 = m.fit
    table = pd.DataFrame({
        "final model (three digital channels)": {
            "parameters": f0.n_params, "AIC": f0.aic, "BIC": f0.bic, "hold-out error %, last 26 weeks": _holdout_mape(m.spec, d),
            "revenue per extra £ of digital spend": _bump_roi(m.spec, f0, d, DIGITAL),
            "revenue per extra £ of TV": _bump_roi(m.spec, f0, d, ["tv"]),
            "revenue per extra £ of POS": _bump_roi(m.spec, f0, d, ["pos_promotion"])},
        f"one digital channel (decay {best})": {
            "parameters": fa.n_params, "AIC": fa.aic, "BIC": fa.bic, "hold-out error %, last 26 weeks": _holdout_mape(spec_a, d),
            "revenue per extra £ of digital spend": _bump_roi(spec_a, fa, d, DIGITAL),
            "revenue per extra £ of TV": _bump_roi(spec_a, fa, d, ["tv"]),
            "revenue per extra £ of POS": _bump_roi(spec_a, fa, d, ["pos_promotion"])},
    })
    cov = m.fit.res_hac.cov_params()
    sd = np.sqrt(np.diag(cov))
    corr = (cov / np.outer(sd, sd)).loc[CHANNELS, CHANNELS]
    return table, corr


# ------------------------------------------------------------------ 3. test design

def forecast_noise(m: FinalModel, weeks=(4, 8, 13, 26), first_origin: int = 52) -> pd.DataFrame:
    """How precisely can a T-week test be read against the model's forecast for the unchanged plan?

    For every possible start week the model forecasts the next T weeks from the actual inputs (multi-week,
    no peeking at sales); the spread of the T-week average error is the noise a test has to beat.
    Minimum detectable effect: one-sided 5% test, 80% power = 2.49 x that spread. In-sample coefficients,
    so slightly optimistic; the out-of-sample back-test in step 8 gives a similar size."""
    d = m.data
    logy = np.log(d["sales_units"].to_numpy(dtype=float))
    k = stats.norm.ppf(0.95) + stats.norm.ppf(0.80)
    rows = {}
    for T in weeks:
        err = []
        for o in range(first_origin, len(d) - T + 1):
            r = np.arange(o, o + T)
            err.append(float(np.mean(logy[r] - np.log(simulate(m.spec, m.fit.params, d, r)))))
        sd = float(np.std(err, ddof=1))
        rows[f"{T} weeks"] = {"forecasts compared": len(err), "spread of the average error %": sd * 100,
                              "minimum detectable change in sales %": (np.exp(k * sd) - 1) * 100}
    return pd.DataFrame(rows).T


# ------------------------------------------------------------------ 4. profit view

def profit_view(roi: pd.DataFrame, elasticities: pd.DataFrame, benchmark: float, margins=(0.20, 0.30, 0.40)) -> pd.DataFrame:
    """Profit per extra £ of spend = margin x revenue per extra £ - 1, for a range of margins, as estimated
    and with every above-benchmark channel scaled down to the benchmark long-term elasticity."""
    rows = {}
    for ch in roi.index:
        mroi = roi.loc[ch, "marginal ROI"]
        factor = min(1.0, benchmark / elasticities.loc[ch, "long-term"])
        rows[ch] = {
            "revenue per extra £": mroi,
            **{f"profit per extra £ at {int(g * 100)}% margin": g * mroi - 1 for g in margins},
            "break-even margin %": 100 / mroi,
            "revenue per extra £ if the effect were benchmark-sized": mroi * factor,
            **{f"same, profit at {int(g * 100)}% margin": g * mroi * factor - 1 for g in margins},
            "effect could be overstated by a factor of … and still pay at 30%": 0.30 * mroi,
        }
    return pd.DataFrame(rows).T
