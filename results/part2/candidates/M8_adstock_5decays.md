# M8_adstock_5decays

as M6 with one decay per channel

n = 155, parameters = 20, R² = 0.964, AIC = -432.3, BIC = -371.4

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 8.6717 | 0.1414 | 0.1524 | 0.0000 |
| regular_price | -0.6607 | 0.2446 | 0.2570 | 0.0102 |
| promo_depth | 0.4356 | 0.0402 | 0.0369 | 0.0000 |
| promo_depth_lag1 | 0.0992 | 0.0353 | 0.0297 | 0.0008 |
| trend | 0.1079 | 0.0187 | 0.0221 | 0.0000 |
| season_sin1 | -0.0052 | 0.0070 | 0.0070 | 0.4595 |
| season_cos1 | -0.0629 | 0.0092 | 0.0116 | 0.0000 |
| season_sin2 | 0.0331 | 0.0069 | 0.0085 | 0.0001 |
| season_cos2 | -0.0144 | 0.0077 | 0.0099 | 0.1471 |
| january | 0.0387 | 0.0241 | 0.0278 | 0.1632 |
| tv | 0.6847 | 0.0273 | 0.0268 | 0.0000 |
| instagram | 1.8087 | 0.0989 | 0.1385 | 0.0000 |
| tiktok | 1.0050 | 0.0616 | 0.0747 | 0.0000 |
| influencer | 3.4160 | 0.1157 | 0.1095 | 0.0000 |
| pos_promotion | 0.3687 | 0.0600 | 0.0714 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 8.724 | -1.452 | 0.413 | 0.120 | 0.179 | -0.016 | -0.073 | 0.030 | -0.040 | 0.062 | 0.734 | 2.000 | 1.225 | 3.299 | 0.298 |
| train<117 | 8.777 | -1.481 | 0.403 | 0.160 | 0.188 | -0.009 | -0.069 | 0.035 | -0.040 | 0.042 | 0.732 | 1.957 | 1.208 | 3.296 | 0.287 |
| train<130 | 8.699 | -0.924 | 0.392 | 0.131 | 0.141 | -0.009 | -0.079 | 0.040 | -0.023 | 0.049 | 0.696 | 1.968 | 1.006 | 3.370 | 0.305 |
| train<143 | 8.662 | -0.604 | 0.418 | 0.108 | 0.103 | -0.005 | -0.065 | 0.033 | -0.015 | 0.042 | 0.683 | 1.811 | 0.992 | 3.417 | 0.371 |
| full | 8.672 | -0.661 | 0.436 | 0.099 | 0.108 | -0.005 | -0.063 | 0.033 | -0.014 | 0.039 | 0.685 | 1.809 | 1.005 | 3.416 | 0.369 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.6 | 0.6 | 0.4 | 0.6 | 0.0 |
| train<117 | 0.6 | 0.6 | 0.4 | 0.6 | 0.0 |
| train<130 | 0.6 | 0.6 | 0.3 | 0.6 | 0.1 |
| train<143 | 0.6 | 0.6 | 0.3 | 0.6 | 0.3 |
| full | 0.6 | 0.6 | 0.3 | 0.6 | 0.3 |

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
| decay tv | 174.3 | 154.2 | 130.2 | 101.2 | 66.4 | 27.8 | 0.0 | 22.1 | 114.2 | 217.8 |
| decay instagram | 90.8 | 73.3 | 54.1 | 34.0 | 15.3 | 1.8 | 0.0 | 17.0 | 56.4 | 112.6 |
| decay tiktok | 29.1 | 15.7 | 5.3 | 0.0 | 1.9 | 13.1 | 34.6 | 66.0 | 104.6 | 142.3 |
| decay influencer | 208.7 | 183.3 | 152.6 | 115.3 | 71.7 | 27.0 | 0.0 | 22.1 | 95.1 | 194.6 |
| decay pos_promotion | 2.0 | 1.2 | 0.5 | 0.0 | 0.2 | 1.5 | 4.5 | 9.6 | 17.2 | 29.3 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.3 | 51 |
| 2023 | 0.3 | 52 |
| 2024 | -0.1 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.1 | 12 |
| 3 | 0.9 | 12 |
| 4 | -3.4 | 13 |
| 5 | -0.5 | 14 |
| 6 | 2.5 | 12 |
| 7 | 1.0 | 14 |
| 8 | -2.1 | 13 |
| 9 | -0.2 | 13 |
| 10 | 1.8 | 14 |
| 11 | 0.3 | 12 |
| 12 | -2.2 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 22.7% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 8.7 | 11,345,786 | 1.22 | 2.11 | 1.96 |
| instagram | 15,393 | 1,192,415 | 17.0 | 23,023,356 | 19.31 | 31.00 | 34.58 |
| tiktok | 9,332 | 1,415,019 | 15.0 | 20,297,646 | 14.34 | 23.49 | 23.60 |
| influencer | 13,406 | 1,021,938 | 31.8 | 42,832,423 | 41.91 | 61.13 | 79.16 |
| pos_promotion | 17,791 | 2,008,661 | 4.8 | 6,316,671 | 3.14 | 5.57 | 5.10 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.9% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 4.8 | 6,339,179 | 0.68 | 2.11 |
| instagram | 0 | 3,578,330 | 28.2 | 38,022,582 | 10.63 | 26.79 |
| tiktok | 0 | 2,861,479 | 18.1 | 24,427,338 | 8.54 | 23.56 |
| influencer | 0 | 3,099,868 | 40.5 | 54,584,061 | 17.61 | 39.38 |
| pos_promotion | 0 | 4,766,266 | 7.5 | 10,026,292 | 2.10 | 6.36 |
