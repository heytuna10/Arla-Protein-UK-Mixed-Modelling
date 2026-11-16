# Part 2 – Extending the marketing mix model (brief)

Owner: Jakob (co-lead: Elvira) · Branch: `jakob_extension` (from `quentin_baseline`) · Written by the planning side, last update 16 Nov 2026.
Target: final model, ROI and budget recommendation by **Sun 22 Nov**; the model interface for the dashboard comes last (step 8), once the model is stable.

This brief sets goals, constraints and acceptance criteria. How to reach them is your call. When you make a judgment call, write it down in LOG.md with the reason and the alternatives you rejected: the team builds the slides from that log. The methods suggested below are suggestions: if you see a better approach, argue it in your LOG entry and go ahead, as long as the goals and deliverables in §2 still hold.

---

## 1. Context

**Business question (codebook).** Arla Protein (high-protein yogurts, puddings, milk drinks; UK grocery) spends about £8m a year on TV, Instagram, TikTok, influencers and point-of-sale (POS) promotion, and runs in-store price promotions. The board wants to know what each channel contributes, the return per £ (on **revenue**, not units), whether TV and in-store promotion still deserve their large budget share, and how to reallocate. The CFO/CMO also want a scenario dashboard (part 3) built on our model: weekly spend per channel, price and promo weeks as inputs; units, revenue and ROI with uncertainty bands as outputs; at least 2 scenarios vs baseline over ≥ 12 weeks.

**Data.** `data/arla_protein_mmm_weekly.csv`, 156 weekly rows (Mondays, 3 Jan 2022 – 23 Dec 2024), no gaps or missing values.
`week_beg`, `sales_units` (pot equivalents), `avg_price` (£/unit, incl. promo discounts), `revenue` (= units × avg_price), `price_promo` (0/1, 52 weeks), spend in £: `tv`, `instagram`, `tiktok`, `influencer`, `pos_promotion`.
Facts that matter: TV is flighted (zero in 115 of 156 weeks); the other channels never hit zero and vary in a narrow band (e.g. influencer £13k–36k/week); spend shares ≈ TV 40%, POS 20%, Instagram 15%, influencer 13%, TikTok 12%. The codebook says the category is seasonal, the brand is growing, and price moves through both promotions and list-price increases.

**Course guidance.** Start from the Session 3 "FourTex" model (log-log OLS with lagged sales, unit effects θ = β·Ȳ/X̄, contribution = θ·ΣX, elasticity-share allocation) and extend it on: zero spend (the log(x+1) problem), carry-over per channel, price, seasonality and trend, synergies, ROI on revenue. Justify choices with AIC/BIC, residual diagnostics and plausibility. Grading rewards a well-argued specification more than a fancy method, so every extension should be motivated, tested against the previous model and explained in plain words.

**Baseline (part 1, Quentin's `notebooks/01_exploratory_analysis.ipynb`).** OLS on log1p of everything:
`sales ~ lagged_sales + avg_price + price_promo + tv + instagram + tiktok + influencer + pos_promotion` → R² 0.930, AIC −350.7, BIC −323.3.
Revenue ROI: influencer ~31, TikTok ~14, Instagram ~13, POS ~4–5, TV ~0.2. His own caveats, which are our to-do list:
1. Contributions sum to ~150–160% of sales, so only the ranking is usable. (Partly because the log-log "spend → 0" counterfactual extrapolates far outside the data for always-on channels.)
2. log(x+1) turns the TV coefficient into an on/off flight effect, not an elasticity.
3. Price and the promo flag are collinear (r ≈ −0.88 in logs); adding them halves the POS effect.
4. No seasonality or trend; carry-over only through one lagged-sales term shared by all channels.
5. Narrow spend ranges → reallocation beyond them is extrapolation.

Ketan's branch (`ketan_baseline`, same model, developed independently) adds two ideas worth reusing: price effects expressed per 1p, per 10p and per 1% price change, and a variant without `price_promo` to deal with the collinearity.

## 2. Goal and definition of done

A final model on the historical data, chosen from a documented ladder of candidates, that delivers:
- channel contributions that add up (base + channels = fitted sales) and are plausible;
- revenue ROI and marginal ROI per channel, **with uncertainty**;
- a budget recommendation with scenarios;
- a reusable Python interface the dashboard team can call;
- slide-ready tables, charts and a short plain-language story for the presentation.

## 3. Requirements and constraints

- **Parsimony.** 156 observations. Count parameters including the nonlinear ones (decay, saturation). Prefer constrained or shared transform parameters, coarse grids and plausible ranges over free-for-all searches. Out-of-sample checks are mandatory, not optional.
- **Model selection** uses all of: AIC/BIC (on a comparable likelihood: same dependent variable and same sample), rolling-origin or last-26-weeks hold-out error (MAPE/RMSE on units), residual diagnostics (Ljung-Box / Durbin-Watson, Breusch-Pagan, Jarque-Bera, VIF), HAC standard errors, coefficient signs and stability across folds. A model that wins on AIC but gives negative media effects or absurd ROIs loses.
- **Statsmodels first.** The main model should be explainable as a regression with transformed inputs. A Bayesian MMM (pymc-marketing or similar) is welcome as a robustness check if time allows, not as the main deliverable.
- **Revenue ROI** = incremental revenue / spend. Report gross revenue ROI; margin is unknown, so keep any profit view as an explicit, adjustable assumption.
- **Don't break the team's work:** keep `data/arla_protein_mmm_weekly.csv` where it is and don't edit part 1's notebooks; reuse what helps.

## 4. Steps

Checkpoints (⏸) are where the run stops so the planning side can review LOG.md and the result tables before continuing.

0. **Setup.** `requirements.txt` (pinned), `pyproject.toml`, package `src/arla_mmm/`, `.gitignore` additions. Reproduce Quentin's baseline inside the package and assert that R²/AIC match his numbers. Commit and push the branch.

1. **Evaluation harness + diagnosis of the baseline.** One function that fits any candidate and writes a comparison row (params, AIC/BIC, hold-out error, diagnostics, sum of contributions vs sales, ROI per channel) to `results/part2/model_comparison.md`. A contribution method that works for every candidate: fitted = base + Σ channel contributions, defined against a stated reference (zero spend for TV; for always-on channels decide whether zero or a low historical level is the honest reference, and say why). Run it on the baseline to set the reference row. ⏸

2. **Controls: trend, seasonality, price, promo.** Trend (linear or piecewise), seasonality (Fourier terms or similar; check for a January / New-Year effect and Christmas), and a price specification that separates **list-price changes from promotional discounts** (e.g. regular price + promo depth, or another construction you can justify) to resolve the price/promo collinearity. Decide whether lagged sales stays (Koyck carry-over) or is replaced by channel adstock in step 3; don't double-count carry-over.

3. **Media response: carry-over, saturation, TV zeros.** Geometric adstock per channel (decays in plausible ranges, e.g. TV longer than social/POS), a saturating response that is well defined at zero spend (log of scaled adstock, Hill, negative exponential … compare at least two), and an explicit solution for the TV flights. Compare against the log(x+1) baseline. ⏸

4. **Synergies.** Test a small, pre-declared set of interactions with a business story (e.g. TV × influencer, TV × social, POS × price promo). Keep only what improves BIC/hold-out and is plausible.

5. **Final model + robustness.** Pick the final specification and argue it in one paragraph. Robustness: HAC SEs, coefficient stability across CV folds, sensitivity of ROI to the decay/saturation choices, optional Bayesian cross-check. ⏸

6. **Contributions, ROI, marginal ROI.** Decomposition over time (stacked area: base, trend/season, price/promo, each channel), revenue ROI and marginal ROI per channel with intervals (parameter simulation or block bootstrap), response curves per channel with the historical spend range marked. Compare with the baseline numbers and explain what changed and why.

7. **Budget recommendation + scenarios.** Optimise the allocation of the same total budget on the response curves, with per-channel bounds that stay near the historical range (state them). Scenarios: (A) current plan, (B) optimised plan, (C) the brief's example "move 10% of TV to influencer", optionally (D) a budget cut/increase. Expected revenue and ROI with intervals. Also answer the board's question directly: do TV and in-store promotion earn their share? ⏸

8. **Model interface + hand-off.** Implement the interface the dashboard will call (§5) with the final model, and write `docs/part2/INTERFACE.md` (inputs, outputs, example call, known limits) for the dashboard team. `notebooks/02_model_extension.ipynb` runs end to end and shows the story; `results/part2/SUMMARY.md` with 8–12 slide-ready bullets and the figure list; pull request to `main`.

## 5. Interface for the dashboard (part 3)

Agree the details with the dashboard team via INTERFACE.md; this is the intent:
- Fit once on the history, save the fitted model, load it in the app.
- Prediction takes the **history plus a future plan** (carry-over needs past spend and possibly past sales): weekly spend per channel, price (or regular price + promo depth) and promo flags for ≥ 12 weeks.
- Returns per week: units and revenue with quantiles (e.g. 5/50/95%) that include parameter and residual uncertainty, plus incremental contribution per channel so the app can show ROI per scenario.
- Helpers for scenario comparison and a flag when inputs leave the historical range.

## 6. Communication rules

- **LOG.md** is written only by Claude Code (append, never rewrite). **BRIEF.md** is written only by the planning side. One writer per file means no conflicts.
- Put numbers in `results/part2/` tables and refer to them from LOG.md; keep LOG entries short enough to read in a minute.
- Questions or a disagreement with this brief go under "Open questions" in your LOG entry. If a question blocks the step, stop there.
- The answers to open questions land in §7 below.

## 7. Decisions

| Date | Decision | Why |
|---|---|---|
| 16 Nov | Branch `jakob_extension` starts from `quentin_baseline` | His branch has the data, EDA and repo structure; ketan_baseline is the same model in one notebook |
| 16 Nov | One brief covers all of part 2; Claude Code works through it in runs that end at the checkpoints | Fewer hand-offs; review happens where judgment matters |
| 16 Nov | Dashboard interface moves to the last step (8) | Agree it with the dashboard team once the model is stable |
