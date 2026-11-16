# Scenario dashboard (part 3, starter)

A starting point for Quentin, Ketan and Paola, built by part 2 on top of `arla_mmm.interface`. It works end to end, and everything in it is yours to change.

## Run it

From the repo root, Python ≥ 3.11:

```bash
pip install -r requirements.txt
pip install -e .
streamlit run app/dashboard.py
```

The browser opens at http://localhost:8501. The fitted model is in the repo (`models/arla_mmm_final.json`), so nothing has to be trained.

## What it does

- **Inputs.** The current plan is `baseline_plan()`: spend and promotions of the same weeks a year earlier, at today's shelf price, for 12 to 52 weeks. Each scenario scales every channel with a slider, sets the shelf price, and lets you edit single weeks in a table (spend, shelf price, promotion % off; 0 = no promotion).
- **Scenarios.** Two or three, compared with the current plan.
- **Outputs.** Units, revenue and revenue per £ of advertising with low / most likely / high (5 / 50 / 95%); a weekly chart with bands; what each channel adds and returns.
- **Warnings.** A red box when a scenario holds a spend level the brand has never held for 13 weeks (the flag that matters), a yellow one when only single weeks are outside the data.
- **Gain as a range.** From `effects="benchmark"` (advertising works as published studies find) to `effects="model"` (as we measured it), because our social and influencer effects are two to seven times larger than the literature.

## How it is built

- One file, `app/dashboard.py`. It contains no model logic: it builds plans with `baseline_plan` and `scale_plan`, calls `gain_range` once per change, and formats the result. If you need a number the interface does not give you, add it in `src/arla_mmm/interface.py` with a test, not here.
- Interface documentation: `docs/part2/INTERFACE.md`.
- A cell edited in the week table keeps its value when a slider moves afterwards. "Reset to current plan" clears sliders, price and edits.
- `tests/test_app.py` runs the app headless and checks that the warning follows the inputs (`pytest`).

## Ideas and open points

See the entry "Dashboard starter" in `docs/part2/LOG.md`.
