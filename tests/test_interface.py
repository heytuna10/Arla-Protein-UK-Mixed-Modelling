import numpy as np
import pandas as pd
import pytest

from arla_mmm.data import CHANNELS, load_data
from arla_mmm.engine import simulate
from arla_mmm.features import promo_depth, regular_price
from arla_mmm.final import final_model
from arla_mmm.interface import (MODEL_PATH, baseline_plan, check_range, compare_scenarios, fit_model, forecast,
                                gain_range, load_model, profit_gain, profit_view, save_model, scale_plan, shift_budget)


@pytest.fixture(scope="module")
def model():
    return fit_model()


@pytest.fixture(scope="module")
def base(model):
    return baseline_plan(model, weeks=12)


def test_interface_model_is_the_final_model(model):
    m = final_model()
    np.testing.assert_allclose(model.params, m.fit.params.to_numpy())
    np.testing.assert_allclose(model.draws(), m.draws)


def test_committed_model_file_is_current_and_round_trips(model, base, tmp_path):
    saved = load_model(MODEL_PATH)                      # stale file = someone changed the model without re-running step 8
    np.testing.assert_allclose(saved.params, model.params, rtol=1e-8)
    np.testing.assert_allclose(saved.cov, model.cov, rtol=1e-6)
    assert saved.config == model.config
    again = load_model(save_model(model, tmp_path / "m.json"))
    np.testing.assert_allclose(forecast(again, base).units_draws, forecast(model, base).units_draws)


def test_forecast_without_uncertainty_equals_the_engine(model):
    """Last 12 weeks forecast from the weeks before them = the harness's multi-week simulation."""
    d, H = load_data(), 12
    shelf, depth = regular_price(d), promo_depth(d)
    hist = d.iloc[:-H].assign(regular_price=shelf.iloc[:-H], promo_depth=depth.iloc[:-H])
    plan = d.iloc[-H:][["week_beg"] + CHANNELS].assign(regular_price=shelf.iloc[-H:],
                                                       promo_discount=1 - np.exp(-depth.iloc[-H:]))
    fc = forecast(model, plan, hist, n_draws=1, residual_uncertainty=False)
    m = final_model()
    expected = simulate(m.spec, m.fit.params, d, np.arange(len(d) - H, len(d)))
    np.testing.assert_allclose(fc.units_draws[0], expected, rtol=1e-10)
    np.testing.assert_allclose(fc.weekly["avg_price"], d["avg_price"].iloc[-H:], rtol=0.02)


def test_outputs_are_consistent(model, base):
    fc = forecast(model, base)
    w, c = fc.weekly, fc.contributions
    assert len(w) == 12 and (w["week_beg"].iloc[0] - load_data()["week_beg"].iloc[-1]).days == 7
    assert (w["units_p5"] < w["units_p50"]).all() and (w["units_p50"] < w["units_p95"]).all()
    # base + channels add up to the total, week by week (means are additive)
    np.testing.assert_allclose(c.groupby("week_beg")["units_mean"].sum().to_numpy(), w["units_mean"].to_numpy(), rtol=1e-9)
    np.testing.assert_allclose(c.groupby("week_beg")["revenue_mean"].sum().to_numpy(), w["revenue_mean"].to_numpy(), rtol=1e-9)
    assert set(c["component"]) == {"base", *CHANNELS}
    assert (fc.channels["roi_mean"] > 0).all()
    assert fc.totals["revenue_p5"] < fc.totals["revenue_p50"] < fc.totals["revenue_p95"]
    # bands widen when residual uncertainty is added to parameter uncertainty
    narrow = forecast(model, base, residual_uncertainty=False).weekly
    assert ((w["units_p95"] - w["units_p5"]) > (narrow["units_p95"] - narrow["units_p5"])).all()


def test_flags(model, base):
    flags = check_range(model, base)
    assert len(flags) == 12 * (len(CHANNELS) + 2)
    assert not flags["sustained_out"].any() and not flags["weekly_out"].any()      # last year's weeks are inside the data
    up = forecast(model, scale_plan(base, {"influencer": 1.3}))
    f = up.flags[up.flags["input"] == "influencer"]
    assert f["sustained_out"].any()
    assert f["sustained_out"].sum() > f["weekly_out"].sum()       # held level leaves the data before single weeks do
    assert any(w.startswith("influencer: the 13-week average") for w in up.warnings)
    assert not up.flags.loc[up.flags["input"] != "influencer", "sustained_out"].any()
    price = check_range(model, base.assign(regular_price=2.0))
    assert price.loc[price["input"] == "regular_price", "weekly_out"].all()


def test_compare_scenarios(model, base):
    plans = {"current": base, "shift": shift_budget(base, "tv", "influencer", 0.10),
             "more": scale_plan(base, {"pos_promotion": 1.2})}
    table, fcs = compare_scenarios(model, plans, baseline="current")
    assert table.loc["current", "delta_revenue_mean"] == 0 and table.loc["current", "delta_revenue_p95"] == 0
    assert table.loc["shift", "media_spend"] == pytest.approx(table.loc["current", "media_spend"])
    assert table.loc["shift", "delta_revenue_p5"] > 0
    assert np.isnan(table.loc["shift", "roi_vs_baseline"]) and table.loc["more", "roi_vs_baseline"] > 0
    assert "influencer" in table.loc["shift", "inputs_out_of_range"]
    assert set(fcs) == set(plans)


def test_plan_defaults_and_validation(model, base):
    spend_only = base[CHANNELS]
    fc = forecast(model, spend_only, n_draws=50)
    assert (fc.plan["promo_discount"] == 0).all() and fc.plan["regular_price"].nunique() == 1
    flagged = forecast(model, spend_only.assign(price_promo=[1] + [0] * 11), n_draws=50).plan
    assert flagged["promo_discount"].iloc[0] == pytest.approx(model.ranges["promo_discount"]["mean"])
    with pytest.raises(ValueError, match="missing spend"):
        forecast(model, base.drop(columns="tv"))
    with pytest.raises(ValueError, match="negative"):
        forecast(model, base.assign(tv=-1.0))
    with pytest.raises(ValueError, match="consecutive"):
        forecast(model, base.assign(week_beg=base["week_beg"] + pd.Timedelta(days=7)))
    with pytest.raises(ValueError, match="promo_discount"):
        forecast(model, base.assign(promo_discount=24.0))


def test_benchmark_mode(model, base):
    plans = {"current": base, "shift": scale_plan(base, {"tv": 0.9, "instagram": 1.1, "tiktok": 1.1, "influencer": 1.1})}
    est, _ = compare_scenarios(model, plans, baseline="current")
    lit, fcs = compare_scenarios(model, plans, baseline="current", effects="benchmark")
    assert 0 < lit.loc["shift", "delta_revenue_pct"] < est.loc["shift", "delta_revenue_pct"] / 3
    w = fcs["current"].weekly
    wide, narrow = w["units_p95"] / w["units_p5"], forecast(model, base).weekly.eval("units_p95 / units_p5")
    assert (wide > narrow).all()                                   # the benchmark-sized model fits worse, so wider bands
    assert load_model(MODEL_PATH).benchmark is not None
    with pytest.raises(ValueError, match="effects"):
        forecast(model, base, effects="other")


def test_media_roi_of_a_plan(model, base):
    fc = forecast(model, base)
    t, ch = fc.totals, fc.channels
    assert t["media_spend_above_reference"] == pytest.approx(ch["spend_above_reference"].sum())
    assert t["media_incremental_revenue_mean"] == pytest.approx(ch["incremental_revenue_mean"].sum())
    assert t["media_roi_mean"] == pytest.approx(ch["incremental_revenue_mean"].sum() / ch["spend_above_reference"].sum())
    assert t["media_roi_p5"] < t["media_roi_p50"] < t["media_roi_p95"]
    assert ch["roi_mean"].min() < t["media_roi_mean"] < ch["roi_mean"].max()      # a spend-weighted mix of the channels
    table, _ = compare_scenarios(model, {"current": base}, baseline="current")
    assert table.loc["current", "media_roi_p50"] == pytest.approx(t["media_roi_p50"])


def test_gain_range(model, base):
    plans = {"current": base, "shift": scale_plan(base, {"tv": 0.9, "instagram": 1.1, "tiktok": 1.1, "influencer": 1.1}),
             "more tv": scale_plan(base, {"tv": 1.2})}
    rng, detail = gain_range(model, plans, baseline="current")
    est, lit = detail["model"][0], detail["benchmark"][0]
    assert list(rng.index) == list(plans) and set(detail["model"][1]) == set(plans)
    assert (rng.loc["current"].to_numpy() == 0).all()
    assert rng.loc["shift", "delta_revenue_pct_low"] == pytest.approx(lit.loc["shift", "delta_revenue_pct"])
    assert rng.loc["shift", "delta_revenue_pct_high"] == pytest.approx(est.loc["shift", "delta_revenue_pct"])
    assert rng.loc["shift", "delta_revenue_model"] == pytest.approx(est.loc["shift", "delta_revenue_mean"])
    # the benchmark doubles TV's effect, so for a TV increase it is the upper end: the ends must be sorted
    assert lit.loc["more tv", "delta_revenue_pct"] > est.loc["more tv", "delta_revenue_pct"]
    assert rng.loc["more tv", "delta_revenue_pct_high"] == pytest.approx(lit.loc["more tv", "delta_revenue_pct"])
    assert (rng["delta_revenue_low"] <= rng["delta_revenue_high"]).all()


def test_shift_budget_is_exact_and_validated(base):
    moved = shift_budget(base, "tv", "influencer", 0.10)
    assert moved[CHANNELS].sum().sum() == pytest.approx(base[CHANNELS].sum().sum())
    assert moved["tv"].sum() == pytest.approx(0.9 * base["tv"].sum())
    assert moved["influencer"].sum() == pytest.approx(base["influencer"].sum() + 0.1 * base["tv"].sum())
    with pytest.raises(ValueError, match="different"):
        shift_budget(base, "tv", "tv", 0.1)
    with pytest.raises(ValueError, match="unknown channel"):
        shift_budget(base, "tv", "radio", 0.1)
    with pytest.raises(ValueError, match="share"):
        shift_budget(base, "tv", "influencer", 10)
    with pytest.raises(ValueError, match="no spend"):
        shift_budget(base.assign(tv=0.0), "influencer", "tv", 0.1)


def test_profit_view(model, base):
    fc = forecast(model, base)
    totals, ch = profit_view(fc, 0.20)
    assert totals["profit_after_media_mean"] == pytest.approx(0.2 * fc.totals["revenue_mean"] - fc.totals["media_spend"])
    assert totals["profit_after_media_p5"] < totals["profit_after_media_p50"] < totals["profit_after_media_p95"]
    np.testing.assert_allclose(ch["breakeven_margin"], 1 / fc.channels["roi_mean"])
    np.testing.assert_allclose(ch["incremental_profit_mean"],
                               0.2 * fc.channels["incremental_revenue_mean"] - fc.channels["spend_above_reference"])
    # at the break-even margin a channel earns exactly nothing; TV needs far more than 20%, influencers far less
    _, at_be = profit_view(fc, float(ch.loc["influencer", "breakeven_margin"]))
    assert at_be.loc["influencer", "incremental_profit_mean"] == pytest.approx(0, abs=1e-6)
    assert not ch.loc["tv", "pays_back"] and ch.loc["influencer", "pays_back"]
    assert ch.loc["tv", "incremental_profit_mean"] < 0 < ch.loc["influencer", "incremental_profit_mean"]
    assert _breakeven_is_margin_free(fc)
    with pytest.raises(ValueError, match="margin"):
        profit_view(fc, 20)


def _breakeven_is_margin_free(fc):
    return np.allclose(profit_view(fc, 0.2)[1]["breakeven_margin"], profit_view(fc, 0.4)[1]["breakeven_margin"])


def test_profit_gain(model, base):
    plans = {"current": base, "more": scale_plan(base, {"pos_promotion": 1.2}), "shift": shift_budget(base, "tv", "influencer", 0.1)}
    gains, _ = gain_range(model, plans, baseline="current")
    pg = profit_gain(gains, 0.25)
    assert (pg.loc["current"] == 0).all()
    assert gains.loc["more", "delta_spend"] == pytest.approx(0.2 * base["pos_promotion"].sum())
    assert pg.loc["more", "delta_profit_model"] == pytest.approx(
        0.25 * gains.loc["more", "delta_revenue_model"] - gains.loc["more", "delta_spend"])
    assert pg.loc["shift", "delta_profit_low"] == pytest.approx(0.25 * gains.loc["shift", "delta_revenue_low"])   # budget unchanged
    assert (pg["delta_profit_low"] <= pg["delta_profit_high"]).all()
