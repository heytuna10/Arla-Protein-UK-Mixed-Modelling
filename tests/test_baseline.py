import numpy as np
import pytest

from arla_mmm.baseline import BASELINE, QUENTIN_REFERENCE, theta_method
from arla_mmm.contributions import decompose
from arla_mmm.data import CHANNELS, load_data
from arla_mmm.engine import fit, one_step, simulate


@pytest.fixture(scope="module")
def data():
    return load_data()


@pytest.fixture(scope="module")
def f(data):
    return fit(BASELINE, data)


def test_reproduces_part1_fit(f):
    ref = QUENTIN_REFERENCE
    assert f.res.nobs == ref["nobs"]
    assert f.res.rsquared == pytest.approx(ref["rsquared"], abs=5e-4)
    assert f.res.aic == pytest.approx(ref["aic"], abs=5e-4)
    assert f.res.bic == pytest.approx(ref["bic"], abs=5e-4)


def test_reproduces_part1_roi(f, data):
    roi = theta_method(f.params, data)["roi"]
    for ch, expected in QUENTIN_REFERENCE["roi"].items():
        assert roi[ch] == pytest.approx(expected, abs=5e-3)


def test_simulation_with_shocks_reproduces_sales(f, data):
    sim = simulate(BASELINE, f.params, data, f.rows, f.res.resid.to_numpy())
    np.testing.assert_allclose(sim, data["sales_units"].to_numpy()[f.rows], rtol=1e-9)


def test_one_step_matches_fitted_values(f, data):
    np.testing.assert_allclose(one_step(BASELINE, f.params, data, f.rows), np.expm1(f.res.fittedvalues), rtol=1e-9)


@pytest.mark.parametrize("reference", ["floor", "zero"])
def test_contributions_add_up_every_week(f, data, reference):
    dec = decompose(f, data, reference)
    np.testing.assert_allclose(dec.sum(axis=1), data["sales_units"].to_numpy()[f.rows], rtol=1e-9)
    assert list(dec.columns) == ["base"] + CHANNELS
