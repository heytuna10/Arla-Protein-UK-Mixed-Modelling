import numpy as np
import pytest

from arla_mmm.candidates import M5, make_spec
from arla_mmm.contributions import decompose, marginal_roi
from arla_mmm.data import CHANNELS, load_data
from arla_mmm.engine import fit
from arla_mmm.features import adstock, promo_depth, regular_price, saturate
from arla_mmm.tune import Search, base_scales, tune


@pytest.fixture(scope="module")
def data():
    return load_data()


def test_adstock_is_normalised_and_decays():
    assert np.allclose(adstock(np.full(30, 100.0), 0.6), 100.0)          # constant spend -> same level
    pulse = adstock(np.r_[0.0, 100.0, np.zeros(5)], 0.5)
    assert np.allclose(pulse[1:4], [50.0, 25.0, 12.5])
    x = np.array([3.0, 0.0, 7.0])
    assert np.array_equal(adstock(x, 0.0), x)


@pytest.mark.parametrize("shape", ["log", "hill", "negexp", "power"])
def test_saturation_is_zero_at_zero_and_increasing(shape):
    y = saturate(np.array([0.0, 1e4, 2e4, 3e4]), shape, 2e4)
    assert y[0] == 0.0
    assert np.all(np.diff(y) > 0)
    assert np.all(np.diff(y, 2) < 0)                                      # diminishing returns


def test_price_split(data):
    reg, depth = regular_price(data), promo_depth(data)
    promo = data["price_promo"] == 1
    assert (depth[~promo] == 0).all() and (depth[promo] > 0.1).all()
    assert reg.between(1.3, 1.65).all()
    assert abs(np.corrcoef(np.log(reg), depth)[0, 1]) < 0.2               # the point of the split


@pytest.fixture(scope="module")
def tuned(data):
    bs = base_scales(data)
    cfg = M5.with_(name="t", media="response", shape="hill", scale=bs, lag_y=True)
    search = Search(decay_groups=(("tv", "influencer"), ("instagram",), ("tiktok", "pos_promotion")), base_scale=bs)
    return tune(cfg, search, data)


def test_tuning_finds_the_documented_decays(tuned):
    cfg, record = tuned
    assert cfg.decay == {"tv": 0.4, "influencer": 0.4, "instagram": 0.3, "tiktok": 0.0, "pos_promotion": 0.0}
    assert cfg.n_extra_params == 3
    assert all(min(p.values()) == pytest.approx(0.0, abs=1e-9) for p in record["profiles"].values())


def test_response_model_contributions_add_up_and_are_positive(tuned, data):
    f = fit(make_spec(tuned[0]), data)
    dec = decompose(f, data, "floor")
    np.testing.assert_allclose(dec.sum(axis=1), data["sales_units"].to_numpy()[f.rows], rtol=1e-9)
    assert (dec[CHANNELS].sum() > 0).all()
    assert (marginal_roi(f, data) > 0).all()
