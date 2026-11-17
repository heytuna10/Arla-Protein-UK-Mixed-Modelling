# M9_adstock_lag

M8 plus lagged sales (ad memory + repeat purchase)

n = 155, parameters = 21, R² = 0.975, AIC = -485.6, BIC = -421.6

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 5.7974 | 0.2360 | 0.2161 | 0.0000 |
| lagged_sales | 0.3511 | 0.0181 | 0.0144 | 0.0000 |
| regular_price | -0.6072 | 0.1918 | 0.1579 | 0.0001 |
| promo_depth | 0.4533 | 0.0342 | 0.0296 | 0.0000 |
| promo_depth_lag1 | -0.0551 | 0.0324 | 0.0262 | 0.0353 |
| trend | 0.0806 | 0.0146 | 0.0132 | 0.0000 |
| season_sin1 | -0.0011 | 0.0058 | 0.0051 | 0.8360 |
| season_cos1 | -0.0419 | 0.0073 | 0.0084 | 0.0000 |
| season_sin2 | 0.0203 | 0.0058 | 0.0059 | 0.0006 |
| season_cos2 | -0.0132 | 0.0063 | 0.0064 | 0.0396 |
| january | 0.0517 | 0.0199 | 0.0209 | 0.0135 |
| tv | 0.4090 | 0.0189 | 0.0153 | 0.0000 |
| instagram | 1.0636 | 0.0595 | 0.0709 | 0.0000 |
| tiktok | 0.7069 | 0.0382 | 0.0430 | 0.0000 |
| influencer | 2.1177 | 0.0753 | 0.0590 | 0.0000 |
| pos_promotion | 0.2445 | 0.0379 | 0.0418 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 5.837 | 0.324 | -0.518 | 0.434 | -0.045 | 0.081 | -0.004 | -0.053 | 0.025 | -0.012 | 0.064 | 0.428 | 1.170 | 0.683 | 2.425 | 0.262 |
| train<117 | 5.695 | 0.360 | -0.727 | 0.453 | -0.043 | 0.096 | -0.001 | -0.045 | 0.024 | -0.018 | 0.047 | 0.418 | 1.114 | 0.705 | 2.092 | 0.229 |
| train<130 | 5.783 | 0.350 | -0.610 | 0.427 | -0.036 | 0.087 | -0.001 | -0.051 | 0.025 | -0.013 | 0.056 | 0.404 | 1.134 | 0.671 | 2.124 | 0.232 |
| train<143 | 5.748 | 0.355 | -0.563 | 0.436 | -0.049 | 0.077 | 0.000 | -0.042 | 0.020 | -0.012 | 0.050 | 0.408 | 1.057 | 0.689 | 2.120 | 0.246 |
| full | 5.797 | 0.351 | -0.607 | 0.453 | -0.055 | 0.081 | -0.001 | -0.042 | 0.020 | -0.013 | 0.052 | 0.409 | 1.064 | 0.707 | 2.118 | 0.244 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.4 | 0.3 | 0.0 | 0.5 | 0.0 |
| train<117 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| train<130 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| train<143 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| full | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |

Scale of the saturation curve, £ per week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<117 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<130 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<143 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| full | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |

Likelihood profiles: AIC penalty for moving one parameter away from its best value, others held (0 = best; below about 2 = the data cannot tell the values apart).

| decay value → | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|---|
| decay tv | 46.0 | 29.6 | 15.1 | 4.3 | 0.0 | 7.2 | 33.1 | 85.3 | 158.9 | 214.0 |
| decay instagram | 19.5 | 8.1 | 1.0 | 0.0 | 6.6 | 21.7 | 44.7 | 74.6 | 109.5 | 146.2 |
| decay tiktok | 0.0 | 4.7 | 15.4 | 31.2 | 50.9 | 73.9 | 99.4 | 127.1 | 155.6 | 180.7 |
| decay influencer | 93.2 | 62.9 | 34.4 | 11.3 | 0.0 | 8.1 | 41.1 | 97.4 | 167.1 | 235.6 |
| decay pos_promotion | 0.0 | 2.8 | 5.7 | 8.9 | 12.5 | 16.5 | 21.1 | 26.3 | 31.9 | 38.2 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.6 | 12 |
| 3 | 0.3 | 12 |
| 4 | -2.8 | 13 |
| 5 | 0.0 | 14 |
| 6 | 1.8 | 12 |
| 7 | 0.4 | 14 |
| 8 | -1.4 | 13 |
| 9 | -0.1 | 13 |
| 10 | 1.3 | 14 |
| 11 | 0.5 | 12 |
| 12 | -2.6 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 24.3% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.7 | 10,050,026 | 1.08 | 1.84 | 1.63 |
| instagram | 15,393 | 1,192,415 | 15.7 | 21,227,955 | 17.80 | 28.26 | 31.02 |
| tiktok | 9,332 | 1,415,019 | 16.4 | 22,159,302 | 15.66 | 24.91 | 25.41 |
| influencer | 13,406 | 1,021,938 | 31.0 | 41,834,842 | 40.94 | 58.91 | 74.98 |
| pos_promotion | 17,791 | 2,008,661 | 4.9 | 6,480,719 | 3.23 | 5.60 | 5.17 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 1.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 4.3 | 5,611,261 | 0.60 | 1.84 |
| instagram | 0 | 3,578,330 | 26.7 | 36,081,108 | 10.08 | 25.36 |
| tiktok | 0 | 2,861,479 | 19.6 | 26,400,335 | 9.23 | 24.76 |
| influencer | 0 | 3,099,868 | 40.6 | 54,705,514 | 17.65 | 38.88 |
| pos_promotion | 0 | 4,766,266 | 7.7 | 10,318,281 | 2.16 | 6.43 |
