# Step 3 – alternatives around the chosen media model (M14_hill)

Each row changes one thing; decays (and scales where tuned) are re-searched for every row and inside every hold-out fold. `params` includes the grid-searched ones.

| variant | params | AIC | BIC | hold-out MAPE % | rolling MAPE % | worst fold % | Breusch-Godfrey p | max VIF | media ≥ 0 |
|---|---|---|---|---|---|---|---|---|---|
| M14 (kept) | 22 | -497.3 | -430.3 | 4.22 | 3.88 | 5.89 | 0.689 | 11.0 | yes |
| negative-exponential curve instead of Hill | 22 | -497.2 | -430.3 | 4.31 | 3.95 | 6.04 | 0.760 | 11.0 | yes |
| log curve instead of Hill | 22 | -485.3 | -418.3 | 4.68 | 4.24 | 6.61 | 0.926 | 11.2 | yes |
| square-root curve, no scale | 21 | -473.1 | -409.2 | 3.94 | 3.98 | 5.29 | 0.263 | 11.2 | yes |
| TV scale grid widened to 64 × mean | 22 | -497.7 | -430.8 | 4.35 | 3.97 | 6.08 | 0.757 | 11.0 | yes |
| a separate scale for every channel | 26 | -490.7 | -411.6 | 4.27 | 4.28 | 5.98 | 0.777 | 11.0 | yes |
| decay grid in steps of 0.05 | 22 | -497.6 | -430.6 | 4.39 | 4.02 | 6.30 | 0.710 | 11.1 | yes |
| no adstock (lagged sales only) | 17 | -423.5 | -371.8 | 5.58 | 5.57 | 6.88 | 0.040 | 10.7 | yes |
| no lagged sales (adstock only) | 21 | -441.5 | -377.6 | 5.61 | 5.42 | 7.96 | 0.001 | 12.9 | yes |
| no post-promo term | 21 | -495.0 | -431.1 | 4.39 | 4.13 | 5.92 | 0.543 | 11.0 | yes |
| no January dummy | 21 | -490.8 | -426.9 | 4.09 | 4.24 | 5.40 | 0.935 | 11.0 | yes |
| no seasonality curve | 18 | -454.1 | -399.4 | 5.64 | 5.50 | 8.53 | 0.018 | 9.8 | yes |
| 1 sine/cosine pair | 20 | -480.3 | -419.5 | 3.91 | 4.28 | 5.35 | 0.171 | 10.2 | yes |
| average price + promo flag | 22 | -498.9 | -431.9 | 4.24 | 3.99 | 6.03 | 0.762 | 13.4 | yes |

## How each channel's effect is spread over time (M14_hill)

Response of log sales to one week of extra spend: the channel's own adstock decay combined with the lagged-sales term (repeat purchase), which applies to every channel.

| channel | adstock decay | % of effect in week of spend | % within 4 weeks | weeks to 90% of effect | total / first-week effect |
|---|---|---|---|---|---|
| tv | 0.4 | 39 | 93 | 4 | 2.59 |
| instagram | 0.3 | 45 | 96 | 4 | 2.22 |
| tiktok | 0.0 | 64 | 98 | 3 | 1.55 |
| influencer | 0.4 | 39 | 93 | 4 | 2.59 |
| pos_promotion | 0.0 | 64 | 98 | 3 | 1.55 |
