"""Step 6: contributions, ROI and marginal ROI with intervals, response curves, price and promotion effects.

Intervals are the 5%-95% range over coefficient draws from the Newey-West covariance, with the
carry-over decays and saturation scales held at their estimates (their effect on ROI is in
results/part2/step5_robustness.md)."""

import numpy as np
import pandas as pd

from .contributions import reference_levels
from .data import CHANNELS
from .features import promo_depth, regular_price, saturate
from .final import FinalModel, quantiles, shapley_paths, with_reference

LABEL = {"tv": "TV", "instagram": "Instagram", "tiktok": "TikTok", "influencer": "Influencer", "pos_promotion": "POS"}
PLAYERS = tuple(CHANNELS) + ("promotions", "growth")


def _q(x) -> dict:
    q = quantiles(np.asarray(x))
    return {k: float(v) for k, v in q.items()}


def roi_summary(m: FinalModel, bump: float = 0.10) -> pd.DataFrame:
    """Per channel: spend, contribution, revenue ROI above the floor, marginal ROI, break-even margins."""
    d = m.data.iloc[m.rows]
    price, sales = d["avg_price"].to_numpy(), d["sales_units"].to_numpy()
    ref = reference_levels(m.data, "floor")
    sh = shapley_paths(m, tuple(CHANNELS))
    rows = {}
    for ch in CHANNELS:
        inc_spend = float((d[ch] - ref[ch]).sum())
        roi = _q((sh[ch] * price).sum(axis=1) / inc_spend)
        up = m.data.copy()
        up[ch] = up[ch] * (1 + bump)
        mroi = _q(((m.paths(up) - sales) * price).sum(axis=1) / (bump * d[ch].sum()))
        share = _q(sh[ch].sum(axis=1) / sales.sum() * 100)
        rows[LABEL[ch]] = {
            "spend £m": d[ch].sum() / 1e6,
            "share of media spend %": d[ch].sum() / d[CHANNELS].sum().sum() * 100,
            "floor £/week": ref[ch],
            "spend above floor £m": inc_spend / 1e6,
            "% of sales": share["estimate"], "% of sales p5": share["p5"], "% of sales p95": share["p95"],
            "ROI": roi["estimate"], "ROI p5": roi["p5"], "ROI p95": roi["p95"],
            "marginal ROI": mroi["estimate"], "mROI p5": mroi["p5"], "mROI p95": mroi["p95"],
            "break-even margin % (marginal £)": 100 / mroi["estimate"],
            "break-even margin % (average £ above floor)": 100 / roi["estimate"],
        }
    out = pd.DataFrame(rows).T
    base = _q(sh["base"].sum(axis=1) / sales.sum() * 100)
    out.attrs["base"] = base
    return out


def decomposition(m: FinalModel) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Weekly decomposition (units, point estimate) into base, growth, promotions and channels,
    and the same as % of sales per year with 5-95% ranges for the total."""
    sh = shapley_paths(m, PLAYERS)
    d = m.data.iloc[m.rows]
    weekly = pd.DataFrame({k: v[0] for k, v in sh.items()})
    weekly.insert(0, "week_beg", d["week_beg"].to_numpy())
    weekly["sales_units"] = d["sales_units"].to_numpy()
    year = d["week_beg"].dt.year.to_numpy()
    cols = ["base", "growth", "promotions"] + CHANNELS
    table = {}
    for label, mask in [(str(y), year == y) for y in sorted(set(year))] + [("all", np.ones(len(d), bool))]:
        tot = d["sales_units"].to_numpy()[mask].sum()
        table[label] = {c: sh[c][0][mask].sum() / tot * 100 for c in cols}
    table["all, p5"] = {c: np.quantile(sh[c].sum(axis=1), 0.05) / d["sales_units"].sum() * 100 for c in cols}
    table["all, p95"] = {c: np.quantile(sh[c].sum(axis=1), 0.95) / d["sales_units"].sum() * 100 for c in cols}
    return weekly[["week_beg", "sales_units"] + cols], pd.DataFrame(table).T


def promotions_history(m: FinalModel) -> dict:
    """What the 52 price-promotion weeks did to units and revenue over the history.

    Counterfactual: no promotion (shelf price paid in every week), everything else as observed,
    including the post-promo dip and repeat purchase that follow from each promotion."""
    d = m.data.iloc[m.rows]
    ref = reference_levels(m.data, "floor")
    cf = with_reference(m.data, ("promotions",), ref)
    units_cf = m.paths(cf)
    shelf = regular_price(m.data).to_numpy()[m.rows]
    rev, units = d["revenue"].to_numpy(), d["sales_units"].to_numpy()
    rev_cf = units_cf * shelf
    n_promo = int(d["price_promo"].sum())
    return {
        "promo weeks": n_promo,
        "units %": _q((units.sum() / units_cf.sum(axis=1) - 1) * 100),
        "revenue %": _q((rev.sum() / rev_cf.sum(axis=1) - 1) * 100),
        "revenue £m": _q((rev.sum() - rev_cf.sum(axis=1)) / 1e6),
        "revenue per promo week £k": _q((rev.sum() - rev_cf.sum(axis=1)) / n_promo / 1e3),
        "units per promo week k": _q((units.sum() - units_cf.sum(axis=1)) / n_promo / 1e3),
    }


def promotion_curve(m: FinalModel, discounts=(0.10, 0.15, 0.20, 0.24, 0.30, 0.35), horizon: int = 12) -> pd.DataFrame:
    """One promotion week at a given discount, starting from a normal week (stylised).

    Effects in % of a normal week's units / revenue: the promotion week itself, the following weeks
    (post-promo dip, then repeat purchase), and the total."""
    b, b_lag, lam = m.coef("promo_depth"), m.coef("promo_depth_lag1"), m.coef("lagged_sales")
    rows = {}
    for disc in discounts:
        depth = -np.log(1 - disc)
        e = np.empty((len(b), horizon))
        e[:, 0] = b * depth
        e[:, 1] = lam * e[:, 0] + b_lag * depth
        for k in range(2, horizon):
            e[:, k] = lam * e[:, k - 1]
        units = np.exp(e) - 1
        rev_week0 = np.exp(e[:, 0]) * (1 - disc) - 1
        after = units[:, 1:].sum(axis=1)
        rows[f"{disc:.0%} off"] = {
            "units, promo week %": _q(units[:, 0] * 100)["estimate"],
            "revenue, promo week %": _q(rev_week0 * 100)["estimate"],
            "following weeks %": _q(after * 100)["estimate"],
            "total units %": _q((units[:, 0] + after) * 100)["estimate"],
            "total revenue %": _q((rev_week0 + after) * 100)["estimate"],
            "total revenue p5": _q((rev_week0 + after) * 100)["p5"],
            "total revenue p95": _q((rev_week0 + after) * 100)["p95"],
            "units uplift needed to break even %": (1 / (1 - disc) - 1) * 100,
        }
    return pd.DataFrame(rows).T


def price_elasticity(m: FinalModel) -> pd.DataFrame:
    b, lam = m.coef("regular_price"), m.coef("lagged_sales")
    total = b / (1 - lam)
    rows = {
        "elasticity in the week of the change": _q(b),
        "total elasticity (incl. repeat purchase)": _q(total),
        "units after a 5% shelf-price increase %": _q((1.05 ** total - 1) * 100),
        "revenue after a 5% shelf-price increase %": _q((1.05 ** (1 + total) - 1) * 100),
    }
    return pd.DataFrame(rows).T


def response_curves(m: FinalModel, points: int = 60) -> pd.DataFrame:
    """Weekly revenue as a function of a constant weekly spend on one channel (others unchanged).

    Steady state: the spend level is held long enough for adstock and repeat purchase to settle,
    so adstock = spend and the long-run multiplier 1/(1 - lagged sales) applies. Revenue is indexed
    to the 2024 average week at the channel's average spend; `incremental` is against the reference
    level (TV: zero; others: lowest weekly spend observed). For TV, which is flighted, read the curve
    as the weekly effect of sustained on-air weight."""
    d = m.data
    last = d[d["week_beg"].dt.year == d["week_beg"].dt.year.max()]
    rev_bar = float(last["revenue"].mean())
    ref = reference_levels(d, "floor")
    lam = m.coef("lagged_sales")
    out = []
    for ch in CHANNELS:
        beta = m.coef(ch)
        scale = m.config.scale[ch]
        mean, lo, hi = float(d[ch].mean()), float(d.loc[d[ch] > 0, ch].min()), float(d[ch].max())
        grid = np.unique(np.r_[np.linspace(0, 1.3 * hi, points), lo, hi, mean, ref[ch]])
        f = lambda x: saturate(np.atleast_1d(x), m.config.shape, scale)                 # noqa: E731
        effect = (beta / (1 - lam))[:, None] * (f(grid) - f(mean))[None, :]
        rev = rev_bar * np.exp(effect)
        rev_ref = rev_bar * np.exp((beta / (1 - lam)) * (f(ref[ch]) - f(mean))[0])
        inc = rev - rev_ref[:, None]
        q = quantiles(inc)
        out.append(pd.DataFrame({
            "channel": ch, "weekly_spend": grid, "incremental_revenue": q["estimate"],
            "p5": q["p5"], "p95": q["p95"],
            "in_observed_range": (grid >= (0 if ch == "tv" else lo)) & (grid <= hi),
            "observed_min": lo, "observed_max": hi, "mean_spend": mean, "reference": ref[ch],
        }))
    return pd.concat(out, ignore_index=True)
