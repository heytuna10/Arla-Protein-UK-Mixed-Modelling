# M17_influencer_x_social

M14 + influencer × social: influencer content is amplified by paid Instagram/TikTok on the same platforms

n = 155, parameters = 23, R² = 0.977, AIC = -497.5, BIC = -427.5

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3240 | 0.2315 | 0.2056 | 0.0000 |
| lagged_sales | 0.3564 | 0.0172 | 0.0143 | 0.0000 |
| regular_price | -0.4718 | 0.1819 | 0.1634 | 0.0039 |
| promo_depth | 0.4457 | 0.0327 | 0.0277 | 0.0000 |
| promo_depth_lag1 | -0.0605 | 0.0309 | 0.0250 | 0.0155 |
| trend | 0.0708 | 0.0139 | 0.0129 | 0.0000 |
| season_sin1 | -0.0010 | 0.0055 | 0.0051 | 0.8388 |
| season_cos1 | -0.0454 | 0.0069 | 0.0079 | 0.0000 |
| season_sin2 | 0.0194 | 0.0055 | 0.0055 | 0.0004 |
| season_cos2 | -0.0120 | 0.0060 | 0.0061 | 0.0473 |
| january | 0.0494 | 0.0192 | 0.0198 | 0.0124 |
| tv | 1.4107 | 0.0632 | 0.0565 | 0.0000 |
| instagram | 2.1692 | 0.1170 | 0.1381 | 0.0000 |
| tiktok | 1.4075 | 0.0729 | 0.0691 | 0.0000 |
| influencer | 4.3704 | 0.1519 | 0.1178 | 0.0000 |
| pos_promotion | 0.5418 | 0.0736 | 0.0748 | 0.0000 |
| ix_influencer_social | 2.7380 | 1.9486 | 1.6531 | 0.0977 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion | ix_influencer_social |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.622 | 0.315 | -0.474 | 0.423 | -0.056 | 0.079 | 0.002 | -0.056 | 0.022 | -0.015 | 0.049 | 1.657 | 2.699 | 1.440 | 4.204 | 0.608 | 7.452 |
| train<117 | 4.279 | 0.359 | -0.509 | 0.446 | -0.051 | 0.078 | 0.001 | -0.048 | 0.024 | -0.013 | 0.044 | 1.429 | 2.291 | 1.428 | 4.275 | 0.523 | 3.878 |
| train<130 | 4.352 | 0.350 | -0.415 | 0.420 | -0.040 | 0.071 | 0.002 | -0.053 | 0.024 | -0.009 | 0.053 | 1.383 | 2.328 | 1.363 | 4.358 | 0.528 | 3.590 |
| train<143 | 4.316 | 0.356 | -0.431 | 0.422 | -0.050 | 0.068 | 0.000 | -0.045 | 0.020 | -0.010 | 0.046 | 1.413 | 2.169 | 1.387 | 4.380 | 0.557 | 3.050 |
| full | 4.324 | 0.356 | -0.472 | 0.446 | -0.060 | 0.071 | -0.001 | -0.045 | 0.019 | -0.012 | 0.049 | 1.411 | 2.169 | 1.407 | 4.370 | 0.542 | 2.738 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.5 | 0.4 | 0.0 | 0.4 | 0.0 |
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
| decay tv | 56.2 | 40.1 | 24.3 | 10.0 | 0.0 | 0.1 | 21.1 | 77.0 | 162.8 | 222.8 |
| decay instagram | 22.9 | 10.0 | 1.7 | 0.0 | 6.7 | 22.8 | 47.4 | 79.0 | 115.1 | 151.0 |
| decay tiktok | 0.0 | 6.4 | 19.1 | 36.7 | 58.1 | 82.2 | 108.7 | 137.1 | 166.4 | 191.3 |
| decay influencer | 92.8 | 58.6 | 28.3 | 6.7 | 0.0 | 13.9 | 50.5 | 106.6 | 174.0 | 243.6 |
| decay pos_promotion | 0.0 | 2.9 | 6.2 | 10.0 | 14.5 | 19.9 | 26.2 | 33.2 | 40.5 | 48.3 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 59.7 | 30.2 | 11.1 | 2.5 | 0.0 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 3.0 | 12 |
| 3 | -0.1 | 12 |
| 4 | -2.8 | 13 |
| 5 | 0.4 | 14 |
| 6 | 1.5 | 12 |
| 7 | 0.3 | 14 |
| 8 | -1.4 | 13 |
| 9 | 0.3 | 13 |
| 10 | 0.8 | 14 |
| 11 | 0.9 | 12 |
| 12 | -3.0 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 22.9% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.3 | 9,468,243 | 1.02 | 1.80 | 1.74 |
| instagram | 15,393 | 1,192,415 | 16.1 | 21,815,721 | 18.30 | 31.10 | 31.24 |
| tiktok | 9,332 | 1,415,019 | 16.8 | 22,720,176 | 16.06 | 27.87 | 24.82 |
| influencer | 13,406 | 1,021,938 | 31.1 | 41,908,240 | 41.01 | 64.04 | 75.30 |
| pos_promotion | 17,791 | 2,008,661 | 5.8 | 7,666,345 | 3.82 | 6.81 | 5.62 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 1.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.7 | 4,765,691 | 0.51 | 1.80 |
| instagram | 0 | 3,578,330 | 28.1 | 37,913,842 | 10.60 | 30.51 |
| tiktok | 0 | 2,861,479 | 21.2 | 28,523,561 | 9.97 | 31.06 |
| influencer | 0 | 3,099,868 | 35.8 | 48,202,951 | 15.55 | 41.91 |
| pos_promotion | 0 | 4,766,266 | 10.2 | 13,750,535 | 2.88 | 9.58 |
