# M14_hill

Hill curve; TV scale tuned, always-on scale fixed at mean spend; decay per channel; lagged sales = step-3 model

n = 155, parameters = 22, R² = 0.977, AIC = -497.3, BIC = -430.3

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3729 | 0.2297 | 0.2059 | 0.0000 |
| lagged_sales | 0.3564 | 0.0173 | 0.0141 | 0.0000 |
| regular_price | -0.4906 | 0.1821 | 0.1588 | 0.0020 |
| promo_depth | 0.4490 | 0.0327 | 0.0279 | 0.0000 |
| promo_depth_lag1 | -0.0613 | 0.0310 | 0.0251 | 0.0145 |
| trend | 0.0719 | 0.0139 | 0.0127 | 0.0000 |
| season_sin1 | -0.0015 | 0.0056 | 0.0049 | 0.7586 |
| season_cos1 | -0.0458 | 0.0069 | 0.0079 | 0.0000 |
| season_sin2 | 0.0198 | 0.0055 | 0.0055 | 0.0003 |
| season_cos2 | -0.0126 | 0.0060 | 0.0060 | 0.0356 |
| january | 0.0533 | 0.0190 | 0.0196 | 0.0066 |
| tv | 1.3968 | 0.0627 | 0.0520 | 0.0000 |
| instagram | 2.1472 | 0.1163 | 0.1388 | 0.0000 |
| tiktok | 1.4124 | 0.0731 | 0.0735 | 0.0000 |
| influencer | 4.3152 | 0.1473 | 0.1162 | 0.0000 |
| pos_promotion | 0.5275 | 0.0732 | 0.0751 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.308 | 0.366 | -0.571 | 0.439 | -0.062 | 0.083 | -0.002 | -0.051 | 0.022 | -0.015 | 0.063 | 1.422 | 2.276 | 1.379 | 4.109 | 0.556 |
| train<117 | 4.336 | 0.363 | -0.589 | 0.451 | -0.049 | 0.085 | -0.001 | -0.048 | 0.024 | -0.015 | 0.048 | 1.424 | 2.251 | 1.414 | 4.188 | 0.501 |
| train<130 | 4.395 | 0.352 | -0.479 | 0.423 | -0.042 | 0.077 | 0.000 | -0.054 | 0.024 | -0.011 | 0.058 | 1.375 | 2.291 | 1.357 | 4.307 | 0.506 |
| train<143 | 4.358 | 0.358 | -0.452 | 0.429 | -0.053 | 0.069 | 0.000 | -0.045 | 0.020 | -0.011 | 0.051 | 1.396 | 2.136 | 1.386 | 4.321 | 0.535 |
| full | 4.373 | 0.356 | -0.491 | 0.449 | -0.061 | 0.072 | -0.001 | -0.046 | 0.020 | -0.013 | 0.053 | 1.397 | 2.147 | 1.412 | 4.315 | 0.528 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| train<117 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| train<130 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| train<143 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| full | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |

Scale of the saturation curve, £ per week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 936,585 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<117 | 936,585 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<130 | 936,585 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<143 | 936,585 | 23,077 | 18,462 | 20,000 | 30,769 |
| full | 936,585 | 23,077 | 18,462 | 20,000 | 30,769 |

Likelihood profiles: AIC penalty for moving one parameter away from its best value, others held (0 = best; below about 2 = the data cannot tell the values apart).

| decay value → | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|---|
| decay tv | 55.0 | 38.2 | 22.1 | 8.3 | 0.0 | 3.2 | 27.4 | 82.9 | 163.0 | 220.7 |
| decay instagram | 21.6 | 9.1 | 1.3 | 0.0 | 7.1 | 23.3 | 48.2 | 80.0 | 116.5 | 153.4 |
| decay tiktok | 0.0 | 5.8 | 18.2 | 35.7 | 57.2 | 81.6 | 108.3 | 136.7 | 165.6 | 190.5 |
| decay influencer | 96.6 | 63.8 | 33.4 | 9.9 | 0.0 | 11.7 | 49.6 | 110.3 | 182.2 | 249.7 |
| decay pos_promotion | 0.0 | 3.0 | 6.3 | 10.0 | 14.2 | 19.2 | 25.0 | 31.6 | 38.6 | 46.2 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 60.2 | 31.1 | 11.9 | 2.8 | 0.0 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.9 | 12 |
| 3 | -0.1 | 12 |
| 4 | -2.6 | 13 |
| 5 | 0.3 | 14 |
| 6 | 1.6 | 12 |
| 7 | 0.3 | 14 |
| 8 | -1.3 | 13 |
| 9 | 0.1 | 13 |
| 10 | 1.0 | 14 |
| 11 | 0.8 | 12 |
| 12 | -2.8 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 20.8% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.1 | 9,257,134 | 0.99 | 1.78 | 1.72 |
| instagram | 15,393 | 1,192,415 | 16.4 | 22,159,724 | 18.58 | 30.80 | 30.82 |
| tiktok | 9,332 | 1,415,019 | 17.7 | 23,919,763 | 16.90 | 27.91 | 24.80 |
| influencer | 13,406 | 1,021,938 | 32.5 | 43,749,715 | 42.81 | 63.70 | 74.55 |
| pos_promotion | 17,791 | 2,008,661 | 5.6 | 7,365,099 | 3.67 | 6.64 | 5.47 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.6 | 4,661,859 | 0.50 | 1.78 |
| instagram | 0 | 3,578,330 | 28.1 | 37,885,668 | 10.59 | 30.37 |
| tiktok | 0 | 2,861,479 | 21.6 | 29,168,437 | 10.19 | 31.07 |
| influencer | 0 | 3,099,868 | 36.7 | 49,473,830 | 15.96 | 41.87 |
| pos_promotion | 0 | 4,766,266 | 9.8 | 13,207,282 | 2.77 | 9.37 |
