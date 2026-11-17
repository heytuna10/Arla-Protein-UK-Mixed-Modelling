# M18_pos_x_promo

M14 + pos × promo: in-store displays make a price promotion more visible, so the discount lifts more

n = 155, parameters = 23, R² = 0.977, AIC = -497.1, BIC = -427.1

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3838 | 0.2292 | 0.2044 | 0.0000 |
| lagged_sales | 0.3543 | 0.0173 | 0.0139 | 0.0000 |
| regular_price | -0.4929 | 0.1816 | 0.1581 | 0.0018 |
| promo_depth | 0.4678 | 0.0357 | 0.0281 | 0.0000 |
| promo_depth_lag1 | -0.0656 | 0.0311 | 0.0247 | 0.0080 |
| trend | 0.0727 | 0.0139 | 0.0126 | 0.0000 |
| season_sin1 | -0.0007 | 0.0056 | 0.0049 | 0.8800 |
| season_cos1 | -0.0464 | 0.0069 | 0.0079 | 0.0000 |
| season_sin2 | 0.0200 | 0.0055 | 0.0054 | 0.0002 |
| season_cos2 | -0.0126 | 0.0060 | 0.0060 | 0.0354 |
| january | 0.0539 | 0.0190 | 0.0190 | 0.0046 |
| tv | 1.3943 | 0.0625 | 0.0510 | 0.0000 |
| instagram | 2.1489 | 0.1160 | 0.1402 | 0.0000 |
| tiktok | 1.4053 | 0.0731 | 0.0718 | 0.0000 |
| influencer | 4.3008 | 0.1474 | 0.1148 | 0.0000 |
| pos_promotion | 0.5846 | 0.0853 | 0.0798 | 0.0000 |
| ix_pos_promo | -0.8136 | 0.6281 | 0.4956 | 0.1006 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion | ix_pos_promo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.357 | 0.359 | -0.541 | 0.460 | -0.067 | 0.081 | -0.001 | -0.052 | 0.024 | -0.015 | 0.063 | 1.417 | 2.279 | 1.363 | 4.116 | 0.625 | -1.169 |
| train<117 | 4.352 | 0.359 | -0.551 | 0.471 | -0.053 | 0.082 | 0.000 | -0.050 | 0.025 | -0.014 | 0.050 | 1.418 | 2.256 | 1.381 | 4.180 | 0.593 | -1.252 |
| train<130 | 4.396 | 0.350 | -0.469 | 0.449 | -0.046 | 0.077 | 0.001 | -0.056 | 0.025 | -0.012 | 0.059 | 1.375 | 2.300 | 1.330 | 4.280 | 0.605 | -1.381 |
| train<143 | 4.355 | 0.356 | -0.433 | 0.457 | -0.057 | 0.068 | 0.001 | -0.047 | 0.021 | -0.011 | 0.052 | 1.392 | 2.135 | 1.364 | 4.295 | 0.623 | -1.348 |
| full | 4.384 | 0.354 | -0.493 | 0.468 | -0.066 | 0.073 | -0.001 | -0.046 | 0.020 | -0.013 | 0.054 | 1.394 | 2.149 | 1.405 | 4.301 | 0.585 | -0.814 |

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
| decay tv | 56.5 | 39.5 | 23.0 | 8.7 | 0.0 | 2.9 | 27.2 | 83.0 | 163.5 | 221.6 |
| decay instagram | 22.0 | 9.3 | 1.3 | 0.0 | 7.1 | 23.5 | 48.6 | 80.7 | 117.3 | 154.4 |
| decay tiktok | 0.0 | 6.0 | 18.4 | 36.0 | 57.4 | 81.8 | 108.5 | 137.0 | 166.0 | 190.6 |
| decay influencer | 95.2 | 62.6 | 32.6 | 9.5 | 0.0 | 12.0 | 49.9 | 110.5 | 182.1 | 249.5 |
| decay pos_promotion | 0.0 | 2.6 | 5.6 | 8.9 | 12.8 | 17.7 | 23.8 | 31.2 | 39.4 | 47.8 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 60.4 | 31.1 | 11.7 | 2.7 | 0.0 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.7 | 12 |
| 3 | 0.0 | 12 |
| 4 | -2.5 | 13 |
| 5 | 0.2 | 14 |
| 6 | 1.5 | 12 |
| 7 | 0.4 | 14 |
| 8 | -1.3 | 13 |
| 9 | 0.0 | 13 |
| 10 | 0.8 | 14 |
| 11 | 0.9 | 12 |
| 12 | -2.8 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 21.2% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.1 | 9,279,717 | 1.00 | 1.77 | 1.71 |
| instagram | 15,393 | 1,192,415 | 16.4 | 22,233,853 | 18.65 | 30.74 | 30.74 |
| tiktok | 9,332 | 1,415,019 | 17.7 | 23,881,144 | 16.88 | 27.72 | 24.59 |
| influencer | 13,406 | 1,021,938 | 32.5 | 43,776,967 | 42.84 | 63.41 | 74.02 |
| pos_promotion | 17,791 | 2,008,661 | 5.0 | 6,801,158 | 3.39 | 6.11 | 5.28 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.6 | 4,675,419 | 0.50 | 1.77 |
| instagram | 0 | 3,578,330 | 28.3 | 38,075,014 | 10.64 | 30.34 |
| tiktok | 0 | 2,861,479 | 21.7 | 29,178,140 | 10.20 | 30.93 |
| influencer | 0 | 3,099,868 | 37.0 | 49,764,092 | 16.05 | 41.84 |
| pos_promotion | 0 | 4,766,266 | 9.3 | 12,693,930 | 2.66 | 8.99 |
