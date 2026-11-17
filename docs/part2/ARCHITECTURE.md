# Code map – `src/arla_mmm/`

One line per module, in dependency order (a module only imports from lines above it). Details are in each file's docstring.

## Idea

Every candidate model is one regression on transformed inputs: `log(sales_t) = x_t'β (+ λ·log(sales_{t-1}))`. A model is a `ModelSpec`, a recipe that turns the weekly table into regressors `x`. One engine fits, simulates and forecasts any spec, so 20 candidates share the same tests, contributions and ROI code. The final model is **M14**.

## Modules

| layer | file | what it does |
|---|---|---|
| 0 | `data.py` | loads the CSV, defines `CHANNELS` |
| 0 | `features.py` | transforms: adstock, saturation curves, seasonality, trend, shelf price, promo depth |
| 0 | `spec.py` | `ModelSpec`: the recipe for one model |
| 1 | `engine.py` | `fit` (OLS + HAC), `simulate` (recursive sales path, used for counterfactuals and forecasts) |
| 1 | `baseline.py` | part 1's model as a `ModelSpec`, plus part 1's attribution formula |
| 1 | `candidates.py` | the `Config` → `ModelSpec` factory; controls (trend, season, price) |
| 2 | `contributions.py` | Shapley decomposition (base + channels = actual sales), ROI, marginal ROI |
| 2 | `tune.py` | grid search for decay and saturation scales |
| 3 | `evaluate.py` | the harness: one call → one comparison row (AIC/BIC, hold-out, diagnostics, ROI) |
| 3 | `ladder.py` | the step 3–4 candidates and the choice of M14 |
| 4 | `final.py` | M14 fitted on all data, with coefficient-draw simulation for intervals |
| 4 | `robustness.py` | step 5: how much results move with the modelling choices |
| 5 | `insights.py` | step 6: ROI with intervals, response curves, price and promotion effects |
| 5 | `scenarios.py` | step 7: budget plans replayed on 2024 |
| 5 | `review.py` | step 9: tests of whether the big effects could be artefacts |
| 6 | `anchored.py` | step 9: model re-estimated with literature-sized effects |
| 7 | `interface.py` | step 8: what the dashboard calls (see `INTERFACE.md`) |
| – | `figures.py` | slide charts; only needs `data.py` |

## Where do I look for…

| question | where |
|---|---|
| a new model variant | `candidates.py` (`Config`), then `ladder.py` |
| how a number in the comparison table is computed | `evaluate.py` |
| how contributions or ROI are defined | `contributions.py` |
| what the final model is | `ladder.py` (`final_config`), `final.py` |
| confidence intervals | `final.py` (draws), `insights.py` |
| what a scenario does | `scenarios.py` |
| a chart | `figures.py` (called from `scripts/`) |
| something the dashboard needs | `interface.py`; add a test in `tests/test_interface.py` |

## Outside the package

- `scripts/run_*.py` rebuild `results/part2/` (run in the order in `README.md`); the package never imports them.
- `app/dashboard.py` imports only `interface.py`; it holds no model logic.
- `tests/` has one file per area (baseline, media, final, interface, review, app).
- Why each design choice was made: `LOG.md`. Results: `results/part2/SUMMARY.md`.
