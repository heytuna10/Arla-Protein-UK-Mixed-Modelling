# M19_all_synergies

M14 + all four interactions

n = 155, parameters = 26, R² = 0.978, AIC = -493.8, BIC = -414.7

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.6641 | 0.2446 | 0.2164 | 0.0000 |
| lagged_sales | 0.3222 | 0.0181 | 0.0139 | 0.0000 |
| regular_price | -0.4512 | 0.1850 | 0.1694 | 0.0077 |
| promo_depth | 0.4516 | 0.0363 | 0.0266 | 0.0000 |
| promo_depth_lag1 | -0.0614 | 0.0314 | 0.0255 | 0.0162 |
| trend | 0.0749 | 0.0141 | 0.0131 | 0.0000 |
| season_sin1 | 0.0022 | 0.0056 | 0.0054 | 0.6832 |
| season_cos1 | -0.0439 | 0.0070 | 0.0077 | 0.0000 |
| season_sin2 | 0.0195 | 0.0056 | 0.0055 | 0.0004 |
| season_cos2 | -0.0111 | 0.0060 | 0.0061 | 0.0704 |
| january | 0.0373 | 0.0195 | 0.0202 | 0.0651 |
| tv | 1.6168 | 0.0738 | 0.0666 | 0.0000 |
| instagram | 2.2261 | 0.1191 | 0.1415 | 0.0000 |
| tiktok | 1.4203 | 0.0738 | 0.0659 | 0.0000 |
| influencer | 4.4155 | 0.1554 | 0.1221 | 0.0000 |
| pos_promotion | 0.6114 | 0.0860 | 0.0783 | 0.0000 |
| ix_tv_influencer | 1.1751 | 2.1506 | 1.8301 | 0.5208 |
| ix_tv_social | 0.4624 | 0.9799 | 0.8233 | 0.5744 |
| ix_influencer_social | 4.0679 | 2.1933 | 1.6538 | 0.0139 |
| ix_pos_promo | -0.8227 | 0.6324 | 0.4981 | 0.0986 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion | ix_tv_influencer | ix_tv_social | ix_influencer_social | ix_pos_promo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.613 | 0.306 | -0.400 | 0.458 | -0.063 | 0.072 | 0.005 | -0.058 | 0.023 | -0.014 | 0.044 | 1.672 | 2.769 | 1.441 | 4.275 | 0.685 | 3.259 | 2.289 | 6.175 | -1.354 |
| train<117 | 4.667 | 0.309 | -0.526 | 0.473 | -0.030 | 0.085 | 0.005 | -0.054 | 0.024 | -0.014 | 0.036 | 1.668 | 2.690 | 1.444 | 4.285 | 0.625 | 1.036 | 2.389 | 4.089 | -1.160 |
| train<130 | 4.708 | 0.300 | -0.418 | 0.448 | -0.026 | 0.078 | 0.005 | -0.060 | 0.025 | -0.010 | 0.043 | 1.627 | 2.698 | 1.370 | 4.416 | 0.648 | 0.889 | 1.443 | 4.474 | -1.406 |
| train<143 | 4.305 | 0.354 | -0.411 | 0.452 | -0.052 | 0.067 | 0.002 | -0.046 | 0.020 | -0.009 | 0.047 | 1.409 | 2.175 | 1.371 | 4.367 | 0.638 | 0.775 | 0.571 | 2.371 | -1.282 |
| full | 4.664 | 0.322 | -0.451 | 0.452 | -0.061 | 0.075 | 0.002 | -0.044 | 0.020 | -0.011 | 0.037 | 1.617 | 2.226 | 1.420 | 4.415 | 0.611 | 1.175 | 0.462 | 4.068 | -0.823 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.5 | 0.4 | 0.0 | 0.4 | 0.0 |
| train<117 | 0.5 | 0.4 | 0.0 | 0.4 | 0.0 |
| train<130 | 0.5 | 0.4 | 0.0 | 0.4 | 0.0 |
| train<143 | 0.4 | 0.3 | 0.0 | 0.4 | 0.0 |
| full | 0.5 | 0.3 | 0.0 | 0.4 | 0.0 |

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
| decay tv | 58.1 | 41.7 | 25.5 | 10.8 | 0.3 | 0.0 | 20.9 | 77.5 | 163.9 | 223.5 |
| decay instagram | 33.1 | 18.1 | 6.4 | 0.0 | 1.5 | 13.2 | 35.7 | 68.2 | 107.7 | 147.9 |
| decay tiktok | 0.0 | 3.9 | 14.1 | 29.8 | 49.9 | 73.7 | 100.8 | 131.2 | 163.5 | 191.6 |
| decay influencer | 99.7 | 65.1 | 33.5 | 9.6 | 0.0 | 11.5 | 46.8 | 101.9 | 168.7 | 240.3 |
| decay pos_promotion | 0.0 | 1.9 | 4.4 | 7.6 | 11.8 | 17.5 | 24.8 | 33.7 | 43.5 | 52.8 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 78.7 | 41.4 | 15.6 | 3.6 | 0.0 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | -0.1 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.4 | 12 |
| 3 | 0.5 | 12 |
| 4 | -2.4 | 13 |
| 5 | -0.4 | 14 |
| 6 | 2.5 | 12 |
| 7 | -0.3 | 14 |
| 8 | -1.1 | 13 |
| 9 | 0.4 | 13 |
| 10 | 0.5 | 14 |
| 11 | 0.9 | 12 |
| 12 | -2.7 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 25.7% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.8 | 10,203,623 | 1.10 | 1.98 | 1.96 |
| instagram | 15,393 | 1,192,415 | 15.8 | 21,320,552 | 17.88 | 30.46 | 30.51 |
| tiktok | 9,332 | 1,415,019 | 15.9 | 21,495,825 | 15.19 | 26.96 | 23.86 |
| influencer | 13,406 | 1,021,938 | 29.6 | 39,805,912 | 38.95 | 62.22 | 72.03 |
| pos_promotion | 17,791 | 2,008,661 | 5.2 | 7,067,487 | 3.52 | 6.14 | 5.29 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 3.5% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 4.0 | 5,169,986 | 0.56 | 1.98 |
| instagram | 0 | 3,578,330 | 27.8 | 37,447,978 | 10.47 | 30.23 |
| tiktok | 0 | 2,861,479 | 20.0 | 26,886,303 | 9.40 | 30.37 |
| influencer | 0 | 3,099,868 | 34.8 | 46,783,682 | 15.09 | 41.68 |
| pos_promotion | 0 | 4,766,266 | 9.9 | 13,576,402 | 2.85 | 9.01 |
