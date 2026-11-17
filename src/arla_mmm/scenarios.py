"""Step 7: budget scenarios on a replay of the last year.

A scenario re-runs the 52 weeks of 2024 with a different media plan: same weeks, prices,
promotions and weekly shocks, only media spend changes. Spend before 2024 is as observed
(it provides the carry-in). Revenue = units x the price actually paid in each week.
Effects that would spill into 2025 are not counted, for any scenario.

A plan is described by one number per channel, theta in [-1, 1]:
    theta = 0   the 2024 plan as it was
    theta = +1  every week at its upper bound,  theta = -1  every week at its lower bound
and linear in between, so each week keeps its place in the pattern and never leaves its bounds.
TV keeps its flight calendar: only on-air weeks move, off-air weeks stay at zero.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .data import CHANNELS
from .final import FinalModel, quantiles


@dataclass
class Plan:
    name: str
    description: str
    spend: pd.DataFrame          # 52 weeks x channels
    theta: dict | None = None


class Replay:
    def __init__(self, m: FinalModel):
        self.m = m
        d = m.data
        year = d["week_beg"].dt.year
        self.rows = np.flatnonzero((year == year.max()).to_numpy())
        self.actual = d.iloc[self.rows][CHANNELS].reset_index(drop=True)
        self.price = d["avg_price"].to_numpy()[self.rows]
        self.budget = float(self.actual.sum().sum())
        on = d.loc[d["tv"] > 0, "tv"]
        self.hist_lo = {ch: float(d[ch].min()) for ch in CHANNELS} | {"tv": float(on.min())}
        self.hist_hi = {ch: float(d[ch].max()) for ch in CHANNELS}

    # ---- bounds and plans
    def bounds(self, pct: float | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Weekly lower/upper bounds. pct=None: the observed weekly range of each channel.
        pct=0.2: additionally no week moves more than 20% from its 2024 value."""
        a = self.actual
        lo = pd.DataFrame({ch: np.minimum(a[ch], self.hist_lo[ch]) for ch in CHANNELS})
        hi = pd.DataFrame({ch: np.maximum(a[ch], self.hist_hi[ch]) for ch in CHANNELS})
        if pct is not None:
            lo = np.maximum(lo, a * (1 - pct))
            hi = np.minimum(hi, a * (1 + pct))
        off_air = a["tv"] == 0
        lo.loc[off_air, "tv"] = 0.0
        hi.loc[off_air, "tv"] = 0.0
        return lo, hi

    def spend(self, theta, lo: pd.DataFrame, hi: pd.DataFrame) -> pd.DataFrame:
        a = self.actual
        out = {}
        for ch, t in zip(CHANNELS, theta):
            out[ch] = a[ch] + t * (hi[ch] - a[ch]) if t >= 0 else a[ch] + t * (a[ch] - lo[ch])
        return pd.DataFrame(out)

    # ---- evaluation
    def _data(self, spend: pd.DataFrame) -> pd.DataFrame:
        cf = self.m.data.copy()
        cf.loc[cf.index[self.rows], CHANNELS] = spend.to_numpy()
        return cf

    def revenue(self, spend: pd.DataFrame, point_only: bool = False) -> np.ndarray:
        """Annual revenue per coefficient draw (first element = point estimate)."""
        return (self.m.paths(self._data(spend), self.rows, point_only=point_only) * self.price).sum(axis=1)

    def units(self, spend: pd.DataFrame) -> np.ndarray:
        return self.m.paths(self._data(spend), self.rows).sum(axis=1)

    # ---- optimisation
    def optimise(self, name: str, description: str, pct: float | None = None, budget: float | None = None) -> Plan:
        """Allocation with the highest expected revenue for the given total budget and bounds."""
        lo, hi = self.bounds(pct)
        budget = self.budget if budget is None else budget
        obj = lambda th: -self.revenue(self.spend(th, lo, hi), point_only=True)[0] / 1e6            # noqa: E731
        con = {"type": "eq", "fun": lambda th: (self.spend(th, lo, hi).sum().sum() - budget) / 1e6}
        best = None
        rng = np.random.default_rng(0)
        starts = [np.zeros(5)] + [rng.uniform(-0.8, 0.8, 5) for _ in range(7)]
        for x0 in starts:
            res = minimize(obj, x0, method="SLSQP", bounds=[(-1, 1)] * 5, constraints=[con],
                           options={"maxiter": 200, "ftol": 1e-9})
            if res.success and abs(con["fun"](res.x)) < 1e-4 and (best is None or res.fun < best.fun):
                best = res
        if best is None:
            raise RuntimeError(f"{name}: no feasible allocation found")
        theta = np.where(np.abs(best.x) > 0.999, np.sign(best.x), best.x)
        return Plan(name, description, self.spend(theta, lo, hi), dict(zip(CHANNELS, theta)))

    def shift(self, name: str, description: str, source: str, target: str, share: float) -> Plan:
        """Move `share` of the source channel's annual spend to the target, both pro rata over their weeks."""
        s = self.actual.copy()
        moved = share * s[source].sum()
        s[target] = s[target] * (1 + moved / s[target].sum())
        s[source] = s[source] * (1 - share)
        return Plan(name, description, s)

    # ---- reporting
    def compare(self, plans: list[Plan], baseline: Plan) -> pd.DataFrame:
        rev0, units0 = self.revenue(baseline.spend), self.units(baseline.spend)
        rows = {}
        for p in plans:
            rev, units = self.revenue(p.spend), self.units(p.spend)
            d_rev = quantiles((rev - rev0) / 1e6)
            d_spend = p.spend.sum().sum() - baseline.spend.sum().sum()
            total = p.spend.sum().sum()
            rows[p.name] = {
                "media spend £m": total / 1e6,
                **{f"{ch} £m": p.spend[ch].sum() / 1e6 for ch in CHANNELS},
                "revenue £m": rev[0] / 1e6,
                "Δ revenue £m": float(d_rev["estimate"]), "Δ p5": float(d_rev["p5"]), "Δ p95": float(d_rev["p95"]),
                "Δ revenue %": (rev[0] / rev0[0] - 1) * 100,
                "Δ units %": (units[0] / units0[0] - 1) * 100,
                "revenue per £ of media": rev[0] / total,
                "Δ revenue per Δ £ of budget": (rev[0] - rev0[0]) / d_spend if abs(d_spend) > 1 else np.nan,
            }
        return pd.DataFrame(rows).T

    def range_check(self, plan: Plan) -> pd.DataFrame:
        """How far a plan leaves what has been observed: weekly range, and the highest/lowest
        13-week average ever seen (a sustained level, which is what the model's long-run effect needs)."""
        d = self.m.data
        roll = d[CHANNELS].rolling(13).mean()
        rows = {}
        for ch in CHANNELS:
            x = plan.spend[ch]
            active = x[x > 0] if ch == "tv" else x
            r13 = x.rolling(13).mean()
            rows[ch] = {
                "change vs 2024 %": (x.sum() / self.actual[ch].sum() - 1) * 100,
                "weeks above observed weekly max": int((active > self.hist_hi[ch] * 1.0001).sum()),
                "weeks below observed weekly min": int((active < self.hist_lo[ch] * 0.9999).sum()),
                "plan 13-week average, max £": float(r13.max()),
                "highest 13-week average observed £": float(roll[ch].max()),
                "plan 13-week average, min £": float(r13.min()),
                "lowest 13-week average observed £": float(roll[ch].min()),
            }
        out = pd.DataFrame(rows).T
        out["beyond sustained range"] = np.where(
            (out["plan 13-week average, max £"] > 1.02 * out["highest 13-week average observed £"])
            | (out["plan 13-week average, min £"] < 0.98 * out["lowest 13-week average observed £"]), "yes", "no")
        return out


def standard_scenarios(m: FinalModel) -> tuple[Replay, dict[str, Plan]]:
    r = Replay(m)
    plans = {
        "A": Plan("A · 2024 plan as run", "the reference", r.actual.copy(), dict.fromkeys(CHANNELS, 0.0)),
        "B10": r.optimise("B1 · optimised, each week within ±10%", "same budget; no week moves more than 10%", pct=0.10),
        "B20": r.optimise("B2 · optimised, each week within ±20%", "same budget; no week moves more than 20% (brief: conservative)", pct=0.20),
        "Bmax": r.optimise("B3 · optimised, observed weekly range", "same budget; every week anywhere inside the channel's observed weekly range (brief: main)"),
        "C": r.shift("C · 10% of TV moved to influencer", "the brief's example", "tv", "influencer", 0.10),
        "D-": r.optimise("D1 · budget −10%, optimised within ±20%", "10% less media budget", pct=0.20, budget=0.9 * r.budget),
        "D+": r.optimise("D2 · budget +10%, optimised within ±20%", "10% more media budget", pct=0.20, budget=1.1 * r.budget),
    }
    return r, plans
