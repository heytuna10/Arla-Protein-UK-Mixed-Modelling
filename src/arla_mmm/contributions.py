"""Contribution decomposition that adds up for any candidate.

Definition
----------
For a set of channels S, v(S) is the sales path the model gives when the channels
in S keep their actual spend and all other channels are set to their reference
level, with the estimated weekly shocks (residuals) kept. Then

    base          = v(no channel)             (all channels at reference)
    actual sales  = v(all channels)           (exact, because shocks are kept)
    contribution  = Shapley value of each channel: its average incremental sales
                    over all orders in which the channels can be "switched on".

So base + sum of channel contributions = actual sales in every single week. The
Shapley average is needed because the model is multiplicative: what one channel
adds depends on which others are already on. With a lagged-sales term the paths
are simulated recursively, so contributions include carry-over.

Reference levels
----------------
TV: zero (flighted, zero is observed in 115 weeks).
Always-on channels: the lowest weekly spend observed ("observed floor"). Zero spend
was never observed for them, so a zero reference asks the model about a world it
has no data on and the answer is driven by the functional form alone. With the
floor reference a channel's contribution is the sales above what the floor spend
would have delivered, and ROI = incremental revenue / spend above the floor.
`reference="zero"` is available as a sensitivity.
"""

from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd

from .data import CHANNELS
from .engine import Fit, simulate


def reference_levels(data: pd.DataFrame, reference: str = "floor") -> dict[str, float]:
    if reference == "zero":
        return {ch: 0.0 for ch in CHANNELS}
    if reference == "floor":
        return {ch: 0.0 if (data[ch] == 0).any() else float(data[ch].min()) for ch in CHANNELS}
    raise ValueError(reference)


def decompose(f: Fit, data: pd.DataFrame, reference: str | dict[str, float] = "floor") -> pd.DataFrame:
    """Weekly decomposition (units): columns base + one per channel; rows = estimation weeks."""
    ref = reference if isinstance(reference, dict) else reference_levels(data, reference)
    shocks = f.res.resid.to_numpy()
    n = len(CHANNELS)

    value: dict[frozenset, np.ndarray] = {}
    for k in range(n + 1):
        for S in combinations(CHANNELS, k):
            cf = data.copy()
            for ch in CHANNELS:
                if ch not in S:
                    cf[ch] = ref[ch]
            value[frozenset(S)] = simulate(f.spec, f.params, cf, f.rows, shocks)

    out = pd.DataFrame({"base": value[frozenset()]}, index=data.index[f.rows])
    for ch in CHANNELS:
        others = [c for c in CHANNELS if c != ch]
        phi = np.zeros(len(f.rows))
        for k in range(n):
            w = factorial(k) * factorial(n - k - 1) / factorial(n)
            for S in combinations(others, k):
                phi += w * (value[frozenset(S) | {ch}] - value[frozenset(S)])
        out[ch] = phi
    return out


def roi_table(f: Fit, data: pd.DataFrame, reference: str | dict[str, float] = "floor") -> pd.DataFrame:
    """Per channel: contribution, share of sales, incremental revenue, spend above reference, ROI.

    Revenue uses each week's actual average price. `roi` = incremental revenue / spend
    above the reference level; `last_in_roi` uses the sales lost when only that channel
    is cut to its reference (all others as observed) instead of the Shapley share.
    """
    ref = reference if isinstance(reference, dict) else reference_levels(data, reference)
    dec = decompose(f, data, ref)
    d = data.iloc[f.rows]
    price = d["avg_price"].to_numpy()
    sales = d["sales_units"].to_numpy()
    shocks = f.res.resid.to_numpy()

    rows = {}
    for ch in CHANNELS:
        spend = d[ch].to_numpy()
        inc_spend = (spend - ref[ch]).sum()
        cf = data.copy()
        cf[ch] = ref[ch]
        last_in = sales - simulate(f.spec, f.params, cf, f.rows, shocks)
        rows[ch] = {
            "reference_spend": ref[ch],
            "spend": spend.sum(),
            "incremental_spend": inc_spend,
            "contribution_units": dec[ch].sum(),
            "pct_of_sales": dec[ch].sum() / sales.sum() * 100,
            "incremental_revenue": (dec[ch].to_numpy() * price).sum(),
            "roi": (dec[ch].to_numpy() * price).sum() / inc_spend,
            "last_in_roi": (last_in * price).sum() / inc_spend,
        }
    out = pd.DataFrame(rows).T
    out.attrs["base_pct"] = dec["base"].sum() / sales.sum() * 100
    out.attrs["sum_check_pct"] = dec.sum(axis=1).sum() / sales.sum() * 100
    out.attrs["max_abs_weekly_gap"] = float(np.abs(dec.sum(axis=1).to_numpy() - sales).max())
    return out
