# Part 2 – summary for the slides

What the extended marketing mix model says, in the order a deck would tell it. Every number comes from a table in this folder (named in brackets) and can be rebuilt with the three scripts in `scripts/`. All returns are **revenue** per £ of spend, not profit. Channel returns are measured above each channel's lowest observed weekly spend (TV: against no TV), because the always-on channels were never switched off.

## The story in ten bullets

1. **A better model, chosen from 20 candidates.** Starting from part 1's model we added growth and seasonality, split price into shelf price and promotion depth, gave each channel its own memory and a diminishing-returns curve that works at zero spend, and kept repeat purchase. Forecast error on the last 26 weeks fell from 11.4% to 4.2%, and all residual checks now pass. [`model_comparison.md`, figure `model_ladder.png`, `fit_holdout.png`]

2. **What drives sales.** Over 2022–24: base including the minimum always-on media 17%, underlying growth 8%, price promotions 3%, influencers 30%, TikTok 16%, Instagram 15%, TV 7%, POS 5%. The parts add up to actual sales in every week, which part 1's did not (150–160%). [`step6_contributions_roi.md` §2, figure `decomposition.png`]

3. **The ranking of channels is clear and stable.** Revenue per £ above the floor: influencer 42.8, Instagram 18.6, TikTok 16.9, POS 3.7, TV 0.99. For the next £: 74.6, 30.8, 24.8, 5.5, 1.72. The order did not change in any of 20 model versions, 13 alternative curve and carry-over settings, an additive model, either half of the history, or after dropping the five most influential weeks. [`step6_contributions_roi.md` §1, `step5_robustness.md`, figure `roi.png`]

4. **TV does not earn its share.** It takes 39% of the media budget and delivers 7% of sales, about £1 of revenue per £. An extra £ of TV returns £1.72, which pays only at a gross margin above 58%. Part 1 made TV look worthless at the margin (£0.16) because of how weeks without TV were handled; treated properly it is weak, not worthless. [`step6_contributions_roi.md` §1 and §3]

5. **POS spend earns its keep; price promotions do not.** POS returns £3.7 per £ (pays above a margin of about 18–27%) and ranks fourth. Price promotions are a different matter: they added 6% to units and cost 3.7% of revenue, about £5.2m over three years. A 24% discount sells 17% more units and would need 32% more to hold revenue; no discount depth in the data pays for itself. [`step6_contributions_roi.md` §4, figure `promotions.png`]

6. **Effects last weeks, not months.** TV and influencer effects arrive 39% in the week of spend and 93% within four weeks; TikTok and POS work almost entirely in the week they run. On top, 36% of any week's uplift comes back the next week as repeat purchase. No extra synergy between channels was found beyond the general effect that everything works better when sales are high. [`step3_media.md`, `step4_synergies.md`]

7. **Demand is not very price-sensitive, but this is the weakest number.** A 1% higher shelf price costs about 0.8% of units in total, so a 5% increase would add about 1% revenue (range −0.8% to +3.1%). In pence: 5p more on today's £1.61 would cost about 16,000 units a week (8,000 to 24,000) and add about £7,000 of weekly revenue (range −£5,000 to +£19,000). The shelf price only ever rose, four times, so the range is wide. Expressing price effects per penny is Ketan's idea from part 1. [`step6_contributions_roi.md` §5]

8. **Recommendation: move budget from TV to influencers, Instagram and TikTok, as a measured first step.** TV −10% within its flights, the three social channels +10% each, POS and the total budget unchanged. This is about as far as the brand has ever held spend away from today's levels (the highest quarter of influencer spend on record is 11% above its average), so it is the largest step the data can support. [`step7_scenarios.md`, figure `allocation_main.png`]

9. **Quote the gain once, as an upper bound.** Replaying 2024 with the first-step plan, the model implies up to +£15m revenue (+30%); the codebook's "10% of TV to influencer" implies up to +£25m. These follow from the steep influencer and social slopes and are not forecasts. The conclusion is the direction, the ranking and the test, not the number. [`step7_scenarios.md`, figure `scenarios_main.png`]

10. **Run it as a test, then scale.** Raise influencer and social spend for a quarter, or in some regions, and compare with the model's prediction. Also test fewer or shallower price promotions. Scale further only on that evidence.

## For the "analytical steps" slide

- **Why revenue is never an explanatory variable.** Revenue is units × price, so it is the target in disguise: part 1 showed that a model with revenue on the right-hand side reaches R² = 1.000 and explains nothing (noted in Ketan's and Quentin's notebooks). We model units and derive revenue from units and price.
- **One change at a time.** Every extension was tested against the previous model on information criteria, forecast error on unseen weeks, residual checks and plausibility, and kept only if it passed all four.

## Magnitude check: do we believe the effect sizes?

Advertising elasticity is the % change in sales for 1% more spend. A meta-analysis of published estimates (Sethuraman, Tellis & Briesch 2011, *Journal of Marketing Research*) finds on average **0.12 short-term and 0.24 long-term**. Ours [`step8_magnitude_check.md`]:

| channel | short-term (week of spend) | long-term | long-term ÷ benchmark |
|---|---|---|---|
| TV | 0.05 | 0.12 | 0.5 |
| POS | 0.13 | 0.20 | 0.8 |
| TikTok | 0.35 | 0.54 | 2.2 |
| Instagram | 0.37 | 0.83 | 3.4 |
| Influencer | 0.64 | 1.67 | 7.0 |

**For the slide:** "TV and POS are in line with what the literature finds. Social is two to three times the benchmark and influencers seven times. That is why we recommend the direction with confidence and treat the size as something to test."

Possible explanations to name if asked: the data were built for teaching and need not be calibrated to real markets; spend is in £, not exposure, so changes in cost per contact are invisible; budgets may follow expected demand at monthly or quarterly horizons (our placebo test only rules this out week to week); and held spend levels moved by only 11–43% around their mean, so a slope measured on small movements is being extended by a curve.

## Why some response curves bend upwards

The model is multiplicative: each channel lifts sales by a percentage, and that percentage shows diminishing returns. But a given percentage of a larger sales base is more £, so in £ a curve can rise ever faster before it flattens. Only the influencer curve does this over its whole observed range (TV does at low sustained weights). Followed far outside the data, the formula would have influencers multiply sales several hundred times, which is the clearest sign that the curve must not be trusted beyond its range. This is the reason for the spend bounds in the scenarios and for the out-of-range warnings in the dashboard. [`step8_magnitude_check.md`, figure `response_curves.png`]

## Caveats for the limitations slide

- Returns are only observed between each channel's historical minimum and maximum spend, and for sustained levels in a much narrower band.
- Revenue ROI, not profit; break-even margins per channel are in `step6_contributions_roi.md`.
- Observational data: budgets set in anticipation of demand can inflate returns. Tested at weekly level (no evidence); slower planning effects cannot be ruled out.
- Intervals cover uncertainty in the coefficients only.
- Next steps: the controlled test above; a Bayesian marketing mix model with priors taken from such experiments (e.g. PyMC-Marketing or Meridian).

## Figures (`figures/`)

Main slides:

| file | shows | bullet |
|---|---|---|
| `model_ladder.png` | forecast error and fit from part 1's model to the final one | 1 |
| `fit_holdout.png` | actual vs fitted sales, with the 26 weeks the model had not seen | 1 |
| `decomposition.png` | sales by driver, per quarter | 2 |
| `roi.png` | revenue per £ and per next £, by channel, with ranges | 3, 4 |
| `promotions.png` | units and revenue effect of a promotion week by discount depth | 5 |
| `allocation_main.png` | budget per channel: 2024, the first-step plan, 10% of TV to influencer | 8 |
| `scenarios_main.png` | model-implied upper bound of the revenue change for the same three plans | 9 |
| `response_curves.png` | revenue against sustained weekly spend per channel, with the observed ranges | curve shape, limitations |

Appendix:

| file | shows |
|---|---|
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
| Forecast accuracy of the dashboard interface | `step8_interface_check.md` |
| What can we claim, what not, what would improve it? Profit view, test design | `step9_critical_review.md`, `step9_diagnostics.md` |
| How to call the model from the dashboard | `docs/part2/INTERFACE.md` |
| Every decision with its reason | `docs/part2/LOG.md` |
| The story with charts, runnable | `notebooks/02_model_extension.ipynb` |
