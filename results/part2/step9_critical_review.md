# Step 9 – critical review of the part-2 results

What we can claim, what we cannot, and what would improve the work before 22 Nov. Tables behind every number: `step9_diagnostics.md` (rebuild with `python scripts/run_review.py`).

## Verdict

The concern is justified, and the diagnostics sharpen it in a useful way.

- **The sizes are not credible as real-market effects.** The model credits media with about three quarters of sales and influencers alone with 30%. The five long-term advertising elasticities add up to 3.4, against a published average of 0.24 for a brand's advertising. Moving £0.3m of budget is credited with +£15m revenue.
- **The model is not making them up.** Every artefact we could test for is absent (next section). The effects are in the data: measured almost entirely on week-to-week movements of spend, the same in every sub-period and every specification, with t-values of 15 to 37.
- **So the most likely explanation is the data itself:** a teaching dataset with strong effects built in, where spend moves almost at random from week to week and sales respond to it. The one real-world explanation we cannot rule out is spend reacting to demand *within* the week; only exposure data or an experiment can settle that.
- **The recommendation survives without the sizes.** Even if every digital channel had only the benchmark elasticity, an extra £ of Instagram, TikTok or influencer spend would still return £9–11 of revenue, against £5.5 for POS and £1.7 for TV, because the digital budgets are small relative to revenue. What does not survive is the order among the three digital channels and the size of the gain: the first-step plan would add about +6% to sales, not +28%.

That is the story to tell: direction and ranking are robust, the size is between "benchmark" and "model" and has to be tested, and the test is cheap.

## What we tested

| hypothesis | test | result | conclusion |
|---|---|---|---|
| Budgets follow demand from week to week | spend regressed on last week's sales; does spend rise in promotion weeks, when demand is 13% higher? | no response for TV or any digital channel (p 0.28–0.86 on last week's sales; promotion coefficients ≈ 0) | not supported |
| Budgets are planned where demand is expected (month, quarter) | future spend (next 1, 4, 8 weeks) as a placebo; effect of the 13-week spend level against the week-to-week deviation | no signal for the always-on channels; level and deviation give the same coefficient (influencer 4.32 and 4.33); 74–97% of the variation is week-to-week | not supported: planning cannot produce an effect that sits in the weekly wiggles |
| One digital effect split three ways | spend correlations; model with one "digital" channel | the three budgets are uncorrelated (largest r 0.12); one digital channel is far worse (hold-out error 10.9% against 4.2%) | rejected: three distinct effects |
| Spend reacts to demand within the same week (platform pacing) | not testable with weekly spend in £ | – | open; needs impressions or an experiment |
| POS spend and price promotions are run together | spend on promotion depth | yes: POS spend is about 30% higher in a 24%-off week (p < 0.001) | the model controls for promotions, but POS (ROI 3.7) and promotions (lose revenue) are less cleanly separated than the other effects |
| TV is scheduled around demand | 8-week placebo | significant for TV (p 0.005), small, negative sign; joint tests not significant | weak evidence; if anything it would mean TV's true effect is not larger than estimated |
| Repeat purchase inflates the long-term numbers | compare short-term elasticities | already 3–5 times the short-term benchmark in the week of spend (influencer 0.64 against 0.12) | the lagged-sales term scales everything by 1.55 but is not the source |

Two facts make the size less absurd than it first looks, and belong in the answer if the jury asks. First, media spend is 18% of revenue in this dataset, so a large media share of sales is less surprising than for a brand spending a few percent. Second, the contributions are measured against the minimum spend and a multiplicative model, where a share of sales is not the same as "sales that would vanish".

## What we can and cannot claim

**Can claim**

1. The model forecasts well: 4.2% error on 26 unseen weeks, 4.0% on 12-week forecasts, 92% of weeks inside the 90% band.
2. The ranking digital > POS > TV, at the margin and on average. It holds in every specification and sub-period, and still holds if the digital effects are cut to benchmark size.
3. TV does not pay back at the margin unless the gross margin exceeds 58%. This is the most believable number in the model: TV's elasticity (0.12) is in line with the literature.
4. Price promotions add volume and lose revenue at every depth observed.
5. Effects are short-lived: most of any channel's effect arrives within four weeks.

**Cannot claim**

1. The size of the gain from reallocating. Honest range for the first-step plan: about +6% of sales if digital effects are benchmark-sized, up to +28% if the model is right.
2. The order among Instagram, TikTok and influencer. At benchmark size they are indistinguishable (£9–11 per extra £).
3. Anything about sustained spend more than about 10% away from today's levels.
4. Profit. We only see revenue, at what are probably shelf prices.
5. That POS spend "earns its keep" independently of promotions. It is measured mostly in weeks when a promotion runs as well.

## Profit view

Profit per extra £ = margin × revenue per extra £ − 1. Margin is not in the data. We use 20–40% of revenue: listed US food processors average a gross margin of about 23% (Damodaran, NYU Stern, January 2026 sector data, as reproduced [here](https://www.christopholivierconsulting.com/profit-margin-by-industry/); his own tables confirm the 10.6% operating margin), and branded chilled products sit above commodity dairy. The revenue in our data is probably at shelf prices, of which the retailer keeps a part, so the lower end is the realistic one. An assumption to replace with Arla's own number.

| profit per extra £ | TV | POS | TikTok | Instagram | Influencer |
|---|---|---|---|---|---|
| at 20% margin, as estimated | −0.66 | +0.09 | +3.96 | +5.16 | +13.91 |
| at 30% margin, as estimated | −0.48 | +0.64 | +6.44 | +8.25 | +21.36 |
| at 40% margin, as estimated | −0.31 | +1.19 | +8.92 | +11.33 | +28.82 |
| at 20% margin, digital at benchmark size | −0.66 | +0.09 | +1.21 | +0.79 | +1.14 |
| at 30% margin, digital at benchmark size | −0.48 | +0.64 | +2.32 | +1.69 | +2.22 |
| effect could be overstated by a factor of … and still pay (30%) | – | 1.6 | 7.4 | 9.3 | 22.4 |

- TV loses money on the next £ at every margin in the range. POS is at break-even at 20% and pays at 30%.
- The digital channels pay at every margin, also at benchmark size. This is the robust core of the recommendation, and it is a profit statement the board can use.

## Test design for the recommendation

No regional data exist, so the test is over time, read against the model's forecast for the unchanged plan (the dashboard interface produces exactly this forecast and its band).

1. **Weeks 1–13: run the first-step plan.** TV −10% within its flights, Instagram, TikTok and influencer +10% each, total budget unchanged. Keep the price and promotion calendar as planned and record what actually ran.
2. **Read-out:** average of actual sales against the forecast for the old plan, given the prices and promotions that actually ran. The model predicts +28% (influencer +15%, Instagram +7%, TikTok +5%, TV −1%). Benchmark-sized effects would give about +6%.
3. **What 13 weeks can detect:** a change of 3–6% in sales (5% one-sided test, 80% power; 3% from the model's own forecast errors, 6% from five out-of-sample forecasts). On the more favourable of the two bases, eight weeks detect about 5% and 26 weeks about 2%. So 13 weeks separate "model" from "benchmark" beyond doubt and are just enough to see a benchmark-sized effect.
4. **Weeks 14–21: return to the old plan.** The uplift should fade within about four weeks. This protects against a demand shift that happened to coincide with the test.
5. **Decision rule** on the 13-week uplift:

| uplift against forecast | reading | action |
|---|---|---|
| +15% or more | effects of the model's order of magnitude | take the next +10% step, re-estimate with the new weeks |
| +6% to +15% | real, but smaller than modelled | keep the shift, rescale the response curves to the test result before any further step |
| below +6%, above zero | benchmark-sized or smaller | keep the shift only on the profit argument; drop all revenue-gain claims; extend the test to 26 weeks |
| zero or negative | the model's digital effects are not causal | return to the old plan |

6. **Cost of being wrong:** the only thing given up is 10% of TV, which the model values at 1.2% of sales (about £150k of revenue in a quarter).
7. **Option:** raise the channels one after another (influencer first, eight weeks each) to read them separately. Influencer alone is detectable if the model is right (+15%), not if it is benchmark-sized (+2.4%).

## Shrinkage towards plausible sizes: proposal (not built)

**What to expect.** The estimates are very precise, so a prior only matters if it is strong. Example, influencer: coefficient 4.32, standard error 0.12. A prior centred on the benchmark-sized coefficient (0.62) with a standard deviation as large as its mean moves the estimate to about 4.2. To pull it halfway, the prior would have to claim the true value is known to within ±20% of the benchmark. In other words: with an honest prior nothing changes, with a strong prior we get the prior back. A posterior is therefore not the interesting output. The interesting output is **what it costs the model to be plausible**: how much fit and forecast accuracy are lost as the effects are forced towards the benchmark, and what the recommendation looks like there.

| option | what it is | effort | risk to 22 Nov | value |
|---|---|---|---|---|
| **A. Benchmark-anchored regression (recommended)** | Normal priors on the five media coefficients centred on benchmark-sized values, in closed form (same as a ridge penalty towards a target instead of towards zero; carry-over and curves fixed). Sweep the prior strength from none to dogmatic; report elasticities, return per extra £, hold-out error and the first-step gain along the sweep. One table, one figure. | 2–3 hours, no new dependency | low | shows the jury a tested range instead of one number; expected result: ranking digital > POS > TV survives the whole sweep, hold-out error rises sharply as effects approach the benchmark |
| B. Ridge as in Robyn | Penalise towards zero, strength by cross-validation. | 1–2 hours | low | little: cross-validation will choose almost no penalty because the effects are so sharply identified |
| C. Full Bayesian model (PyMC-Marketing) | Priors on coefficients, carry-over and saturation; full posterior. | 1–1.5 days incl. dependency, convergence checks and redoing contributions | high | same answer as A expected; only worth it if a Bayesian model is graded as such |

Recommended: A, plus one use of it in the dashboard (improvement 4 below). Waiting for a decision before building.

## Improvements, ranked

| # | improvement | expected impact | effort | risk to deadline |
|---|---|---|---|---|
| 1 | **Reframe the slides around what survives:** ranking and profit hold even at benchmark size; gain quoted as a range (+6% benchmark-sized to +28% model); magnitude check and "what we tested" as one slide | high: turns the weakest point into the strongest | 1 hour, text only | none |
| 2 | **Profit table and test design on the slides** (both sections above) | high: answers the board in its own terms | done here; 30 minutes to move into SUMMARY | none |
| 3 | **Benchmark-anchored regression** (option A) | medium: a tested range and a figure instead of an argument | 2–3 hours | low |
| 4 | **"Conservative mode" in the dashboard interface:** a switch that scales the digital effects to benchmark size, so every scenario shows a range instead of one very large number | high for part 3: the dashboard otherwise shows +30% for small changes | 2 hours after 3; needs agreement with the dashboard team | low to medium |
| 5 | **Report POS and price promotions together** as "in-store" in one sensitivity, since they run in the same weeks | low to medium | 1 hour | low |
| 6 | **Limitations slide: what data would settle it:** impressions or reach per channel, competitor prices, distribution, regional sales | medium, costs nothing | 15 minutes | none |
| 7 | Full Bayesian model (option C) | low beyond 3 | 1–1.5 days | high |
| 8 | Time-varying effects, more synergy terms, other curves | none expected: steps 4–5 found nothing | – | – |

Recommended for this week: 1, 2, 6 now; 3 and 4 if the planning side agrees; not 7.

## Proposed wording changes for the slides

- Decomposition slide: add "media spend is 18% of revenue; shares are measured above each channel's minimum spend".
- ROI slide: add the profit row at 20–30% margin and the line "also holds if digital effects were only as large as the literature average".
- Scenario slide: replace "+£15m (upper bound)" by "between about +6% (benchmark-sized effects) and +28% (model) over a quarter; the test tells us where".
- New slide "How we tried to break it": the table in "What we tested".
- Recommendation slide: the 13-week test with its decision rule.
