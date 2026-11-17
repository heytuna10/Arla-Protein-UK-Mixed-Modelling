# M10_log_scales

M9 with log curve, scale tuned (TV; always-on shared)

n = 155, parameters = 23, R² = 0.977, AIC = -492.7, BIC = -422.7

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3661 | 0.2311 | 0.2114 | 0.0000 |
| lagged_sales | 0.3580 | 0.0174 | 0.0143 | 0.0000 |
| regular_price | -0.5143 | 0.1840 | 0.1574 | 0.0011 |
| promo_depth | 0.4529 | 0.0330 | 0.0291 | 0.0000 |
| promo_depth_lag1 | -0.0602 | 0.0313 | 0.0253 | 0.0175 |
| trend | 0.0734 | 0.0140 | 0.0128 | 0.0000 |
| season_sin1 | -0.0018 | 0.0056 | 0.0049 | 0.7144 |
| season_cos1 | -0.0457 | 0.0070 | 0.0081 | 0.0000 |
| season_sin2 | 0.0199 | 0.0056 | 0.0056 | 0.0004 |
| season_cos2 | -0.0127 | 0.0061 | 0.0061 | 0.0372 |
| january | 0.0549 | 0.0191 | 0.0199 | 0.0059 |
| tv | 1.2634 | 0.0567 | 0.0468 | 0.0000 |
| instagram | 0.6667 | 0.0363 | 0.0433 | 0.0000 |
| tiktok | 0.4375 | 0.0229 | 0.0242 | 0.0000 |
| influencer | 1.3385 | 0.0460 | 0.0350 | 0.0000 |
| pos_promotion | 0.1606 | 0.0229 | 0.0243 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.286 | 0.367 | -0.606 | 0.441 | -0.061 | 0.086 | -0.003 | -0.051 | 0.022 | -0.017 | 0.065 | 1.293 | 0.707 | 0.428 | 1.290 | 0.170 |
| train<117 | 4.310 | 0.364 | -0.627 | 0.453 | -0.047 | 0.088 | -0.002 | -0.048 | 0.024 | -0.016 | 0.049 | 1.296 | 0.699 | 0.438 | 1.310 | 0.152 |
| train<130 | 4.378 | 0.354 | -0.515 | 0.425 | -0.040 | 0.080 | -0.001 | -0.054 | 0.025 | -0.012 | 0.059 | 1.250 | 0.712 | 0.418 | 1.339 | 0.155 |
| train<143 | 4.346 | 0.360 | -0.470 | 0.432 | -0.052 | 0.070 | -0.001 | -0.045 | 0.020 | -0.011 | 0.053 | 1.263 | 0.663 | 0.429 | 1.340 | 0.163 |
| full | 4.366 | 0.358 | -0.514 | 0.453 | -0.060 | 0.073 | -0.002 | -0.046 | 0.020 | -0.013 | 0.055 | 1.263 | 0.667 | 0.438 | 1.338 | 0.161 |

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
| train<104 | 936,585 | 5,769 | 4,615 | 5,000 | 7,692 |
| train<117 | 936,585 | 5,769 | 4,615 | 5,000 | 7,692 |
| train<130 | 936,585 | 5,769 | 4,615 | 5,000 | 7,692 |
| train<143 | 936,585 | 5,769 | 4,615 | 5,000 | 7,692 |
| full | 936,585 | 5,769 | 4,615 | 5,000 | 7,692 |

Likelihood profiles: AIC penalty for moving one parameter away from its best value, others held (0 = best; below about 2 = the data cannot tell the values apart).

| decay value → | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|---|
| decay tv | 52.8 | 36.6 | 21.0 | 7.7 | 0.0 | 4.3 | 30.3 | 88.0 | 168.1 | 222.1 |
| decay instagram | 21.4 | 9.1 | 1.3 | 0.0 | 6.9 | 22.9 | 47.3 | 78.6 | 114.7 | 151.9 |
| decay tiktok | 0.0 | 6.2 | 18.7 | 36.1 | 57.3 | 81.2 | 107.3 | 135.0 | 163.1 | 187.5 |
| decay influencer | 96.7 | 64.5 | 34.3 | 10.5 | 0.0 | 10.7 | 47.5 | 107.2 | 178.8 | 246.9 |
| decay pos_promotion | 0.0 | 3.0 | 6.3 | 10.0 | 14.2 | 19.2 | 24.8 | 31.1 | 37.6 | 44.4 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 15.6 | 6.6 | 1.9 | 0.2 | 0.0 |
| scale instagram+tiktok+influencer+pos_promotion | 0.0 | 3.6 | 9.4 | 16.7 | 23.5 |

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
| 3 | 0.0 | 12 |
| 4 | -2.7 | 13 |
| 5 | 0.2 | 14 |
| 6 | 1.8 | 12 |
| 7 | 0.3 | 14 |
| 8 | -1.6 | 13 |
| 9 | 0.2 | 13 |
| 10 | 1.1 | 14 |
| 11 | 0.6 | 12 |
| 12 | -2.7 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 21.9% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.1 | 9,290,283 | 1.00 | 1.76 | 1.87 |
| instagram | 15,393 | 1,192,415 | 16.2 | 21,889,762 | 18.36 | 29.98 | 31.06 |
| tiktok | 9,332 | 1,415,019 | 17.3 | 23,385,578 | 16.53 | 26.94 | 25.08 |
| influencer | 13,406 | 1,021,938 | 32.1 | 43,269,696 | 42.34 | 62.25 | 75.31 |
| pos_promotion | 17,791 | 2,008,661 | 5.4 | 7,111,431 | 3.54 | 6.32 | 5.43 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.5 | 4,606,421 | 0.49 | 1.76 |
| instagram | 0 | 3,578,330 | 28.2 | 37,976,146 | 10.61 | 30.40 |
| tiktok | 0 | 2,861,479 | 21.7 | 29,238,176 | 10.22 | 31.11 |
| influencer | 0 | 3,099,868 | 36.8 | 49,535,206 | 15.98 | 41.88 |
| pos_promotion | 0 | 4,766,266 | 9.7 | 13,041,874 | 2.74 | 9.26 |
