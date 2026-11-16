# M4_postpromo

M3 + last week's promo depth (post-promotion dip)

n = 155, parameters = 15, R² = 0.955, AIC = -406.9, BIC = -361.2

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | -9.3107 | 0.6190 | 0.4394 | 0.0000 |
| lagged_sales | 0.5923 | 0.0215 | 0.0195 | 0.0000 |
| regular_price | -0.7567 | 0.2519 | 0.2047 | 0.0002 |
| promo_depth | 0.4663 | 0.0452 | 0.0442 | 0.0000 |
| promo_depth_lag1 | -0.2035 | 0.0421 | 0.0352 | 0.0000 |
| trend | 0.0763 | 0.0190 | 0.0154 | 0.0000 |
| season_sin1 | -0.0011 | 0.0076 | 0.0055 | 0.8457 |
| season_cos1 | -0.0146 | 0.0077 | 0.0062 | 0.0196 |
| season_sin2 | 0.0153 | 0.0073 | 0.0051 | 0.0028 |
| season_cos2 | -0.0162 | 0.0075 | 0.0058 | 0.0053 |
| tv | 0.0167 | 0.0010 | 0.0010 | 0.0000 |
| instagram | 0.3574 | 0.0301 | 0.0263 | 0.0000 |
| tiktok | 0.3367 | 0.0252 | 0.0230 | 0.0000 |
| influencer | 0.6785 | 0.0332 | 0.0237 | 0.0000 |
| pos_promotion | 0.1225 | 0.0250 | 0.0216 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | -9.288 | 0.605 | -0.823 | 0.427 | -0.175 | 0.081 | -0.003 | -0.013 | 0.013 | -0.018 | 0.017 | 0.363 | 0.329 | 0.650 | 0.137 |
| train<117 | -9.344 | 0.597 | -0.948 | 0.459 | -0.159 | 0.095 | -0.002 | -0.012 | 0.012 | -0.019 | 0.017 | 0.360 | 0.340 | 0.673 | 0.125 |
| train<130 | -9.473 | 0.588 | -0.836 | 0.424 | -0.175 | 0.085 | -0.001 | -0.013 | 0.014 | -0.016 | 0.017 | 0.368 | 0.335 | 0.689 | 0.126 |
| train<143 | -9.387 | 0.587 | -0.806 | 0.426 | -0.182 | 0.082 | 0.000 | -0.012 | 0.013 | -0.014 | 0.017 | 0.357 | 0.336 | 0.683 | 0.134 |
| full | -9.311 | 0.592 | -0.757 | 0.466 | -0.204 | 0.076 | -0.001 | -0.015 | 0.015 | -0.016 | 0.017 | 0.357 | 0.337 | 0.679 | 0.122 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.2 | 52 |
| 2024 | 0.2 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 2.7 | 14 |
| 2 | 0.4 | 12 |
| 3 | -0.3 | 12 |
| 4 | -1.1 | 13 |
| 5 | 0.3 | 14 |
| 6 | -0.5 | 12 |
| 7 | 0.6 | 14 |
| 8 | 0.2 | 13 |
| 9 | 0.0 | 13 |
| 10 | 0.9 | 14 |
| 11 | -0.4 | 12 |
| 12 | -3.4 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 16.2% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.0 | 9,212,228 | 0.99 | 1.91 |
| instagram | 15,393 | 1,192,415 | 15.7 | 21,189,288 | 17.77 | 31.96 |
| tiktok | 9,332 | 1,415,019 | 24.4 | 33,005,727 | 23.33 | 39.54 |
| influencer | 13,406 | 1,021,938 | 29.1 | 39,277,488 | 38.43 | 62.88 |
| pos_promotion | 17,791 | 2,008,661 | 7.5 | 10,022,253 | 4.99 | 9.63 |

## Sensitivity – reference: zero spend for every channel

Base = 0.0% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 2.7 | 3,604,116 | 0.39 | 1.91 |
| instagram | 0 | 3,578,330 | 24.7 | 33,262,546 | 9.30 | 37.60 |
| tiktok | 0 | 2,861,479 | 24.7 | 33,251,084 | 11.62 | 47.00 |
| influencer | 0 | 3,099,868 | 24.7 | 33,278,927 | 10.74 | 43.42 |
| pos_promotion | 0 | 4,766,266 | 23.2 | 31,188,518 | 6.54 | 26.88 |
