# Step 7 – budget scenarios and recommendation (final model M14)

## How the scenarios work

Each scenario replays the 52 weeks of 2024 with a different media plan: same weeks, prices, promotions and weekly shocks; only media spend changes. Revenue = units × the price actually paid each week. Effects spilling into 2025 are not counted. 2024 media budget: £7.94m; revenue £50.5m.

Optimised plans maximise expected revenue for a fixed total budget. Every week keeps its place in the 2024 pattern and moves between a lower and an upper bound. TV keeps its flight calendar: on-air weeks move between the lowest on-air week and the highest week observed; off-air weeks stay off. Three sets of bounds, from tight to wide:

- **±10%**: no week moves more than 10% from its 2024 value (added by me: about the widest sustained change the data contain);
- **±20%**: no week moves more than 20% (the brief's conservative variant);
- **observed weekly range**: any week anywhere between the channel's lowest and highest week ever (the brief's main scenario).

| channel | 2024 spend £m | lowest week observed £ | highest week observed £ | lowest 13-week average observed £ | highest 13-week average observed £ |
|---|---|---|---|---|---|
| TV | 3.10 | 147,859 | 376,150 | 0 | 126,654 |
| Instagram | 1.18 | 15,393 | 40,772 | 20,763 | 28,849 |
| TikTok | 0.91 | 9,332 | 33,776 | 15,103 | 26,379 |
| Influencer | 1.07 | 13,406 | 36,009 | 18,115 | 22,178 |
| POS | 1.69 | 17,791 | 52,942 | 26,676 | 35,330 |

## Results

| scenario | media budget £m | revenue £m | Δ revenue £m (5–95%) | Δ revenue % | Δ units % | revenue per £ of media |
|---|---|---|---|---|---|---|
| A · 2024 plan as run | 7.94 | 50.54 | 0.0 (0.0–0.0) | 0 | 0 | 6.37 |
| B1 · optimised, each week within ±10% | 7.94 | 65.94 | 15.4 (14.5–16.3) | 30 | 30 | 8.30 |
| B2 · optimised, each week within ±20% | 7.94 | 83.63 | 33.1 (30.9–35.3) | 65 | 65 | 10.53 |
| B3 · optimised, observed weekly range | 7.94 | 193.62 | 143.1 (127.0–160.6) | 283 | 278 | 24.38 |
| C · 10% of TV moved to influencer | 7.94 | 75.38 | 24.8 (23.4–26.4) | 49 | 49 | 9.49 |
| D1 · budget −10%, optimised within ±20% | 7.15 | 59.44 | 8.9 (7.7–10.2) | 18 | 17 | 8.32 |
| D2 · budget +10%, optimised within ±20% | 8.73 | 88.55 | 38.0 (35.9–40.2) | 75 | 75 | 10.14 |

Intervals reflect coefficient uncertainty only. They do **not** cover the larger risk, that the response measured on small week-to-week changes does not hold for a sustained shift (see range check).

Annual spend per channel, £m:

| scenario | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| A · 2024 plan as run | 3.10 | 1.18 | 0.91 | 1.07 | 1.69 |
| B1 · optimised, each week within ±10% | 2.79 | 1.29 | 1.00 | 1.17 | 1.68 |
| B2 · optimised, each week within ±20% | 2.52 | 1.41 | 1.09 | 1.28 | 1.64 |
| B3 · optimised, observed weekly range | 1.92 | 1.91 | 1.31 | 1.87 | 0.93 |
| C · 10% of TV moved to influencer | 2.79 | 1.18 | 0.91 | 1.38 | 1.69 |
| D1 · budget −10%, optimised within ±20% | 2.52 | 1.21 | 0.78 | 1.28 | 1.35 |
| D2 · budget +10%, optimised within ±20% | 2.95 | 1.41 | 1.09 | 1.28 | 2.00 |

Change against 2024, %:

| scenario | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| A · 2024 plan as run | 0 | 0 | 0 | 0 | 0 |
| B1 · optimised, each week within ±10% | -10 | 10 | 10 | 10 | 0 |
| B2 · optimised, each week within ±20% | -19 | 20 | 20 | 19 | -3 |
| B3 · optimised, observed weekly range | -38 | 63 | 44 | 75 | -45 |
| C · 10% of TV moved to influencer | -10 | 0 | 0 | 29 | 0 |
| D1 · budget −10%, optimised within ±20% | -19 | 3 | -14 | 19 | -20 |
| D2 · budget +10%, optimised within ±20% | -5 | 20 | 20 | 19 | 19 |

Weekly plans for every scenario: `scenario_plans.csv`. Charts: `figures/scenarios.png`, `figures/allocation.png`.

## Range check: how far does each plan leave what has been observed?

The model's long-run effect needs a spend level to be held for weeks. Single weeks have ranged widely, but sustained levels have not: the highest 13-week average of influencer spend ever observed is only 11% above its long-run mean. 'Beyond sustained range' = the plan's 13-week average leaves the range of 13-week averages in the data by more than 2%.

**B1 · optimised, each week within ±10%**

| channel | change vs 2024 % | weeks above observed weekly max | plan 13-week average, max £ | highest 13-week average observed £ | plan 13-week average, min £ | lowest 13-week average observed £ | beyond sustained range |
|---|---|---|---|---|---|---|---|
| TV | -10 | 0 | 93,568 | 126,654 | 0 | 0 | no |
| Instagram | 10 | 0 | 27,396 | 28,849 | 22,839 | 20,763 | no |
| TikTok | 10 | 0 | 22,269 | 26,379 | 16,613 | 15,103 | no |
| Influencer | 10 | 0 | 24,118 | 22,178 | 21,141 | 18,115 | yes |
| POS | 0 | 0 | 34,417 | 35,330 | 29,132 | 26,676 | no |

**B2 · optimised, each week within ±20%**

| channel | change vs 2024 % | weeks above observed weekly max | plan 13-week average, max £ | highest 13-week average observed £ | plan 13-week average, min £ | lowest 13-week average observed £ | beyond sustained range |
|---|---|---|---|---|---|---|---|
| TV | -19 | 0 | 85,555 | 126,654 | 0 | 0 | no |
| Instagram | 20 | 0 | 29,887 | 28,849 | 24,916 | 20,763 | yes |
| TikTok | 20 | 0 | 24,294 | 26,379 | 18,124 | 15,103 | no |
| Influencer | 19 | 0 | 26,059 | 22,178 | 23,063 | 18,115 | yes |
| POS | -3 | 0 | 33,548 | 35,330 | 28,423 | 26,676 | no |

**B3 · optimised, observed weekly range**

| channel | change vs 2024 % | weeks above observed weekly max | plan 13-week average, max £ | highest 13-week average observed £ | plan 13-week average, min £ | lowest 13-week average observed £ | beyond sustained range |
|---|---|---|---|---|---|---|---|
| TV | -38 | 0 | 68,243 | 126,654 | 0 | 0 | no |
| Instagram | 63 | 0 | 37,240 | 28,849 | 36,318 | 20,763 | yes |
| TikTok | 44 | 0 | 26,658 | 26,379 | 23,953 | 15,103 | no |
| Influencer | 75 | 0 | 36,009 | 22,178 | 36,009 | 18,115 | yes |
| POS | -45 | 0 | 17,791 | 35,330 | 17,791 | 26,676 | yes |

**C · 10% of TV moved to influencer**

| channel | change vs 2024 % | weeks above observed weekly max | plan 13-week average, max £ | highest 13-week average observed £ | plan 13-week average, min £ | lowest 13-week average observed £ | beyond sustained range |
|---|---|---|---|---|---|---|---|
| TV | -10 | 0 | 93,158 | 126,654 | 0 | 0 | no |
| Instagram | 0 | 0 | 24,905 | 28,849 | 20,763 | 20,763 | no |
| TikTok | 0 | 0 | 20,245 | 26,379 | 15,103 | 15,103 | no |
| Influencer | 29 | 3 | 28,591 | 22,178 | 24,778 | 18,115 | yes |
| POS | 0 | 0 | 34,572 | 35,330 | 29,264 | 26,676 | no |

## Reading the numbers

- Every optimised plan does the same thing: TV to its lower bound, Instagram, TikTok and influencers to their upper bound, POS roughly unchanged under tight bounds and cut under wide ones. The allocation is set by the bounds, as expected; the *direction* is the finding.
- The size is not credible as a forecast. A ±10% reshuffle is credited with +30% revenue, ±20% with +65%, the observed weekly range with +283%. This is the arithmetic of the marginal ROIs (an extra £ of influencer spend ≈ £75 of revenue) applied to a sustained shift, compounded because the model is multiplicative. No brand triples its revenue by moving £1m of media.
- What the data support: week-to-week movements in social and influencer spend line up with large movements in sales, robustly (step 5). What they cannot show: that the same response holds when the level is raised and kept there.

## Recommendation

1. **Direction:** shift budget from TV to influencers, Instagram and TikTok. Every scenario, every model variant and both halves of the history agree on the ranking.
2. **First step: the ±10% plan (B1)**: TV −10% within its flights, influencer, Instagram and TikTok +10% each, POS unchanged, total budget unchanged. It stays inside the sustained range for every channel except influencer (9% above the highest 13-week average seen).
3. **Treat the first step as a test.** Present the model-implied gain as an upper bound, not a plan number, and measure: e.g. raise influencer and social spend for one quarter, or in some regions, and compare. Scale further only on that evidence.
4. **Do not use the wide scenarios (B2, B3, C) as plan numbers.** They are shown to make the extrapolation visible.

## The board's question: do TV and in-store promotion earn their share?

- **TV**: 39% of media spend, 7% of sales. Revenue ROI 0.99 on the average £ and 1.72 on the next £. It pays for itself only above a gross margin of 58% at the margin (and not at all on average: ROI ≈ 1 means £1 of revenue per £1 spent). It is the weakest channel by a factor of three or more, and the first to cut in every scenario. No saturation was found, so cutting within flights loses revenue proportionally, no more.
- **POS promotion spend**: 20% of media spend, 6% of sales. Revenue ROI 3.7 and 5.5 on the next £; pays above a margin of about 18%. It earns its keep but is the second-weakest channel; hold it, do not grow it ahead of social.
- **Price promotions** (not a media line, but the larger in-store question): they lifted units by 6% and cost 3.7% of revenue (£5.2m over three years). On revenue they do not earn their share; fewer or shallower promotions is the first lever to test.
