# M5_january

M4 + January dummy = step-2 controls

n = 155, parameters = 16, R² = 0.957, AIC = -412.1, BIC = -363.4

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | -9.2666 | 0.6072 | 0.4209 | 0.0000 |
| lagged_sales | 0.5810 | 0.0215 | 0.0199 | 0.0000 |
| regular_price | -0.7846 | 0.2473 | 0.2021 | 0.0001 |
| promo_depth | 0.4514 | 0.0447 | 0.0407 | 0.0000 |
| promo_depth_lag1 | -0.2050 | 0.0413 | 0.0347 | 0.0000 |
| trend | 0.0803 | 0.0187 | 0.0149 | 0.0000 |
| season_sin1 | -0.0034 | 0.0075 | 0.0055 | 0.5323 |
| season_cos1 | -0.0274 | 0.0091 | 0.0069 | 0.0001 |
| season_sin2 | 0.0091 | 0.0076 | 0.0057 | 0.1131 |
| season_cos2 | -0.0251 | 0.0082 | 0.0064 | 0.0001 |
| january | 0.0654 | 0.0254 | 0.0230 | 0.0045 |
| tv | 0.0157 | 0.0010 | 0.0008 | 0.0000 |
| instagram | 0.3594 | 0.0295 | 0.0263 | 0.0000 |
| tiktok | 0.3379 | 0.0247 | 0.0227 | 0.0000 |
| influencer | 0.6775 | 0.0326 | 0.0231 | 0.0000 |
| pos_promotion | 0.1311 | 0.0247 | 0.0232 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | -9.262 | 0.591 | -0.891 | 0.427 | -0.167 | 0.091 | -0.004 | -0.026 | 0.008 | -0.027 | 0.066 | 0.016 | 0.370 | 0.330 | 0.650 | 0.145 |
| train<117 | -9.332 | 0.583 | -0.939 | 0.441 | -0.158 | 0.095 | -0.004 | -0.025 | 0.007 | -0.027 | 0.060 | 0.016 | 0.368 | 0.339 | 0.672 | 0.133 |
| train<130 | -9.452 | 0.576 | -0.846 | 0.410 | -0.176 | 0.087 | -0.004 | -0.027 | 0.009 | -0.026 | 0.065 | 0.016 | 0.376 | 0.335 | 0.686 | 0.136 |
| train<143 | -9.362 | 0.576 | -0.818 | 0.413 | -0.183 | 0.084 | -0.003 | -0.026 | 0.007 | -0.024 | 0.065 | 0.016 | 0.361 | 0.337 | 0.681 | 0.143 |
| full | -9.267 | 0.581 | -0.785 | 0.451 | -0.205 | 0.080 | -0.003 | -0.027 | 0.009 | -0.025 | 0.065 | 0.016 | 0.359 | 0.338 | 0.677 | 0.131 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.2 | 51 |
| 2023 | 0.2 | 52 |
| 2024 | 0.1 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.3 | 12 |
| 3 | -0.2 | 12 |
| 4 | -1.0 | 13 |
| 5 | -0.6 | 14 |
| 6 | 0.0 | 12 |
| 7 | 1.0 | 14 |
| 8 | -0.3 | 13 |
| 9 | 0.3 | 13 |
| 10 | 0.5 | 14 |
| 11 | -0.2 | 12 |
| 12 | -1.8 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 16.9% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.6 | 8,584,210 | 0.92 | 1.77 | 0.16 |
| instagram | 15,393 | 1,192,415 | 15.5 | 21,034,086 | 17.64 | 31.39 | 31.70 |
| tiktok | 9,332 | 1,415,019 | 24.3 | 32,754,306 | 23.15 | 38.85 | 37.18 |
| influencer | 13,406 | 1,021,938 | 28.8 | 38,836,002 | 38.00 | 61.65 | 71.57 |
| pos_promotion | 17,791 | 2,008,661 | 7.9 | 10,566,931 | 5.26 | 10.00 | 8.46 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.0% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 2.5 | 3,326,690 | 0.36 | 1.77 |
| instagram | 0 | 3,578,330 | 24.7 | 33,270,172 | 9.30 | 37.60 |
| tiktok | 0 | 2,861,479 | 24.7 | 33,257,275 | 11.62 | 47.00 |
| influencer | 0 | 3,099,868 | 24.7 | 33,287,730 | 10.74 | 43.42 |
| pos_promotion | 0 | 4,766,266 | 23.3 | 31,443,324 | 6.60 | 27.04 |
