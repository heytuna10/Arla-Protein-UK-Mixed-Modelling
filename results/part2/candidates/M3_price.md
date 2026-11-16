# M3_price

M2 with regular price + promo depth instead of average price + promo flag

n = 155, parameters = 14, R² = 0.947, AIC = -384.9, BIC = -342.3

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | -8.9816 | 0.6623 | 0.5053 | 0.0000 |
| lagged_sales | 0.5470 | 0.0209 | 0.0193 | 0.0000 |
| regular_price | -0.6744 | 0.2706 | 0.2061 | 0.0011 |
| promo_depth | 0.4790 | 0.0486 | 0.0510 | 0.0000 |
| trend | 0.0708 | 0.0205 | 0.0150 | 0.0000 |
| season_sin1 | -0.0022 | 0.0082 | 0.0064 | 0.7252 |
| season_cos1 | -0.0166 | 0.0083 | 0.0070 | 0.0179 |
| season_sin2 | 0.0185 | 0.0078 | 0.0061 | 0.0022 |
| season_cos2 | -0.0151 | 0.0081 | 0.0068 | 0.0266 |
| tv | 0.0170 | 0.0011 | 0.0010 | 0.0000 |
| instagram | 0.3728 | 0.0322 | 0.0259 | 0.0000 |
| tiktok | 0.3287 | 0.0271 | 0.0254 | 0.0000 |
| influencer | 0.7015 | 0.0354 | 0.0267 | 0.0000 |
| pos_promotion | 0.1151 | 0.0269 | 0.0240 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | -9.002 | 0.580 | -0.864 | 0.451 | 0.091 | -0.002 | -0.011 | 0.016 | -0.016 | 0.017 | 0.366 | 0.318 | 0.668 | 0.129 |
| train<117 | -9.083 | 0.566 | -0.851 | 0.458 | 0.086 | -0.004 | -0.013 | 0.013 | -0.016 | 0.017 | 0.368 | 0.327 | 0.692 | 0.121 |
| train<130 | -9.281 | 0.554 | -0.757 | 0.423 | 0.079 | -0.002 | -0.015 | 0.015 | -0.015 | 0.017 | 0.380 | 0.326 | 0.712 | 0.122 |
| train<143 | -9.121 | 0.550 | -0.759 | 0.428 | 0.079 | -0.002 | -0.014 | 0.015 | -0.014 | 0.017 | 0.369 | 0.329 | 0.703 | 0.129 |
| full | -8.982 | 0.547 | -0.674 | 0.479 | 0.071 | -0.002 | -0.017 | 0.019 | -0.015 | 0.017 | 0.373 | 0.329 | 0.702 | 0.115 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.6 | 51 |
| 2023 | 0.6 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 2.6 | 14 |
| 2 | 0.4 | 12 |
| 3 | -1.4 | 12 |
| 4 | -0.5 | 13 |
| 5 | 0.4 | 14 |
| 6 | -0.3 | 12 |
| 7 | 0.5 | 14 |
| 8 | 0.2 | 13 |
| 9 | 0.2 | 13 |
| 10 | 0.6 | 14 |
| 11 | -0.3 | 12 |
| 12 | -3.0 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 19.0% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.8 | 8,929,318 | 0.96 | 1.77 |
| instagram | 15,393 | 1,192,415 | 15.6 | 21,050,604 | 17.65 | 30.35 |
| tiktok | 9,332 | 1,415,019 | 23.0 | 30,983,688 | 21.90 | 35.89 |
| influencer | 13,406 | 1,021,938 | 28.9 | 38,990,354 | 38.15 | 59.88 |
| pos_promotion | 17,791 | 2,008,661 | 6.7 | 8,969,938 | 4.47 | 8.27 |

## Sensitivity – reference: zero spend for every channel

Base = 0.0% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 2.6 | 3,364,770 | 0.36 | 1.77 |
| instagram | 0 | 3,578,330 | 25.0 | 33,626,729 | 9.40 | 37.59 |
| tiktok | 0 | 2,861,479 | 24.9 | 33,594,135 | 11.74 | 46.98 |
| influencer | 0 | 3,099,868 | 25.0 | 33,646,869 | 10.85 | 43.42 |
| pos_promotion | 0 | 4,766,266 | 22.5 | 30,352,688 | 6.37 | 26.10 |
