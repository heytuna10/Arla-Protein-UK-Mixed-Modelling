"""Steps 6-7: contributions, ROI with intervals, response curves, price and promotion effects,
budget scenarios, figures. Uses the final model; run scripts/run_part2.py first (model comparison)."""

import warnings

import numpy as np
import pandas as pd

from arla_mmm import figures as fg
from arla_mmm import insights as ins
from arla_mmm.baseline import QUENTIN_REFERENCE
from arla_mmm.data import CHANNELS, RESULTS_DIR
from arla_mmm.engine import fit, one_step, simulate
from arla_mmm.evaluate import HOLDOUT_WEEKS, md_table
from arla_mmm.final import N_DRAWS, final_model
from arla_mmm.scenarios import standard_scenarios

L = ins.LABEL


def pm(est, lo, hi, nd=1) -> str:
    return f"{est:.{nd}f} ({lo:.{nd}f}–{hi:.{nd}f})"


def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    m = final_model()
    d = m.data
    comparison = pd.read_csv(RESULTS_DIR / "model_comparison.csv")

    # ------------------------------------------------------------ step 6
    roi = ins.roi_summary(m)
    weekly, yearly = ins.decomposition(m)
    promo_hist = ins.promotions_history(m)
    promo_curve = ins.promotion_curve(m)
    price = ins.price_elasticity(m)
    curves = ins.response_curves(m)
    weekly.round(0).to_csv(RESULTS_DIR / "decomposition_weekly.csv", index=False)
    curves.round(1).to_csv(RESULTS_DIR / "response_curves.csv", index=False)

    roi_md = pd.DataFrame({
        "spend £m": roi["spend £m"], "share of media spend %": roi["share of media spend %"],
        "% of sales (5–95%)": [pm(r["% of sales"], r["% of sales p5"], r["% of sales p95"]) for _, r in roi.iterrows()],
        "revenue ROI above floor (5–95%)": [pm(r["ROI"], r["ROI p5"], r["ROI p95"], 2) for _, r in roi.iterrows()],
        "marginal ROI (5–95%)": [pm(r["marginal ROI"], r["mROI p5"], r["mROI p95"], 2) for _, r in roi.iterrows()],
        "break-even margin %, next £": roi["break-even margin % (marginal £)"],
        "break-even margin %, average £ above floor": roi["break-even margin % (average £ above floor)"],
    }, index=roi.index)
    m0 = comparison.set_index("model").loc["M0_baseline"]
    before_after = pd.DataFrame({
        "part 1 (its own method)": [QUENTIN_REFERENCE["roi"][c] for c in CHANNELS],
        "part 1 model, contributions that add up": [m0[f"roi_{c}"] for c in CHANNELS],
        "final model": roi["ROI"].to_numpy(),
        "part 1 model, marginal ROI": [m0[f"mroi_{c}"] for c in CHANNELS],
        "final model, marginal ROI": roi["marginal ROI"].to_numpy(),
    }, index=roi.index)
    yearly_md = yearly.rename(columns={**{c: L[c] for c in CHANNELS}, "growth": "growth since Jan 2022",
                                       "promotions": "price promotions", "base": "base incl. minimum always-on media"})
    ph = promo_hist
    base = roi.attrs["base"]
    (RESULTS_DIR / "step6_contributions_roi.md").write_text("\n".join([
        "# Step 6 – contributions, ROI and marginal ROI (final model M14)",
        "",
        f"History: {len(m.rows)} weeks (10 Jan 2022 – 23 Dec 2024). Intervals: 5–95% range over {N_DRAWS:,} coefficient draws "
        "from the Newey-West covariance; carry-over decays and curve scales are held at their estimates "
        "(their effect is in `step5_robustness.md`: at most ±15% on any ROI). Revenue ROI, not profit.",
        "",
        "## 1. Channel contributions and returns",
        "",
        "Reference: TV against zero spend; the four always-on channels against their lowest weekly spend observed. "
        f"Base incl. that minimum media: {pm(base['estimate'], base['p5'], base['p95'])}% of sales.",
        "",
        md_table(roi_md.rename_axis("channel"), nd={"share of media spend %": 0, "break-even margin %, next £": 1,
                                                    "break-even margin %, average £ above floor": 1}),
        "",
        "- *Revenue ROI above floor*: incremental revenue / spend above the floor (TV: / total spend).",
        "- *Marginal ROI*: revenue per extra £ if the channel's spend were 10% higher in every week.",
        "- *Break-even margin*: the gross margin at which the £ pays for itself = 1 / ROI. Margin is not in the data; "
        "read the column against whatever margin the business has (e.g. at a 40% margin, anything below 40 pays off).",
        "",
        "## 2. Decomposition of sales (% of units)",
        "",
        "Shapley split over seven drivers (five channels, price promotions, underlying growth); the parts add up to actual sales. "
        "Weekly series: `decomposition_weekly.csv`; chart: `figures/decomposition.png`.",
        "",
        md_table(yearly_md.rename_axis("period"), nd=1),
        "",
        "Price promotions here = extra units against paying the shelf price in every week. Growth = the trend since the first week "
        "(+7% a year); seasonality and the shelf-price level are inside the base.",
        "",
        "## 3. What changed against part 1, and why",
        "",
        md_table(before_after.rename_axis("revenue ROI"), nd=2),
        "",
        "- Part 1's own numbers are short-run and do not add up (channels sum to 149% of sales).",
        "- Column 2 is the same model with carry-over counted and contributions forced to add up; column 3 the final model. "
        "The always-on channels move little; the ranking is unchanged.",
        "- TV changes most at the margin: 0.16 → 1.72. Part 1 used log(spend + 1), which turns TV into an on/off switch, "
        "so 10% more TV spend did almost nothing in that model.",
        "- POS falls (5.3 → 3.7) once each channel has its own carry-over: POS has none of its own, whereas part 1's single "
        "lagged-sales term gave every channel the same 2.3× long-run multiplier.",
        "",
        "## 4. Price promotions (kept separate from POS spend)",
        "",
        f"Over the history there were {ph['promo weeks']} promotion weeks at an average 24% off. Against charging the shelf price in "
        "every week, and counting the dip in the week after and repeat purchase:",
        "",
        f"- units: **{ph['units %']['estimate']:+.1f}%** ({ph['units %']['p5']:+.1f} to {ph['units %']['p95']:+.1f});",
        f"- revenue: **{ph['revenue %']['estimate']:+.1f}%** ({ph['revenue %']['p5']:+.1f} to {ph['revenue %']['p95']:+.1f}), "
        f"i.e. £{ph['revenue £m']['estimate']:.1f}m over three years, about £{-ph['revenue per promo week £k']['estimate']:.0f}k "
        "of revenue given up per promotion week.",
        "",
        "One promotion week at different discounts (stylised: starting from a normal week; % of a normal week's units or revenue):",
        "",
        md_table(promo_curve.rename_axis("discount"), nd=1),
        "",
        "The uplift is far below what a discount needs to pay for itself in revenue (last column), at every depth. "
        "Promotions buy volume, not revenue, and since the margin on a discounted unit is lower still, not profit either. "
        "Not in the model: retailer listing or shelf-space benefits, and any long-term effect on what shoppers consider the normal price.",
        "",
        "## 5. Shelf price",
        "",
        md_table(price.rename_axis(""), nd=2),
        "",
        "Demand is inelastic: a higher shelf price loses fewer units than it gains in price. Caveat: identified from four upward "
        "price steps that coincide with the growth trend (VIF 11), so the interval is wide and includes no revenue gain at all.",
        "",
        "## 6. Response curves",
        "",
        "`figures/response_curves.png`, data in `response_curves.csv`: weekly revenue against a constant weekly spend per channel, "
        "with the range the model has evidence for. Carry-over profile per channel: `step3_media.md`.",
        "",
    ]))

    # ------------------------------------------------------------ step 7
    replay, plans = standard_scenarios(m)
    table = replay.compare(list(plans.values()), plans["A"])
    pd.concat([p.spend.assign(scenario=p.name, week_beg=d["week_beg"].iloc[replay.rows].to_numpy())
               for p in plans.values()])[["scenario", "week_beg"] + CHANNELS].round(0).to_csv(
        RESULTS_DIR / "scenario_plans.csv", index=False)
    spend_cols = [f"{c} £m" for c in CHANNELS]
    alloc = table[spend_cols].rename(columns={f"{c} £m": L[c] for c in CHANNELS})
    alloc_pct = (alloc.div(alloc.loc[plans["A"].name]) - 1) * 100
    result = pd.DataFrame({
        "media budget £m": table["media spend £m"], "revenue £m": table["revenue £m"],
        "Δ revenue £m (5–95%)": [pm(r["Δ revenue £m"], r["Δ p5"], r["Δ p95"]) for _, r in table.iterrows()],
        "Δ revenue %": table["Δ revenue %"], "Δ units %": table["Δ units %"],
        "revenue per £ of media": table["revenue per £ of media"],
    }, index=table.index)
    checks = []
    for key in ("B10", "B20", "Bmax", "C"):
        rc = replay.range_check(plans[key])
        rc.index = [L[c] for c in rc.index]
        cols = ["change vs 2024 %", "weeks above observed weekly max", "plan 13-week average, max £",
                "highest 13-week average observed £", "plan 13-week average, min £", "lowest 13-week average observed £",
                "beyond sustained range"]
        checks += [f"**{plans[key].name}**", "", md_table(rc[cols].rename_axis("channel"), nd=0), ""]
    lo, hi = replay.bounds()
    bounds_md = pd.DataFrame({
        "2024 spend £m": replay.actual.sum() / 1e6,
        "lowest week observed £": [replay.hist_lo[c] for c in CHANNELS],
        "highest week observed £": [replay.hist_hi[c] for c in CHANNELS],
        "lowest 13-week average observed £": d[CHANNELS].rolling(13).mean().min().to_numpy(),
        "highest 13-week average observed £": d[CHANNELS].rolling(13).mean().max().to_numpy(),
    })
    bounds_md.index = [L[c] for c in CHANNELS]
    b10, b20, bmax = table.loc[plans["B10"].name], table.loc[plans["B20"].name], table.loc[plans["Bmax"].name]
    tv, pos = roi.loc["TV"], roi.loc["POS"]
    (RESULTS_DIR / "step7_scenarios.md").write_text("\n".join([
        "# Step 7 – budget scenarios and recommendation (final model M14)",
        "",
        "## How the scenarios work",
        "",
        "Each scenario replays the 52 weeks of 2024 with a different media plan: same weeks, prices, promotions and weekly shocks; "
        "only media spend changes. Revenue = units × the price actually paid each week. Effects spilling into 2025 are not counted. "
        f"2024 media budget: £{replay.budget / 1e6:.2f}m; revenue £{table.loc[plans['A'].name, 'revenue £m']:.1f}m.",
        "",
        "Optimised plans maximise expected revenue for a fixed total budget. Every week keeps its place in the 2024 pattern and moves "
        "between a lower and an upper bound. TV keeps its flight calendar: on-air weeks move between the lowest on-air week and the "
        "highest week observed; off-air weeks stay off. Three sets of bounds, from tight to wide:",
        "",
        "- **±10%**: no week moves more than 10% from its 2024 value (added by me: about the widest sustained change the data contain);",
        "- **±20%**: no week moves more than 20% (the brief's conservative variant);",
        "- **observed weekly range**: any week anywhere between the channel's lowest and highest week ever (the brief's main scenario).",
        "",
        md_table(bounds_md.rename_axis("channel"), nd={"2024 spend £m": 2, **{c: 0 for c in bounds_md.columns[1:]}}),
        "",
        "## Results",
        "",
        md_table(result.rename_axis("scenario"), nd={"Δ revenue %": 0, "Δ units %": 0}),
        "",
        "Intervals reflect coefficient uncertainty only. They do **not** cover the larger risk, that the response measured on small "
        "week-to-week changes does not hold for a sustained shift (see range check).",
        "",
        "Annual spend per channel, £m:",
        "",
        md_table(alloc.rename_axis("scenario"), nd=2),
        "",
        "Change against 2024, %:",
        "",
        md_table(alloc_pct.rename_axis("scenario"), nd=0),
        "",
        "Weekly plans for every scenario: `scenario_plans.csv`. Charts: `figures/scenarios.png`, `figures/allocation.png`.",
        "",
        "## Range check: how far does each plan leave what has been observed?",
        "",
        "The model's long-run effect needs a spend level to be held for weeks. Single weeks have ranged widely, but sustained levels "
        "have not: the highest 13-week average of influencer spend ever observed is only 11% above its long-run mean. "
        "'Beyond sustained range' = the plan's 13-week average leaves the range of 13-week averages in the data by more than 2%.",
        "",
        *checks,
        "## Reading the numbers",
        "",
        f"- Every optimised plan does the same thing: TV to its lower bound, Instagram, TikTok and influencers to their upper bound, "
        "POS roughly unchanged under tight bounds and cut under wide ones. The allocation is set by the bounds, as expected; "
        "the *direction* is the finding.",
        f"- The size is not credible as a forecast. A ±10% reshuffle is credited with {b10['Δ revenue %']:+.0f}% revenue, ±20% with "
        f"{b20['Δ revenue %']:+.0f}%, the observed weekly range with {bmax['Δ revenue %']:+.0f}%. This is the arithmetic of the marginal "
        "ROIs (an extra £ of influencer spend ≈ £75 of revenue) applied to a sustained shift, compounded because the model is "
        "multiplicative. No brand triples its revenue by moving £1m of media.",
        "- What the data support: week-to-week movements in social and influencer spend line up with large movements in sales, "
        "robustly (step 5). What they cannot show: that the same response holds when the level is raised and kept there.",
        "",
        "## Recommendation",
        "",
        "1. **Direction:** shift budget from TV to influencers, Instagram and TikTok. Every scenario, every model variant and both "
        "halves of the history agree on the ranking.",
        "2. **First step: the ±10% plan (B1)**: TV −10% within its flights, influencer, Instagram and TikTok +10% each, POS unchanged, "
        "total budget unchanged. It stays inside the sustained range for every channel except influencer (9% above the highest "
        "13-week average seen).",
        "3. **Treat the first step as a test.** Present the model-implied gain as an upper bound, not a plan number, and measure: "
        "e.g. raise influencer and social spend for one quarter, or in some regions, and compare. Scale further only on that evidence.",
        "4. **Do not use the wide scenarios (B2, B3, C) as plan numbers.** They are shown to make the extrapolation visible.",
        "",
        "## The board's question: do TV and in-store promotion earn their share?",
        "",
        f"- **TV**: {tv['share of media spend %']:.0f}% of media spend, {tv['% of sales']:.0f}% of sales. Revenue ROI "
        f"{tv['ROI']:.2f} on the average £ and {tv['marginal ROI']:.2f} on the next £. It pays for itself only above a gross margin of "
        f"{tv['break-even margin % (marginal £)']:.0f}% at the margin (and not at all on average: ROI ≈ 1 means £1 of revenue per £1 spent). "
        "It is the weakest channel by a factor of three or more, and the first to cut in every scenario. No saturation was found, "
        "so cutting within flights loses revenue proportionally, no more.",
        f"- **POS promotion spend**: {pos['share of media spend %']:.0f}% of media spend, {pos['% of sales']:.0f}% of sales. Revenue ROI "
        f"{pos['ROI']:.1f} and {pos['marginal ROI']:.1f} on the next £; pays above a margin of about "
        f"{pos['break-even margin % (marginal £)']:.0f}%. It earns its keep but is the second-weakest channel; hold it, do not grow it "
        "ahead of social.",
        f"- **Price promotions** (not a media line, but the larger in-store question): they lifted units by {ph['units %']['estimate']:.0f}% "
        f"and cost {-ph['revenue %']['estimate']:.1f}% of revenue (£{-ph['revenue £m']['estimate']:.1f}m over three years). "
        "On revenue they do not earn their share; fewer or shallower promotions is the first lever to test.",
        "",
    ]))

    # ------------------------------------------------------------ figures
    fg.decomposition(weekly)
    fg.roi(roi)
    roll = d[CHANNELS].rolling(13).mean()
    fg.response_curves(curves, {c: (float(roll[c].min()), float(roll[c].max())) for c in CHANNELS})
    fg.model_ladder(comparison)
    origin = len(d) - HOLDOUT_WEEKS
    f_train = fit(m.spec, d, end=origin)
    rows_test = np.arange(origin, len(d))
    fitted = np.r_[np.nan, one_step(m.spec, m.fit.params, d, m.rows)]
    fg.fit_holdout(d["week_beg"].to_numpy(), d["sales_units"].to_numpy(dtype=float), fitted,
                   simulate(m.spec, f_train.params, d, rows_test), origin)
    fg.scenarios(table, [plans[k].name for k in ("B10", "B20", "C", "D-", "D+")])
    fg.allocation({"2024 plan": plans["A"].spend.sum(), "Optimised, ±10%": plans["B10"].spend.sum(),
                   "Optimised, ±20%": plans["B20"].spend.sum()},
                  "Annual media spend per channel, total unchanged at £%.2fm" % (replay.budget / 1e6))
    fg.promotions(promo_curve)
    print("step 6-7 results and figures written to", RESULTS_DIR)


if __name__ == "__main__":
    main()
