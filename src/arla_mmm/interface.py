"""Model interface for the scenario dashboard (part 3). Documentation: docs/part2/INTERFACE.md.

    from arla_mmm.interface import load_model, baseline_plan, scale_plan, forecast, compare_scenarios

    model = load_model()                                  # the fitted final model (models/arla_mmm_final.json)
    base = baseline_plan(model, weeks=12)                 # next 12 weeks, same weeks as a year earlier
    test = scale_plan(base, {"tv": 0.9, "instagram": 1.1, "tiktok": 1.1, "influencer": 1.1})
    fc = forecast(model, test)                            # fc.weekly, fc.contributions, fc.channels, fc.flags
    table, forecasts = compare_scenarios(model, {"Current plan": base, "Shift 10%": test}, baseline="Current plan")

A forecast continues the history: adstock carries past spend into the plan weeks and the
lagged-sales term starts from the last observed week. Uncertainty = coefficient draws (Newey-West
covariance; carry-over decays and curve scales fixed) + one normal shock per week and draw.
"""

import json
from dataclasses import asdict, dataclass, field
from itertools import combinations
from math import factorial
from pathlib import Path

import numpy as np
import pandas as pd

from .candidates import Config, make_spec
from .data import CHANNELS, REPO_ROOT, load_data
from .engine import LAG_COL, fit
from .features import promo_depth, regular_price
from .final import N_DRAWS, SEED
from .ladder import final_config
from .spec import ModelSpec
from .tune import tune

MODEL_PATH = REPO_ROOT / "models" / "arla_mmm_final.json"
SUSTAINED_WEEKS = 13                 # window of the "sustained level" range check
HISTORY_COLUMNS = ["week_beg", "sales_units", "avg_price", "price_promo"] + CHANNELS
QUANTILES = {"p5": 0.05, "p50": 0.50, "p95": 0.95}


# ------------------------------------------------------------------ the fitted model

@dataclass
class SavedModel:
    """Everything a forecast needs, without the training data or statsmodels objects."""
    config: Config
    columns: list[str]
    params: np.ndarray               # point estimates, in the order of `columns`
    cov: np.ndarray                  # Newey-West covariance of the coefficients
    sigma: float                     # residual standard deviation of weekly log sales
    ranges: dict                     # what the training data covered (used for the out-of-range flags)
    meta: dict = field(default_factory=dict)

    @property
    def spec(self) -> ModelSpec:
        if not hasattr(self, "_spec"):
            self._spec = make_spec(self.config)
        return self._spec

    def coef(self, name: str) -> float:
        return float(self.params[self.columns.index(name)])

    def draws(self, n: int = N_DRAWS) -> np.ndarray:
        """Coefficient draws (n x k); row 0 is the point estimate. Same seed and method as the
        step-6 tables, so the first n rows are identical to the draws used there."""
        if not hasattr(self, "_draws"):
            rng = np.random.default_rng(SEED)
            d = rng.multivariate_normal(self.params, self.cov, size=N_DRAWS)
            d[0] = self.params
            self._draws = d
        if not 1 <= n <= N_DRAWS:
            raise ValueError(f"n_draws must be between 1 and {N_DRAWS}")
        return self._draws[:n]


def _ranges(data: pd.DataFrame) -> dict:
    roll = data[CHANNELS].rolling(SUSTAINED_WEEKS).mean()
    shelf, depth = regular_price(data), promo_depth(data)
    out = {}
    for ch in CHANNELS:
        x = data[ch]
        out[ch] = {
            "weekly_min": float(x.min()), "weekly_max": float(x.max()), "mean": float(x.mean()),
            "sustained_min": float(roll[ch].min()), "sustained_max": float(roll[ch].max()),
            # reference level of the contributions: zero if the channel was ever off, else its lowest week
            "floor": 0.0 if (x == 0).any() else float(x.min()),
        }
    disc = 1 - np.exp(-depth[depth > 0])
    out["regular_price"] = {"min": float(shelf.min()), "max": float(shelf.max()), "last": float(shelf.iloc[-1])}
    out["promo_discount"] = {"max": float(disc.max()), "mean": float(disc.mean())}
    return out


def fit_model(data: pd.DataFrame | None = None) -> SavedModel:
    """Tune the carry-over decays and the TV scale, fit the final specification (M14) and keep what a
    forecast needs. With the default data this is the model behind every table in results/part2/."""
    data = load_data() if data is None else data.reset_index(drop=True)
    cfg, search = final_config(data)
    cfg = tune(cfg, search, data)[0]
    f = fit(make_spec(cfg), data)
    return SavedModel(
        config=cfg, columns=list(f.X.columns), params=f.params.to_numpy(),
        cov=f.res_hac.cov_params().to_numpy(), sigma=float(np.sqrt(f.res.mse_resid)), ranges=_ranges(data),
        meta={"model": cfg.name, "first_week": str(data["week_beg"].iloc[0].date()),
              "last_week": str(data["week_beg"].iloc[-1].date()), "weeks": int(len(data)),
              "weeks_in_fit": int(f.res.nobs), "r2": float(f.res.rsquared)},
    )


def save_model(model: SavedModel, path: str | Path = MODEL_PATH) -> Path:
    """Write the fitted model as JSON (readable, no pickle)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"meta": model.meta, "config": asdict(model.config), "columns": model.columns,
               "params": model.params.tolist(), "cov": model.cov.tolist(), "sigma": model.sigma,
               "ranges": model.ranges}
    path.write_text(json.dumps(payload, indent=1) + "\n")
    return path


def load_model(path: str | Path = MODEL_PATH) -> SavedModel:
    p = json.loads(Path(path).read_text())
    cfg = dict(p["config"])
    for key in ("dummies", "interactions"):
        cfg[key] = tuple(cfg[key])
    return SavedModel(config=Config(**cfg), columns=p["columns"], params=np.array(p["params"]),
                      cov=np.array(p["cov"]), sigma=p["sigma"], ranges=p["ranges"], meta=p["meta"])


# ------------------------------------------------------------------ plans

def _history(history: pd.DataFrame | None) -> pd.DataFrame:
    h = load_data() if history is None else history.copy()
    missing = [c for c in HISTORY_COLUMNS if c not in h.columns]
    if missing:
        raise ValueError(f"history is missing columns: {missing}")
    h["week_beg"] = pd.to_datetime(h["week_beg"])
    h = h.sort_values("week_beg").reset_index(drop=True)
    if len(h) < SUSTAINED_WEEKS:
        raise ValueError(f"history needs at least {SUSTAINED_WEEKS} weeks")
    if "regular_price" not in h.columns:
        h["regular_price"] = regular_price(h)
    if "promo_depth" not in h.columns:
        h["promo_depth"] = promo_depth(h)
    return h


def baseline_plan(model: SavedModel, weeks: int = 12, history: pd.DataFrame | None = None) -> pd.DataFrame:
    """A neutral starting plan for the weeks after the history: spend and promotions of the same weeks
    one year (52 weeks) earlier, shelf price as in the last observed week. Keeps the TV flight
    calendar and the seasonal pattern of the budget."""
    h = _history(history)
    src = (len(h) - 52 + np.arange(weeks) % 52)
    plan = h.iloc[src][CHANNELS].reset_index(drop=True)
    plan.insert(0, "week_beg", h["week_beg"].iloc[-1] + pd.to_timedelta(7 * (np.arange(weeks) + 1), unit="D"))
    plan["regular_price"] = float(h["regular_price"].iloc[-1])
    plan["promo_discount"] = 1 - np.exp(-h["promo_depth"].to_numpy()[src])
    return plan


def scale_plan(plan: pd.DataFrame, factors: dict[str, float]) -> pd.DataFrame:
    """Multiply the weekly spend of some channels, e.g. {"tv": 0.9, "influencer": 1.1}."""
    out = plan.copy()
    for ch, k in factors.items():
        if ch not in CHANNELS:
            raise ValueError(f"unknown channel {ch!r}; channels are {CHANNELS}")
        out[ch] = out[ch] * k
    return out


def shift_budget(plan: pd.DataFrame, source: str, target: str, share: float) -> pd.DataFrame:
    """Move `share` of the source channel's spend to the target channel (both pro rata over their
    weeks), total budget unchanged. shift_budget(plan, "tv", "influencer", 0.10) is the codebook's example."""
    out = plan.copy()
    moved = share * out[source].sum()
    out[target] = out[target] * (1 + moved / out[target].sum())
    out[source] = out[source] * (1 - share)
    return out


def _plan(model: SavedModel, h: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
    """Validate a plan and complete it to the columns the model needs."""
    p = plan.copy().reset_index(drop=True)
    missing = [c for c in CHANNELS if c not in p.columns]
    if missing:
        raise ValueError(f"plan is missing spend columns: {missing}")
    if len(p) == 0:
        raise ValueError("plan has no weeks")
    expected = h["week_beg"].iloc[-1] + pd.to_timedelta(7 * (np.arange(len(p)) + 1), unit="D")
    if "week_beg" in p.columns:
        if not (pd.to_datetime(p["week_beg"]).to_numpy() == expected.to_numpy()).all():
            raise ValueError(f"plan weeks must be consecutive Mondays starting {expected[0].date()} "
                             "(the week after the history ends)")
    p["week_beg"] = expected
    if "regular_price" not in p.columns:
        p["regular_price"] = float(h["regular_price"].iloc[-1])
    if "promo_discount" not in p.columns:
        flag = p["price_promo"].astype(float) if "price_promo" in p.columns else 0.0
        p["promo_discount"] = flag * model.ranges["promo_discount"]["mean"]
    num = p[CHANNELS + ["regular_price", "promo_discount"]].astype(float)
    if num.isna().any().any():
        raise ValueError("plan has missing values")
    if (num[CHANNELS] < 0).any().any():
        raise ValueError("spend cannot be negative")
    if (num["regular_price"] <= 0).any() or not num["promo_discount"].between(0, 0.9).all():
        raise ValueError("regular_price must be positive and promo_discount between 0 and 0.9 (0.24 = 24% off)")
    p[num.columns] = num
    p["promo_depth"] = -np.log(1 - p["promo_discount"])
    p["price_promo"] = (p["promo_discount"] > 0).astype(int)
    p["avg_price"] = p["regular_price"] * (1 - p["promo_discount"])
    p["sales_units"] = np.nan
    return p


def check_range(model: SavedModel, plan: pd.DataFrame, history: pd.DataFrame | None = None,
                tolerance: float = 0.0) -> pd.DataFrame:
    """Out-of-range flags, one row per plan week and input.

    weekly_out     the week's value is outside the range of single weeks in the training data;
    sustained_out  (channels only) the 13-week average ending in that week, taken over history + plan,
                   is outside the range of 13-week averages in the training data. This is the flag
                   that matters: the model's long-run effects were only ever observed for spend
                   levels that were held, and held levels moved far less than single weeks.
    `sustained_excess_pct` says how far outside (+ above the highest, - below the lowest held level).
    `tolerance` (e.g. 0.02) ignores excursions of up to that fraction of the limit."""
    tolerance = tolerance + 1e-9                       # values equal to an observed limit are inside
    h = _history(history)
    p = _plan(model, h, plan)
    n = len(p)
    rows = []
    for ch in CHANNELS:
        r = model.ranges[ch]
        x = p[ch].to_numpy()
        avg = pd.concat([h[ch], p[ch]], ignore_index=True).rolling(SUSTAINED_WEEKS).mean().to_numpy()[-n:]
        hi, lo = r["sustained_max"], r["sustained_min"]
        excess = np.where(avg > hi, (avg / hi - 1) * 100, np.where(avg < lo, (avg / lo - 1) * 100 if lo > 0 else 0.0, 0.0))
        rows.append(pd.DataFrame({
            "week_beg": p["week_beg"], "input": ch, "value": x,
            "weekly_min": r["weekly_min"], "weekly_max": r["weekly_max"],
            "weekly_out": (x > r["weekly_max"] * (1 + tolerance)) | (x < r["weekly_min"] * (1 - tolerance)),
            "avg_13w": avg, "sustained_min": lo, "sustained_max": hi,
            "sustained_out": (avg > hi * (1 + tolerance)) | (avg < lo * (1 - tolerance)),
            "sustained_excess_pct": excess,
        }))
    pr, dr = model.ranges["regular_price"], model.ranges["promo_discount"]
    for name, x, lo, hi in [("regular_price", p["regular_price"].to_numpy(), pr["min"], pr["max"]),
                            ("promo_discount", p["promo_discount"].to_numpy(), 0.0, dr["max"])]:
        rows.append(pd.DataFrame({
            "week_beg": p["week_beg"], "input": name, "value": x, "weekly_min": lo, "weekly_max": hi,
            "weekly_out": (x > hi * (1 + tolerance)) | (x < lo * (1 - tolerance)),
            "avg_13w": np.nan, "sustained_min": np.nan, "sustained_max": np.nan,
            "sustained_out": False, "sustained_excess_pct": 0.0,
        }))
    return pd.concat(rows, ignore_index=True)


def range_warnings(flags: pd.DataFrame) -> list[str]:
    """The flags as sentences for the dashboard, sustained-level warnings first."""
    out = []
    for ch, g in flags[flags["sustained_out"]].groupby("input", sort=False):
        worst = g.loc[g["sustained_excess_pct"].abs().idxmax()]
        side = "above the highest" if worst["sustained_excess_pct"] > 0 else "below the lowest"
        out.append(f"{ch}: the 13-week average spend is up to {abs(worst['sustained_excess_pct']):.0f}% {side} level "
                   f"ever held in the data ({len(g)} of {flags['week_beg'].nunique()} weeks). "
                   "The model has no evidence here; read the result as extrapolation.")
    for ch, g in flags[flags["weekly_out"]].groupby("input", sort=False):
        nd = 0 if ch in CHANNELS else 2
        out.append(f"{ch}: {len(g)} week(s) outside the range of single weeks in the data "
                   f"({g['weekly_min'].iloc[0]:,.{nd}f} to {g['weekly_max'].iloc[0]:,.{nd}f}).")
    return out


# ------------------------------------------------------------------ forecast

@dataclass
class Forecast:
    weekly: pd.DataFrame             # one row per plan week: inputs, units and revenue (mean, p5, p50, p95)
    contributions: pd.DataFrame      # one row per week and component (base + channels): units and revenue
    channels: pd.DataFrame           # one row per channel over the whole horizon: spend, incremental revenue, ROI
    totals: pd.Series                # whole horizon: media spend, units and revenue (mean, p5, p50, p95)
    flags: pd.DataFrame              # check_range() for this plan
    warnings: list[str]              # the flags as sentences
    plan: pd.DataFrame               # the plan as the model used it (all columns completed)
    units_draws: np.ndarray          # simulations x weeks, for anything not covered above
    revenue_draws: np.ndarray


def _summary(x: np.ndarray, prefix: str) -> dict:
    """Mean and quantiles over the simulations (axis 0)."""
    out = {f"{prefix}_mean": x.mean(axis=0)}
    for name, q in QUANTILES.items():
        out[f"{prefix}_{name}"] = np.quantile(x, q, axis=0)
    return out


def forecast(model: SavedModel, plan: pd.DataFrame, history: pd.DataFrame | None = None, *,
             n_draws: int = 1000, reference: str = "floor", parameter_uncertainty: bool = True,
             residual_uncertainty: bool = True, seed: int = SEED, tolerance: float = 0.0) -> Forecast:
    """Units and revenue for the weeks of `plan`, which follow directly after `history`.

    plan      one row per future week. Required: weekly spend in £ for tv, instagram, tiktok, influencer,
              pos_promotion. Optional: regular_price (shelf price in £; default: last observed),
              promo_discount (fraction off the shelf price, 0 = no promotion; default 0) or a 0/1
              price_promo flag (then the average historical discount is used), week_beg.
    history   the weekly data up to now in the format of data/arla_protein_mmm_weekly.csv
              (default: that file). Needed for carry-over and for last week's sales.
    reference what a channel's contribution is measured against in the plan weeks: "floor" (TV: zero;
              always-on channels: their lowest week in the training data, as in all part-2 tables) or "zero".

    Every simulation uses the same coefficient draw and the same weekly shocks for the plan and for its
    counterfactuals, and the same seed gives the same shocks for every plan of the same length, so
    differences between scenarios are not blurred by simulation noise."""
    if reference not in ("floor", "zero"):
        raise ValueError(reference)
    h = _history(history)
    p = _plan(model, h, plan)
    cols = HISTORY_COLUMNS + ["regular_price", "promo_depth"]
    frame = pd.concat([h[cols], p[cols]], ignore_index=True)
    rows = np.arange(len(h), len(frame))
    n = len(p)

    draws = model.draws(n_draws) if parameter_uncertainty else np.repeat(model.params[None, :], n_draws, axis=0)
    rng = np.random.default_rng(seed)
    shocks = rng.normal(0.0, model.sigma, size=(n_draws, n)) if residual_uncertainty else np.zeros((n_draws, n))
    exog = [c for c in model.columns if c != LAG_COL]
    ie = [model.columns.index(c) for c in exog]
    lam = draws[:, model.columns.index(LAG_COL)]
    z0 = float(np.log(h["sales_units"].iloc[-1]))

    def paths(f: pd.DataFrame) -> np.ndarray:
        lin = draws[:, ie] @ model.spec.build(f)[exog].to_numpy(dtype=float)[rows].T + shocks
        z_prev = np.full(n_draws, z0)
        out = np.empty_like(lin)
        for t in range(n):
            z_prev = lin[:, t] + lam * z_prev
            out[:, t] = z_prev
        return np.exp(out)

    # Shapley split of the plan weeks over the five channels (history stays as observed, so what
    # past spend still carries into the plan weeks is part of the base)
    ref = {ch: (model.ranges[ch]["floor"] if reference == "floor" else 0.0) for ch in CHANNELS}
    value = {}
    for k in range(len(CHANNELS) + 1):
        for S in combinations(CHANNELS, k):
            cf = frame.copy()
            for ch in CHANNELS:
                if ch not in S:
                    cf.loc[rows, ch] = ref[ch]
            value[frozenset(S)] = paths(cf)
    units = value[frozenset(CHANNELS)]
    parts = {"base": value[frozenset()]}
    m = len(CHANNELS)
    for ch in CHANNELS:
        others = [c for c in CHANNELS if c != ch]
        phi = 0.0
        for k in range(m):
            w = factorial(k) * factorial(m - k - 1) / factorial(m)
            for S in combinations(others, k):
                phi = phi + w * (value[frozenset(S) | {ch}] - value[frozenset(S)])
        parts[ch] = phi

    price = p["avg_price"].to_numpy()
    revenue = units * price
    weekly = p[["week_beg"] + CHANNELS + ["regular_price", "promo_discount", "avg_price"]].copy()
    weekly["media_spend"] = p[CHANNELS].sum(axis=1)
    weekly = weekly.assign(**_summary(units, "units"), **_summary(revenue, "revenue"))

    contributions = pd.concat([
        pd.DataFrame({"week_beg": p["week_beg"], "component": name,
                      "spend": p[name].to_numpy() if name in CHANNELS else np.nan,
                      **_summary(x, "units"), **_summary(x * price, "revenue")})
        for name, x in parts.items()], ignore_index=True)

    ch_rows = {}
    for ch in CHANNELS:
        inc_rev = (parts[ch] * price).sum(axis=1)
        spend = float(p[ch].sum())
        above = spend - ref[ch] * n
        roi = inc_rev / above if above > 1e-9 else np.full(n_draws, np.nan)
        ch_rows[ch] = {"spend": spend, "reference_spend": ref[ch] * n, "spend_above_reference": above,
                       **{k: float(v) for k, v in _summary(parts[ch].sum(axis=1), "incremental_units").items()},
                       **{k: float(v) for k, v in _summary(inc_rev, "incremental_revenue").items()},
                       **{k: float(v) for k, v in _summary(roi, "roi").items()}}
    totals = pd.Series({"weeks": n, "media_spend": float(p[CHANNELS].sum().sum()),
                        **{k: float(v) for k, v in _summary(units.sum(axis=1), "units").items()},
                        **{k: float(v) for k, v in _summary(revenue.sum(axis=1), "revenue").items()}})
    flags = check_range(model, plan, history, tolerance)
    return Forecast(weekly=weekly, contributions=contributions, channels=pd.DataFrame(ch_rows).T, totals=totals,
                    flags=flags, warnings=range_warnings(flags), plan=p, units_draws=units, revenue_draws=revenue)


def compare_scenarios(model: SavedModel, plans: dict[str, pd.DataFrame], baseline: str,
                      history: pd.DataFrame | None = None, **kwargs) -> tuple[pd.DataFrame, dict[str, Forecast]]:
    """Forecast several plans of the same length and compare them with the one named `baseline`.

    Returns (table, forecasts). The differences are computed simulation by simulation (same coefficient
    draw, same shocks), so their intervals reflect what the model is unsure about, not simulation noise.
    `roi_vs_baseline` = extra revenue per extra £ of media; empty when the budgets differ by less than 1%
    (a reallocation has no meaningful return per extra £)."""
    if baseline not in plans:
        raise ValueError(f"baseline {baseline!r} is not one of the plans")
    if len({len(p) for p in plans.values()}) != 1:
        raise ValueError("all plans must cover the same weeks")
    fcs = {name: forecast(model, p, history, **kwargs) for name, p in plans.items()}
    rev0, units0 = fcs[baseline].revenue_draws.sum(axis=1), fcs[baseline].units_draws.sum(axis=1)
    spend0 = fcs[baseline].totals["media_spend"]
    rows = {}
    for name, fc in fcs.items():
        rev, units = fc.revenue_draws.sum(axis=1), fc.units_draws.sum(axis=1)
        d_spend = fc.totals["media_spend"] - spend0
        fl = fc.flags
        rows[name] = {
            "media_spend": fc.totals["media_spend"], "delta_spend": d_spend,
            **{k: float(v) for k, v in _summary(units, "units").items()},
            **{k: float(v) for k, v in _summary(rev, "revenue").items()},
            **{k: float(v) for k, v in _summary(rev - rev0, "delta_revenue").items()},
            "delta_revenue_pct": float((rev - rev0).mean() / rev0.mean() * 100),
            "delta_units_pct": float((units - units0).mean() / units0.mean() * 100),
            "revenue_per_media_pound": float(rev.mean() / fc.totals["media_spend"]),
            "roi_vs_baseline": float((rev - rev0).mean() / d_spend) if abs(d_spend) > 0.01 * spend0 else np.nan,
            "weeks_weekly_out": int(fl.loc[fl["weekly_out"], "week_beg"].nunique()),
            "weeks_sustained_out": int(fl.loc[fl["sustained_out"], "week_beg"].nunique()),
            "inputs_out_of_range": ", ".join(fl.loc[fl["sustained_out"] | fl["weekly_out"], "input"].unique()),
        }
    return pd.DataFrame.from_dict(rows, orient="index"), fcs


def backtest(data: pd.DataFrame | None = None, horizon: int = 12, origins: tuple[int, ...] = (104, 117, 130, 143)) -> pd.DataFrame:
    """How good are the forecasts and their bands? For each origin the model is re-tuned and re-fitted
    on the weeks before it only, then forecasts the next `horizon` weeks from the inputs that actually
    followed. Returns one row per origin and forecast week."""
    data = load_data() if data is None else data.reset_index(drop=True)
    shelf, depth = regular_price(data), promo_depth(data)
    out = []
    for o in origins:
        hist = data.iloc[:o].reset_index(drop=True)
        fut = data.iloc[o:o + horizon].reset_index(drop=True)
        plan = fut[["week_beg"] + CHANNELS].copy()
        plan["regular_price"] = shelf.to_numpy()[o:o + horizon]
        plan["promo_discount"] = 1 - np.exp(-depth.to_numpy()[o:o + horizon])
        w = forecast(fit_model(hist), plan, hist).weekly
        out.append(pd.DataFrame({
            "origin": str(data["week_beg"].iloc[o].date()), "step": np.arange(1, len(fut) + 1), "week_beg": fut["week_beg"],
            "actual_units": fut["sales_units"].to_numpy(dtype=float), "units_p5": w["units_p5"], "units_p50": w["units_p50"],
            "units_p95": w["units_p95"],
        }))
    out = pd.concat(out, ignore_index=True)
    out["abs_pct_error"] = (out["units_p50"] / out["actual_units"] - 1).abs() * 100
    out["inside_band"] = (out["actual_units"] >= out["units_p5"]) & (out["actual_units"] <= out["units_p95"])
    return out
