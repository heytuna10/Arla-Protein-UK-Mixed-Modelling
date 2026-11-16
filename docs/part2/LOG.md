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
