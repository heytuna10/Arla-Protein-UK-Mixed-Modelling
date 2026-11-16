import numpy as np
import pytest

from arla_mmm.contributions import roi_table
from arla_mmm.data import CHANNELS
from arla_mmm.final import final_model, shapley_paths
from arla_mmm.insights import PLAYERS, promotion_curve
from arla_mmm.scenarios import Replay


@pytest.fixture(scope="module")
def m():
    return final_model()


def test_every_draw_reproduces_observed_sales(m):
    paths = m.paths(m.data)
    np.testing.assert_allclose(paths, np.broadcast_to(m.data["sales_units"].to_numpy()[m.rows], paths.shape), rtol=1e-8)


def test_decomposition_adds_up_and_matches_harness(m):
    sh = shapley_paths(m, PLAYERS)
    total = sum(sh.values())
    np.testing.assert_allclose(total, np.broadcast_to(m.data["sales_units"].to_numpy()[m.rows], total.shape), rtol=1e-8)
    sh5 = shapley_paths(m, tuple(CHANNELS))
    d = m.data.iloc[m.rows]
    harness = roi_table(m.fit, m.data, "floor")
    for ch in CHANNELS:
        assert (sh5[ch][0] * d["avg_price"].to_numpy()).sum() == pytest.approx(harness.loc[ch, "incremental_revenue"], rel=1e-8)


def test_replay_reproduces_2024_and_plans_respect_budget_and_bounds(m):
    r = Replay(m)
    actual_rev = m.data["revenue"].to_numpy()[r.rows].sum()
    assert r.revenue(r.actual, point_only=True)[0] == pytest.approx(actual_rev, rel=1e-6)
    plan = r.optimise("t", "", pct=0.10)
    assert plan.spend.sum().sum() == pytest.approx(r.budget, rel=1e-6)
    lo, hi = r.bounds(0.10)
    assert ((plan.spend >= lo - 1e-6) & (plan.spend <= hi + 1e-6)).all().all()
    assert (plan.spend.loc[r.actual["tv"] == 0, "tv"] == 0).all()                 # flight calendar kept
    assert r.revenue(plan.spend, point_only=True)[0] > actual_rev


def test_promotions_lose_revenue_at_every_depth(m):
    curve = promotion_curve(m)
    assert (curve["total units %"] > 0).all() and (curve["total revenue %"] < 0).all()
