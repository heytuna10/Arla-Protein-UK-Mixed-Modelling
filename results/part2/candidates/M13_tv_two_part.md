# M13_tv_two_part

M9 with TV as on-air flag + log(spend) on air, no TV adstock

n = 155, parameters = 21, R² = 0.969, AIC = -455.6, BIC = -391.7

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3477 | 0.2494 | 0.2577 | 0.0000 |
| lagged_sales | 0.4917 | 0.0188 | 0.0191 | 0.0000 |
| regular_price | -0.5720 | 0.2118 | 0.2036 | 0.0050 |
| promo_depth | 0.4652 | 0.0379 | 0.0333 | 0.0000 |
| promo_depth_lag1 | -0.1244 | 0.0354 | 0.0299 | 0.0000 |
| trend | 0.0662 | 0.0161 | 0.0154 | 0.0000 |
| season_sin1 | -0.0057 | 0.0064 | 0.0055 | 0.3053 |
| season_cos1 | -0.0408 | 0.0078 | 0.0074 | 0.0000 |
| season_sin2 | 0.0132 | 0.0064 | 0.0057 | 0.0212 |
| season_cos2 | -0.0153 | 0.0070 | 0.0064 | 0.0167 |
| january | 0.0823 | 0.0214 | 0.0185 | 0.0000 |
| tv_on_air | 0.1993 | 0.0109 | 0.0083 | 0.0000 |
| tv_log_spend_on_air | 0.1783 | 0.0421 | 0.0324 | 0.0000 |
| instagram | 0.8517 | 0.0544 | 0.0551 | 0.0000 |
| tiktok | 0.6456 | 0.0429 | 0.0465 | 0.0000 |
| influencer | 1.8382 | 0.0737 | 0.0571 | 0.0000 |
| pos_promotion | 0.2423 | 0.0419 | 0.0466 | 0.0000 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv_on_air | tv_log_spend_on_air | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.199 | 0.501 | -0.567 | 0.426 | -0.127 | 0.070 | -0.006 | -0.045 | 0.014 | -0.017 | 0.088 | 0.206 | 0.254 | 0.911 | 0.614 | 1.826 | 0.252 |
| train<117 | 4.220 | 0.501 | -0.634 | 0.438 | -0.110 | 0.077 | -0.005 | -0.042 | 0.016 | -0.018 | 0.076 | 0.207 | 0.208 | 0.891 | 0.632 | 1.847 | 0.234 |
| train<130 | 4.348 | 0.490 | -0.571 | 0.424 | -0.100 | 0.071 | -0.005 | -0.046 | 0.016 | -0.014 | 0.084 | 0.198 | 0.185 | 0.905 | 0.613 | 1.837 | 0.242 |
| train<143 | 4.331 | 0.493 | -0.552 | 0.432 | -0.111 | 0.065 | -0.005 | -0.040 | 0.013 | -0.014 | 0.080 | 0.200 | 0.183 | 0.851 | 0.628 | 1.835 | 0.257 |
| full | 4.348 | 0.492 | -0.572 | 0.465 | -0.124 | 0.066 | -0.006 | -0.041 | 0.013 | -0.015 | 0.082 | 0.199 | 0.178 | 0.852 | 0.646 | 1.838 | 0.242 |

## Carry-over and saturation parameters (full sample and re-tuned per training window)

Decay = share of the media effect that carries into the next week.

| sample | tv | instagram | tiktok | influencer | pos_promotion |
|---|---|---|---|---|---|
| train<104 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |
| train<117 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |
| train<130 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |
| train<143 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |
| full | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |

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
| decay instagram | 1.7 | 0.0 | 3.6 | 12.5 | 26.4 | 44.3 | 65.0 | 87.4 | 110.7 | 134.1 |
| decay tiktok | 0.0 | 12.4 | 27.4 | 44.1 | 61.7 | 79.6 | 97.4 | 114.7 | 130.8 | 143.9 |
| decay influencer | 49.8 | 24.4 | 6.4 | 0.0 | 8.6 | 32.8 | 71.0 | 119.5 | 172.2 | 220.9 |
| decay pos_promotion | 0.0 | 3.3 | 6.9 | 10.9 | 15.2 | 19.7 | 24.2 | 28.2 | 31.3 | 33.4 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.3 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.8 | 12 |
| 3 | -0.2 | 12 |
| 4 | -2.3 | 13 |
| 5 | 0.1 | 14 |
| 6 | 0.8 | 12 |
| 7 | 1.0 | 14 |
| 8 | -2.0 | 13 |
| 9 | 1.1 | 13 |
| 10 | 0.5 | 14 |
| 11 | 0.3 | 12 |
| 12 | -2.0 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 21.8% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 6.0 | 7,899,859 | 0.85 | 1.51 | 1.50 |
| instagram | 15,393 | 1,192,415 | 15.3 | 20,750,680 | 17.40 | 28.62 | 31.58 |
| tiktok | 9,332 | 1,415,019 | 18.3 | 24,640,024 | 17.41 | 28.25 | 29.65 |
| influencer | 13,406 | 1,021,938 | 32.7 | 43,978,211 | 43.03 | 63.07 | 83.44 |
| pos_promotion | 17,791 | 2,008,661 | 5.9 | 7,863,123 | 3.91 | 6.96 | 6.53 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.8% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.4 | 4,411,768 | 0.47 | 1.51 |
| instagram | 0 | 3,578,330 | 25.8 | 34,777,339 | 9.72 | 25.60 |
| tiktok | 0 | 2,861,479 | 21.0 | 28,368,107 | 9.91 | 27.28 |
| influencer | 0 | 3,099,868 | 39.9 | 53,762,008 | 17.34 | 39.80 |
| pos_promotion | 0 | 4,766,266 | 9.1 | 12,261,779 | 2.57 | 7.85 |
