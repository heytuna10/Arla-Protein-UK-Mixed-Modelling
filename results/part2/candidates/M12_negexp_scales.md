# M12_negexp_scales

M9 with negative-exponential curve, scale tuned (TV; always-on shared)

n = 155, parameters = 23, R² = 0.977, AIC = -495.2, BIC = -425.2

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.9184 | 0.2266 | 0.2037 | 0.0000 |
| lagged_sales | 0.3579 | 0.0173 | 0.0143 | 0.0000 |
| regular_price | -0.4677 | 0.1819 | 0.1611 | 0.0037 |
| promo_depth | 0.4485 | 0.0328 | 0.0281 | 0.0000 |
| promo_depth_lag1 | -0.0613 | 0.0310 | 0.0250 | 0.0140 |
| trend | 0.0702 | 0.0139 | 0.0128 | 0.0000 |
| season_sin1 | -0.0015 | 0.0056 | 0.0049 | 0.7604 |
| season_cos1 | -0.0470 | 0.0069 | 0.0080 | 0.0000 |
| season_sin2 | 0.0197 | 0.0055 | 0.0055 | 0.0004 |
| season_cos2 | -0.0123 | 0.0060 | 0.0060 | 0.0397 |
| january | 0.0549 | 0.0190 | 0.0197 | 0.0054 |
| tv | 1.2640 | 0.0567 | 0.0477 | 0.0000 |
| instagram | 1.4675 | 0.0795 | 0.0958 | 0.0000 |
| tiktok | 0.9670 | 0.0503 | 0.0502 | 0.0000 |
| influencer | 2.9439 | 0.1006 | 0.0805 | 0.0000 |
| pos_promotion | 0.3654 | 0.0504 | 0.0517 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.858 | 0.366 | -0.553 | 0.438 | -0.062 | 0.082 | -0.002 | -0.052 | 0.022 | -0.015 | 0.063 | 1.291 | 1.560 | 0.945 | 2.804 | 0.384 |
| train<117 | 4.883 | 0.364 | -0.572 | 0.451 | -0.049 | 0.084 | -0.001 | -0.050 | 0.024 | -0.014 | 0.049 | 1.292 | 1.542 | 0.968 | 2.853 | 0.348 |
| train<130 | 4.947 | 0.353 | -0.460 | 0.422 | -0.042 | 0.075 | 0.000 | -0.055 | 0.025 | -0.011 | 0.059 | 1.246 | 1.569 | 0.929 | 2.939 | 0.352 |
| train<143 | 4.902 | 0.359 | -0.426 | 0.427 | -0.053 | 0.067 | 0.000 | -0.046 | 0.020 | -0.010 | 0.052 | 1.264 | 1.461 | 0.949 | 2.947 | 0.372 |
| full | 4.918 | 0.358 | -0.468 | 0.449 | -0.061 | 0.070 | -0.001 | -0.047 | 0.020 | -0.012 | 0.055 | 1.264 | 1.467 | 0.967 | 2.944 | 0.365 |

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
| decay tv | 54.9 | 38.6 | 22.6 | 8.6 | 0.0 | 2.9 | 27.5 | 84.7 | 165.9 | 221.6 |
| decay instagram | 22.3 | 9.6 | 1.5 | 0.0 | 6.9 | 23.1 | 48.0 | 79.9 | 116.4 | 153.3 |
| decay tiktok | 0.0 | 6.2 | 18.7 | 36.5 | 58.0 | 82.4 | 108.8 | 136.7 | 165.1 | 189.5 |
| decay influencer | 96.5 | 63.6 | 33.1 | 9.6 | 0.0 | 12.1 | 50.2 | 111.0 | 182.7 | 250.0 |
| decay pos_promotion | 0.0 | 3.1 | 6.5 | 10.2 | 14.6 | 19.7 | 25.7 | 32.3 | 39.3 | 46.9 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 68.6 | 25.0 | 5.8 | 0.8 | 0.0 |
| scale instagram+tiktok+influencer+pos_promotion | 118.3 | 20.5 | 0.0 | 11.6 | 23.1 |

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
| 3 | -0.2 | 12 |
| 4 | -2.6 | 13 |
| 5 | 0.3 | 14 |
| 6 | 1.6 | 12 |
| 7 | 0.3 | 14 |
| 8 | -1.4 | 13 |
| 9 | 0.1 | 13 |
| 10 | 1.0 | 14 |
| 11 | 0.8 | 12 |
| 12 | -2.9 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 21.1% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.0 | 9,128,857 | 0.98 | 1.75 | 1.83 |
| instagram | 15,393 | 1,192,415 | 16.4 | 22,176,362 | 18.60 | 30.70 | 30.89 |
| tiktok | 9,332 | 1,415,019 | 17.5 | 23,616,386 | 16.69 | 27.49 | 24.67 |
| influencer | 13,406 | 1,021,938 | 32.5 | 43,757,705 | 42.82 | 63.48 | 74.65 |
| pos_promotion | 17,791 | 2,008,661 | 5.6 | 7,408,959 | 3.69 | 6.65 | 5.50 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.3% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.7 | 4,829,882 | 0.52 | 1.75 |
| instagram | 0 | 3,578,330 | 27.6 | 37,284,429 | 10.42 | 28.56 |
| tiktok | 0 | 2,861,479 | 20.8 | 27,997,620 | 9.78 | 28.59 |
| influencer | 0 | 3,099,868 | 38.3 | 51,628,540 | 16.66 | 40.99 |
| pos_promotion | 0 | 4,766,266 | 9.2 | 12,400,156 | 2.60 | 8.41 |
