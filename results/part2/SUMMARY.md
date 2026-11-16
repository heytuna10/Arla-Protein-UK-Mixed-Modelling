# Part 2 – summary for the slides

What the extended marketing mix model says, in the order a deck would tell it. Every number comes from a table in this folder (named in brackets) and can be rebuilt with the scripts in `scripts/`. All returns are **revenue** per £ of spend unless a margin is stated. Channel returns are measured above each channel's lowest observed weekly spend (TV: against no TV), because the always-on channels were never switched off.

## The message in three sentences

The model forecasts well, and it ranks the channels the same way under every check we could think of: social and influencers first, in-store promotion second, TV last. The *size* of the social and influencer effects is far larger than any published study finds, so we do not sell the model's revenue gain as a forecast. We recommend the direction, give the gain as a range, and propose a 13-week test that costs almost nothing and tells us where in that range the truth lies.

## The story in ten bullets

1. **A better model, chosen from 20 candidates.** Starting from part 1's model we added growth and seasonality, split price into shelf price and promotion depth, gave each channel its own memory and a diminishing-returns curve that works at zero spend, and kept repeat purchase. Forecast error on the last 26 weeks fell from 11.4% to 4.2%, and all residual checks pass. Twelve-week forecasts from four starting points were off by 4.0% on average, with 92% of weeks inside the 90% band. [`model_comparison.md`, `step8_interface_check.md`; figures `model_ladder.png`, `fit_holdout.png`]

2. **What drives sales, according to the model.** Over 2022–24: base including the minimum always-on media 17%, underlying growth 8%, price promotions 3%, influencers 30%, TikTok 16%, Instagram 15%, TV 7%, POS 5%. The parts add up to actual sales in every week, which part 1's did not (150–160%). Media is 18% of revenue in this dataset, and shares are measured above each channel's minimum spend. [`step6_contributions_roi.md` §2; figure `decomposition.png`]

3. **The ranking is clear: digital, then POS, then TV.** Revenue per £ above the floor: influencer 42.8, Instagram 18.6, TikTok 16.9, POS 3.7, TV 0.99. For the next £: 74.6, 30.8, 24.8, 5.5, 1.72. The order digital > POS > TV did not change in any of 20 model versions, 13 alternative curve and carry-over settings, an additive model, either half of the history, or after dropping the five most influential weeks. [`step6_contributions_roi.md` §1, `step5_robustness.md`; figure `roi.png`]

4. **But the sizes are too large to take at face value.** Published studies find an average long-term advertising elasticity of 0.24. Ours: TV 0.12 and POS 0.20, in line; TikTok 0.54, Instagram 0.83, influencer 1.67, two to seven times higher. [`step8_magnitude_check.md`]

5. **We tried to explain the sizes away and could not.** Budgets do not follow demand: spend does not react to last week's sales or to promotion weeks, future spend explains nothing, and slow and fast movements of spend give the same effect. The three digital channels do not share one effect: their budgets are uncorrelated, and a single "digital" channel forecasts far worse (10.9% error against 4.2%). The effects are in the data, most likely because the dataset was built with strong effects. [`step9_critical_review.md`, `step9_diagnostics.md`]

6. **Forced to literature-sized effects, the model stops working, and the ranking still holds.** Re-estimated with every channel tied to the benchmark, forecast error triples to 12.2% (worse than part 1's model). Even then an extra £ returns about £9–11 on each digital channel, £6.9 on POS and £3.5 on TV, because the digital budgets are small relative to revenue. What does not hold is the order among Instagram, TikTok and influencer. [`step9_anchored.md`; figure `anchored.png`]

7. **In profit terms: TV loses money on the next £, digital pays under every assumption.** At a gross margin of 20–30%, the next £ of TV returns 34–52p of margin and loses the rest; POS is at break-even at 20% and pays at 30%; the digital channels pay at every margin, also with literature-sized effects. TV needs a margin above 58% to break even. Margin is our assumption (listed food processors average about 23% gross margin). [`step9_critical_review.md`, profit view]

8. **Price promotions add volume and lose revenue.** They added 6% to units and cost 3.7% of revenue, about £5.2m over three years. A 24% discount sells 17% more units and would need 32% more to hold revenue; no depth in the data pays for itself. POS spend returns £3.7 per £, but it is higher in promotion weeks, so the two are harder to separate than the other effects. [`step6_contributions_roi.md` §4; figure `promotions.png`]

9. **Recommendation: move 10% of the TV budget into influencers, Instagram and TikTok.** TV −10% within its flights, the three digital channels +10% each, POS and the total unchanged. This is about as far as the brand has ever held spend from today's levels. The gain: **between about +5% of revenue (literature-sized effects) and +30% (the model as estimated)**. The model's own number, +£15m a year, is the upper end and not a forecast. [`step7_scenarios.md`, `step9_anchored.md`; figures `allocation_main.png`, `scenarios_main.png`]

10. **Run it as a 13-week test with a decision rule.** Compare actual sales with the model's forecast for the unchanged plan, then return to the old plan for eight weeks to see the uplift fade. Thirteen weeks can detect a change of 3–6% in sales. Uplift of +15% or more: take the next step. +6% to +15%: keep the shift and rescale the model. Below that: keep it only on the profit argument and extend the test. The cost of being wrong is the TV cut, about 1.2% of sales. [`step9_critical_review.md`, test design]

## Further findings

- **Effects last weeks, not months.** TV and influencer effects arrive 39% in the week of spend and 93% within four weeks; TikTok and POS work almost entirely in the week they run. On top, 36% of any week's uplift comes back the next week as repeat purchase. No extra synergy between channels beyond the general effect that everything works better when sales are high. [`step3_media.md`, `step4_synergies.md`]
- **Demand is not very price-sensitive, but this is the weakest number.** A 1% higher shelf price costs about 0.8% of units, so a 5% increase would add about 1% revenue (range −0.8% to +3.1%). In pence: 5p more on today's £1.61 would cost about 16,000 units a week (8,000 to 24,000) and add about £7,000 of weekly revenue (−£5,000 to +£19,000). The shelf price only ever rose, four times. Expressing price effects per penny is Ketan's idea from part 1. [`step6_contributions_roi.md` §5]
- **TV in part 1 and now.** Part 1 made TV look worthless at the margin (£0.16 per extra £) because of how weeks without TV were handled; treated properly it returns £1.72. TV's elasticity is the one most in line with the literature, which makes "TV does not pay back" the most believable single result. [`step6_contributions_roi.md` §3]

## For the "analytical steps" slide

- **Why revenue is never an explanatory variable.** Revenue is units × price, so it is the target in disguise: part 1 showed that a model with revenue on the right-hand side reaches R² = 1.000 and explains nothing (noted in Ketan's and Quentin's notebooks). We model units and derive revenue from units and price.
- **One change at a time.** Every extension was tested against the previous model on information criteria, forecast error on unseen weeks, residual checks and plausibility, and kept only if it passed all four.

## For the "how we tried to break it" slide

| we asked | we found |
|---|---|
| Do budgets follow last week's sales, or rise when demand is high (promotion weeks)? | No, for TV and all digital channels |
| Are budgets planned where demand is expected? | No: future spend explains nothing, and the effect sits in week-to-week movements (74–97% of the variation) |
| Is it one digital effect split three ways? | No: budgets are uncorrelated; one digital channel forecasts far worse |
| Does the model need the large effects? | Yes: tied to literature sizes, forecast error triples |
| Does the ranking need the large effects? | No: digital > POS > TV at every prior strength |
| What could still be wrong? | Spend reacting to demand within the same week; only impressions data or the test can tell |

## Magnitude check in numbers

Advertising elasticity is the % change in sales for 1% more spend. Benchmark: Sethuraman, Tellis & Briesch (2011, *Journal of Marketing Research*), 0.12 short-term and 0.24 long-term on average. [`step8_magnitude_check.md`]

| channel | short-term (week of spend) | long-term | long-term ÷ benchmark | revenue per extra £, as estimated | revenue per extra £, at benchmark size |
|---|---|---|---|---|---|
| TV | 0.05 | 0.12 | 0.5 | 1.7 | 3.5 |
| POS | 0.13 | 0.20 | 0.8 | 5.5 | 6.9 |
| TikTok | 0.35 | 0.54 | 2.2 | 24.8 | 11.4 |
| Instagram | 0.37 | 0.83 | 3.4 | 30.8 | 9.1 |
| Influencer | 0.64 | 1.67 | 7.0 | 74.6 | 10.5 |

Possible reasons for the size, if asked: the data were built for teaching; spend is in £, not exposure; platforms may spend more within a week when demand is high; sustained spend levels moved by only 11–43% around their mean.

## Why some response curves bend upwards

The model is multiplicative: each channel lifts sales by a percentage, and that percentage shows diminishing returns. But a given percentage of a larger sales base is more £, so in £ a curve can rise ever faster before it flattens. Only the influencer curve does this over its whole observed range. Followed far outside the data, the formula would have influencers multiply sales several hundred times, the clearest sign that the curve must not be trusted beyond its range. This is why the scenarios are bounded and why the dashboard warns when a plan leaves the data. [`step8_magnitude_check.md`; figure `response_curves.png`]

## Caveats for the limitations slide

- Effects are only observed between each channel's historical minimum and maximum spend, and for sustained levels in a much narrower band.
- Revenue, not profit; the margin range is an assumption.
- Observational data without exposure measures (impressions, reach), competitor prices, distribution or regions. These are the data that would settle the open question.
- Intervals cover uncertainty in the coefficients only.
- Next steps: the test; then a model with priors taken from its result (a Bayesian marketing mix model, e.g. PyMC-Marketing or Meridian).

## Figures (`figures/`)

Main slides:

| file | shows | bullet |
|---|---|---|
| `model_ladder.png` | forecast error and fit from part 1's model to the final one | 1 |
| `fit_holdout.png` | actual vs fitted sales, with the 26 weeks the model had not seen | 1 |
| `decomposition.png` | sales by driver, per quarter | 2 |
| `roi.png` | revenue per £ and per next £, by channel, with ranges | 3 |
| `anchored.png` | effect sizes and forecast error as the model is tied to literature-sized effects | 4, 6 |
| `promotions.png` | units and revenue effect of a promotion week by discount depth | 8 |
| `allocation_main.png` | budget per channel: 2024, the first-step plan, 10% of TV to influencer | 9 |
| `scenarios_main.png` | model-implied upper bound of the revenue change for the same three plans | 9 |

Appendix:

| file | shows |
|---|---|
| `response_curves.png` | revenue against sustained weekly spend per channel, with the observed ranges |
| `scenarios.png` | all scenarios incl. ±20% and total budget ±10% |
| `allocation.png` | budget per channel for the ±10% and ±20% plans |
| `forecast_example.png` | what the dashboard interface returns: 12-week forecast with bands for three plans |

## Where things are

| question | file |
|---|---|
| Which models were compared, and how do they score? | `model_comparison.md`, `candidates/` |
| Why this specification? | `step2_controls.md`, `step3_media.md`, `step4_synergies.md` |
| How robust is it? | `step5_robustness.md` |
| Contributions, ROI, promotions, price | `step6_contributions_roi.md` |
| Scenarios and recommendation | `step7_scenarios.md` |
| Effect sizes against the literature | `step8_magnitude_check.md` |
| What can we claim, what not; profit view; test design | `step9_critical_review.md`, `step9_diagnostics.md` |
| What happens with literature-sized effects | `step9_anchored.md` |
| Forecast accuracy of the dashboard interface | `step8_interface_check.md` |
| How to call the model from the dashboard | `docs/part2/INTERFACE.md` |
| Every decision with its reason | `docs/part2/LOG.md` |
| The story with charts, runnable | `notebooks/02_model_extension.ipynb` |
