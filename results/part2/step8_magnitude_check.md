# Step 8 – magnitude check: are the effect sizes plausible?

Advertising elasticity = % change in units for 1% more spend. Benchmark: the meta-analysis of Sethuraman, Tellis & Briesch (2011, *Journal of Marketing Research* 48(3), 457–471), mean over published brand-level estimates: **0.12 short-term, 0.24 long-term**.

Ours, from the final model (M14): *long-term* = % change in total units over the history when the channel's spend is 1% higher in every week (adstock and repeat purchase included); *short-term* = the part that arrives in the week of the spend. Intervals: coefficient uncertainty only.

| channel | short-term, week of spend (5–95%) | long-term (5–95%) | long-term if the typical level were held | short-term ÷ benchmark | long-term ÷ benchmark |
|---|---|---|---|---|---|
| TV | 0.05 (0.04–0.05) | 0.12 (0.11–0.13) | 0.35 | 0.4 | 0.5 |
| Instagram | 0.37 (0.33–0.41) | 0.83 (0.73–0.93) | 0.83 | 3.1 | 3.4 |
| TikTok | 0.35 (0.32–0.38) | 0.54 (0.49–0.59) | 0.55 | 2.9 | 2.2 |
| Influencer | 0.64 (0.62–0.67) | 1.67 (1.59–1.75) | 1.68 | 5.4 | 7.0 |
| POS | 0.13 (0.10–0.16) | 0.20 (0.15–0.25) | 0.20 | 1.1 | 0.8 |

TV's first two columns are over its actual flight calendar (on air in 41 of 156 weeks); held on air at its average on-air weight its long-term elasticity would be the third column.

## Reading

- TV (0.12) and POS (0.20) are in the range the literature finds.
- Instagram (0.83), TikTok (0.54) and above all influencer (1.67) are 2 to 7 times the long-term benchmark. An elasticity above 1 means sales grow faster than the spend that causes them; published estimates of that size are rare.
- So the ranking (social and influencers ahead of POS, POS ahead of TV) is credible and robust (step 5), but the *size* of the social and influencer effects should be treated as untested. This is the strongest argument for the recommendation "direction yes, size to be tested".

## Why might they be this large?

1. **Teaching dataset.** The data were built for the course; effect sizes need not be calibrated to real markets.
2. **Spend in £, not exposure.** We see budgets, not impressions or reach. If the cost per contact fell over time or differs by week, £ understate the change in exposure and the elasticity per £ is inflated.
3. **Budgets that follow demand.** If social and influencer budgets are set higher in periods when demand is expected to be high (launches, seasons, retailer events), the model credits the spend with sales that would have come anyway. The placebo test in step 5 found no sign of this from one week to the next, but it cannot see planning at monthly or quarterly horizons.
4. **Narrow range.** Held spend levels moved by only 11–43% around their mean; a slope measured on small movements is then extrapolated by the curve.

## Why some £ response curves bend upwards

The model is multiplicative: a channel held at spend x multiplies sales by exp(B × f(x)), with f(x) = x / (x + scale) and B = its coefficient ÷ (1 − lagged-sales coefficient). f shows diminishing returns in *percent*. But a given percent lift is worth more £ the larger the sales it applies to, so in £ the curve can rise ever faster before it flattens. It bends upwards for spend below scale × (B/2 − 1).

| channel | long-run coefficient B | max. sales multiple exp(B) | curve bends upwards below £/week | lowest 13-week average observed £ | highest 13-week average observed £ | bends upwards over |
|---|---|---|---|---|---|---|
| TV | 2.17 | 9 | 79,767 | 0 | 126,654 | the lower part of the held range |
| Instagram | 3.34 | 28 | 15,418 | 20,763 | 28,849 | nowhere in the held range |
| TikTok | 2.19 | 9 | 1,795 | 15,103 | 26,379 | nowhere in the held range |
| Influencer | 6.70 | 816 | 47,048 | 18,115 | 22,178 | the whole held range |
| POS | 0.82 | 2 | 0 | 26,676 | 35,330 | nowhere in the held range |

- Only influencer bends upwards over its whole observed range (and TV at low sustained weights). Its B of 6.7 says that saturating the channel would multiply sales by 816 against zero spend. Nobody should believe that; it is what a steep slope measured on a narrow range turns into when the formula is followed outside it.
- This is why every optimiser pushes influencer to its bound, why the scenario gains grow faster than the budget shift, and why the interface flags plans whose 13-week average leaves the observed range.
