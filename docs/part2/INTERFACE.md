# Model interface for the dashboard (part 3)

For Quentin, Ketan and Paola. This is everything the dashboard needs from part 2: one module, `arla_mmm.interface`, and one model file, `models/arla_mmm_final.json`. You give it a weekly plan (spend per channel, shelf price, promotions) for the weeks after the data end; it returns units and revenue per week with uncertainty bands, what each channel adds, ROI, and warnings when a plan leaves what the data cover.

Nothing here is final: if an input or output is awkward for the app, tell Jakob and we change it.

## Setup

```bash
pip install -r requirements.txt
pip install -e .          # makes `arla_mmm` importable; run from the repo root
```

The model is already fitted and saved in the repo, so the app only loads it. Python ≥ 3.11.

## Minimal example

```python
from arla_mmm.interface import load_model, baseline_plan, scale_plan, shift_budget, forecast, compare_scenarios

model = load_model()                       # reads models/arla_mmm_final.json, a few milliseconds

base = baseline_plan(model, weeks=12)      # 12 weeks from 30 Dec 2024: same weeks a year earlier
test = scale_plan(base, {"tv": 0.9, "instagram": 1.1, "tiktok": 1.1, "influencer": 1.1})
tv_to_inf = shift_budget(base, "tv", "influencer", 0.10)        # the codebook's example

fc = forecast(model, test)                 # about 0.1 s
fc.weekly                                  # units and revenue per week: mean, p5, p50, p95
fc.channels                                # per channel: spend, incremental revenue, ROI with ranges
fc.warnings                                # sentences to show when the plan is out of range

table, forecasts = compare_scenarios(
    model, {"Current plan": base, "Shift 10%": test, "TV to influencer": tv_to_inf}, baseline="Current plan")
```

In Streamlit, wrap `load_model()` in `@st.cache_resource`. A forecast is fast enough to re-run on every slider move.

## Inputs

### The plan: one row per future week

A pandas DataFrame. Weeks follow directly after the last week of the history (the data end on Monday 23 Dec 2024, so the first plan week is 30 Dec 2024). Any length works; the brief asks for at least 12 weeks.

| column | required | meaning | if left out |
|---|---|---|---|
| `tv`, `instagram`, `tiktok`, `influencer`, `pos_promotion` | yes | spend in £ for that week | error |
| `regular_price` | no | shelf price in £ (the price without a promotion) | last observed shelf price, £1.61 |
| `promo_discount` | no | fraction off the shelf price that week; 0 = no promotion, 0.24 = 24% off | 0, or the historical average of 24% in weeks where `price_promo` is 1 |
| `price_promo` | no | 0/1 flag, only used when `promo_discount` is missing | no promotions |
| `week_beg` | no | Monday dates; if given they must be the consecutive weeks after the history | filled in |

The price paid is derived: `avg_price = regular_price × (1 − promo_discount)`. Price and promotion are two separate levers in the model (shelf-price elasticity, and a promotion lift followed by a small dip the week after), so the app should offer them as two controls, not as one average price.

`baseline_plan(model, weeks)` gives a sensible starting plan to edit: spend and promotions of the same weeks one year earlier, so it keeps the TV flight calendar. `scale_plan` and `shift_budget` are small helpers; the app can equally build the DataFrame itself from its input widgets.

### The history

`forecast(model, plan, history=None)`. By default the history is `data/arla_protein_mmm_weekly.csv`. It is needed because the effect of advertising carries over (spend in December still works in January) and because the model uses last week's sales. If new weeks of actual data arrive, pass the longer table as `history` (same columns as the CSV); the model does not need refitting for that.

### Options of `forecast`

| argument | default | meaning |
|---|---|---|
| `n_draws` | 1000 | number of simulations (up to 2000). 1000 is plenty for the 5/50/95% bands |
| `reference` | `"floor"` | what a channel's contribution is measured against, see "Contributions and ROI" |
| `parameter_uncertainty`, `residual_uncertainty` | both `True` | switch off either source of uncertainty; with both off you get one deterministic path |
| `seed` | fixed | keep it fixed so a scenario gives the same numbers every time |
| `tolerance` | 0 | ignore range excursions up to this fraction (e.g. 0.02) |

## Outputs

`forecast` returns a `Forecast` object with these parts.

**`weekly`**: one row per plan week. The inputs as used (`week_beg`, the five spend columns, `regular_price`, `promo_discount`, `avg_price`, `media_spend`) and `units_mean`, `units_p5`, `units_p50`, `units_p95`, `revenue_mean`, `revenue_p5`, `revenue_p50`, `revenue_p95`. Draw the line from `_p50` and the band from `_p5` to `_p95`.

**`contributions`**: one row per week and component (`base`, then the five channels), with the same eight unit and revenue columns plus `spend`. The `_mean` columns add up exactly to the weekly totals, so use them for stacked charts. `base` is what would be sold with every channel at its reference level; it includes trend, season, price, promotions, and what past spend still carries into the plan weeks.

**`channels`**: one row per channel over the whole horizon: `spend`, `reference_spend`, `spend_above_reference`, `incremental_units_*`, `incremental_revenue_*`, `roi_*` (each with mean, p5, p50, p95).

**`totals`**: the horizon in one row: `weeks`, `media_spend`, `units_*`, `revenue_*`. Use these for totals: the sum of the weekly p5 values is *not* the p5 of the total.

**`flags`** and **`warnings`**: see the next section.

**`plan`**, **`units_draws`**, **`revenue_draws`**: the completed plan and the raw simulations (simulations × weeks) in case you need a quantity that is not listed.

`compare_scenarios(model, plans, baseline)` takes a dict of named plans of equal length and returns `(table, forecasts)`. The table has one row per plan: `media_spend`, `delta_spend`, `units_*`, `revenue_*`, `delta_revenue_*` (against the baseline, with range), `delta_revenue_pct`, `delta_units_pct`, `revenue_per_media_pound`, `roi_vs_baseline` (extra revenue per extra £; empty when the budgets differ by less than 1%), `weeks_weekly_out`, `weeks_sustained_out`, `inputs_out_of_range`. `forecasts` is the dict of `Forecast` objects, so nothing has to be computed twice.

### Contributions and ROI

A channel's contribution is the revenue it adds above a reference level in the plan weeks, split fairly between channels (the model is multiplicative, so channels amplify each other). With `reference="floor"`, the default and the one used in all part-2 tables:

- TV is measured against no TV;
- Instagram, TikTok, influencer and POS are measured against their lowest weekly spend ever observed (£15.4k, £9.3k, £13.4k, £17.8k), because none of them was ever switched off, so "zero spend" is not something the data can speak about.

ROI = incremental revenue ÷ spend above the reference. It is a **revenue** ROI, not profit; margin is not in the data. `reference="zero"` is available but extrapolates heavily; we do not recommend showing it.

Effects that arrive after the last plan week are not counted, so the ROI of a short horizon is slightly understated (most of a channel's effect arrives within four weeks).

## Out-of-range flags: please show them prominently

The model is trustworthy inside the spend levels it has seen and not outside them, and the dashboard makes it very easy to leave them. `fc.flags` has one row per week and input (five channels, `regular_price`, `promo_discount`):

| column | meaning |
|---|---|
| `weekly_out` | that week's value is outside the range of single weeks in the data |
| `sustained_out` | channels only: the 13-week average ending in that week (history + plan) is outside the range of 13-week averages in the data |
| `sustained_excess_pct` | how far outside, in % (+ above the highest, − below the lowest level ever held) |
| `value`, `weekly_min`, `weekly_max`, `avg_13w`, `sustained_min`, `sustained_max` | the numbers behind the flags |

**`sustained_out` is the one that matters.** The model's long-run effects need a spend level to be held, and held levels have moved much less than single weeks:

| channel | single weeks observed, £ | 13-week averages observed, £ |
|---|---|---|
| TV | 0 – 376,150 | 0 – 126,654 |
| Instagram | 15,393 – 40,772 | 20,763 – 28,849 |
| TikTok | 9,332 – 33,776 | 15,103 – 26,379 |
| Influencer | 13,406 – 36,009 | 18,115 – 22,178 |
| POS | 17,791 – 52,942 | 26,676 – 35,330 |

So a plan that sets influencer spend to £30k in every week passes the weekly check and is still 35% above anything the brand has ever sustained. In that region the model answers with very large revenue gains that nobody should present as a forecast.

`fc.warnings` gives the flags as ready sentences, sustained-level warnings first, for example: *"influencer: the 13-week average spend is up to 17% above the highest level ever held in the data (8 of 12 weeks). The model has no evidence here; read the result as extrapolation."* An empty list means the plan is inside the data. Our suggestion: a red banner when any `sustained_out` is true, a quieter note for `weekly_out`, and grey out or caveat the revenue numbers of a flagged scenario.

## How good are the forecasts?

Back-test (`results/part2/step8_interface_check.md`): four 12-week forecasts in 2024, each from a model that had only seen the earlier weeks, given the spend, prices and promotions that actually followed.

- The median forecast is off by 4.0% on average and does not get worse towards week 12.
- 44 of the 48 actual weeks (92%) fall inside the 5–95% band. The band is about ±10% around the median.

Example output for the next 12 weeks: same file, and `results/part2/figures/forecast_example.png`.

## Known limits (worth a line in the app)

1. **The size of the social and influencer effects is not credible outside the observed range.** Within the data, influencer spend returns about £43 of revenue per £ and the next £ about £75; a 10% budget shift is credited with roughly +30% revenue. The ranking of channels is robust; the size is far above what published studies find (`results/part2/step8_magnitude_check.md`). Present scenario gains as "what the model implies", next to the flags.
2. **Why returns can seem to increase.** The model is multiplicative: each channel lifts sales by a percentage, and a percentage of a larger base is more £. For influencers this makes the £ response curve bend upwards over the whole observed range, so doubling the increase more than doubles the gain. This is a property of the formula outside its evidence, and the main reason for the flags.
3. **The bands cover two things only:** uncertainty in the estimated coefficients and normal week-to-week noise. They do not cover the risk of leaving the observed range (limit 1), and they hold the carry-over rates and curve shapes fixed (moving those changes any ROI by at most ±15%, `step5_robustness.md`).
4. **Growth is assumed to continue** at about 7% a year, and seasonality to repeat. Fine for 12–26 weeks; for a horizon beyond a year, say so.
5. **Shelf price is weakly identified.** It only ever rose, in four steps, between £1.34 and £1.61. The elasticity is −0.5 in the week and −0.8 in total, with a wide interval that includes no revenue gain from a price rise. Prices outside that range are flagged.
6. **Promotions lift units and lose revenue** at every discount depth in the data (up to 32% off). That is a finding, not a bug: a 24% discount would need +32% units to hold revenue and gets about +17%.
7. **TV is flighted.** The model has seen TV weeks at £0 or between £148k and £376k. A small TV spend in every week is inside the weekly range but is not a pattern the data contain.
8. **Revenue, not profit.** Break-even margins per channel are in `step6_contributions_roi.md` if the app wants a margin slider.

## Reproducing and refitting

```bash
python scripts/run_part2.py       # model comparison, about 5 minutes
python scripts/run_insights.py    # ROI, decomposition, 2024 scenarios, figures
python scripts/run_interface.py   # saves models/arla_mmm_final.json, back-test, magnitude check
pytest                            # 25 tests; one fails if the saved model is out of date
```

To refit on new data, `fit_model(new_data)` followed by `save_model(model)`; `fit_model` re-selects the carry-over rates and fits the same specification. The model file is plain JSON (coefficients, their covariance, residual spread, the observed ranges), so it can be read without our code.

What the model is and why: `results/part2/SUMMARY.md`; the full reasoning, step by step: `docs/part2/LOG.md`.
