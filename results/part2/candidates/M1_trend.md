# M1_trend

M0 + linear trend

n = 155, parameters = 10, R² = 0.942, AIC = -379.6, BIC = -349.2

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | -8.7757 | 0.6776 | 0.5981 | 0.0000 |
| lagged_sales | 0.5501 | 0.0213 | 0.0186 | 0.0000 |
| avg_price | -0.6090 | 0.1383 | 0.1294 | 0.0000 |
| price_promo | -0.0411 | 0.0407 | 0.0404 | 0.3087 |
| trend | 0.0629 | 0.0111 | 0.0106 | 0.0000 |
| tv | 0.0171 | 0.0011 | 0.0009 | 0.0000 |
| instagram | 0.3521 | 0.0311 | 0.0298 | 0.0000 |
| tiktok | 0.3174 | 0.0250 | 0.0244 | 0.0000 |
| influencer | 0.7015 | 0.0362 | 0.0296 | 0.0000 |
| pos_promotion | 0.1209 | 0.0282 | 0.0232 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | avg_price | price_promo | trend | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | -8.926 | 0.585 | -0.722 | -0.074 | 0.075 | 0.017 | 0.347 | 0.305 | 0.679 | 0.132 |
| train<117 | -8.868 | 0.566 | -0.660 | -0.060 | 0.066 | 0.017 | 0.345 | 0.312 | 0.698 | 0.128 |
| train<130 | -9.133 | 0.557 | -0.605 | -0.054 | 0.062 | 0.017 | 0.356 | 0.315 | 0.719 | 0.129 |
| train<143 | -8.944 | 0.550 | -0.606 | -0.053 | 0.068 | 0.017 | 0.353 | 0.313 | 0.707 | 0.135 |
| full | -8.776 | 0.550 | -0.609 | -0.041 | 0.063 | 0.017 | 0.352 | 0.317 | 0.701 | 0.121 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.7 | 51 |
| 2023 | 0.6 | 52 |
| 2024 | 0.1 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.9 | 14 |
| 2 | 1.3 | 12 |
| 3 | -0.2 | 12 |
| 4 | -0.2 | 13 |
| 5 | -0.5 | 14 |
| 6 | -1.2 | 12 |
| 7 | 1.9 | 14 |
| 8 | 3.4 | 13 |
| 9 | 2.7 | 13 |
| 10 | 0.2 | 14 |
| 11 | -2.9 | 12 |
| 12 | -6.4 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 19.3% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.9 | 9,076,734 | 0.97 | 1.79 |
| instagram | 15,393 | 1,192,415 | 14.9 | 20,167,635 | 16.91 | 29.08 |
| tiktok | 9,332 | 1,415,019 | 22.5 | 30,329,861 | 21.43 | 35.11 |
| influencer | 13,406 | 1,021,938 | 29.2 | 39,422,229 | 38.58 | 60.15 |
| pos_promotion | 17,791 | 2,008,661 | 7.1 | 9,520,662 | 4.74 | 8.71 |

## Sensitivity – reference: zero spend for every channel

Base = 0.0% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 2.6 | 3,394,627 | 0.36 | 1.79 |
| instagram | 0 | 3,578,330 | 24.9 | 33,502,907 | 9.36 | 37.59 |
| tiktok | 0 | 2,861,479 | 24.9 | 33,468,409 | 11.70 | 46.97 |
| influencer | 0 | 3,099,868 | 24.9 | 33,530,999 | 10.82 | 43.42 |
| pos_promotion | 0 | 4,766,266 | 22.8 | 30,688,248 | 6.44 | 26.39 |
