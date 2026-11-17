# M2_season

M1 + annual seasonality (2 sine/cosine pairs)

n = 155, parameters = 14, R² = 0.948, AIC = -386.5, BIC = -343.9

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | -9.0220 | 0.6619 | 0.5056 | 0.0000 |
| lagged_sales | 0.5452 | 0.0208 | 0.0190 | 0.0000 |
| avg_price | -0.6527 | 0.1346 | 0.1290 | 0.0000 |
| price_promo | -0.0527 | 0.0397 | 0.0389 | 0.1752 |
| trend | 0.0681 | 0.0110 | 0.0091 | 0.0000 |
| season_sin1 | -0.0023 | 0.0082 | 0.0065 | 0.7185 |
| season_cos1 | -0.0170 | 0.0083 | 0.0070 | 0.0154 |
| season_sin2 | 0.0192 | 0.0077 | 0.0062 | 0.0019 |
| season_cos2 | -0.0147 | 0.0078 | 0.0064 | 0.0224 |
| tv | 0.0170 | 0.0010 | 0.0010 | 0.0000 |
| instagram | 0.3739 | 0.0320 | 0.0255 | 0.0000 |
| tiktok | 0.3257 | 0.0254 | 0.0233 | 0.0000 |
| influencer | 0.7040 | 0.0352 | 0.0262 | 0.0000 |
| pos_promotion | 0.1205 | 0.0274 | 0.0238 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | avg_price | price_promo | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | -9.100 | 0.578 | -0.752 | -0.084 | 0.081 | -0.002 | -0.010 | 0.019 | -0.014 | 0.017 | 0.368 | 0.314 | 0.675 | 0.133 |
| train<117 | -9.125 | 0.564 | -0.697 | -0.069 | 0.072 | -0.004 | -0.013 | 0.015 | -0.015 | 0.017 | 0.369 | 0.320 | 0.695 | 0.127 |
| train<130 | -9.331 | 0.553 | -0.627 | -0.060 | 0.067 | -0.002 | -0.015 | 0.016 | -0.013 | 0.017 | 0.383 | 0.319 | 0.716 | 0.126 |
| train<143 | -9.161 | 0.549 | -0.613 | -0.053 | 0.067 | -0.002 | -0.014 | 0.017 | -0.013 | 0.017 | 0.370 | 0.322 | 0.707 | 0.133 |
| full | -9.022 | 0.545 | -0.653 | -0.053 | 0.068 | -0.002 | -0.017 | 0.019 | -0.015 | 0.017 | 0.374 | 0.326 | 0.704 | 0.121 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.6 | 51 |
| 2023 | 0.6 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 2.6 | 14 |
| 2 | 0.5 | 12 |
| 3 | -1.6 | 12 |
| 4 | -0.4 | 13 |
| 5 | 0.5 | 14 |
| 6 | -0.6 | 12 |
| 7 | 0.6 | 14 |
| 8 | 0.1 | 13 |
| 9 | 0.3 | 13 |
| 10 | 0.5 | 14 |
| 11 | -0.1 | 12 |
| 12 | -3.2 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 19.0% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.8 | 8,889,472 | 0.95 | 1.76 | 0.16 |
| instagram | 15,393 | 1,192,415 | 15.6 | 21,037,947 | 17.64 | 30.33 | 30.38 |
| tiktok | 9,332 | 1,415,019 | 22.7 | 30,616,633 | 21.64 | 35.53 | 32.92 |
| influencer | 13,406 | 1,021,938 | 28.9 | 38,983,693 | 38.15 | 59.85 | 68.38 |
| pos_promotion | 17,791 | 2,008,661 | 7.0 | 9,350,361 | 4.66 | 8.60 | 7.16 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.0% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 2.5 | 3,343,245 | 0.36 | 1.76 |
| instagram | 0 | 3,578,330 | 24.9 | 33,547,328 | 9.38 | 37.59 |
| tiktok | 0 | 2,861,479 | 24.9 | 33,510,752 | 11.71 | 46.98 |
| influencer | 0 | 3,099,868 | 24.9 | 33,567,379 | 10.83 | 43.42 |
| pos_promotion | 0 | 4,766,266 | 22.7 | 30,616,487 | 6.42 | 26.32 |
