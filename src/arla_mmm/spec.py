"""A candidate model = a design-matrix builder + a few flags.

Every candidate is a linear regression on transformed inputs:

    z_t = x_t' beta (+ lambda * z_{t-1}) + e_t,      z = log1p(sales) or log(sales)

`build(data)` returns the exogenous regressors x_t (including the constant) for
every row of `data`. It must only use exogenous columns (spend, price, promo
flag, dates), because the harness calls it again on counterfactual data (spend
set to a reference level) and on future plans. The lagged-sales term, if any,
is added by the harness so that counterfactuals and multi-week forecasts feed
the simulated, not the observed, sales back in.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

_TRANSFORMS = {
    "log1p": (np.log1p, np.expm1),
    "log": (np.log, np.exp),
}


@dataclass(frozen=True)
class ModelSpec:
    name: str
    build: Callable[[pd.DataFrame], pd.DataFrame]
    lag_y: bool = False              # include z_{t-1} (Koyck carry-over)
    y_transform: str = "log"         # "log" or "log1p"
    n_extra_params: int = 0          # nonlinear params chosen outside OLS (decay, saturation ...)
    description: str = ""

    def z(self, sales):
        return _TRANSFORMS[self.y_transform][0](sales)

    def z_inv(self, z):
        return _TRANSFORMS[self.y_transform][1](z)
