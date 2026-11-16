"""Feature transforms shared by the candidates. All take the raw weekly frame (history,
optionally followed by a future plan) and use only exogenous columns."""

import numpy as np
import pandas as pd

ORIGIN = pd.Timestamp("2022-01-03")       # first week of the data; trend is measured from here


def trend_years(data: pd.DataFrame) -> pd.Series:
    """Years since the first week (so the coefficient is growth per year in log points)."""
    return (data["week_beg"] - ORIGIN).dt.days / 365.25


def fourier(data: pd.DataFrame, order: int) -> pd.DataFrame:
    """Annual sine/cosine pairs; `order` pairs describe a smooth seasonal curve with 2*order parameters."""
    # mid-week position in the year
    pos = 2 * np.pi * ((data["week_beg"] + pd.Timedelta(days=3)).dt.dayofyear / 365.25)
    out = {}
    for k in range(1, order + 1):
        out[f"season_sin{k}"] = np.sin(k * pos)
        out[f"season_cos{k}"] = np.cos(k * pos)
    return pd.DataFrame(out, index=data.index)


def regular_price(data: pd.DataFrame, window: int = 5) -> pd.Series:
    """Shelf (list) price per week, in £.

    Observed directly in non-promo weeks (avg_price then moves by only +-1-2p around a level
    that rises in steps). In promo weeks it is not observed, so it is filled from the
    neighbouring non-promo weeks, and a centred median over `window` weeks removes the pence noise.
    """
    shelf = data["avg_price"].where(data["price_promo"] == 0)
    shelf = shelf.interpolate(method="nearest", limit_direction="both") if shelf.notna().sum() > 1 else shelf
    shelf = shelf.ffill().bfill()
    return shelf.rolling(window, center=True, min_periods=1).median()


def promo_depth(data: pd.DataFrame) -> pd.Series:
    """Discount vs the regular price in promo weeks, as log(regular / paid); 0 in non-promo weeks.

    0.25 means the average price paid was about 22% below the shelf price.
    """
    depth = np.log(regular_price(data) / data["avg_price"])
    return depth.where(data["price_promo"] == 1, 0.0).clip(lower=0.0)


def adstock(x: pd.Series | np.ndarray, decay: float) -> np.ndarray:
    """Geometric carry-over, normalised: a_t = (1 - decay) * x_t + decay * a_{t-1}.

    Normalising keeps the adstock in the same £/week units as spend (a constant spend of X
    gives an adstock of X), so saturation scales and reference levels keep their meaning.
    Spend before the first week is unknown; the series starts as if it had equalled the
    first week's spend (a_0 = x_0). With the decays considered this matters for a few weeks only.
    """
    x = np.asarray(x, dtype=float)
    if decay == 0:
        return x.copy()
    out = np.empty_like(x)
    carry = x[0]
    for i, v in enumerate(x):
        carry = (1 - decay) * v + decay * carry
        out[i] = carry
    return out


def saturate(a: np.ndarray, shape: str, scale: float) -> np.ndarray:
    """Diminishing-returns curves, all equal to 0 at zero spend. `scale` is in £/week.

    log    : log(1 + a/scale)            keeps rising, ever more slowly
    hill   : a / (a + scale)             levels off at 1; half of the maximum at a = scale
    negexp : 1 - exp(-a/scale)           levels off at 1, faster than hill; 63% at a = scale
    power  : (a/scale) ** 0.5            square root, no ceiling
    """
    r = np.asarray(a, dtype=float) / scale
    if shape == "log":
        return np.log1p(r)
    if shape == "hill":
        return r / (1.0 + r)
    if shape == "negexp":
        return 1.0 - np.exp(-r)
    if shape == "power":
        return np.sqrt(r)
    raise ValueError(shape)
