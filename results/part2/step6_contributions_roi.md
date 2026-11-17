# Step 6 – contributions, ROI and marginal ROI (final model M14)

History: 155 weeks (10 Jan 2022 – 23 Dec 2024). Intervals: 5–95% range over 2,000 coefficient draws from the Newey-West covariance; carry-over decays and curve scales are held at their estimates (their effect is in `step5_robustness.md`: at most ±15% on any ROI). Revenue ROI, not profit.

## 1. Channel contributions and returns

Reference: TV against zero spend; the four always-on channels against their lowest weekly spend observed. Base incl. that minimum media: 20.8 (19.5–22.1)% of sales.

| channel | spend £m | share of media spend % | % of sales (5–95%) | revenue ROI above floor (5–95%) | marginal ROI (5–95%) | break-even margin %, next £ | break-even margin %, average £ above floor |
|---|---|---|---|---|---|---|---|
| TV | 9.31 | 39 | 7.1 (6.7–7.5) | 0.99 (0.94–1.05) | 1.72 (1.60–1.84) | 58.1 | 100.6 |
| Instagram | 3.58 | 15 | 16.4 (14.7–18.1) | 18.58 (16.65–20.49) | 30.82 (27.09–34.69) | 3.2 | 5.4 |
| TikTok | 2.86 | 12 | 17.7 (16.4–19.0) | 16.90 (15.64–18.17) | 24.80 (22.53–27.06) | 4.0 | 5.9 |
| Influencer | 3.10 | 13 | 32.5 (31.4–33.6) | 42.81 (41.37–44.29) | 74.55 (70.85–78.54) | 1.3 | 2.3 |
| POS | 4.77 | 20 | 5.6 (4.3–6.8) | 3.67 (2.81–4.50) | 5.47 (4.15–6.73) | 18.3 | 27.3 |

- *Revenue ROI above floor*: incremental revenue / spend above the floor (TV: / total spend).
- *Marginal ROI*: revenue per extra £ if the channel's spend were 10% higher in every week.
- *Break-even margin*: the gross margin at which the £ pays for itself = 1 / ROI. Margin is not in the data; read the column against whatever margin the business has (e.g. at a 40% margin, anything below 40 pays off).

## 2. Decomposition of sales (% of units)

Shapley split over seven drivers (five channels, price promotions, underlying growth); the parts add up to actual sales. Weekly series: `decomposition_weekly.csv`; chart: `figures/decomposition.png`.

| period | base incl. minimum always-on media | growth since Jan 2022 | price promotions | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|---|---|---|
| 2022 | 19.4 | 2.7 | 2.6 | 7.5 | 16.4 | 16.3 | 30.2 | 4.9 |
| 2023 | 16.8 | 7.8 | 2.1 | 6.1 | 15.5 | 18.2 | 28.5 | 5.0 |
| 2024 | 14.3 | 12.3 | 3.7 | 6.2 | 13.6 | 14.5 | 30.1 | 5.3 |
| all | 16.7 | 7.9 | 2.9 | 6.5 | 15.1 | 16.3 | 29.6 | 5.1 |
| all, p5 | 15.5 | 5.9 | 2.5 | 6.2 | 13.5 | 15.1 | 28.3 | 3.9 |
| all, p95 | 18.0 | 9.9 | 3.3 | 6.9 | 16.6 | 17.4 | 30.9 | 6.3 |

Price promotions here = extra units against paying the shelf price in every week. Growth = the trend since the first week (+7% a year); seasonality and the shelf-price level are inside the base.

## 3. What changed against part 1, and why

| revenue ROI | part 1 (its own method) | part 1 model, contributions that add up | final model | part 1 model, marginal ROI | final model, marginal ROI |
|---|---|---|---|---|---|
| TV | 0.23 | 0.97 | 0.99 | 0.16 | 1.72 |
| Instagram | 13.24 | 17.43 | 18.58 | 30.27 | 30.82 |
| TikTok | 13.56 | 20.18 | 16.90 | 30.79 | 24.80 |
| Influencer | 30.61 | 39.80 | 42.81 | 72.83 | 74.55 |
| POS | 3.67 | 5.25 | 3.67 | 8.20 | 5.47 |

- Part 1's own numbers are short-run and do not add up (channels sum to 149% of sales).
- Column 2 is the same model with carry-over counted and contributions forced to add up; column 3 the final model. The always-on channels move little; the ranking is unchanged.
- TV changes most at the margin: 0.16 → 1.72. Part 1 used log(spend + 1), which turns TV into an on/off switch, so 10% more TV spend did almost nothing in that model.
- POS falls (5.3 → 3.7) once each channel has its own carry-over: POS has none of its own, whereas part 1's single lagged-sales term gave every channel the same 2.3× long-run multiplier.

## 4. Price promotions (kept separate from POS spend)

Over the history there were 51 promotion weeks at an average 24% off. Against charging the shelf price in every week, and counting the dip in the week after and repeat purchase:

- units: **+6.2%** (+5.3 to +7.1);
- revenue: **-3.7%** (-4.5 to -2.9), i.e. £-5.2m over three years, about £102k of revenue given up per promotion week.

One promotion week at different discounts (stylised: starting from a normal week; % of a normal week's units or revenue):

| discount | units, promo week % | revenue, promo week % | following weeks % | total units % | total revenue % | total revenue p5 | total revenue p95 | units uplift needed to break even % |
|---|---|---|---|---|---|---|---|---|
| 10% off | 4.8 | -5.6 | 1.6 | 6.5 | -4.0 | -4.9 | -3.1 | 11.1 |
| 15% off | 7.6 | -8.6 | 2.5 | 10.1 | -6.1 | -7.4 | -4.7 | 17.6 |
| 20% off | 10.5 | -11.6 | 3.5 | 14.0 | -8.1 | -10.0 | -6.3 | 25.0 |
| 24% off | 13.1 | -14.0 | 4.3 | 17.4 | -9.8 | -12.0 | -7.5 | 31.6 |
| 30% off | 17.4 | -17.8 | 5.5 | 22.9 | -12.3 | -15.2 | -9.4 | 42.9 |
| 35% off | 21.3 | -21.1 | 6.7 | 28.1 | -14.4 | -17.8 | -10.9 | 53.8 |

The uplift is far below what a discount needs to pay for itself in revenue (last column), at every depth. Promotions buy volume, not revenue, and since the margin on a discounted unit is lower still, not profit either. Not in the model: retailer listing or shelf-space benefits, and any long-term effect on what shoppers consider the normal price.

## 5. Shelf price

|  | estimate | p5 | p50 | p95 |
|---|---|---|---|---|
| elasticity in the week of the change | -0.49 | -0.75 | -0.49 | -0.23 |
| total elasticity (incl. repeat purchase) | -0.76 | -1.15 | -0.76 | -0.37 |
| units after a 5% shelf-price increase % | -3.65 | -5.47 | -3.64 | -1.80 |
| revenue after a 5% shelf-price increase % | 1.17 | -0.75 | 1.18 | 3.11 |

Demand is inelastic: a higher shelf price loses fewer units than it gains in price. Caveat: identified from four upward price steps that coincide with the growth trend (VIF 11), so the interval is wide and includes no revenue gain at all.

In pence, for a manager (the per-1p / per-10p / per-1% view comes from Ketan's part-1 notebook). Per week, from the current shelf price of £1.61 and the 2024 average week (700k units, £972k revenue), once repeat purchase has settled:

| shelf price | new shelf price £ | price change % | units per week (5–95%) | revenue per week £ (5–95%) |
|---|---|---|---|---|
| +1p | 1.62 | 0.6 | -3,298 (-4,986 to -1,615) | +1,432 (-925 to +3,782) |
| +5p | 1.66 | 3.1 | -16,141 (-24,284 to -7,942) | +7,092 (-4,559 to +18,823) |
| +10p | 1.71 | 6.2 | -31,447 (-47,042 to -15,563) | +14,023 (-8,962 to +37,435) |
| +1% | 1.63 | 1.0 | -5,293 (-7,995 to -2,594) | +2,302 (-1,486 to +6,084) |

## 6. Response curves

`figures/response_curves.png`, data in `response_curves.csv`: weekly revenue against a constant weekly spend per channel, with the range the model has evidence for. Carry-over profile per channel: `step3_media.md`.
