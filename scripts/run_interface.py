"""Step 8: save the fitted model for the dashboard, back-test the forecast interface, write the
magnitude check and the main-slide figures. Run after scripts/run_part2.py and scripts/run_insights.py."""

import warnings

import numpy as np
import pandas as pd

from arla_mmm import figures as fg
from arla_mmm import insights as ins
from arla_mmm.data import CHANNELS, REPO_ROOT, RESULTS_DIR
from arla_mmm.evaluate import md_table
from arla_mmm.final import final_model
from arla_mmm.interface import (MODEL_PATH, backtest, baseline_plan, compare_scenarios, fit_model, save_model,
                                scale_plan, shift_budget)
from arla_mmm.scenarios import standard_scenarios

L = ins.LABEL


def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    m = final_model()

    # ------------------------------------------------------------ the model file the dashboard loads
    model = fit_model()
    assert np.allclose(model.params, m.fit.params.to_numpy())
    save_model(model)

    # ------------------------------------------------------------ magnitude check + curve shape
    el = ins.elasticities(m)
    shape = ins.curve_shape(m)
    b = ins.BENCHMARK
    el_md = pd.DataFrame({
        "short-term, week of spend (5–95%)": [f"{r['short-term']:.2f} ({r['short p5']:.2f}–{r['short p95']:.2f})" for _, r in el.iterrows()],
        "long-term (5–95%)": [f"{r['long-term']:.2f} ({r['long p5']:.2f}–{r['long p95']:.2f})" for _, r in el.iterrows()],
        "long-term if the typical level were held": el["long-term at typical spend"],
        "short-term ÷ benchmark": el["short-term vs benchmark ×"],
        "long-term ÷ benchmark": el["long-term vs benchmark ×"],
    }, index=el.index)
    lines = [
        "# Step 8 – magnitude check: are the effect sizes plausible?",
        "",
        "Advertising elasticity = % change in units for 1% more spend. Benchmark: the meta-analysis of Sethuraman, Tellis & "
        "Briesch (2011, *Journal of Marketing Research* 48(3), 457–471), mean over published brand-level estimates: "
        f"**{b['short']:.2f} short-term, {b['long']:.2f} long-term**.",
        "",
        "Ours, from the final model (M14): *long-term* = % change in total units over the history when the channel's spend is 1% "
        "higher in every week (adstock and repeat purchase included); *short-term* = the part that arrives in the week of the spend. "
        "Intervals: coefficient uncertainty only.",
        "",
        md_table(el_md.rename_axis("channel"), nd={"long-term if the typical level were held": 2,
                                                  "short-term ÷ benchmark": 1, "long-term ÷ benchmark": 1}),
        "",
        "TV's first two columns are over its actual flight calendar (on air in 41 of 156 weeks); held on air at its average "
        "on-air weight its long-term elasticity would be the third column.",
        "",
        "## Reading",
        "",
        f"- TV ({el.loc['TV', 'long-term']:.2f}) and POS ({el.loc['POS', 'long-term']:.2f}) are in the range the literature finds.",
        f"- Instagram ({el.loc['Instagram', 'long-term']:.2f}), TikTok ({el.loc['TikTok', 'long-term']:.2f}) and above all "
        f"influencer ({el.loc['Influencer', 'long-term']:.2f}) are {el.loc['TikTok', 'long-term vs benchmark ×']:.0f} to "
        f"{el.loc['Influencer', 'long-term vs benchmark ×']:.0f} times the long-term benchmark. An elasticity above 1 means sales "
        "grow faster than the spend that causes them; published estimates of that size are rare.",
        "- So the ranking (social and influencers ahead of POS, POS ahead of TV) is credible and robust (step 5), but the *size* of "
        "the social and influencer effects should be treated as untested. This is the strongest argument for the recommendation "
        "\"direction yes, size to be tested\".",
        "",
        "## Why might they be this large?",
        "",
        "1. **Teaching dataset.** The data were built for the course; effect sizes need not be calibrated to real markets.",
        "2. **Spend in £, not exposure.** We see budgets, not impressions or reach. If the cost per contact fell over time or "
        "differs by week, £ understate the change in exposure and the elasticity per £ is inflated.",
        "3. **Budgets that follow demand.** If social and influencer budgets are set higher in periods when demand is expected to "
        "be high (launches, seasons, retailer events), the model credits the spend with sales that would have come anyway. The "
        "placebo test in step 5 found no sign of this from one week to the next, but it cannot see planning at monthly or "
        "quarterly horizons.",
        "4. **Narrow range.** Held spend levels moved by only 11–43% around their mean; a slope measured on small movements is "
        "then extrapolated by the curve.",
        "",
        "## Why some £ response curves bend upwards",
        "",
        "The model is multiplicative: a channel held at spend x multiplies sales by exp(B × f(x)), with f(x) = x / (x + scale) "
        "and B = its coefficient ÷ (1 − lagged-sales coefficient). f shows diminishing returns in *percent*. But a given percent "
        "lift is worth more £ the larger the sales it applies to, so in £ the curve can rise ever faster before it flattens. "
        "It bends upwards for spend below scale × (B/2 − 1).",
        "",
        md_table(shape.rename_axis("channel"), nd={"long-run coefficient B": 2, "max. sales multiple exp(B)": 0,
                                                  "curve bends upwards below £/week": 0, "lowest 13-week average observed £": 0,
                                                  "highest 13-week average observed £": 0}),
        "",
        f"- Only influencer bends upwards over its whole observed range (and TV at low sustained weights). Its B of "
        f"{shape.loc['Influencer', 'long-run coefficient B']:.1f} says that saturating the channel would multiply sales by "
        f"{shape.loc['Influencer', 'max. sales multiple exp(B)']:.0f} against zero spend. Nobody should believe that; it is what a "
        "steep slope measured on a narrow range turns into when the formula is followed outside it.",
        "- This is why every optimiser pushes influencer to its bound, why the scenario gains grow faster than the budget shift, "
        "and why the interface flags plans whose 13-week average leaves the observed range.",
        "",
    ]
    (RESULTS_DIR / "step8_magnitude_check.md").write_text("\n".join(lines))

    # ------------------------------------------------------------ interface: back-test and example
    bt = backtest()
    by_origin = bt.groupby("origin").agg(**{
        "median-forecast error %, mean over 12 weeks": ("abs_pct_error", "mean"),
        "worst week %": ("abs_pct_error", "max"),
        "actual inside the 5–95% band, weeks of 12": ("inside_band", "sum"),
    })
    by_origin.loc["all four"] = [bt["abs_pct_error"].mean(), bt["abs_pct_error"].max(), bt["inside_band"].sum()]
    by_origin["actual inside the 5–95% band, weeks of 12"] = by_origin["actual inside the 5–95% band, weeks of 12"].astype(int)
    width = float(((bt["units_p95"] / bt["units_p5"] - 1) * 100).mean())

    base = baseline_plan(model, weeks=12)
    plans = {
        "Current plan": base,
        "TV −10%, social and influencer +10%": scale_plan(base, {"tv": 0.9, "instagram": 1.1, "tiktok": 1.1, "influencer": 1.1}),
        "10% of TV moved to influencer": shift_budget(base, "tv", "influencer", 0.10),
    }
    table, fcs = compare_scenarios(model, plans, baseline="Current plan")
    ex = pd.DataFrame({
        "media spend £m": table["media_spend"] / 1e6,
        "revenue £m, median (5–95%)": [f"{r['revenue_p50'] / 1e6:.1f} ({r['revenue_p5'] / 1e6:.1f}–{r['revenue_p95'] / 1e6:.1f})" for _, r in table.iterrows()],
        "Δ revenue £m (5–95%)": [f"{r['delta_revenue_mean'] / 1e6:.1f} ({r['delta_revenue_p5'] / 1e6:.1f}–{r['delta_revenue_p95'] / 1e6:.1f})" for _, r in table.iterrows()],
        "weeks with a sustained-level flag": table["weeks_sustained_out"].astype(int),
        "inputs out of range": table["inputs_out_of_range"].replace("", "none"),
    }, index=table.index)
    ch = fcs["Current plan"].channels
    ch_md = pd.DataFrame({
        "spend £k": (ch["spend"] / 1e3).to_numpy(), "spend above floor £k": (ch["spend_above_reference"] / 1e3).to_numpy(),
        "incremental revenue £k (5–95%)": [f"{r['incremental_revenue_mean'] / 1e3:,.0f} ({r['incremental_revenue_p5'] / 1e3:,.0f}–{r['incremental_revenue_p95'] / 1e3:,.0f})" for _, r in ch.iterrows()],
        "ROI above floor (5–95%)": [f"{r['roi_mean']:.1f} ({r['roi_p5']:.1f}–{r['roi_p95']:.1f})" for _, r in ch.iterrows()],
    }, index=[L[c] for c in ch.index])
    weeks = fcs["Current plan"].weekly
    lines = [
        "# Step 8 – forecast interface: back-test and example output",
        "",
        f"Model file: `{MODEL_PATH.relative_to(REPO_ROOT)}` (M14, fitted on {model.meta['weeks_in_fit']} weeks to {model.meta['last_week']}). "
        "How to call it: `docs/part2/INTERFACE.md`.",
        "",
        "## Back-test: 12-week forecasts from four starting points",
        "",
        "For each starting week the model was re-tuned and re-fitted on the earlier weeks only, then asked for the next 12 weeks "
        "given the spend, prices and promotions that actually followed. No information from the forecast weeks is used.",
        "",
        md_table(by_origin.rename_axis("forecast starts"), nd={"actual inside the 5–95% band, weeks of 12": 0}),
        "",
        f"- The median forecast is off by {bt['abs_pct_error'].mean():.1f}% on average, with no sign of getting worse towards week 12.",
        f"- {bt['inside_band'].mean() * 100:.0f}% of the 48 actual weeks fall inside the 5–95% band (90% would be ideal), so the bands "
        f"are honest for plans like the ones seen so far. The band is about ±{width / 2:.0f}% around the median in every week.",
        "- This says nothing about plans that leave the observed spend range; those are covered by the flags, not by the band.",
        "",
        f"## Example: the next 12 weeks ({weeks['week_beg'].iloc[0].date()} to {weeks['week_beg'].iloc[-1].date()})",
        "",
        "`baseline_plan` = spend and promotions of the same weeks a year earlier, shelf price as in the last observed week. "
        "Chart: `figures/forecast_example.png`.",
        "",
        md_table(ex.rename_axis("scenario"), nd={"media spend £m": 2, "weeks with a sustained-level flag": 0}),
        "",
        "The gains have the same character as in step 7 (large, because the influencer and social slopes are steep): show them "
        "as what the model implies, next to the flags.",
        "",
        "Channel view for the current plan (what `Forecast.channels` returns):",
        "",
        md_table(ch_md.rename_axis("channel"), nd=0),
        "",
        "Warnings returned for \"10% of TV moved to influencer\":",
        "",
        *[f"- {w}" for w in fcs["10% of TV moved to influencer"].warnings],
        "",
    ]
    (RESULTS_DIR / "step8_interface_check.md").write_text("\n".join(lines))

    # ------------------------------------------------------------ figures for the main slides
    fg.forecast_fan(m.data, {k: f.weekly for k, f in fcs.items()})
    replay, sp = standard_scenarios(m)
    comp = replay.compare(list(sp.values()), sp["A"])
    fg.scenarios(comp, [sp[k].name for k in ("A", "B10", "C")], name="scenarios_main.png",
                 title="Model-implied upper bound of the revenue change vs the 2024 plan",
                 subtitle="Replay of 2024, same total budget. Black line: 5–95% range from coefficient uncertainty only.\n"
                          "Direction and ranking are robust; the size is extrapolated and is what the proposed test should measure.")
    fg.allocation({"2024 plan": sp["A"].spend.sum(), "First step: TV −10%, social and influencer +10%": sp["B10"].spend.sum(),
                   "10% of TV moved to influencer": sp["C"].spend.sum()},
                  "Annual media spend per channel, total unchanged at £%.2fm" % (replay.budget / 1e6), name="allocation_main.png", legend_below=True)
    print("step 8 outputs written:", MODEL_PATH, "and", RESULTS_DIR)


if __name__ == "__main__":
    main()
