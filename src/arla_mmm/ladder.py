"""Step 3 candidates (carry-over, saturation, TV zeros) and the side experiments around the choice."""

import numpy as np
import pandas as pd

from .candidates import M5, Config
from .data import CHANNELS
from .spec import ModelSpec
from .tune import SCALE_GRID, Search, base_scales, tune, tuned_spec

SOCIAL = ("instagram", "tiktok", "influencer")
ALWAYS_ON = ("instagram", "tiktok", "influencer", "pos_promotion")
PER_CHANNEL = tuple((ch,) for ch in CHANNELS)
CHOSEN = "M14_hill"


def step3_ladder(data: pd.DataFrame) -> list[ModelSpec]:
    bs = base_scales(data)
    R = M5.with_(media="response", shape="log", scale=bs, lag_y=False)      # M5 controls, no lagged sales
    L = R.with_(lag_y=True)
    S = lambda **kw: Search(base_scale=bs, **kw)                             # noqa: E731
    both_scales = (("tv",), ALWAYS_ON)
    defs = [
        # --- stage A: carry-over, curve fixed at log(1 + adstock / mean spend)
        (R.with_(name="M6_adstock_1decay", description="M5 controls, no lagged sales; adstock with one decay for all channels; log curve"),
         S(decay_groups=(tuple(CHANNELS),))),
        (R.with_(name="M7_adstock_3decays", description="as M6 with three decays: TV / social / POS"),
         S(decay_groups=(("tv",), SOCIAL, ("pos_promotion",)))),
        (R.with_(name="M8_adstock_5decays", description="as M6 with one decay per channel"),
         S(decay_groups=PER_CHANNEL)),
        (L.with_(name="M9_adstock_lag", description="M8 plus lagged sales (ad memory + repeat purchase)"),
         S(decay_groups=PER_CHANNEL)),
        # --- stage B: saturation curve, on M9's structure
        (L.with_(name="M10_log_scales", description="M9 with log curve, scale tuned (TV; always-on shared)"),
         S(decay_groups=PER_CHANNEL, scale_groups=both_scales)),
        (L.with_(name="M11_hill_scales", shape="hill", description="M9 with Hill curve, scale tuned (TV; always-on shared)"),
         S(decay_groups=PER_CHANNEL, scale_groups=both_scales)),
        (L.with_(name="M12_negexp_scales", shape="negexp", description="M9 with negative-exponential curve, scale tuned (TV; always-on shared)"),
         S(decay_groups=PER_CHANNEL, scale_groups=both_scales)),
        (L.with_(name="M13_tv_two_part", tv_two_part=True, description="M9 with TV as on-air flag + log(spend) on air, no TV adstock"),
         S(decay_groups=tuple((ch,) for ch in CHANNELS if ch != "tv"))),
        (L.with_(name=CHOSEN, shape="hill", description="Hill curve; TV scale tuned, always-on scale fixed at mean spend; "
                                                        "decay per channel; lagged sales = step-3 model"),
         S(decay_groups=PER_CHANNEL, scale_groups=(("tv",),))),
    ]
    return [tuned_spec(cfg, search, data) for cfg, search in defs]


def step3_variants(data: pd.DataFrame) -> list[ModelSpec]:
    """One change at a time around the chosen model (not rows of the main comparison)."""
    bs = base_scales(data)
    H = M5.with_(media="response", shape="hill", scale=bs, lag_y=True)
    tv_only = dict(decay_groups=PER_CHANNEL, scale_groups=(("tv",),))
    S = lambda **kw: Search(base_scale=bs, **kw)                             # noqa: E731
    wide = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 64.0)
    defs = [
        (H.with_(name="M14 (kept)"), S(**tv_only)),
        (H.with_(name="negative-exponential curve instead of Hill", shape="negexp"), S(**tv_only)),
        (H.with_(name="log curve instead of Hill", shape="log"), S(**tv_only)),
        (H.with_(name="square-root curve, no scale", shape="power"), S(decay_groups=PER_CHANNEL)),
        (H.with_(name="TV scale grid widened to 64 × mean"), S(decay_groups=PER_CHANNEL, scale_groups=(("tv",),), scale_grid=wide)),
        (H.with_(name="a separate scale for every channel"), S(decay_groups=PER_CHANNEL, scale_groups=PER_CHANNEL)),
        (H.with_(name="decay grid in steps of 0.05"),
         S(decay_groups=PER_CHANNEL, scale_groups=(("tv",),), decay_grid=tuple(round(0.05 * i, 2) for i in range(19)))),
        (H.with_(name="no adstock (lagged sales only)"), S(scale_groups=(("tv",),))),
        (H.with_(name="no lagged sales (adstock only)", lag_y=False), S(**tv_only)),
        (H.with_(name="no post-promo term", post_promo=False), S(**tv_only)),
        (H.with_(name="no January dummy", dummies=()), S(**tv_only)),
        (H.with_(name="no seasonality curve", fourier=0), S(**tv_only)),
        (H.with_(name="1 sine/cosine pair", fourier=1), S(**tv_only)),
        (H.with_(name="average price + promo flag", price="avg+flag"), S(**tv_only)),
    ]
    return [tuned_spec(cfg, search, data) for cfg, search in defs]


def carryover_table(cfg: Config, lagged_sales_coef: float, horizon: int = 26) -> pd.DataFrame:
    """How a channel's effect on log sales is spread over time, combining its own adstock decay
    with the lagged-sales term (response to one week of extra spend)."""
    rows = {}
    for ch in CHANNELS:
        d = cfg.decay.get(ch, 0.0)
        ad = (1 - d) * d ** np.arange(horizon)                       # adstock weights
        path = np.zeros(horizon)
        for t in range(horizon):
            path[t] = ad[t] + (lagged_sales_coef * path[t - 1] if t else 0.0)
        share = np.cumsum(path) / path.sum()
        rows[ch] = {
            "adstock decay": d,
            "% of effect in week of spend": path[0] / path.sum() * 100,
            "% within 4 weeks": share[3] * 100,
            "weeks to 90% of effect": int(np.argmax(share >= 0.9) + 1),
            "total / first-week effect": path.sum() / path[0],
        }
    return pd.DataFrame(rows).T
