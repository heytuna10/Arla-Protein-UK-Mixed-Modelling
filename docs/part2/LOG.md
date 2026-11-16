# Part 2 – Work log

Append-only, newest entry at the bottom. One entry per run, written by Claude Code before it finishes. Keep each entry readable in about a minute; put the numbers in `results/part2/` and link them.

```
## YYYY-MM-DD · Step N(–M) · short title
**Done:** what was built or run (files touched).
**Decisions:** decision — why — alternatives rejected.
**Results:** 2–5 key numbers + link to the table/figure.
**For the slides:** 0–2 bullets in plain language (optional).
**Open questions:** for the planning side; mark (blocking) if work stopped because of it.
**Next:** the step to do next.
```

---

## 2026-11-16 · Planning · repo cloned, brief written (planning side)
**Done:** Cloned the team repo, created `jakob_extension` from `quentin_baseline`, wrote `CLAUDE.md`, `docs/part2/BRIEF.md`, this log.
**Decisions:** Branch from `quentin_baseline` (data + structure already there). One brief for the whole part with checkpoints after steps 1, 3, 5 and 7; dashboard interface last (step 8).
**Results:** Baseline reference (Quentin): R² 0.930, AIC −350.7; revenue ROI influencer ~31, TikTok ~14, Instagram ~13, POS ~4–5, TV ~0.2; contributions sum to ~150–160% of sales.
**Open questions:** None yet.
**Next:** Steps 0–1.

## 2026-11-16 · Steps 0–1 · package, baseline reproduced, evaluation harness
**Done:** `requirements.txt` (pinned, Python 3.12 venv), `pyproject.toml`, package `src/arla_mmm/` (`data`, `spec`, `baseline`, `engine`, `contributions`, `evaluate`), `tests/` (6 tests, pass), `scripts/run_part2.py` (rebuilds `results/part2/`). A candidate is a `ModelSpec` (a function raw data → regressors, plus flags); `evaluate(spec)` fits it and writes its row to `results/part2/model_comparison.md` and a detail sheet to `results/part2/candidates/<name>.md`. Baseline reproduced exactly (R² 0.930, AIC −350.661, BIC −323.271, part 1's ROIs to 2 decimals; asserted in the tests).

**Decisions:**
- *Contributions = Shapley values on counterfactual sales paths.* Switch channels to their reference level, re-simulate sales, average each channel's incremental sales over all switch-on orders. Why: the model is multiplicative, so "remove one channel at a time" does not add up (it gives 60–85% more than Shapley here); Shapley adds up by construction and needs no model-specific formula, so it works unchanged for adstock/saturation candidates. Rejected: part 1's θ method (sums to 149% of sales), splitting by share of log-effects (adds up but arbitrary).
- *Differs from brief: base + channels = **actual** sales, not fitted sales.* The counterfactuals keep each week's estimated residual. Why: with lagged sales a counterfactual has to be simulated recursively, and the recursive path without residuals is not the regression's fitted series, so "fitted" has no single meaning; keeping residuals makes the sum exact every week (checked in the tests) and gives stacked charts that match the sales line. Carry-over through lagged sales is therefore inside each channel's contribution.
- *Reference level: zero for TV, lowest observed weekly spend ("floor") for the four always-on channels; ROI = incremental revenue / spend above the floor.* Why: zero spend on those channels was never observed. With a zero reference the baseline puts base sales at 0.0% and gives each always-on channel 23–25% of sales whatever its coefficient, i.e. the answer comes from log(0), not from the data. What the floor spend itself earns is not identified and stays in base. Rejected: 5th percentile (weeks below it get negative contributions). The zero reference is reported next to it as a sensitivity in every table.
- *Hold-out error is a multi-week forecast* (spend and price known, sales fed back from the model's own forecast), last 26 weeks plus 4 rolling folds of 13 weeks. Why: that is what the dashboard does over ≥ 12 weeks; a one-week-ahead error flatters any model with lagged sales (7.5% vs 11.4% for the baseline). Both are in the table.
- *Comparable AIC/BIC:* all candidates are fitted on the same 155 weeks (week 1 dropped, as the baseline's lag requires) with log units as dependent variable; decay/saturation parameters chosen outside OLS are added to the parameter count and the penalties (`ModelSpec.n_extra_params`). The baseline keeps log1p to match part 1; later candidates use log (difference ≈ 1e-6).
- statsmodels 0.15.0 / pandas 3.1.1 / numpy 2.5.5 pinned (current releases; statsmodels is the version Quentin used).

**Results:** [model_comparison.md](../../results/part2/model_comparison.md) · [M0_baseline.md](../../results/part2/candidates/M0_baseline.md) · [baseline_part1_method.md](../../results/part2/baseline_part1_method.md)
- Part 1 method: channel contributions sum to 149% of sales (influencer alone 71%).
- Same model, contributions that add up (floor reference): base 18.5%, channels 81.5% of sales; revenue ROI influencer 39.8, TikTok 20.2, Instagram 17.4, POS 5.3, TV 0.97. Higher than part 1 because carry-over is now counted: lagged-sales coefficient 0.57 multiplies every short-run effect by 2.3, the same for all channels. Still implausible; this is the row steps 2–3 have to beat.
- Hold-out MAPE 11.4% (rolling 9.9%, worst fold 12.6%) vs 26.6% for "same week last year". Media coefficients are positive and stable across folds; residual tests pass (Breusch-Godfrey p 0.13).
- What the baseline misses: residuals drift from −2.1% (2022) to +2.8% (2024) → no trend; August +3.8%, December −4.4% → no seasonality; price coefficient +0.05 (p 0.78, flips sign across folds, VIF 5.5 with the promo flag).

**For the slides:**
- "The baseline cannot say what a channel is worth: its contributions add up to 149% of sales, and when forced to add up it credits 81% of sales to the top third of media spend."
- "We measure each channel against the lowest spend we have ever observed, not against zero: we have no data on switching Instagram, TikTok, influencers or POS off."

**Open questions:**
1. Are you fine with the floor reference and "ROI per £ above the floor" as the headline, with zero as sensitivity? It means we will not claim a total contribution for the always-on channels. Not blocking; it is one argument (`reference=`) to change.
2. OK that the decomposition adds up to actual rather than fitted sales (residual spread proportionally over base and channels)?
3. Marginal ROI (+10% spend) is not in the comparison row yet; I plan to add it in step 3 when response curves exist, rather than wait for step 6. Say if you want it earlier.

**Next:** Step 2 (trend, seasonality, list price vs promo depth; decide lagged sales vs adstock). Run: `pip install -r requirements.txt && pip install -e . && pytest && python scripts/run_part2.py`.

## 2026-11-16 · Steps 2–3 · controls, then carry-over and saturation
*(Step 2 and the step-3 plan were written and committed before any step-3 code; step-3 results follow below the plan.)*

### Step 2 – controls
**Done:** `features.py` (trend, Fourier seasonality, regular price, promo depth), `candidates.py` (a `Config` per candidate; ladder M1–M5), `results/part2/step2_controls.md` (13 one-change alternatives around M5). Media and lagged sales unchanged from part 1 in this step, so every change is attributable to one control.

**Decisions:**
- *Linear trend (in years)* — the largest single gain: hold-out MAPE 11.4% → 7.6%, and the price coefficient gets the right sign (+0.02 → −0.61). A slope change after year 1 is not significant (p 0.4) and pushes VIF to 53: rejected.
- *Seasonality = 2 annual sine/cosine pairs + January dummy.* The seasonal swing is small (about ±4%) but cuts hold-out error 7.0% → 4.8% and the worst fold 10.0% → 5.5%; BIC is indifferent (−363.0 vs −363.4), so this is decided by forecast error. January: +6.5% (HAC p 0.005), a New-Year effect that fits a high-protein brand. Christmas weeks: −5% but only 6 observations and no gain once January is in: not kept. 1 pair and 3 pairs are both worse out of sample.
- *Price = log regular price + promo depth*, replacing average price + promo flag. Regular price = the shelf price seen in non-promo weeks (it rises in steps: £1.35 → 1.45 in Sep 2022 → 1.55 in Apr 2023 → ~1.60 in 2024), carried into promo weeks; promo depth = log(regular / paid) in promo weeks, 0 otherwise (mean 0.28 ≈ 24% off). The two are uncorrelated (r 0.04) and the price/promo VIF problem disappears. Honest caveats: (i) part 1's price pair fits marginally better (AIC −414.5 vs −412.1, hold-out 4.4% vs 4.8%) but its promo flag then has the wrong sign and VIF 13, and the dashboard needs "shelf price" and "promo depth" as separate levers, so I keep the split; (ii) regular price moved only four times and always upwards, so it is collinear with the trend (r 0.94, VIF 10.8): the elasticity (−0.78 short-run) is identified from four steps and its interval is wide (HAC se 0.20; −0.76 to −0.95 across folds). Dropping it costs 1.2 points of hold-out MAPE, so it stays.
- *Post-promotion dip (last week's promo depth): kept, and it changes the reading of carry-over.* Coefficient −0.205 (HAC p < 0.001), AIC −389 → −412. With lagged sales at 0.58, a promotion's implied carry-over is 0.45 × 0.58 − 0.205 ≈ +0.06, i.e. nil. Lagged sales was carrying promo spikes into the next week, which the data reject: promotions lift the week they run and nothing after.
- *Lagged sales stays for step 2 only.* Dropping it with media still un-lagged wrecks the model (AIC −412 → −131, autocorrelated residuals), so media carry-over is real and large; but M5's Breusch-Godfrey p of 0.007 says one shared carry-over rate does not fit. Step 3 tests replacing it with per-channel adstock; the two will not be used together unless the data insist (checked below).

**Results:** [model_comparison.md](../../results/part2/model_comparison.md) · [step2_controls.md](../../results/part2/step2_controls.md) · [M5_january.md](../../results/part2/candidates/M5_january.md)
- M0 → M5: AIC −350.7 → −412.1, BIC −323.3 → −363.4, hold-out MAPE 11.4% → 4.8%, rolling 9.9% → 5.0%; residual drift by year gone (−2.1/+2.8% → within ±0.2%).
- Growth +8.0% a year at constant price and media; regular-price elasticity −0.78 short-run; a 24%-off promotion lifts that week's units by about 13% short-run.
- Media coefficients and ROIs barely move (influencer 38.0, TikTok 23.2, Instagram 17.6, POS 5.3, TV 0.92 above floor). The controls were not what made them implausible; the media specification is.

### Step 3 – plan (before coding)
Media enters as `beta_c × f(adstock(spend_c; decay_c); scale_c)` in the log-sales regression, on top of M5's controls. Every `f` is 0 at zero spend, so TV's off-air weeks need no log(x+1): an off-air week simply has whatever adstock is left from the last flight. Adstock is normalised (constant spend X → adstock X) so scales stay in £/week.

*Stage A – carry-over* (curve fixed at log(1 + adstock/scale), scale = mean weekly spend, TV: mean on-air spend; 0 extra parameters for the curve):
| candidate | carry-over | extra params |
|---|---|---|
| A0 = M5 | lagged sales, log(spend+1) | 0 |
| A1 | one decay for all channels, no lagged sales | 1 |
| A2 | three decays: TV / social (Instagram, TikTok, influencer) / POS | 3 |
| A3 | one decay per channel | 5 |
| A4 | best of A1–A3 **plus** lagged sales | +0 (check only: if adstock has done the job, lagged sales ≈ 0) |

Decay grid 0 to 0.9 in steps of 0.1 (0.5 = half the effect left after 1 week, 0.8 after 3 weeks, 0.9 after 6–7). Expectation: TV 0.3–0.8, social 0–0.6, POS 0–0.3. I search the whole grid and do not clamp; an estimate at the edge or against expectation is reported as a finding, not hidden.

*Stage B – saturation*, at the decay structure that wins stage A (decays re-tuned jointly with the curve):
| candidate | curve | extra params |
|---|---|---|
| B1 | log(1 + a/scale), scale re-tuned | +1 TV scale, +1 shared always-on scale |
| B2 | Hill with slope 1: a/(a + scale) | same |
| B3 | negative exponential: 1 − exp(−a/scale) | same |
| B4 | TV as on-air flag + log(spend) on air, no adstock (the "two-part" answer to the zeros) | TV: 0 nonlinear, 1 more coefficient |

Scale grid = {0.25, 0.5, 1, 2, 4} × mean spend. TV ranges from 0 to £376k, so its curvature should be identifiable. The always-on channels move only ±20–30% around their mean, so I expect their scale to be nearly unidentified (flat likelihood); if so it is fixed by convention at the mean and the response curve outside the observed range is labelled as assumption. I will show the likelihood profile either way.

*Budget:* M5 has 16 parameters; the largest step-3 candidate has 15 regression coefficients + up to 7 grid-chosen ones = 22 on 155 weeks. Every grid-chosen parameter counts as one parameter in AIC/BIC.
*No peeking:* decays and scales are re-selected inside each hold-out fold on the training weeks only.
*Also:* marginal ROI (+10% spend, revenue at actual prices) joins the comparison row; the post-promo term and seasonality are re-tested once lagged sales is gone.

### Step 3 – results
**Done:** `tune.py` (grid search for decay/scale as a profile likelihood; re-run inside every hold-out fold), `ladder.py` (candidates M6–M14 + 13 one-change variants), `features.adstock/saturate`, marginal ROI in `contributions.py` and in the comparison row, `tests/test_media.py` (14 tests pass). Detail sheets now show the tuned parameters per fold and their likelihood profiles. `python scripts/run_part2.py` rebuilds everything in about 3 minutes.

**Decisions:**
- *Differs from brief: the step-3 model keeps lagged sales **and** adds per-channel adstock.* Plan was one or the other. Adstock alone (M8) beats M5 on AIC (−432 vs −412) but not out of sample (5.7% vs 4.8%) and leaves autocorrelated residuals (Breusch-Godfrey p 0.002). Adding lagged sales to it (M9) gives AIC −486, hold-out 4.5%, clean residuals; lagged sales is 0.36 (t 25) and the adstock decays stay sharply identified next to it. Lagged sales alone with the new curves: AIC −424. An AR(1) error term instead of lagged sales was clearly worse (one-off check, not in the repo). Reading: two different things carry over. Adstock = how long an ad is remembered, per channel. Lagged sales = repeat purchase: 36% of any week's uplift comes back the next week whatever caused it. This is not double counting: both are estimated jointly and the contribution paths are simulated through both. Promotions are the exception, as in step 2: the post-promo term (−0.06) cancels part of their repeat effect.
- *One decay per channel (5 parameters).* Estimates: TV 0.4, influencer 0.4, Instagram 0.3, TikTok 0, POS 0, identical in all four training windows and with sharp profiles (moving any decay by 0.2 costs 6–35 AIC points). Against my expectation TV does not last longer than influencer. Grouping TV/social/POS (M7) is rejected by the data because TikTok behaves like POS, not like Instagram. A post-hoc grouping (TV+influencer / Instagram / TikTok+POS) would save 2 parameters and 6 AIC points, but choosing groups after seeing the estimates is the search I was asked to avoid, so I count all 5.
- *Curve = Hill with slope 1, f = a/(a + scale).* Hill and negative exponential are indistinguishable (AIC −497.3 vs −497.2, same ROIs); log(1 + a/scale) is 12 points worse, square root 24 worse. Hill kept because it is the standard MMM curve and flattens more slowly outside the data than the negative exponential, which will be the sensitivity case in step 5.
- *TV scale tuned (1 parameter), always-on scale fixed at mean weekly spend (0 parameters)*, as anticipated in the plan. Always-on channels: with a separate scale each, no value is rejected (profile differences 0.2–4 AIC across a 32-fold range) and the picks jump between folds, so the data cannot tell where these curves bend. Fixing "half of the maximum effect at the average spend" is a convention; it fits as well as tuning (M14 vs M11) and saves a parameter.
- *TV: no saturation found.* The TV scale goes to the top of the grid (4 × on-air mean ≈ £0.94m/week); widening the grid to 64 × changes AIC by 0.4. Between £150k and £376k a week the TV response on log sales is a straight line. In £ terms that means no diminishing returns inside the range observed; beyond £376k the model has no information.
- *TV zeros: adstock + curve that is zero at zero, not a two-part model.* On-air flag + log(spend) on air (M13) is 42 AIC points worse and has no carry-over. The log(x+1) problem is gone: TV's marginal ROI moves from 0.16 (part 1 form, where +10% spend barely changes log(x+1)) to 1.72.
- *Controls re-tested on M14:* seasonality curve needed (−43 AIC without it), January kept (AIC and rolling error better), post-promo term kept but now marginal (AIC +2.3, BIC −0.8), part 1's price pair still marginally ahead on AIC (−498.9 vs −497.3) with VIF 13; same decision as step 2.

**Results:** [model_comparison.md](../../results/part2/model_comparison.md) · [step3_media.md](../../results/part2/step3_media.md) · [M14_hill.md](../../results/part2/candidates/M14_hill.md)
- M0 → M5 → M14: AIC −350.7 → −412.1 → −497.3; BIC −323.3 → −363.4 → −430.3; hold-out MAPE 11.4% → 4.8% → 4.2%; rolling 9.9% → 5.0% → 3.9%. All residual tests pass; every media coefficient is positive in every fold; 22 parameters (16 coefficients + 6 grid-chosen).
- Carry-over: TV and influencer deliver 39% of their effect in the week of spend and 93% within 4 weeks; TikTok and POS 64% in the week. Total effect = 1.55 × (TikTok, POS) to 2.6 × (TV, influencer) the first-week effect.
- M14, above floor: base 20.8% of sales; revenue ROI influencer 42.8, Instagram 18.6, TikTok 16.9, POS 3.7, TV 0.99. Marginal ROI: influencer 74.6, Instagram 30.8, TikTok 24.8, POS 5.5, TV 1.72.
- **The ROIs did not come down, and I now think they are what this dataset contains.** They are the same within ±15% across all 15 candidates and all three curves, and a plain linear regression of units on adstocked spend (no logs; one-off check) gives the same order of magnitude: about £68 of revenue per £ of influencer spend, £23 Instagram, £24 TikTok, £5 POS, £2 TV. Weekly sales swing between 330k and 1m units while influencer spend moves by a few £k, and the two line up. What the model cannot say is how far this extends: influencer spend has only been observed between £13k and £36k a week.
- Price (M14): regular-price elasticity −0.49 in the week, −0.76 in total (folds −0.45 to −0.59; still collinear with trend, VIF 11); a 24%-off promotion lifts that week's units by about 13%.
- Correction to the step-2 text above: M5's regular-price coefficient ranges from −0.78 to −0.94 across folds (I wrote −0.76 to −0.95).

**For the slides:**
- "Adding trend, seasonality and a proper price split halved the forecast error; modelling how long each channel's effect lasts took it from 4.8% to 4.2% and removed the last pattern in the errors."
- "TV and influencer effects last about four weeks, TikTok and in-store promotion work almost entirely in the week they run."
- "Part 1 made TV look worthless at the margin (16p per extra £) because of how zeros were handled. Treated properly, an extra £ of TV returns about £1.70 of revenue; an extra £ of influencer spend about £75, within the narrow range we have ever spent."

**Open questions:**
1. Lagged sales + adstock together: accepted as the step-3 model? If you want a pure-adstock model for simplicity it costs 56 AIC points, 1.5 points of hold-out MAPE and autocorrelated residuals.
2. The size of the social/influencer ROIs will decide step 7: any optimiser will push influencer, Instagram and TikTok to their upper bounds and cut TV and POS to their lower bounds, so the recommendation is the bounds. Which bounds do you want? My proposal: each channel's weekly spend stays inside its observed weekly range (and I also show a tighter ±20% of the current mean), with the result labelled "direction and first step", not "optimum".
3. TV has no measurable saturation in range. In a multiplicative model that makes TV's £ response slightly convex, which optimisers exploit. I plan to cap TV at its observed weekly maximum in step 7.
4. Step 4 note: a multiplicative model already makes every driver amplify every other. The interaction tests will therefore ask whether there is synergy *beyond* that; I will say so on the slide to avoid claiming "no synergy" if they fail.
5. Nothing was pushed in this run; say if you want the branch pushed.

**Next:** Step 4 (synergies: TV × influencer, TV × social, POS × promo depth), then step 5 (final model, robustness) and stop at the checkpoint.

## 2026-11-16 · Steps 4–5 · synergies tested, final model and robustness
**Done:** interaction terms in `candidates.py` and in the tuner; candidates M15–M19 in the comparison; `robustness.py`; `results/part2/step4_synergies.md` and `step5_robustness.md` (both rebuilt by `scripts/run_part2.py`, now about 5 minutes). BRIEF §7 decisions after checkpoint 3 committed; branch pushed before and after this run.

**Decisions:**
- *Step 4: no interaction is kept.* Four pairs were fixed with their business story before testing (TV × influencer, TV × social, influencer × social, POS × promo depth; I added influencer × social to the brief's three because influencers post on the platforms where the paid social runs). Rule: keep if BIC and hold-out error improve and the sign is stable. None passes: BIC is 2.8–5.0 worse for each, hold-out error is not better for any, all four together are 15.6 BIC points worse. Closest: influencer × social (positive in every training window, p 0.10, AIC −0.2) and POS × promo (negative in every window, p 0.10: if anything displays and discounts substitute for each other). Both are noted as "suggestive, not established". As agreed, the wording is "no synergy beyond the multiplicative structure": the model already makes each channel worth more when the others are high.
- *Final model = M14, unchanged.* One paragraph for the slides: **Weekly log sales are explained by (1) a base that grows 7% a year with a mild seasonal curve and a January lift, (2) shelf price and promotion depth as separate levers, with a small dip the week after a promotion, (3) five media channels, each with its own memory (adstock) and a diminishing-returns curve that is zero at zero spend, and (4) repeat purchase: 36% of any week's uplift returns the next week. It was chosen from 20 candidates because it has the lowest BIC and the lowest out-of-sample error (4.2% on the last 26 weeks, 3.9% rolling, against 11.4% and 9.9% for part 1's model), passes every residual test, has positive and stable media effects in every training window, and every term has a plain business meaning. Richer versions (synergies, a separate curve shape per channel) did not forecast better.**
- *Differs from brief: no Bayesian cross-check.* With flat priors it would reproduce the regression; with informative priors it would mostly show the priors, given how sharply the data identify the coefficients (media t-values 7–37). It would also add pymc as a heavy dependency for the dashboard team. I used the time for checks that could have broken the model (below). Parameter simulation for the ROI intervals comes in step 6 and covers the "uncertainty" purpose.
- *Robustness checks chosen:* sensitivity to every transform choice, additive instead of multiplicative form, sub-periods, a placebo test for the planning side's caveat (iii) (budgets set in anticipation of demand), influential weeks, HAC vs OLS errors.

**Results:** [step4_synergies.md](../../results/part2/step4_synergies.md) · [step5_robustness.md](../../results/part2/step5_robustness.md) · [model_comparison.md](../../results/part2/model_comparison.md)
- *Transform choices barely move the answer.* Across 13 variants (other curves, decays ±0.1, curves bending at half/twice the mean, TV scale halved/doubled, other controls, no lagged sales) influencer ROI stays 41.2–43.9 and its marginal ROI 73.2–77.8; the widest spread is TV's marginal ROI, 1.53–2.05. The ranking never changes.
- *Multiplicative beats additive.* An additive model of units has hold-out error 8.8% (vs 4.2%) and an AIC 99 points worse on a common scale. Its marginal ROIs agree with ours (influencer 71 vs 75, Instagram 25 vs 31, TikTok 26 vs 25, POS 5.2 vs 5.5, TV 1.4 vs 1.7), so the ROI sizes are not produced by the log form. This check is now in the repo, replacing the one-off I mentioned at checkpoint 3.
- *Stable over time.* Estimated on the first or the last two years only, influencer ROI is 38.9 and 45.3, TV 0.94 and 1.08, POS 3.7 and 4.3; decays identical. On 78-week halves the ranges widen (Instagram 15.2–18.1, POS 2.7–4.9) but the order holds. TV and POS look somewhat better in the later period.
- *Placebo passes.* Next week's spend does not "explain" this week's sales: joint p 0.70, no single channel below p 0.21. No sign that budgets were raised ahead of expected demand at a weekly horizon. This does not rule out slower planning effects, so caveat (iii) stays on the slide, but it can be worded as "tested, no evidence at weekly level".
- *Not driven by a few weeks.* Dropping the 5 most influential weeks moves media coefficients by at most 2.2%. Regular-price elasticity moves 10% (−0.49 → −0.44), consistent with its known weak identification.
- *Standard errors:* Newey-West errors are within 0.8–1.2 × OLS; every media coefficient has |t| ≥ 7. 95% interval for lagged sales 0.33–0.38, for regular price −0.80 to −0.18.

**For the slides:**
- "We tried to break the model five ways: other response curves, an additive form, half the data, a placebo test and removing the most influential weeks. The channel ranking never changed and influencer ROI stayed within 39–45."
- "Channels do not need to be bought in pairs: we found no extra synergy between TV and social or influencers beyond the general effect that everything works better when sales are high."
- "The weakest number in the model is price elasticity (95% interval −0.2 to −0.8 in the week of the change): the shelf price has only ever gone up, four times."

**Open questions:**
1. Is skipping the Bayesian cross-check acceptable? If the course expects one as a visible "advanced" element, say so and I will add it as an appendix in step 6 (roughly an hour including the dependency).
2. Step 6 intervals: I plan to simulate coefficients from their Newey-West covariance (decays and scales held at their estimates) and to report separately how much the ROI moves across the neighbouring decay/scale values from this step's sensitivity table, rather than a block bootstrap that re-tunes everything. Reason: the transform choices move ROI by ±3–15%, far less than they would need to matter, and the simulation is what the dashboard can reuse for its bands. Object if you want the bootstrap.
3. For board metric (b), promotions: I will report the revenue effect of a typical promotion week including the dip the week after and the repeat-purchase effect, at the average depth (24% off) and as a curve over depth. OK?

**Next:** Step 6 (decomposition over time, ROI and marginal ROI with intervals, response curves, break-even margin, promotion and price insights, figures), then step 7 and its checkpoint.

*Correction to the first slide bullet above:* across the sub-period fits influencer ROI ranges from 38.9 to 45.6, so the bullet should read "within 39–46".

## 2026-11-16 · Steps 6–7 · contributions and ROI with intervals, scenarios, recommendation
*(No new BRIEF decisions were available; Jakob told me to choose the next steps. I went ahead with the defaults I proposed at checkpoint 5: coefficient simulation for intervals, no Bayesian appendix, promotions reported including the dip after. All three are easy to revisit.)*

**Done:** `final.py` (final model + 2,000 coefficient draws from the Newey-West covariance, vectorised same-shocks simulation), `insights.py`, `scenarios.py`, `figures.py`, `scripts/run_insights.py` (about 30 seconds; run `scripts/run_part2.py` first), `tests/test_final.py` (18 tests pass). `features.py` now accepts `regular_price` and `promo_depth` given directly, which the dashboard interface will need. Outputs: `step6_contributions_roi.md`, `step7_scenarios.md`, `decomposition_weekly.csv`, `response_curves.csv`, `scenario_plans.csv`, 8 figures in `results/part2/figures/`.

**Decisions:**
- *Intervals = 5–95% range over coefficient draws, decays and scales fixed.* They are narrow (influencer ROI 41.4–44.3) and cover estimation noise only. On every table and chart I say so, because the real uncertainty is elsewhere (next point).
- ***Differs from brief (important): I do not recommend the "observed weekly range" plan as the main scenario, and I added a ±10% plan as the headline.*** The weekly range is not the range the model has evidence for. Its long-run effect needs a spend level to be *held*, and held levels have barely moved: the highest 13-week average of influencer spend ever observed is 11% above its mean (Instagram 25%, TikTok 43%, POS 15%), although single weeks reached +80%. The observed-weekly-range plan holds influencer at 75% above 2024 all year and the model answers with +283% revenue. ±20% gives +65%, ±10% gives +30%. I computed all three as the brief asks, added a range check per plan (`step7_scenarios.md`), and recommend ±10% as "first step, run as a test".
- *Even the ±10% number should not go on a slide as a forecast.* +£15m (+30%) from moving £0.3m is simply the marginal ROIs (influencer ≈ £75 per £) applied to a sustained shift and compounded by the multiplicative form. The data support the direction and the ranking very robustly; they cannot show that a response measured on week-to-week wiggles holds when the level is raised and kept. I wrote the recommendation as: direction → first step ±10% → measure → scale. My suggestion is to show the allocation chart and the ROI chart on the slides and to quote the revenue gain only as "model-implied upper bound".
- *Scenarios are a replay of 2024, not a forward forecast:* same weeks, prices, promotions and shocks, only media changes. Why: it isolates the media decision, needs no assumptions about 2025 prices or promotions, and reproduces actual 2024 revenue exactly for the unchanged plan. Spill-over into 2025 is not counted for any scenario. The forward-looking version is the dashboard's job (step 8).
- *Plans keep each week's place in the 2024 pattern* and move it between a lower and an upper bound (one number per channel), TV within its flight calendar and capped at its observed maximum, as decided in §7. The optimiser hits the bounds as predicted: TV to its lower bound, Instagram/TikTok/influencer to their upper bound in every plan; POS is the swing channel.
- *Decomposition chart = stacked columns per quarter, not a weekly stacked area.* 155 weekly points × 8 layers is unreadable at slide size; the weekly series is in the CSV. Price promotions and growth since Jan 2022 are separate layers (Shapley over seven drivers); seasonality and price level stay in the base because their reference level would be arbitrary and their contribution changes sign.
- *Response curves show sustained spend levels* with two shaded ranges (seen in single weeks / held for a quarter) and a thick line only where the model has evidence, to make the point above visible.

**Results:** [step6_contributions_roi.md](../../results/part2/step6_contributions_roi.md) · [step7_scenarios.md](../../results/part2/step7_scenarios.md) · figures: `roi.png`, `decomposition.png`, `response_curves.png`, `model_ladder.png`, `fit_holdout.png`, `allocation.png`, `scenarios.png`, `promotions.png`
- ROI above floor (5–95%): influencer 42.8 (41.4–44.3), Instagram 18.6 (16.7–20.5), TikTok 16.9 (15.6–18.2), POS 3.7 (2.8–4.5), TV 0.99 (0.94–1.05). Marginal ROI: 74.6, 30.8, 24.8, 5.5, 1.72. Break-even margin on the next £: TV 58%, POS 18%, social and influencer 1–4%.
- Sales split 2022–24: base incl. minimum media 17%, growth 8%, price promotions 3%, POS 5%, TV 7%, Instagram 15%, TikTok 16%, influencer 30%.
- Price promotions (board metric b): +6.2% units, **−3.7% revenue** (−£5.2m over three years, about £100k per promotion week). A 24%-off week sells +17% units in total but needs +32% to hold revenue; no depth pays for itself.
- Shelf price (board metric c): total elasticity −0.76 (−1.15 to −0.37); a 5% price rise gives −3.6% units and +1.2% revenue (−0.8% to +3.1%).
- Scenarios, revenue against the 2024 plan (£50.5m): ±10% plan +£15.4m, ±20% +£33.1m, observed weekly range +£143m, 10% of TV to influencer +£24.8m, budget −10% optimised +£8.9m, budget +10% optimised +£38.0m. All beyond the sustained range for influencer; only the ±10% plan is close to it (9% above).
- TV and in-store (the board's question): TV is 39% of spend for 7% of sales and returns about £1 of revenue per £; it is cut first in every plan. POS spend earns its keep (ROI 3.7) but ranks fourth. Price promotions cost revenue.

**For the slides:**
- "Shift budget from TV towards influencers, Instagram and TikTok: every model version and every scenario agrees on the direction."
- "First step: 10% out of TV, 10% more on each of the three social channels, same total budget, run as a measured test. The model's numbers beyond that are extrapolation: we have never held influencer spend more than 11% above its average for a quarter."
- "Price promotions add 6% volume and cost 4% of revenue. They are the first in-store lever to test, ahead of POS spend."

**Open questions:**
1. (important) Do you accept ±10% as the headline plan and the wording "model-implied upper bound" for its revenue number, with the observed-weekly-range plan shown only as an illustration of extrapolation? This reverses the §7 decision on which scenario is "main".
2. Should the slides quote any revenue gain at all? My view: show direction, allocation and ROI, quote the gain once with the caveat, and make the recommended test the conclusion.
3. For step 8, the dashboard will produce the same very large numbers whenever a user raises social spend. I propose that the interface returns an out-of-range flag based on the 13-week average (not the weekly range) and that INTERFACE.md tells the dashboard team to display it prominently. OK?
4. Still open from checkpoint 5: Bayesian appendix yes/no.

**Next:** Step 8 (model interface for the dashboard, INTERFACE.md, `notebooks/02_model_extension.ipynb`, SUMMARY.md, pull request) after the planning side has reviewed this checkpoint.

## 2026-11-16 · Step 8 · dashboard interface, magnitude check, summary, notebook, hand-off
**Done:** `src/arla_mmm/interface.py` (fit / save / load, `forecast`, `compare_scenarios`, `check_range`, plan helpers, `backtest`), the saved model `models/arla_mmm_final.json`, `docs/part2/INTERFACE.md`, `results/part2/SUMMARY.md`, `notebooks/02_model_extension.ipynb` (runs from a fresh kernel in about 10 seconds), `scripts/run_interface.py`, `insights.elasticities` and `insights.curve_shape`, three new figures (`scenarios_main.png`, `allocation_main.png`, `forecast_example.png`), `tests/test_interface.py` (25 tests pass in total), a part-2 section in the README, notebook packages pinned in `requirements.txt`. BRIEF decisions after checkpoint 7 committed; branch pushed.

**Decisions:**
- *Saved model = a JSON file, committed.* Coefficients, their Newey-West covariance, residual spread, the tuned decays and scales, and the observed ranges. Why: the app loads it in milliseconds without refitting, anyone can read it, and no pickle is involved. A test fails if the file no longer matches a fresh fit. Rejected: pickle (the spec holds a lambda; unsafe to share), refitting in the app (works, 1 second, but then the app depends on the tuning code).
- *Plan inputs are shelf price and discount as two levers, not an average price.* That is how the model sees price; the paid price is derived. A 0/1 promo flag is accepted and uses the historical average discount (24%).
- *Bands = coefficient draws + one normal shock per week.* Same draws and shocks for every plan of the same length, so scenario differences carry no simulation noise. Checked by a back-test (below), which is the evidence the bands are honest.
- *Per-channel contributions in a forecast use the same definition as step 6* (Shapley against the floor, TV against zero) over the plan weeks only. What past spend still carries into the plan weeks is in the base, and effects after the last plan week are not counted, so a 12-week ROI is slightly below the historical one. Stated in INTERFACE.md.
- *Flags as decided in §7*, plus two I added: shelf price and discount outside their observed ranges. Flags come back as a table and as ready sentences (`Forecast.warnings`). No tolerance by default; the step-7 tables used 2%, available as an option.
- *`baseline_plan` = the same weeks one year earlier.* It keeps the TV flights and promotions in place and is inside the data by construction, so a user starts from an unflagged plan.
- *Magnitude check: long-term elasticity = the effect of 1% more spend in every week of the history*, not the formula value at average spend. They agree for the always-on channels; for TV the history gives 0.12 and "held on air" would give 0.35. The first is what published studies measure, so it is the headline.
- *Notebook shows the slide figures from `results/part2/figures/` and computes every table live.* Why: one set of figure files for slides and notebook, and the notebook stays small.

**Results:** [SUMMARY.md](../../results/part2/SUMMARY.md) · [INTERFACE.md](INTERFACE.md) · [step8_magnitude_check.md](../../results/part2/step8_magnitude_check.md) · [step8_interface_check.md](../../results/part2/step8_interface_check.md)
- Back-test, four 12-week forecasts in 2024 from models fitted on earlier weeks only: median forecast off by 4.0% on average, 44 of 48 actual weeks (92%) inside the 5–95% band, band about ±10%. One forecast (from July 2024) is weaker: 6.4%, 9 of 12 weeks inside.
- Long-term elasticity against the benchmark of 0.24: TV 0.12, POS 0.20, TikTok 0.54, Instagram 0.83, influencer 1.67 (7 times). Short-term against 0.12: 0.05, 0.13, 0.35, 0.37, 0.64.
- Curve shape: only influencer bends upwards over its whole observed range (TV below about £80k a week sustained). Its long-run coefficient implies sales × 816 at saturation against zero spend, the plainest sign of what the formula does outside the data.
- Interface example, next 12 weeks: current plan £11.5m revenue (11.0–12.0); TV −10% / social +10% is credited with +£3.3m and raises no flag; 10% of TV to influencer with +£5.4m and is flagged in 8 of 12 weeks (13-week average 17% above anything held).

**For the slides:**
- "TV and in-store promotion respond the way the literature says advertising does. Social is two to three times that, influencers seven times: we trust the ranking and want to test the size."
- "On weeks it had not seen, the model's 12-week forecast was off by 4% on average."

**Open questions:**
1. **(blocking the last item) The pull request is not open.** The GitHub CLI is not installed and I was not permitted to use the stored git credential with the GitHub API. Everything is pushed; Jakob needs to open the PR from the compare page (title and description are prepared) and ask Quentin to review. Not merged, as decided.
2. The ±10% plan raises no flag in the 12-week interface example, while step 7 flagged influencer in the 2024 replay (9% above). Both are right: in the first weeks of a forecast the 13-week average still contains history. The dashboard team should know that a plan can become flagged as the horizon grows.
3. A flagged plan still returns numbers. Should the interface refuse or cap them instead? I left the decision to the dashboard (INTERFACE.md suggests a red banner and greyed-out numbers).
4. `CLAUDE.md` and `docs/part2/BRIEF.md` are part of the PR to `main`. Say if you would rather keep them off `main`.

**Next:** Open the PR and get the team's review; agree the interface with the dashboard team and adjust it to what the app needs; slides from SUMMARY.md.
