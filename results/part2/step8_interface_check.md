# Step 8 – forecast interface: back-test and example output

Model file: `models/arla_mmm_final.json` (M14, fitted on 155 weeks to 2024-12-23). How to call it: `docs/part2/INTERFACE.md`.

## Back-test: 12-week forecasts from four starting points

For each starting week the model was re-tuned and re-fitted on the earlier weeks only, then asked for the next 12 weeks given the spend, prices and promotions that actually followed. No information from the forecast weeks is used.

| forecast starts | median-forecast error %, mean over 12 weeks | worst week % | actual inside the 5–95% band, weeks of 12 |
|---|---|---|---|
| 2024-01-01 | 3.36 | 8.64 | 12 |
| 2024-04-01 | 3.90 | 9.55 | 11 |
| 2024-07-01 | 6.38 | 19.25 | 9 |
| 2024-09-30 | 2.26 | 6.13 | 12 |
| all four | 3.97 | 19.25 | 44 |

- The median forecast is off by 4.0% on average, with no sign of getting worse towards week 12.
- 92% of the 48 actual weeks fall inside the 5–95% band (90% would be ideal), so the bands are honest for plans like the ones seen so far. The band is about ±10% around the median in every week.
- This says nothing about plans that leave the observed spend range; those are covered by the flags, not by the band.

## Example: the next 12 weeks (2024-12-30 to 2025-03-17)

`baseline_plan` = spend and promotions of the same weeks a year earlier, shelf price as in the last observed week. Chart: `figures/forecast_example.png`.

| scenario | media spend £m | revenue £m, median (5–95%) | Δ revenue £m (5–95%) | weeks with a sustained-level flag | inputs out of range |
|---|---|---|---|---|---|
| Current plan | 1.88 | 11.5 (11.0–12.0) | 0.0 (0.0–0.0) | 0 | none |
| TV −10%, social and influencer +10% | 1.88 | 14.7 (14.1–15.4) | 3.3 (3.0–3.5) | 0 | none |
| 10% of TV moved to influencer | 1.88 | 16.9 (16.2–17.6) | 5.4 (5.1–5.8) | 8 | influencer |

The gains have the same character as in step 7 (large, because the influencer and social slopes are steep): show them as what the model implies, next to the flags.

Channel view for the current plan (what `Forecast.channels` returns):

| channel | spend £k | spend above floor £k | incremental revenue £k (5–95%) | ROI above floor (5–95%) |
|---|---|---|---|---|
| TV | 748 | 748 | 882 (804–957) | 1.2 (1.1–1.3) |
| Instagram | 264 | 80 | 1,646 (1,448–1,836) | 20.7 (18.2–23.1) |
| TikTok | 209 | 97 | 1,923 (1,742–2,112) | 19.8 (17.9–21.8) |
| Influencer | 244 | 83 | 3,405 (3,241–3,579) | 41.2 (39.2–43.3) |
| POS | 419 | 205 | 773 (599–933) | 3.8 (2.9–4.5) |

Warnings returned for "10% of TV moved to influencer":

- influencer: the 13-week average spend is up to 17% above the highest level ever held in the data (8 of 12 weeks). The model has no evidence here; read the result as extrapolation.
- influencer: 1 week(s) outside the range of single weeks in the data (13,406 to 36,009).
