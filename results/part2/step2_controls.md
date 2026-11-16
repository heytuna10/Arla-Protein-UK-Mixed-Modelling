# Step 2 – alternatives around the chosen controls (M5)

Each row changes one thing in M5 (media still as in part 1: log(spend + 1), lagged sales). Same sample and error measures as `model_comparison.md`.

| variant | params | AIC | BIC | hold-out MAPE % | rolling MAPE % | worst fold % | Breusch-Godfrey p | max VIF | media ≥ 0 |
|---|---|---|---|---|---|---|---|---|---|
| M5 (kept) | 16 | -412.1 | -363.4 | 4.83 | 4.97 | 5.48 | 0.007 | 10.8 | yes |
| no seasonality curve | 12 | -399.6 | -363.0 | 6.97 | 6.36 | 10.02 | 0.423 | 9.6 | yes |
| 1 sine/cosine pair | 14 | -402.8 | -360.2 | 5.42 | 5.51 | 7.24 | 0.239 | 9.9 | yes |
| 3 sine/cosine pairs | 18 | -409.1 | -354.3 | 4.89 | 5.23 | 6.17 | 0.004 | 10.9 | yes |
| no January dummy (= M4) | 15 | -406.9 | -361.2 | 4.90 | 5.27 | 6.05 | 0.021 | 10.7 | yes |
| Christmas + New-Year weeks instead of January | 17 | -412.4 | -360.6 | 4.79 | 4.71 | 5.68 | 0.023 | 10.8 | yes |
| January + Christmas weeks | 17 | -412.0 | -360.3 | 4.94 | 5.02 | 5.80 | 0.008 | 10.8 | yes |
| trend with slope change after year 1 | 17 | -410.5 | -358.8 | 4.53 | 4.76 | 5.27 | 0.004 | 53.4 | yes |
| no trend | 15 | -394.9 | -349.2 | 8.97 | 8.04 | 9.02 | 0.203 | 2.2 | yes |
| average price + promo flag (part 1 price spec) | 16 | -414.5 | -365.8 | 4.40 | 4.79 | 5.33 | 0.007 | 13.3 | yes |
| regular price + promo depth + promo flag | 17 | -411.6 | -359.8 | 4.86 | 5.08 | 5.59 | 0.007 | 20.6 | yes |
| promo depth only (no regular price) | 15 | -403.3 | -357.6 | 6.04 | 5.55 | 6.43 | 0.134 | 2.2 | yes |
| no post-promo term (= M3 + January) | 15 | -388.8 | -343.1 | 5.33 | 6.63 | 9.36 | 0.085 | 10.7 | yes |
| no lagged sales | 15 | -130.5 | -84.8 | 8.66 | 11.28 | 14.81 | 0.000 | 10.7 | yes |
