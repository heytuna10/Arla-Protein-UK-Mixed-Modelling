"""Step 5: how much do the conclusions move when the modelling choices move?"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .candidates import Config, make_spec
from .contributions import marginal_roi, roi_table
from .data import CHANNELS
from .engine import HAC_MAXLAGS, fit
from .evaluate import evaluate
from .features import saturate
from .ladder import PER_CHANNEL
from .tune import Search, tune, tuned_spec

SHORT = {"tv": "TV", "instagram": "Instagram", "tiktok": "TikTok", "influencer": "Influencer", "pos_promotion": "POS"}


def _row(label: str, spec, data, aic_note: str = "") -> dict:
    r = evaluate(spec, data, write=False)["row"]
    return {
        "variant": label, "AIC": r["aic"], "hold-out MAPE %": r["ho26_mape"],
        **{f"ROI {SHORT[c]}": r[f"roi_{c}"] for c in CHANNELS},
        **{f"mROI {SHORT[c]}": r[f"mroi_{c}"] for c in CHANNELS},
    }


def sensitivity(final: Config, search: Search, data: pd.DataFrame) -> pd.DataFrame:
    """ROI and marginal ROI when one transform choice is changed and the regression re-estimated.

    Decay/scale are held at the stated alternative values (not re-tuned), except where noted."""
    shift = lambda d: {ch: float(np.clip(round(v + d, 1), 0.0, 0.9)) for ch, v in final.decay.items()}      # noqa: E731
    ao = lambda m: {ch: (v if ch == "tv" else v * m) for ch, v in final.scale.items()}                      # noqa: E731
    tv = lambda m: {**final.scale, "tv": final.scale["tv"] * m}                                             # noqa: E731
    fixed = [
        ("final model (M14)", final),
        ("negative-exponential curve", final.with_(shape="negexp")),
        ("log curve", final.with_(shape="log")),
        ("all decays − 0.1", final.with_(decay=shift(-0.1))),
        ("all decays + 0.1", final.with_(decay=shift(+0.1))),
        ("always-on curves bend at half the mean spend", final.with_(scale=ao(0.5))),
        ("always-on curves bend at twice the mean spend", final.with_(scale=ao(2.0))),
        ("TV scale halved (more TV saturation)", final.with_(scale=tv(0.5))),
        ("TV scale doubled (less TV saturation)", final.with_(scale=tv(2.0))),
        ("average price + promo flag", final.with_(price="avg+flag")),
        ("no post-promo term", final.with_(post_promo=False)),
        ("no January dummy", final.with_(dummies=())),
    ]
    rows = [_row(label, make_spec(cfg.with_(name=label)), data) for label, cfg in fixed]
    no_lag = final.with_(name="no lagged sales (decays re-tuned)", lag_y=False)
    rows.append(_row(no_lag.name, tuned_spec(no_lag, search, data), data))
    return pd.DataFrame(rows).set_index("variant")


def additive_model(final: Config, search: Search, data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Same drivers in an additive model of units (no logs), decays re-tuned.

    AIC is put on the same scale as the log models by the change-of-variable term:
    AIC of a log model for units = its AIC + 2 * sum(log units)."""
    add = final.with_(name="additive model in units (decays re-tuned)", y_transform="level")
    spec = tuned_spec(add, search, data)
    row = _row(add.name, spec, data)
    f_log = fit(make_spec(final), data)
    jac = 2 * np.log(data["sales_units"].to_numpy(dtype=float)[f_log.rows]).sum()
    info = {
        "aic_additive_units": fit(spec, data).aic,
        "aic_final_units": f_log.aic + jac,
        "decay": spec.config.decay,
        "holdout_additive": row["hold-out MAPE %"],
    }
    return pd.DataFrame([row]).set_index("variant"), info


def subperiods(final: Config, search: Search, data: pd.DataFrame) -> pd.DataFrame:
    """Re-estimate (decays re-tuned) on parts of the history: do the ROIs hold in each?"""
    n = len(data)
    windows = {"all 155 weeks": (1, n), "first 104 weeks (2022–23)": (1, 105), "last 104 weeks (2023–24)": (n - 104, n),
               "first 78 weeks": (1, 79), "last 78 weeks": (n - 78, n)}
    rows = {}
    for label, (start, end) in windows.items():
        sub = data.iloc[:end]
        if start == 1:
            cfg = tune(final, search, sub, end)[0]
        else:                                           # the tuner always starts at week 1; keep final's decays here
            cfg = final
        f = fit(make_spec(cfg), data, end=end, start=start)
        roi = roi_table(f, data, "floor")["roi"]
        mroi = marginal_roi(f, data)
        rows[label] = {
            "lagged sales": f.params["lagged_sales"],
            **{f"decay {SHORT[c]}": cfg.decay[c] for c in CHANNELS},
            **{f"ROI {SHORT[c]}": roi[c] for c in CHANNELS},
            **{f"mROI {SHORT[c]}": mroi[c] for c in CHANNELS},
        }
    return pd.DataFrame(rows).T


def lead_test(final: Config, data: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Placebo: next week's spend cannot cause this week's sales.

    If budgets were set in anticipation of demand, next week's spend would 'predict' this
    week's sales after controlling for everything in the model. Adds the lead of each channel's
    (saturated, un-adstocked) spend and tests them individually and jointly (HAC)."""
    spec = make_spec(final)
    f = fit(spec, data, end=len(data) - 1)              # last week has no lead
    X = f.X.copy()
    for ch in CHANNELS:
        lead = saturate(data[ch].shift(-1).to_numpy(), final.shape, final.scale[ch])
        X[f"lead_{ch}"] = lead[f.rows]
    res = sm.OLS(f.z, X).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_MAXLAGS})
    leads = [f"lead_{ch}" for ch in CHANNELS]
    joint = res.wald_test(np.eye(len(res.params))[[list(X.columns).index(c) for c in leads]], scalar=True, use_f=True)
    table = pd.DataFrame({"coef on next week's spend": res.params[leads], "coef on this week's (adstocked) spend": res.params[CHANNELS].to_numpy(),
                          "t (HAC)": res.tvalues[leads], "p (HAC)": res.pvalues[leads]})
    table.index = [SHORT[c] for c in CHANNELS]
    return table, float(joint.pvalue)


def influence(final: Config, data: pd.DataFrame, drop: int = 5) -> tuple[pd.DataFrame, list[str]]:
    """Re-estimate without the most influential weeks (largest Cook's distance)."""
    spec = make_spec(final)
    f = fit(spec, data)
    cooks = f.res.get_influence().cooks_distance[0]
    worst = np.argsort(cooks)[-drop:]
    keep = np.setdiff1d(np.arange(len(f.rows)), worst)
    res = sm.OLS(f.z.iloc[keep], f.X.iloc[keep]).fit()
    media = [c for c in CHANNELS] + ["lagged_sales", "regular_price", "promo_depth"]
    table = pd.DataFrame({"all weeks": f.params[media], f"without the {drop} most influential weeks": res.params[media]})
    table["change %"] = (table.iloc[:, 1] / table.iloc[:, 0] - 1) * 100
    weeks = [str(d.date()) for d in data["week_beg"].iloc[f.rows[np.sort(worst)]]]
    return table, weeks


def se_comparison(final: Config, data: pd.DataFrame) -> pd.DataFrame:
    f = fit(make_spec(final), data)
    t = pd.DataFrame({"coef": f.params, "se OLS": f.res.bse, "se HAC": f.res_hac.bse})
    t["HAC / OLS"] = t["se HAC"] / t["se OLS"]
    t["t (HAC)"] = f.res_hac.tvalues
    lo, hi = f.res_hac.conf_int()[0], f.res_hac.conf_int()[1]
    t["95% low"], t["95% high"] = lo, hi
    return t
