# Arla Protein UK – Marketing Mix Model

DSBA term project (ESSEC × CentraleSupélec). A weekly marketing mix model for Arla Protein UK (156 weeks, Jan 2022 – Dec 2024): what each channel (TV, Instagram, TikTok, influencers, in-store promotion) contributes, what it returns per £, and how to reallocate the budget.

Data: `data/arla_protein_mmm_weekly.csv`. Variables are described in [docs/part2/BRIEF.md](docs/part2/BRIEF.md).

## Status

| part | what | status |
|---|---|---|
| 1 | Baseline model and data preparation (`notebooks/01_exploratory_analysis.ipynb`) | done |
| 2 | Model extension: final model, ROI with intervals, scenarios, critical review, interface for the dashboard | **done, in this branch** |
| 3 | Scenario dashboard (Streamlit) | a starter exists on the branch `dashboard_starter`, not merged yet |
| 4–5 | Slides, pitch video | in progress |

## Part 2 in short

The final model (M14) is a regression on log sales with lagged sales (repeat purchase), a separate carry-over and diminishing-returns curve per channel, trend, seasonality, and shelf price and promotion depth as separate effects. It was chosen from 20 candidates. Forecast error on the last 26 weeks fell from 11.4% (part 1's model) to 4.2%.

- **Ranking:** digital channels first, in-store promotion second, TV last. It did not change in any robustness check.
- **Caveat:** the size of the social and influencer effects is far above published studies, so the recommendation is the direction (move about 10% of the TV budget into digital) and a 13-week test, not a revenue forecast.

Full story: [results/part2/SUMMARY.md](results/part2/SUMMARY.md).

## Where to look

- Summary for the slides: [results/part2/SUMMARY.md](results/part2/SUMMARY.md)
- The story with charts, runnable: [notebooks/02_model_extension.ipynb](notebooks/02_model_extension.ipynb)
- Model comparison (20 candidates): [results/part2/model_comparison.md](results/part2/model_comparison.md)
- Critical review (what we can claim, profit view, test design): [results/part2/step9_critical_review.md](results/part2/step9_critical_review.md); literature-sized effects: [results/part2/step9_anchored.md](results/part2/step9_anchored.md)
- How the dashboard calls the model: [docs/part2/INTERFACE.md](docs/part2/INTERFACE.md)
- Goals, steps and decisions: [docs/part2/BRIEF.md](docs/part2/BRIEF.md)
- Every decision with its reason: [docs/part2/LOG.md](docs/part2/LOG.md)

## Repository layout

```
data/        the weekly dataset
src/arla_mmm/  the model package (data, features, engine, candidates, contributions, evaluate, final, insights, scenarios, review, interface, figures, ...)
scripts/     run_*.py rebuild everything in results/part2/
models/      the fitted final model (arla_mmm_final.json) that the dashboard loads
notebooks/   01 = part 1 (Quentin), 02 = part 2 story
results/part2/  tables (.md/.csv) and slide figures (figures/*.png)
docs/part2/  brief, log, interface description
tests/       pytest
```

## Run it

Python ≥ 3.11 (built with 3.12).

```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
python scripts/run_part2.py && python scripts/run_insights.py && python scripts/run_interface.py && python scripts/run_review.py   # rebuilds results/part2/ (about 5 minutes, mostly the first script)
pytest
```

The saved model and all result tables are committed, so reading and using them needs no rebuild.

## Working in this repo

See [CLAUDE.md](CLAUDE.md): reusable logic lives in `src/arla_mmm/`, notebooks only call it, work on your own branch and merge via pull request, commit messages start with the part (`part2: ...`).
