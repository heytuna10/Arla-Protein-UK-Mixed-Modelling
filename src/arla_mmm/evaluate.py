"""Evaluation harness: one call per candidate -> one comparison row + a detail sheet.

    from arla_mmm.evaluate import evaluate
    evaluate(spec)            # fits, validates, decomposes, updates results/part2/

Selection criteria reported for every candidate (same sample, same dependent variable):
fit (R2, AIC, BIC incl. nonlinear parameters), out-of-sample error on units
(last 26 weeks + rolling origin, multi-week forecasts that do not peek at future
sales), residual diagnostics, coefficient signs and their stability across folds,
and the contribution/ROI picture.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera

from .contributions import marginal_roi, reference_levels, roi_table
from .data import CHANNELS, RESULTS_DIR, load_data
from .engine import LAG_COL, Fit, fit, one_step, simulate
from .spec import ModelSpec

HOLDOUT_WEEKS = 26
CV_HORIZON = 13
CV_ORIGINS = (104, 117, 130, 143)     # expanding window: train on weeks < origin, forecast 13


def _mape(actual, pred) -> float:
    return float(np.mean(np.abs(pred - actual) / actual) * 100)


def _rmse(actual, pred) -> float:
    return float(np.sqrt(np.mean((pred - actual) ** 2)))


def media_columns(columns) -> list[str]:
    """Regressors that carry a media effect (name starts with a channel name)."""
    return [c for c in columns if any(c.startswith(ch) for ch in CHANNELS)]


def diagnostics(f: Fit) -> dict:
    resid, X = f.res.resid, f.X
    lb = acorr_ljungbox(resid, lags=[4, 13])
    vif_cols = [i for i, c in enumerate(X.columns) if c != "Intercept"]
    vifs = {X.columns[i]: variance_inflation_factor(X.to_numpy(), i) for i in vif_cols}
    worst = max(vifs, key=vifs.get)
    return {
        "dw": float(durbin_watson(resid)),
        "bg4_p": float(acorr_breusch_godfrey(f.res, nlags=4, result_object=False)[1]),   # valid with a lagged dependent variable
        "lb4_p": float(lb["lb_pvalue"].iloc[0]),
        "lb13_p": float(lb["lb_pvalue"].iloc[1]),
        "bp_p": float(het_breuschpagan(resid, X)[1]),
        "jb_p": float(jarque_bera(resid)[1]),
        "max_vif": float(vifs[worst]),
        "max_vif_var": worst,
    }


def residual_patterns(f: Fit, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Mean residual (in %, log points x 100) by year and by calendar month: what the model misses."""
    d = pd.DataFrame({"resid_pct": f.res.resid.to_numpy() * 100, "week": data["week_beg"].iloc[f.rows].to_numpy()})
    by_year = d.groupby(d["week"].dt.year)["resid_pct"].agg(["mean", "count"]).rename_axis("year")
    by_month = d.groupby(d["week"].dt.month)["resid_pct"].agg(["mean", "count"]).rename_axis("month")
    return by_year, by_month


def holdout(spec: ModelSpec, data: pd.DataFrame, origin: int, horizon: int) -> dict:
    """Train on weeks < origin, forecast weeks origin..origin+horizon-1."""
    if spec.refit is not None:          # re-select decay/saturation on the training weeks only
        spec = spec.refit(data, origin)
    f = fit(spec, data, end=origin)
    rows = np.arange(origin, origin + horizon)
    actual = data["sales_units"].to_numpy(dtype=float)[rows]
    dyn = simulate(spec, f.params, data, rows)          # multi-week: feeds its own forecasts back
    one = one_step(spec, f.params, data, rows)          # one week ahead: uses observed lagged sales
    return {
        "mape_dyn": _mape(actual, dyn),
        "rmse_dyn": _rmse(actual, dyn),
        "mape_1step": _mape(actual, one),
        "params": f.params,
        "config": spec.config,
    }


def naive_benchmarks(data: pd.DataFrame) -> dict:
    """Hold-out MAPE of forecasts that use no model, for context."""
    y = data["sales_units"].to_numpy(dtype=float)
    n = len(y)
    rows = np.arange(n - HOLDOUT_WEEKS, n)
    return {
        "same_week_last_year": _mape(y[rows], y[rows - 52]),
        "mean_of_previous_52_weeks": _mape(y[rows], np.full(len(rows), y[rows[0] - 52: rows[0]].mean())),
    }


def evaluate(spec: ModelSpec, data: pd.DataFrame | None = None, write: bool = True) -> dict:
    data = load_data() if data is None else data
    n = len(data)
    f = fit(spec, data)
    media = media_columns(f.X.columns)

    ho = holdout(spec, data, n - HOLDOUT_WEEKS, HOLDOUT_WEEKS)
    folds = [holdout(spec, data, o, CV_HORIZON) for o in CV_ORIGINS]
    fold_params = pd.DataFrame([fo["params"] for fo in folds], index=[f"train<{o}" for o in CV_ORIGINS])
    all_fits = pd.concat([fold_params, ho["params"].to_frame(f"train<{n - HOLDOUT_WEEKS}").T, f.params.to_frame("full").T])
    all_fits = all_fits[~all_fits.index.duplicated()]
    negative_media = [c for c in media if (all_fits[c] < 0).any()]

    roi_floor = roi_table(f, data, "floor")
    roi_zero = roi_table(f, data, "zero")
    mroi = marginal_roi(f, data)
    roi_floor["marginal_roi"] = mroi
    tuned = None
    cfg = spec.config
    if cfg is not None and getattr(cfg, "media", "") == "response":
        tuned = {
            "decay": pd.DataFrame({ch: {**{f"train<{o}": fo["config"].decay.get(ch, 0.0) for o, fo in zip(CV_ORIGINS, folds)},
                                        "full": cfg.decay.get(ch, 0.0)} for ch in CHANNELS}),
            "scale": pd.DataFrame({ch: {**{f"train<{o}": fo["config"].scale[ch] for o, fo in zip(CV_ORIGINS, folds)},
                                        "full": cfg.scale[ch]} for ch in CHANNELS}),
        }

    row = {
        "model": spec.name,
        "description": spec.description,
        "n": int(f.res.nobs),
        "k": f.n_params,
        "r2": float(f.res.rsquared),
        "adj_r2": float(f.res.rsquared_adj),
        "aic": f.aic,
        "bic": f.bic,
        "ho26_mape": ho["mape_dyn"],
        "ho26_rmse": ho["rmse_dyn"],
        "ho26_mape_1step": ho["mape_1step"],
        "cv_mape": float(np.mean([fo["mape_dyn"] for fo in folds])),
        "cv_mape_worst": float(np.max([fo["mape_dyn"] for fo in folds])),
        **diagnostics(f),
        "media_signs_ok": not negative_media,
        "negative_media": ", ".join(negative_media),
        "base_pct_floor": roi_floor.attrs["base_pct"],
        "base_pct_zero": roi_zero.attrs["base_pct"],
        "sum_check_pct": roi_floor.attrs["sum_check_pct"],
        **{f"roi_{ch}": roi_floor.loc[ch, "roi"] for ch in CHANNELS},
        **{f"roi0_{ch}": roi_zero.loc[ch, "roi"] for ch in CHANNELS},
        **{f"mroi_{ch}": mroi[ch] for ch in CHANNELS},
    }
    result = {"row": row, "fit": f, "roi_floor": roi_floor, "roi_zero": roi_zero, "fold_params": all_fits,
              "tuned": tuned, "search_record": getattr(spec, "search_record", None)}
    if write:
        _write_detail(result, data)
        _update_comparison(row, data)
    return result


def variants_table(specs: list[ModelSpec], data: pd.DataFrame) -> pd.DataFrame:
    """Key numbers for side experiments that do not get a row in the main comparison."""
    rows = []
    for spec in specs:
        r = evaluate(spec, data, write=False)["row"]
        rows.append(
            {
                "variant": spec.name, "params": r["k"], "AIC": r["aic"], "BIC": r["bic"],
                "hold-out MAPE %": r["ho26_mape"], "rolling MAPE %": r["cv_mape"], "worst fold %": r["cv_mape_worst"],
                "Breusch-Godfrey p": r["bg4_p"], "max VIF": r["max_vif"], "media ≥ 0": r["media_signs_ok"],
            }
        )
    return pd.DataFrame(rows).set_index("variant")


# ---------------------------------------------------------------- reporting

def _fmt(v, nd=2) -> str:
    if isinstance(v, (bool, np.bool_)):
        return "yes" if v else "NO"
    if isinstance(v, (int, np.integer)):
        return f"{v:,}" if abs(v) >= 10_000 else str(v)
    if isinstance(v, (float, np.floating)):
        if np.isnan(v):
            return ""
        if abs(v) >= 1e15:
            return f"{v:.1e}"
        return f"{round(float(v), nd) + 0.0:,.{nd}f}"      # + 0.0 turns -0.0 into 0.0
    return str(v)


def md_table(df: pd.DataFrame, nd: int | dict = 2, index: bool = True) -> str:
    if index:
        df = df.reset_index()
    nds = nd if isinstance(nd, dict) else {}
    default = nd if isinstance(nd, int) else 2
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    for i in range(len(df)):      # by position: iterrows() would turn integer columns into floats
        lines.append("| " + " | ".join(_fmt(df[c].iloc[i], nds.get(c, default)) for c in df.columns) + " |")
    return "\n".join(lines)


def _write_detail(result: dict, data: pd.DataFrame) -> Path:
    f, row = result["fit"], result["row"]
    coefs = pd.DataFrame(
        {
            "coef": f.res.params,
            "se_ols": f.res.bse,
            "se_hac": f.res_hac.bse,
            "p_hac": f.res_hac.pvalues,
        }
    )
    roi_cols = ["reference_spend", "incremental_spend", "pct_of_sales", "incremental_revenue", "roi", "last_in_roi"]
    roi_cols_main = roi_cols + ["marginal_roi"]
    tuned_parts = []
    if result.get("tuned"):
        tuned_parts = [
            "## Carry-over and saturation parameters (full sample and re-tuned per training window)",
            "",
            "Decay = share of the media effect that carries into the next week.",
            "",
            md_table(result["tuned"]["decay"].rename_axis("sample"), nd=1),
            "",
            "Scale of the saturation curve, £ per week.",
            "",
            md_table(result["tuned"]["scale"].rename_axis("sample"), nd=0),
            "",
        ]
    if result.get("search_record") and result["search_record"]["profiles"]:
        prof = pd.DataFrame(result["search_record"]["profiles"]).T
        prof = prof[sorted(prof.columns)]
        prof.columns = [str(c) for c in prof.columns]
        dec = prof.loc[[i for i in prof.index if i.startswith("decay")]].dropna(axis=1, how="all")
        sca = prof.loc[[i for i in prof.index if i.startswith("scale")]].dropna(axis=1, how="all")
        tuned_parts += [
            "Likelihood profiles: AIC penalty for moving one parameter away from its best value, others held "
            "(0 = best; below about 2 = the data cannot tell the values apart).",
            "",
        ]
        if len(dec):
            tuned_parts += [md_table(dec.rename_axis("decay value →"), nd=1), ""]
        if len(sca):
            tuned_parts += [md_table(sca.rename_axis("scale × mean spend →"), nd=1), ""]
    roi_nd = {"reference_spend": 0, "incremental_spend": 0, "pct_of_sales": 1, "incremental_revenue": 0}
    parts = [
        f"# {row['model']}",
        "",
        row["description"],
        "",
        f"n = {row['n']}, parameters = {row['k']}, R² = {row['r2']:.3f}, AIC = {row['aic']:.1f}, BIC = {row['bic']:.1f}",
        "",
        f"## Coefficients (HAC = Newey-West, 4 lags)",
        "",
        md_table(coefs.rename_axis("term"), nd=4),
        "",
        "## Coefficient stability (expanding training windows)",
        "",
        md_table(result["fold_params"].rename_axis("sample"), nd=3),
        "",
        *tuned_parts,
        "## Residual patterns (mean residual in %, positive = model too low)",
        "",
        md_table(residual_patterns(f, data)[0], nd=1),
        "",
        md_table(residual_patterns(f, data)[1], nd=1),
        "",
        "## Contributions and revenue ROI – reference: observed floor (TV: zero)",
        "",
        f"Base = {result['roi_floor'].attrs['base_pct']:.1f}% of sales; base + channels = "
        f"{result['roi_floor'].attrs['sum_check_pct']:.2f}% of actual sales "
        f"(largest weekly gap {result['roi_floor'].attrs['max_abs_weekly_gap']:.3f} units).",
        "",
        md_table(result["roi_floor"][roi_cols_main].rename_axis("channel"), nd=roi_nd),
        "",
        "`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only "
        "this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.",
        "",
        "## Sensitivity – reference: zero spend for every channel",
        "",
        f"Base = {result['roi_zero'].attrs['base_pct']:.1f}% of sales.",
        "",
        md_table(result["roi_zero"][roi_cols].rename_axis("channel"), nd=roi_nd),
        "",
    ]
    path = RESULTS_DIR / "candidates" / f"{row['model']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts))
    return path


def _update_comparison(row: dict, data: pd.DataFrame) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv = RESULTS_DIR / "model_comparison.csv"
    table = pd.read_csv(csv) if csv.exists() else pd.DataFrame()
    if len(table):
        table = table[table["model"] != row["model"]]
    table = pd.concat([table, pd.DataFrame([row])], ignore_index=True)
    table.to_csv(csv, index=False)
    (RESULTS_DIR / "model_comparison.md").write_text(render_comparison(table, data))


def render_comparison(table: pd.DataFrame, data: pd.DataFrame) -> str:
    t = table.set_index("model")
    ref = reference_levels(data, "floor")
    naive = naive_benchmarks(data)
    short = {"tv": "TV", "instagram": "Instagram", "tiktok": "TikTok", "influencer": "Influencer", "pos_promotion": "POS"}

    fit_tab = t[["k", "r2", "adj_r2", "aic", "bic", "ho26_mape", "ho26_mape_1step", "cv_mape", "cv_mape_worst"]].rename(
        columns={
            "k": "params", "r2": "R²", "adj_r2": "adj R²", "aic": "AIC", "bic": "BIC",
            "ho26_mape": "hold-out MAPE %", "ho26_mape_1step": "hold-out MAPE % (1 week ahead)",
            "cv_mape": "rolling MAPE %", "cv_mape_worst": "worst fold %",
        }
    )
    diag_tab = t[["dw", "bg4_p", "lb13_p", "bp_p", "jb_p", "max_vif", "max_vif_var", "media_signs_ok"]].rename(
        columns={
            "dw": "Durbin-Watson", "bg4_p": "Breusch-Godfrey p (4)", "lb13_p": "Ljung-Box p (13)",
            "bp_p": "Breusch-Pagan p", "jb_p": "Jarque-Bera p", "max_vif": "max VIF", "max_vif_var": "on",
            "media_signs_ok": "media ≥ 0 in all fits",
        }
    )
    roi_tab = t[["base_pct_floor"] + [f"roi_{c}" for c in CHANNELS]].rename(
        columns={"base_pct_floor": "base % of sales", **{f"roi_{c}": short[c] for c in CHANNELS}}
    )
    roi0_tab = t[["base_pct_zero"] + [f"roi0_{c}" for c in CHANNELS]].rename(
        columns={"base_pct_zero": "base % of sales", **{f"roi0_{c}": short[c] for c in CHANNELS}}
    )
    mroi_tab = t[[f"mroi_{c}" for c in CHANNELS]].rename(columns={f"mroi_{c}": short[c] for c in CHANNELS})
    floor_txt = ", ".join(f"{short[c]} £{ref[c]:,.0f}" for c in CHANNELS)
    return "\n".join(
        [
            "# Part 2 – model comparison",
            "",
            "Generated by `arla_mmm.evaluate.evaluate` (run `python scripts/run_part2.py`); do not edit by hand. "
            "One row per candidate, details per candidate in `candidates/`.",
            "",
            f"All candidates: dependent variable log weekly units, same {int(t['n'].iloc[0])} weeks "
            "(first week dropped), so AIC/BIC are comparable. `params` counts the constant and any "
            "decay/saturation parameters chosen outside the regression; AIC/BIC are penalised for those too.",
            "",
            "## Fit and out-of-sample error",
            "",
            md_table(fit_tab, nd={"R²": 3, "adj R²": 3, "AIC": 1, "BIC": 1}),
            "",
            f"Hold-out = last {HOLDOUT_WEEKS} weeks, model trained on the weeks before. MAPE on units. "
            "The main figure is a multi-week forecast: actual spend and price are known, sales are not, "
            "so a model with lagged sales has to feed its own forecasts back in (what the dashboard will do). "
            "'1 week ahead' uses last week's actual sales and is shown only for comparison with part 1. "
            f"Rolling = mean over {len(CV_ORIGINS)} expanding-window folds of {CV_HORIZON} weeks "
            f"(training ends at week {', '.join(map(str, CV_ORIGINS))}).",
            "",
            f"Benchmarks without a model on the same hold-out: same week last year {naive['same_week_last_year']:.1f}%, "
            f"mean of the previous 52 weeks {naive['mean_of_previous_52_weeks']:.1f}%.",
            "",
            "## Residual diagnostics and signs",
            "",
            md_table(diag_tab, nd={"max VIF": 1, "Breusch-Godfrey p (4)": 3, "Ljung-Box p (13)": 3,
                                   "Breusch-Pagan p": 3, "Jarque-Bera p": 3}),
            "",
            "p-values below 0.05 flag a problem (autocorrelation, heteroskedasticity, non-normal residuals). "
            "Durbin-Watson is biased towards 2 when lagged sales is a regressor; Breusch-Godfrey is the valid test there.",
            "",
            "## Revenue ROI (£ incremental revenue per £ of spend above the reference)",
            "",
            "Contributions are Shapley values on counterfactual sales paths, so base + channels = actual sales "
            "in every week and carry-over is included (method: `src/arla_mmm/contributions.py`).",
            "",
            f"**Reference = observed floor** (TV: zero; always-on channels: lowest weekly spend observed – {floor_txt}). "
            "ROI = incremental revenue / spend above the floor.",
            "",
            md_table(roi_tab, nd={"base % of sales": 1}),
            "",
            "**Marginal ROI** (£ revenue per extra £ when the channel's spend is raised 10% in every week; TV: on-air weeks).",
            "",
            md_table(mroi_tab),
            "",
            "**Sensitivity: reference = zero spend for every channel** (extrapolates outside the data for the always-on channels).",
            "",
            md_table(roi0_tab, nd={"base % of sales": 1}),
            "",
        ]
    )
