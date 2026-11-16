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
