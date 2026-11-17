"""Candidate models. A `Config` describes a specification in plain fields; `make_spec`
turns it into the `ModelSpec` the harness evaluates."""

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

from .data import CHANNELS
from .features import adstock, fourier, promo_depth, regular_price, saturate, trend_years
from .spec import ModelSpec


@dataclass(frozen=True)
class Config:
    name: str
    description: str = ""
    # --- controls
    price: str = "avg+flag"            # "avg+flag" | "reg+depth" | "reg+depth+flag" | "depth"
    post_promo: bool = False           # last week's promo depth (demand pulled forward by a promotion)
    trend: str | None = None           # None | "linear" | "kink" (slope change after year 1)
    fourier: int = 0                   # annual sine/cosine pairs
    dummies: tuple[str, ...] = ()      # "january", "christmas", "newyear"
    lag_y: bool = True                 # lagged sales (Koyck carry-over, same for every driver)
    # --- media
    media: str = "log1p"               # "log1p" (part 1) | "response" (adstock + saturation)
    decay: dict = field(default_factory=dict)       # channel -> weekly carry-over rate (0 = none)
    shape: str = "log"                 # saturation curve: "log" | "hill" | "negexp" | "power"
    scale: dict = field(default_factory=dict)       # channel -> £/week at which the curve bends
    tv_two_part: bool = False          # TV as on-air flag + log(spend) when on air (no adstock)
    # synergies beyond the multiplicative structure: "tv:influencer", "tv:social",
    # "influencer:social", "pos:promo" (social = Instagram + TikTok)
    interactions: tuple[str, ...] = ()
    centre: dict = field(default_factory=dict)      # channel -> £/week at which interaction factors are centred
    n_extra_params: int = 0            # decay/saturation parameters chosen by grid search
    y_transform: str = "log"

    def with_(self, **kw) -> "Config":
        return replace(self, **kw)


def build_controls(cfg: Config, data: pd.DataFrame) -> pd.DataFrame:
    X = pd.DataFrame({"Intercept": 1.0}, index=data.index)
    if cfg.price == "avg+flag":
        X["avg_price"] = np.log(data["avg_price"])
        X["price_promo"] = data["price_promo"].astype(float)
    else:
        if "reg" in cfg.price:
            X["regular_price"] = np.log(regular_price(data))
        X["promo_depth"] = promo_depth(data)
        if "flag" in cfg.price:
            X["price_promo"] = data["price_promo"].astype(float)
    if cfg.post_promo:
        X["promo_depth_lag1"] = promo_depth(data).shift(1).fillna(0.0)
    if cfg.trend:
        X["trend"] = trend_years(data)
        if cfg.trend == "kink":
            X["trend_after_year1"] = (trend_years(data) - 1.0).clip(lower=0.0)
    if cfg.fourier:
        X = X.join(fourier(data, cfg.fourier))
    week = data["week_beg"].dt.isocalendar().week.astype(int)
    if "january" in cfg.dummies:
        X["january"] = (data["week_beg"].dt.month == 1).astype(float)
    if "christmas" in cfg.dummies:
        X["christmas"] = (week >= 51).astype(float)
    if "newyear" in cfg.dummies:
        X["newyear"] = (week <= 2).astype(float)
    return X


def media_response(cfg: Config, data: pd.DataFrame, channel: str) -> np.ndarray:
    """Transformed media variable for one channel (adstock, then saturation)."""
    a = adstock(data[channel], cfg.decay.get(channel, 0.0))
    return saturate(a, cfg.shape, cfg.scale[channel])


def interaction_columns(cfg: Config, data: pd.DataFrame, media: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Interaction regressors from the transformed media variables.

    Each media factor is centred at its value for the channel's average spend, so a main
    effect keeps its meaning ("effect when the partner channel is at its average level") and
    the interaction coefficient reads as: does the effect of A get larger when B is above average?
    Promo depth is not centred (0 = no promotion).
    """
    c = {ch: float(saturate(np.array([cfg.centre[ch]]), cfg.shape, cfg.scale[ch])[0]) for ch in media}
    m = {ch: media[ch] - c[ch] for ch in media}
    social = m.get("instagram", 0) + m.get("tiktok", 0)
    out = {}
    for name in cfg.interactions:
        if name == "tv:influencer":
            out["ix_tv_influencer"] = m["tv"] * m["influencer"]
        elif name == "tv:social":
            out["ix_tv_social"] = m["tv"] * social
        elif name == "influencer:social":
            out["ix_influencer_social"] = m["influencer"] * social
        elif name == "pos:promo":
            out["ix_pos_promo"] = m["pos_promotion"] * promo_depth(data).to_numpy()
        else:
            raise ValueError(name)
    return out


def build(cfg: Config, data: pd.DataFrame) -> pd.DataFrame:
    X = build_controls(cfg, data)
    for ch in CHANNELS:
        if cfg.media == "log1p":
            X[ch] = np.log1p(data[ch])
        elif ch == "tv" and cfg.tv_two_part:
            on = data[ch] > 0
            X["tv_on_air"] = on.astype(float)
            X["tv_log_spend_on_air"] = np.where(on, np.log(data[ch].where(on, 1.0) / cfg.scale[ch]), 0.0)
        else:
            X[ch] = media_response(cfg, data, ch)
    if cfg.interactions:
        for name, col in interaction_columns(cfg, data, {ch: X[ch].to_numpy() for ch in CHANNELS if ch in X}).items():
            X[name] = col
    return X


def make_spec(cfg: Config) -> ModelSpec:
    return ModelSpec(
        name=cfg.name,
        build=lambda data: build(cfg, data),
        lag_y=cfg.lag_y,
        y_transform=cfg.y_transform,
        n_extra_params=cfg.n_extra_params,
        description=cfg.description,
        config=cfg,
    )


# ------------------------------------------------------------------ step 2: controls

M1 = Config("M1_trend", "M0 + linear trend", trend="linear")
M2 = M1.with_(name="M2_season", description="M1 + annual seasonality (2 sine/cosine pairs)", fourier=2)
M3 = M2.with_(name="M3_price", description="M2 with regular price + promo depth instead of average price + promo flag",
              price="reg+depth")
M4 = M3.with_(name="M4_postpromo", description="M3 + last week's promo depth (post-promotion dip)", post_promo=True)
M5 = M4.with_(name="M5_january", description="M4 + January dummy = step-2 controls", dummies=("january",))

STEP2_LADDER = [M1, M2, M3, M4, M5]

# Alternatives tried around M5 and not kept (table: results/part2/step2_controls.md).
STEP2_VARIANTS = [
    M5.with_(name="M5 (kept)"),
    M5.with_(name="no seasonality curve", fourier=0),
    M5.with_(name="1 sine/cosine pair", fourier=1),
    M5.with_(name="3 sine/cosine pairs", fourier=3),
    M5.with_(name="no January dummy (= M4)", dummies=()),
    M5.with_(name="Christmas + New-Year weeks instead of January", dummies=("christmas", "newyear")),
    M5.with_(name="January + Christmas weeks", dummies=("january", "christmas")),
    M5.with_(name="trend with slope change after year 1", trend="kink"),
    M5.with_(name="no trend", trend=None),
    M5.with_(name="average price + promo flag (part 1 price spec)", price="avg+flag"),
    M5.with_(name="regular price + promo depth + promo flag", price="reg+depth+flag"),
    M5.with_(name="promo depth only (no regular price)", price="depth"),
    M5.with_(name="no post-promo term (= M3 + January)", post_promo=False),
    M5.with_(name="no lagged sales", lag_y=False),
]
