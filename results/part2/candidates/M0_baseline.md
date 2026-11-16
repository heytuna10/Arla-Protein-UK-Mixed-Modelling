# M0_baseline

Part 1 baseline: log1p-log1p OLS with lagged sales, price and promo flag

n = 155, parameters = 9, R² = 0.930, AIC = -350.7, BIC = -323.3

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | -9.0964 | 0.7445 | 0.6430 | 0.0000 |
| lagged_sales | 0.5705 | 0.0231 | 0.0229 | 0.0000 |
| avg_price | 0.0509 | 0.1603 | 0.1802 | 0.7777 |
| price_promo | 0.1310 | 0.0303 | 0.0327 | 0.0001 |
| tv | 0.0164 | 0.0012 | 0.0011 | 0.0000 |
| instagram | 0.3522 | 0.0342 | 0.0378 | 0.0000 |
| tiktok | 0.2885 | 0.0269 | 0.0281 | 0.0000 |
| influencer | 0.7055 | 0.0398 | 0.0341 | 0.0000 |
| pos_promotion | 0.1302 | 0.0310 | 0.0252 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | avg_price | price_promo | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|
| train<104 | -8.615 | 0.581 | -0.284 | 0.063 | 0.016 | 0.343 | 0.295 | 0.667 | 0.138 |
| train<117 | -8.770 | 0.567 | -0.220 | 0.082 | 0.016 | 0.337 | 0.301 | 0.701 | 0.133 |
| train<130 | -9.239 | 0.572 | -0.086 | 0.097 | 0.017 | 0.342 | 0.306 | 0.722 | 0.131 |
| train<143 | -9.173 | 0.569 | 0.108 | 0.124 | 0.017 | 0.344 | 0.295 | 0.706 | 0.136 |
| full | -9.096 | 0.570 | 0.051 | 0.131 | 0.016 | 0.352 | 0.288 | 0.706 | 0.130 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -2.1 | 51 |
| 2023 | -0.7 | 52 |
| 2024 | 2.8 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.6 | 14 |
| 2 | 0.2 | 12 |
| 3 | -0.7 | 12 |
| 4 | -1.2 | 13 |
| 5 | -1.1 | 14 |
| 6 | 0.0 | 12 |
| 7 | 1.5 | 14 |
| 8 | 3.8 | 13 |
| 9 | 2.8 | 13 |
| 10 | 0.2 | 14 |
| 11 | -2.3 | 12 |
| 12 | -4.4 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 18.5% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.9 | 9,021,316 | 0.97 | 1.80 |
| instagram | 15,393 | 1,192,415 | 15.4 | 20,778,203 | 17.43 | 30.24 |
| tiktok | 9,332 | 1,415,019 | 21.1 | 28,548,170 | 20.18 | 33.78 |
| influencer | 13,406 | 1,021,938 | 30.2 | 40,675,325 | 39.80 | 62.37 |
| pos_promotion | 17,791 | 2,008,661 | 7.9 | 10,554,883 | 5.25 | 9.72 |

## Sensitivity – reference: zero spend for every channel

Base = -0.0% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 2.6 | 3,400,443 | 0.37 | 1.80 |
| instagram | 0 | 3,578,330 | 24.7 | 33,307,145 | 9.31 | 37.59 |
| tiktok | 0 | 2,861,479 | 24.7 | 33,243,667 | 11.62 | 46.94 |
| influencer | 0 | 3,099,868 | 24.8 | 33,329,547 | 10.75 | 43.42 |
| pos_promotion | 0 | 4,766,266 | 23.2 | 31,304,601 | 6.57 | 26.92 |
