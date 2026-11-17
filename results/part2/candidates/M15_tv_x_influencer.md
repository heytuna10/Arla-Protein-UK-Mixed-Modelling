# M15_tv_x_influencer

M14 + tv × influencer: TV makes the brand familiar, so influencer posts convert better while TV is on air

n = 155, parameters = 23, R² = 0.977, AIC = -495.3, BIC = -425.3

## Coefficients (HAC = Newey-West, 4 lags)

| term | coef | se_ols | se_hac | p_hac |
|---|---|---|---|---|
| Intercept | 4.3644 | 0.2353 | 0.2123 | 0.0000 |
| lagged_sales | 0.3568 | 0.0175 | 0.0142 | 0.0000 |
| regular_price | -0.4859 | 0.1846 | 0.1626 | 0.0028 |
| promo_depth | 0.4493 | 0.0329 | 0.0280 | 0.0000 |
| promo_depth_lag1 | -0.0617 | 0.0312 | 0.0253 | 0.0148 |
| trend | 0.0716 | 0.0140 | 0.0129 | 0.0000 |
| season_sin1 | -0.0015 | 0.0056 | 0.0049 | 0.7641 |
| season_cos1 | -0.0458 | 0.0070 | 0.0079 | 0.0000 |
| season_sin2 | 0.0198 | 0.0056 | 0.0055 | 0.0003 |
| season_cos2 | -0.0125 | 0.0060 | 0.0060 | 0.0360 |
| january | 0.0533 | 0.0191 | 0.0196 | 0.0066 |
| tv | 1.3950 | 0.0638 | 0.0542 | 0.0000 |
| instagram | 2.1471 | 0.1167 | 0.1390 | 0.0000 |
| tiktok | 1.4136 | 0.0737 | 0.0746 | 0.0000 |
| influencer | 4.3173 | 0.1482 | 0.1154 | 0.0000 |
| pos_promotion | 0.5270 | 0.0735 | 0.0750 | 0.0000 |
| ix_tv_influencer | 0.3394 | 1.9072 | 1.5489 | 0.8266 |

## Coefficient stability (expanding training windows)

| sample | Intercept | lagged_sales | regular_price | promo_depth | promo_depth_lag1 | trend | season_sin1 | season_cos1 | season_sin2 | season_cos2 | january | tv | instagram | tiktok | influencer | pos_promotion | ix_tv_influencer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train<104 | 4.238 | 0.370 | -0.561 | 0.438 | -0.067 | 0.084 | -0.002 | -0.051 | 0.022 | -0.016 | 0.063 | 1.426 | 2.282 | 1.382 | 4.123 | 0.560 | 2.169 |
| train<117 | 4.307 | 0.364 | -0.580 | 0.451 | -0.050 | 0.084 | -0.001 | -0.049 | 0.024 | -0.015 | 0.048 | 1.424 | 2.254 | 1.414 | 4.196 | 0.502 | 0.784 |
| train<130 | 4.385 | 0.352 | -0.474 | 0.423 | -0.042 | 0.076 | 0.000 | -0.054 | 0.024 | -0.011 | 0.058 | 1.374 | 2.292 | 1.357 | 4.311 | 0.506 | 0.307 |
| train<143 | 4.357 | 0.358 | -0.450 | 0.429 | -0.053 | 0.069 | 0.000 | -0.045 | 0.020 | -0.011 | 0.051 | 1.396 | 2.136 | 1.387 | 4.321 | 0.535 | 0.057 |
| full | 4.364 | 0.357 | -0.486 | 0.449 | -0.062 | 0.072 | -0.001 | -0.046 | 0.020 | -0.013 | 0.053 | 1.395 | 2.147 | 1.414 | 4.317 | 0.527 | 0.339 |

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
| decay tv | 55.0 | 38.2 | 22.0 | 8.2 | 0.0 | 3.2 | 27.3 | 82.4 | 162.7 | 220.0 |
| decay instagram | 21.7 | 9.2 | 1.3 | 0.0 | 7.0 | 23.2 | 48.0 | 79.9 | 116.4 | 153.4 |
| decay tiktok | 0.0 | 5.9 | 18.2 | 35.5 | 56.5 | 80.2 | 106.1 | 134.2 | 163.6 | 189.2 |
| decay influencer | 96.5 | 63.7 | 33.3 | 9.8 | 0.0 | 11.8 | 49.2 | 108.5 | 178.5 | 246.2 |
| decay pos_promotion | 0.0 | 3.0 | 6.2 | 9.9 | 14.0 | 19.0 | 24.8 | 31.3 | 38.3 | 46.0 |

| scale × mean spend → | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 |
|---|---|---|---|---|---|
| scale tv | 59.2 | 30.3 | 11.4 | 2.7 | 0.0 |

## Residual patterns (mean residual in %, positive = model too low)

| year | mean | count |
|---|---|---|
| 2022 | -0.4 | 51 |
| 2023 | 0.4 | 52 |
| 2024 | 0.0 | 52 |

| month | mean | count |
|---|---|---|
| 1 | 0.0 | 14 |
| 2 | 2.8 | 12 |
| 3 | -0.1 | 12 |
| 4 | -2.6 | 13 |
| 5 | 0.3 | 14 |
| 6 | 1.6 | 12 |
| 7 | 0.3 | 14 |
| 8 | -1.3 | 13 |
| 9 | 0.1 | 13 |
| 10 | 1.0 | 14 |
| 11 | 0.8 | 12 |
| 12 | -2.8 | 12 |

## Contributions and revenue ROI – reference: observed floor (TV: zero)

Base = 20.8% of sales; base + channels = 100.00% of actual sales (largest weekly gap 0.000 units).

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi | marginal_roi |
|---|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 7.0 | 9,193,847 | 0.99 | 1.78 | 1.72 |
| instagram | 15,393 | 1,192,415 | 16.4 | 22,173,937 | 18.60 | 30.81 | 30.84 |
| tiktok | 9,332 | 1,415,019 | 17.7 | 23,955,355 | 16.93 | 27.94 | 24.83 |
| influencer | 13,406 | 1,021,938 | 32.4 | 43,718,096 | 42.78 | 63.77 | 74.66 |
| pos_promotion | 17,791 | 2,008,661 | 5.6 | 7,362,721 | 3.67 | 6.64 | 5.46 |

`roi` = Shapley share of incremental revenue / spend above the reference; `last_in_roi` = revenue lost if only this channel is cut to its reference; `marginal_roi` = revenue per extra £ for +10% spend in every week.

## Sensitivity – reference: zero spend for every channel

Base = 0.1% of sales.

| channel | reference_spend | incremental_spend | pct_of_sales | incremental_revenue | roi | last_in_roi |
|---|---|---|---|---|---|---|
| tv | 0 | 9,310,186 | 3.6 | 4,655,866 | 0.50 | 1.78 |
| instagram | 0 | 3,578,330 | 28.1 | 37,889,723 | 10.59 | 30.37 |
| tiktok | 0 | 2,861,479 | 21.7 | 29,192,402 | 10.20 | 31.10 |
| influencer | 0 | 3,099,868 | 36.7 | 49,456,577 | 15.95 | 41.88 |
| pos_promotion | 0 | 4,766,266 | 9.8 | 13,200,646 | 2.77 | 9.37 |
