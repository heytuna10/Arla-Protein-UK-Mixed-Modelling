# Step 5 – robustness of the final model (M14_hill)

ROI = revenue ROI above the observed floor (TV: vs zero); mROI = revenue per extra £ for +10% spend.

## 1. Sensitivity to the carry-over and saturation choices

One choice changed at a time, regression re-estimated.

| variant | AIC | hold-out MAPE % | ROI TV | ROI Instagram | ROI TikTok | ROI Influencer | ROI POS | mROI TV | mROI Instagram | mROI TikTok | mROI Influencer | mROI POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| final model (M14) | -497.3 | 4.22 | 0.99 | 18.58 | 16.90 | 42.81 | 3.67 | 1.72 | 30.82 | 24.80 | 74.55 | 5.47 |
| negative-exponential curve | -497.2 | 4.31 | 0.98 | 18.60 | 16.69 | 42.82 | 3.69 | 1.83 | 30.89 | 24.67 | 74.65 | 5.50 |
| log curve | -485.3 | 4.68 | 1.04 | 17.89 | 15.63 | 41.24 | 3.28 | 1.88 | 31.22 | 25.37 | 75.71 | 5.26 |
| all decays − 0.1 | -489.8 | 4.09 | 0.96 | 18.01 | 18.52 | 41.58 | 4.04 | 1.64 | 30.22 | 27.70 | 73.16 | 6.10 |
| all decays + 0.1 | -490.4 | 4.51 | 1.05 | 18.71 | 16.28 | 43.68 | 3.55 | 1.85 | 31.10 | 23.83 | 76.61 | 5.28 |
| always-on curves bend at half the mean spend | -496.9 | 4.33 | 0.95 | 19.04 | 17.78 | 43.89 | 3.95 | 1.71 | 30.54 | 24.26 | 73.90 | 5.62 |
| always-on curves bend at twice the mean spend | -490.8 | 4.40 | 1.04 | 18.10 | 16.04 | 41.67 | 3.39 | 1.73 | 31.04 | 25.21 | 75.11 | 5.30 |
| TV scale halved (more TV saturation) | -494.4 | 4.18 | 1.02 | 18.52 | 16.94 | 42.60 | 3.62 | 1.53 | 30.68 | 24.83 | 74.05 | 5.39 |
| TV scale doubled (less TV saturation) | -497.7 | 4.30 | 0.98 | 18.63 | 16.88 | 42.94 | 3.70 | 1.85 | 30.91 | 24.77 | 74.84 | 5.51 |
| average price + promo flag | -498.9 | 4.24 | 1.00 | 18.58 | 16.87 | 42.72 | 3.73 | 1.72 | 30.82 | 24.75 | 74.38 | 5.57 |
| no post-promo term | -495.0 | 4.39 | 0.99 | 18.62 | 16.56 | 42.88 | 3.54 | 1.70 | 30.61 | 24.03 | 73.87 | 5.23 |
| no January dummy | -490.8 | 4.09 | 1.05 | 18.60 | 16.96 | 42.81 | 3.50 | 1.83 | 30.95 | 24.97 | 74.86 | 5.22 |
| no lagged sales (decays re-tuned) | -441.5 | 5.61 | 1.11 | 20.29 | 15.80 | 43.39 | 3.58 | 2.05 | 34.54 | 23.43 | 77.81 | 5.36 |

Range over all rows above:

| metric | final | lowest | highest | spread % of final |
|---|---|---|---|---|
| ROI TV | 0.99 | 0.95 | 1.11 | 16 |
| ROI Instagram | 18.58 | 17.89 | 20.29 | 13 |
| ROI TikTok | 16.90 | 15.63 | 18.52 | 17 |
| ROI Influencer | 42.81 | 41.24 | 43.89 | 6 |
| ROI POS | 3.67 | 3.28 | 4.04 | 21 |
| mROI TV | 1.72 | 1.53 | 2.05 | 30 |
| mROI Instagram | 30.82 | 30.22 | 34.54 | 14 |
| mROI TikTok | 24.80 | 23.43 | 27.70 | 17 |
| mROI Influencer | 74.55 | 73.16 | 77.81 | 6 |
| mROI POS | 5.47 | 5.22 | 6.10 | 16 |

## 2. Multiplicative vs additive

The same drivers in an additive model of units (no logs), decays re-tuned (tv 0.3, instagram 0.2, tiktok 0.0, influencer 0.4, pos_promotion 0.0).

| variant | AIC | hold-out MAPE % | ROI TV | ROI Instagram | ROI TikTok | ROI Influencer | ROI POS | mROI TV | mROI Instagram | mROI TikTok | mROI Influencer | mROI POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| additive model in units (decays re-tuned) | 3,732.6 | 8.82 | 1.71 | 30.39 | 35.40 | 88.41 | 6.51 | 1.40 | 24.72 | 26.10 | 71.45 | 5.21 |

On a common scale (likelihood of units) the final model's AIC is 3,633.8 against 3,732.6 for the additive model, and the additive hold-out error is 8.8%. The ROI columns are not like for like (in an additive model the average and the marginal return coincide up to saturation); the marginal ROIs are the comparable numbers.

## 3. Stability over time

Model re-estimated on parts of the history (decays re-tuned for windows starting at week 1; windows starting later use the final decays).

| sample | lagged sales | decay TV | decay Instagram | decay TikTok | decay Influencer | decay POS | ROI TV | ROI Instagram | ROI TikTok | ROI Influencer | ROI POS | mROI TV | mROI Instagram | mROI TikTok | mROI Influencer | mROI POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all 155 weeks | 0.36 | 0.40 | 0.30 | 0.00 | 0.40 | 0.00 | 0.99 | 18.58 | 16.90 | 42.81 | 3.67 | 1.72 | 30.82 | 24.80 | 74.55 | 5.47 |
| first 104 weeks (2022–23) | 0.37 | 0.40 | 0.30 | 0.00 | 0.40 | 0.00 | 0.94 | 18.59 | 15.53 | 38.87 | 3.73 | 1.63 | 30.91 | 22.45 | 68.51 | 5.69 |
| last 104 weeks (2023–24) | 0.35 | 0.40 | 0.30 | 0.00 | 0.40 | 0.00 | 1.08 | 19.91 | 17.18 | 45.25 | 4.31 | 1.90 | 33.04 | 25.13 | 78.96 | 6.38 |
| first 78 weeks | 0.35 | 0.40 | 0.20 | 0.00 | 0.50 | 0.00 | 0.87 | 15.21 | 14.61 | 45.00 | 2.69 | 1.50 | 24.78 | 21.40 | 82.40 | 4.13 |
| last 78 weeks | 0.33 | 0.40 | 0.30 | 0.00 | 0.40 | 0.00 | 1.11 | 18.08 | 18.40 | 45.59 | 4.91 | 1.90 | 29.33 | 26.24 | 76.59 | 7.05 |

## 4. Placebo: does next week's spend 'explain' this week's sales?

It cannot be causal. If budgets were raised ahead of expected demand, these coefficients would be positive and significant.

| channel | coef on next week's spend | coef on this week's (adstocked) spend | t (HAC) | p (HAC) |
|---|---|---|---|---|
| TV | -0.079 | 1.462 | -1.228 | 0.219 |
| Instagram | 0.014 | 2.155 | 0.169 | 0.866 |
| TikTok | 0.036 | 1.417 | 0.469 | 0.639 |
| Influencer | -0.115 | 4.348 | -1.247 | 0.212 |
| POS | 0.011 | 0.530 | 0.212 | 0.832 |

Joint test of all five (HAC F-test): p = 0.70.

## 5. Influential weeks

Weeks with the largest Cook's distance: 2022-12-26, 2023-02-20, 2023-05-22, 2023-12-25, 2024-08-12.

| coefficient | all weeks | without the 5 most influential weeks | change % |
|---|---|---|---|
| tv | 1.397 | 1.389 | -0.6 |
| instagram | 2.147 | 2.101 | -2.2 |
| tiktok | 1.412 | 1.423 | 0.8 |
| influencer | 4.315 | 4.288 | -0.6 |
| pos_promotion | 0.528 | 0.522 | -1.1 |
| lagged_sales | 0.356 | 0.354 | -0.6 |
| regular_price | -0.491 | -0.440 | -10.3 |
| promo_depth | 0.449 | 0.450 | 0.3 |

## 6. Standard errors

Newey-West (4 lags) against plain OLS, with 95% intervals from the Newey-West errors.

| term | coef | se OLS | se HAC | HAC / OLS | t (HAC) | 95% low | 95% high |
|---|---|---|---|---|---|---|---|
| Intercept | 4.373 | 0.230 | 0.206 | 0.897 | 21.238 | 3.969 | 4.776 |
| lagged_sales | 0.356 | 0.017 | 0.014 | 0.812 | 25.347 | 0.329 | 0.384 |
| regular_price | -0.491 | 0.182 | 0.159 | 0.872 | -3.090 | -0.802 | -0.179 |
| promo_depth | 0.449 | 0.033 | 0.028 | 0.851 | 16.118 | 0.394 | 0.504 |
| promo_depth_lag1 | -0.061 | 0.031 | 0.025 | 0.809 | -2.444 | -0.110 | -0.012 |
| trend | 0.072 | 0.014 | 0.013 | 0.914 | 5.671 | 0.047 | 0.097 |
| season_sin1 | -0.001 | 0.006 | 0.005 | 0.876 | -0.307 | -0.011 | 0.008 |
| season_cos1 | -0.046 | 0.007 | 0.008 | 1.146 | -5.765 | -0.061 | -0.030 |
| season_sin2 | 0.020 | 0.006 | 0.005 | 0.991 | 3.603 | 0.009 | 0.031 |
| season_cos2 | -0.013 | 0.006 | 0.006 | 0.996 | -2.101 | -0.024 | -0.001 |
| january | 0.053 | 0.019 | 0.020 | 1.030 | 2.717 | 0.015 | 0.092 |
| tv | 1.397 | 0.063 | 0.052 | 0.830 | 26.843 | 1.295 | 1.499 |
| instagram | 2.147 | 0.116 | 0.139 | 1.194 | 15.466 | 1.875 | 2.419 |
| tiktok | 1.412 | 0.073 | 0.074 | 1.006 | 19.213 | 1.268 | 1.556 |
| influencer | 4.315 | 0.147 | 0.116 | 0.789 | 37.129 | 4.087 | 4.543 |
| pos_promotion | 0.528 | 0.073 | 0.075 | 1.026 | 7.023 | 0.380 | 0.675 |
