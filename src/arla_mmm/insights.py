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


# ------------------------------------------------------------------ step 8: magnitude check

# Sethuraman, Tellis & Briesch (2011), "How well does advertising work? Generalizations from
# meta-analysis of brand advertising elasticities", Journal of Marketing Research 48(3): mean
# advertising elasticity over 751 short-term and 402 long-term estimates.
BENCHMARK = {"short": 0.12, "long": 0.24}


def elasticities(m: FinalModel, bump: float = 0.01) -> pd.DataFrame:
    """Advertising elasticity per channel implied by the final model, next to the meta-analytic benchmark.

    long-term : % change in total units when the channel's spend is 1% higher in every week of the
                history (same shocks; adstock and repeat purchase included).
    short-term: the part of it that arrives in the week of the spend = long-term x (1 - decay) x
                (1 - lagged-sales coefficient).
    at typical spend: the formula value beta x curve elasticity / (1 - lagged sales) at the channel's
                average weekly spend (TV: average on-air week), i.e. if that level were held."""
    d = m.data.iloc[m.rows]
    total = d["sales_units"].sum()
    lam = m.coef("lagged_sales")
    rows = {}
    for ch in CHANNELS:
        up = m.data.copy()
        up[ch] = up[ch] * (1 + bump)
        long = (m.paths(up).sum(axis=1) / total - 1) / bump
        short = long * (1 - m.config.decay.get(ch, 0.0)) * (1 - lam)
        x = float(m.data.loc[m.data[ch] > 0, ch].mean())
        r = x / m.config.scale[ch]
        typical = m.coef(ch) * r / (1 + r) ** 2 / (1 - lam)          # Hill: d f / d ln x = r / (1 + r)^2
        ql, qs = _q(long), _q(short)
        rows[LABEL[ch]] = {
            "short-term": qs["estimate"], "short p5": qs["p5"], "short p95": qs["p95"],
            "long-term": ql["estimate"], "long p5": ql["p5"], "long p95": ql["p95"],
            "long-term at typical spend": _q(typical)["estimate"],
            "short-term vs benchmark ×": qs["estimate"] / BENCHMARK["short"],
            "long-term vs benchmark ×": ql["estimate"] / BENCHMARK["long"],
        }
    return pd.DataFrame(rows).T


def curve_shape(m: FinalModel) -> pd.DataFrame:
    """Where each channel's revenue curve bends upwards, and why.

    Held at a level x, a channel multiplies sales by exp(B * f(x)) with f(x) = x / (x + scale) and
    B = coefficient / (1 - lagged sales). f flattens (diminishing returns in %), but a constant % lift
    is worth more £ the larger the sales it applies to. The £ curve bends upwards wherever
    B * f'(x)^2 + f''(x) > 0, i.e. for x below scale * (B / 2 - 1); above that it flattens."""
    if m.config.shape != "hill":
        raise ValueError("curve_shape is written for the Hill curve")
    lam = float(m.coef("lagged_sales")[0])
    roll = m.data[CHANNELS].rolling(13).mean()
    rows = {}
    for ch in CHANNELS:
        B = float(m.coef(ch)[0]) / (1 - lam)
        scale = m.config.scale[ch]
        turn = max(scale * (B / 2 - 1), 0.0)
        lo, hi = float(roll[ch].min()), float(roll[ch].max())
        where = "the whole held range" if turn >= hi else ("nowhere in the held range" if turn <= lo else "the lower part of the held range")
        rows[LABEL[ch]] = {
            "long-run coefficient B": B, "max. sales multiple exp(B)": float(np.exp(B)),
            "curve bends upwards below £/week": turn,
            "lowest 13-week average observed £": lo, "highest 13-week average observed £": hi,
            "bends upwards over": where,
        }
    return pd.DataFrame.from_dict(rows, orient="index")


def price_steps(m: FinalModel, steps=(0.01, 0.05, 0.10)) -> pd.DataFrame:
    """The shelf-price effect in pence, for managers (the idea of expressing price effects per 1p / 10p / 1%
    comes from Ketan's part-1 notebook). Per week, at the 2024 average week and the current shelf price,
    once repeat purchase has settled; 5-95% range from the coefficient draws."""
    d = m.data
    last = d[d["week_beg"].dt.year == d["week_beg"].dt.year.max()]
    units, rev = float(last["sales_units"].mean()), float(last["revenue"].mean())
    p0 = float(regular_price(d).iloc[-1])
    total = m.coef("regular_price") / (1 - m.coef("lagged_sales"))
    rows = {}
    for label, ratio in [(f"+{int(round(s * 100))}p", (p0 + s) / p0) for s in steps] + [("+1%", 1.01)]:
        du, dr = _q(units * (ratio ** total - 1)), _q(rev * (ratio ** (1 + total) - 1))
        rows[label] = {"new shelf price £": p0 * ratio, "price change %": (ratio - 1) * 100,
                       "units per week": du["estimate"], "units p5": du["p5"], "units p95": du["p95"],
                       "revenue per week £": dr["estimate"], "revenue p5": dr["p5"], "revenue p95": dr["p95"]}
    out = pd.DataFrame(rows).T
    out.attrs.update(units=units, revenue=rev, price=p0)
    return out
