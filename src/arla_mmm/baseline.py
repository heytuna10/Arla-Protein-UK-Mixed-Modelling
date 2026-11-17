"""Part 1 baseline (Quentin, notebooks/01_exploratory_analysis.ipynb, `model2`).

log1p(sales) ~ lag(log1p(sales)) + log1p(avg_price) + price_promo
               + log1p(tv) + log1p(instagram) + log1p(tiktok)
               + log1p(influencer) + log1p(pos_promotion)
"""

import numpy as np
import pandas as pd

from .data import CHANNELS
from .spec import ModelSpec

# Numbers printed in Quentin's notebook; tests assert we reproduce them.
QUENTIN_REFERENCE = {
    "rsquared": 0.930,
    "aic": -350.661,
    "bic": -323.271,
    "nobs": 155,
    "roi": {"tv": 0.23, "instagram": 13.24, "tiktok": 13.56, "influencer": 30.61, "pos_promotion": 3.67},
}


def build_baseline(data: pd.DataFrame) -> pd.DataFrame:
    X = pd.DataFrame({"Intercept": 1.0}, index=data.index)
    X["avg_price"] = np.log1p(data["avg_price"])
    X["price_promo"] = data["price_promo"].astype(float)
    for ch in CHANNELS:
        X[ch] = np.log1p(data[ch])
    return X


BASELINE = ModelSpec(
    name="M0_baseline",
    build=build_baseline,
    lag_y=True,
    y_transform="log1p",
    description="Part 1 baseline: log1p-log1p OLS with lagged sales, price and promo flag",
)


def theta_method(params: pd.Series, data: pd.DataFrame) -> pd.DataFrame:
    """Course ("FourTex") attribution exactly as in part 1.

    unit effect theta = beta * mean(sales) / mean(spend); contribution = theta * total spend;
    ROI = contribution * average price / total spend. Short-run only (ignores the lagged-sales
    multiplier) and linearises the log-log curve from zero spend, which is why the
    contributions do not add up to sales.
    """
    beta = params[CHANNELS]
    theta = beta * data["sales_units"].mean() / data[CHANNELS].mean()
    contribution = theta * data[CHANNELS].sum()
    price = data["revenue"].sum() / data["sales_units"].sum()
    return pd.DataFrame(
        {
            "beta": beta,
            "contribution_units": contribution,
            "pct_of_total_sales": contribution / data["sales_units"].sum() * 100,
            "roi": contribution * price / data[CHANNELS].sum(),
        }
    )
