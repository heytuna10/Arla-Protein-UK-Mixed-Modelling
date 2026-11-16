# M6_adstock_1decay

M5 controls, no lagged sales; adstock with one decay for all channels; log curve

n = 155, parameters = 16, R² = 0.953, AIC = -398.0, BIC = -349.3

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 8.4509 | 0.1726 | 0.1705 | 0.0000 |
| regular_price | -1.0506 | 0.3110 | 0.3256 | 0.0013 |
| promo_depth | 0.4560 | 0.0438 | 0.0368 | 0.0000 |
| promo_depth_lag1 | 0.0800 | 0.0415 | 0.0348 | 0.0216 |
| trend | 0.1337 | 0.0237 | 0.0268 | 0.0000 |
| season_sin1 | -0.0068 | 0.0081 | 0.0098 | 0.4857 |
| season_cos1 | -0.0511 | 0.0109 | 0.0109 | 0.0000 |
| season_sin2 | 0.0247 | 0.0079 | 0.0101 | 0.0147 |
| season_cos2 | -0.0264 | 0.0094 | 0.0119 | 0.0268 |
| january | 0.0416 | 0.0276 | 0.0281 | 0.1385 |
| tv | 0.6783 | 0.0312 | 0.0337 | 0.0000 |
| instagram | 1.8350 | 0.1140 | 0.1461 | 0.0000 |
| tiktok | 1.2874 | 0.1033 | 0.1199 | 0.0000 |
| influencer | 3.4492 | 0.1326 | 0.1187 | 0.0000 |
| pos_promotion | 0.5153 | 0.0990 | 0.0969 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 8.537 | -1.601 | 0.444 | 0.089 | 0.185 | -0.013 | -0.059 | 0.017 | -0.047 | 0.059 | 0.732 | 2.008 | 1.362 | 3.282 | 0.510 |
| train<117 | 8.568 | -1.616 | 0.430 | 0.123 | 0.191 | -0.009 | -0.055 | 0.021 | -0.047 | 0.040 | 0.732 | 1.977 | 1.344 | 3.281 | 0.515 |
| train<130 | 8.435 | -1.175 | 0.411 | 0.091 | 0.152 | -0.010 | -0.059 | 0.027 | -0.033 | 0.044 | 0.699 | 1.947 | 1.244 | 3.446 | 0.512 |
| train<143 | 8.451 | -1.008 | 0.432 | 0.087 | 0.131 | -0.007 | -0.052 | 0.024 | -0.027 | 0.043 | 0.679 | 1.825 | 1.260 | 3.459 | 0.526 |
| full | 8.451 | -1.051 | 0.456 | 0.080 | 0.134 | -0.007 | -0.051 | 0.025 | -0.026 | 0.042 | 0.678 | 1.835 | 1.287 | 3.449 | 0.515 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 |
| train<117 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 |
| train<130 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 |
| train<143 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 |
| full | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 |

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
| decay tv+instagram+tiktok+influencer+pos_promotion | 268.5 | 235.4 | 194.7 | 144.1 | 82.5 | 18.6 | 0.0 | 79.0 | 202.7 | 313.7 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.1 | 51 |
| 2023 | 0.1 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.4 | 12 |
| 3 | 0.1 | 12 |
| 4 | -2.9 | 13 |
| 5 | -0.8 | 14 |
| 6 | 2.2 | 12 |
| 7 | 1.7 | 14 |
| 8 | -3.4 | 13 |
| 9 | 0.7 | 13 |
| 10 | 1.8 | 14 |
| 11 | 0.0 | 12 |
| 12 | -1.9 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 20.0% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 8.2 | 10,756,095 | 1.16 | 2.09 | 1.94 |
| instagram | 15,393 | 1,192,415 | 16.5 | 22,320,937 | 18.72 | 31.38 | 35.11 |
| tiktok | 9,332 | 1,415,019 | 18.3 | 24,687,442 | 17.45 | 29.08 | 30.50 |
| influencer | 13,406 | 1,021,938 | 30.6 | 41,205,448 | 40.32 | 61.55 | 80.00 |
| pos_promotion | 17,791 | 2,008,661 | 6.4 | 8,495,252 | 4.23 | 7.70 | 7.18 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.6% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 4.6 | 5,952,758 | 0.64 | 2.09 |
| instagram | 0 | 3,578,330 | 26.7 | 35,972,583 | 10.05 | 26.98 |
| tiktok | 0 | 2,861,479 | 20.8 | 28,006,794 | 9.79 | 27.75 |
| influencer | 0 | 3,099,868 | 37.7 | 50,866,444 | 16.41 | 39.48 |
| pos_promotion | 0 | 4,766,266 | 9.6 | 12,941,897 | 2.72 | 8.48 |
