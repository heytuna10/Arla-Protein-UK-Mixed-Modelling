# M7_adstock_3decays

as M6 with three decays: TV / social / POS

n = 155, parameters = 18, R² = 0.955, AIC = -401.7, BIC = -346.9

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 8.5953 | 0.1581 | 0.1571 | 0.0000 |
| regular_price | -1.1698 | 0.3001 | 0.3209 | 0.0003 |
| promo_depth | 0.4168 | 0.0449 | 0.0408 | 0.0000 |
| promo_depth_lag1 | 0.0919 | 0.0395 | 0.0355 | 0.0097 |
| trend | 0.1441 | 0.0228 | 0.0262 | 0.0000 |
| season_sin1 | -0.0076 | 0.0079 | 0.0095 | 0.4229 |
| season_cos1 | -0.0504 | 0.0106 | 0.0108 | 0.0000 |
| season_sin2 | 0.0248 | 0.0077 | 0.0097 | 0.0109 |
| season_cos2 | -0.0296 | 0.0092 | 0.0116 | 0.0109 |
| january | 0.0494 | 0.0270 | 0.0278 | 0.0753 |
| tv | 0.6709 | 0.0305 | 0.0341 | 0.0000 |
| instagram | 1.7695 | 0.1109 | 0.1434 | 0.0000 |
| tiktok | 1.3445 | 0.0988 | 0.1146 | 0.0000 |
| influencer | 3.4181 | 0.1294 | 0.1205 | 0.0000 |
| pos_promotion | 0.3991 | 0.0669 | 0.0775 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 8.688 | -1.725 | 0.369 | 0.107 | 0.190 | -0.016 | -0.059 | 0.019 | -0.052 | 0.063 | 0.735 | 1.964 | 1.466 | 3.214 | 0.360 |
| train<117 | 8.721 | -1.758 | 0.386 | 0.144 | 0.202 | -0.010 | -0.054 | 0.024 | -0.051 | 0.046 | 0.731 | 1.919 | 1.435 | 3.239 | 0.363 |
| train<130 | 8.583 | -1.320 | 0.363 | 0.112 | 0.164 | -0.010 | -0.060 | 0.029 | -0.038 | 0.053 | 0.695 | 1.895 | 1.329 | 3.408 | 0.364 |
| train<143 | 8.576 | -1.068 | 0.394 | 0.102 | 0.135 | -0.007 | -0.053 | 0.026 | -0.029 | 0.051 | 0.672 | 1.770 | 1.320 | 3.431 | 0.396 |
| full | 8.595 | -1.170 | 0.417 | 0.092 | 0.144 | -0.008 | -0.050 | 0.025 | -0.030 | 0.049 | 0.671 | 1.769 | 1.344 | 3.418 | 0.399 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.6 | 0.6 | 0.6 | 0.6 | 0.1 |
| train<117 | 0.6 | 0.6 | 0.6 | 0.6 | 0.2 |
| train<130 | 0.6 | 0.6 | 0.6 | 0.6 | 0.2 |
| train<143 | 0.6 | 0.6 | 0.6 | 0.6 | 0.3 |
| full | 0.6 | 0.6 | 0.6 | 0.6 | 0.3 |

Scale of the saturation curve, £ per week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<117 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<130 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| train<143 | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |
| full | 234,146 | 23,077 | 18,462 | 20,000 | 30,769 |

Likelihood profiles: AIC penalty for moving one parameter away from its best value, others held (0 = best; below about 2 = the data cannot tell the values apart).

| decay value → | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|---|
| decay tv | 144.2 | 126.4 | 105.4 | 80.4 | 50.9 | 19.9 | 0.0 | 21.2 | 100.0 | 191.4 |
| decay instagram+tiktok+influencer | 199.1 | 168.4 | 131.5 | 88.1 | 40.6 | 1.7 | 0.0 | 52.9 | 136.3 | 220.5 |
| decay pos_promotion | 3.2 | 1.6 | 0.4 | 0.0 | 0.8 | 3.2 | 7.6 | 14.1 | 22.3 | 32.1 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | 0.0 | 51 |
| 2023 | -0.2 | 52 |
| 2024 | 0.2 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.6 | 12 |
| 3 | -0.3 | 12 |
| 4 | -2.8 | 13 |
| 5 | -0.5 | 14 |
| 6 | 1.8 | 12 |
| 7 | 1.9 | 14 |
| 8 | -3.1 | 13 |
| 9 | 0.3 | 13 |
| 10 | 1.6 | 14 |
| 11 | 0.5 | 12 |
| 12 | -2.2 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 20.6% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 8.2 | 10,761,053 | 1.16 | 2.07 | 1.92 |
| instagram | 15,393 | 1,192,415 | 16.1 | 21,815,499 | 18.30 | 30.44 | 33.80 |
| tiktok | 9,332 | 1,415,019 | 19.3 | 26,027,793 | 18.39 | 30.12 | 31.90 |
| influencer | 13,406 | 1,021,938 | 30.7 | 41,377,625 | 40.49 | 61.16 | 79.22 |
| pos_promotion | 17,791 | 2,008,661 | 5.0 | 6,614,070 | 3.29 | 6.01 | 5.53 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.7% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 4.6 | 5,996,063 | 0.64 | 2.07 |
| instagram | 0 | 3,578,330 | 26.6 | 35,845,192 | 10.02 | 26.49 |
| tiktok | 0 | 2,861,479 | 21.9 | 29,515,755 | 10.31 | 28.49 |
| influencer | 0 | 3,099,868 | 38.5 | 51,889,447 | 16.74 | 39.39 |
| pos_promotion | 0 | 4,766,266 | 7.8 | 10,395,177 | 2.18 | 6.81 |
