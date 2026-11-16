# M16_tv_x_social

M14 + tv × social: TV drives search and social traffic, so paid Instagram/TikTok works harder during flights

n = 155, parameters = 23, R² = 0.977, AIC = -495.6, BIC = -425.6

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3730 | 0.2302 | 0.2043 | 0.0000 |
| lagged_sales | 0.3552 | 0.0175 | 0.0142 | 0.0000 |
| regular_price | -0.4932 | 0.1826 | 0.1582 | 0.0018 |
| promo_depth | 0.4502 | 0.0329 | 0.0279 | 0.0000 |
| promo_depth_lag1 | -0.0596 | 0.0312 | 0.0257 | 0.0204 |
| trend | 0.0719 | 0.0139 | 0.0126 | 0.0000 |
| season_sin1 | -0.0015 | 0.0056 | 0.0049 | 0.7536 |
| season_cos1 | -0.0458 | 0.0069 | 0.0079 | 0.0000 |
| season_sin2 | 0.0196 | 0.0056 | 0.0055 | 0.0004 |
| season_cos2 | -0.0123 | 0.0060 | 0.0059 | 0.0373 |
| january | 0.0523 | 0.0192 | 0.0195 | 0.0073 |
| tv | 1.4029 | 0.0638 | 0.0564 | 0.0000 |
| instagram | 2.1593 | 0.1186 | 0.1379 | 0.0000 |
| tiktok | 1.4145 | 0.0734 | 0.0740 | 0.0000 |
| influencer | 4.3315 | 0.1505 | 0.1169 | 0.0000 |
| pos_promotion | 0.5300 | 0.0735 | 0.0747 | 0.0000 |
| ix_tv_social | 0.4609 | 0.8288 | 0.7665 | 0.5476 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion | ix_tv_social |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.946 | 0.255 | -0.567 | 0.437 | -0.013 | 0.088 | -0.001 | -0.058 | 0.024 | -0.014 | 0.052 | 1.737 | 2.791 | 1.594 | 4.969 | 0.579 | 2.781 |
| train<117 | 4.942 | 0.258 | -0.630 | 0.446 | 0.006 | 0.095 | 0.001 | -0.054 | 0.026 | -0.014 | 0.038 | 1.737 | 2.735 | 1.622 | 4.981 | 0.534 | 2.704 |
| train<130 | 4.406 | 0.349 | -0.463 | 0.426 | -0.036 | 0.074 | 0.000 | -0.054 | 0.024 | -0.010 | 0.056 | 1.378 | 2.313 | 1.362 | 4.336 | 0.510 | 0.970 |
| train<143 | 4.366 | 0.355 | -0.466 | 0.429 | -0.048 | 0.070 | -0.001 | -0.045 | 0.020 | -0.010 | 0.049 | 1.407 | 2.154 | 1.390 | 4.350 | 0.541 | 0.811 |
| full | 4.373 | 0.355 | -0.493 | 0.450 | -0.060 | 0.072 | -0.002 | -0.046 | 0.020 | -0.012 | 0.052 | 1.403 | 2.159 | 1.415 | 4.332 | 0.530 | 0.461 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.5 | 0.4 | 0.1 | 0.5 | 0.0 |
| train<117 | 0.5 | 0.4 | 0.1 | 0.5 | 0.0 |
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
| decay tv | 55.1 | 38.4 | 22.4 | 8.6 | 0.0 | 2.1 | 24.8 | 80.4 | 162.7 | 221.0 |
| decay instagram | 21.9 | 9.5 | 1.5 | 0.0 | 6.7 | 22.7 | 47.6 | 79.6 | 116.3 | 153.4 |
| decay tiktok | 0.0 | 5.9 | 18.3 | 35.8 | 57.1 | 81.3 | 107.6 | 135.5 | 164.1 | 188.8 |
| decay influencer | 95.9 | 62.8 | 32.4 | 9.2 | 0.0 | 12.1 | 49.2 | 108.1 | 178.6 | 246.3 |
| decay pos_promotion | 0.0 | 3.1 | 6.5 | 10.2 | 14.5 | 19.6 | 25.4 | 31.8 | 38.8 | 46.5 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 59.6 | 30.7 | 11.7 | 2.8 | 0.0 |

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
| 4 | -2.7 | 13 |
| 5 | 0.4 | 14 |
| 6 | 1.6 | 12 |
| 7 | 0.3 | 14 |
| 8 | -1.3 | 13 |
| 9 | 0.2 | 13 |
| 10 | 0.9 | 14 |
| 11 | 0.8 | 12 |
| 12 | -2.8 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 21.0% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.9 | 8,982,260 | 0.96 | 1.78 | 1.72 |
| instagram | 15,393 | 1,192,415 | 16.4 | 22,157,213 | 18.58 | 30.90 | 30.97 |
| tiktok | 9,332 | 1,415,019 | 17.6 | 23,774,217 | 16.80 | 27.94 | 24.82 |
| influencer | 13,406 | 1,021,938 | 32.6 | 43,896,500 | 42.95 | 63.79 | 74.70 |
| pos_promotion | 17,791 | 2,008,661 | 5.6 | 7,395,237 | 3.68 | 6.66 | 5.48 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.5 | 4,518,161 | 0.49 | 1.78 |
| instagram | 0 | 3,578,330 | 28.1 | 37,939,523 | 10.60 | 30.42 |
| tiktok | 0 | 2,861,479 | 21.6 | 29,097,219 | 10.17 | 31.09 |
| influencer | 0 | 3,099,868 | 36.8 | 49,584,042 | 16.00 | 41.88 |
| pos_promotion | 0 | 4,766,266 | 9.9 | 13,252,536 | 2.78 | 9.39 |
