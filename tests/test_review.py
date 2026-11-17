import pytest

from arla_mmm import insights as ins
from arla_mmm import review as rv
from arla_mmm.final import final_model


@pytest.fixture(scope="module")
def m():
    return final_model()


def test_frequency_split_nests_the_final_model(m):
    fs = rv.frequency_split(m)
    assert fs.attrs["aic_final"] == pytest.approx(m.fit.res.aic)
    # slow + fast parts with equal coefficients reproduce the final model, so the estimates must bracket it loosely
    assert ((fs["fast part (week-to-week)"] / fs["final model"]).between(0.8, 1.2)).all()


def test_digital_aggregate_and_noise(m):
    table, corr = rv.digital_aggregate(m)
    final, agg = table.iloc[:, 0], table.iloc[:, 1]
    assert final["AIC"] == pytest.approx(m.fit.aic) and agg["parameters"] == final["parameters"] - 4
    assert corr.shape == (5, 5)
    noise = rv.forecast_noise(m, weeks=(4, 13))
    assert noise["minimum detectable change in sales %"].iloc[0] > noise["minimum detectable change in sales %"].iloc[1] > 0


def test_profit_view_and_price_steps(m):
    roi, el = ins.roi_summary(m), ins.elasticities(m)
    p = rv.profit_view(roi, el, ins.BENCHMARK["long"])
    assert p.loc["TV", "profit per extra £ at 30% margin"] < 0 < p.loc["Influencer", "same, profit at 20% margin"]
    assert p.loc["TV", "revenue per extra £ if the effect were benchmark-sized"] == p.loc["TV", "revenue per extra £"]
    steps = ins.price_steps(m)
    assert (steps["units per week"] < 0).all() and (steps["units p5"] < steps["units p95"]).all()


def test_anchored_regression_ends(m):
    import numpy as np
    from arla_mmm import anchored as an
    from arla_mmm.data import CHANNELS

    target = an.benchmark_coefficients(m)
    free = an.fit_anchored(m.spec, m.data, target, None, m.rows)
    np.testing.assert_allclose(free.params.to_numpy(), m.fit.params.to_numpy(), rtol=1e-8)        # no prior = the final model
    fixed = an.fit_anchored(m.spec, m.data, target, 0.0, m.rows)
    np.testing.assert_allclose(fixed.params[CHANNELS].to_numpy(), target[CHANNELS].to_numpy())
    tight = an.fit_anchored(m.spec, m.data, target, 1e-4, m.rows)
    np.testing.assert_allclose(tight.params.to_numpy(), fixed.params.to_numpy(), rtol=1e-3)       # sweep converges to the fixed end
    assert free.ssr < an.fit_anchored(m.spec, m.data, target, 0.25, m.rows).ssr < fixed.ssr
