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

- **Inputs.** The current plan is `baseline_plan()`: spend and promotions of the same weeks a year earlier, at today's shelf price, for 12 to 52 weeks. Each scenario scales every channel with a slider, moves a share of one channel's budget to another (exact, total unchanged; the brief's "10% of TV to influencers" is a button), sets the shelf price, and lets you edit single weeks in a table (spend, shelf price, promotion % off; 0 = no promotion).
- **Scenarios.** Two or three, compared with the current plan.
- **Outputs.** Units, revenue and revenue per £ of advertising with low / most likely / high (5 / 50 / 95%); a weekly chart with bands; what each channel adds and returns.
- **Warnings.** A red box when a scenario holds a spend level the brand has never held for 13 weeks (the flag that matters), a yellow one when only single weeks are outside the data.
- **Profit.** A margin slider (default 20%, an assumption: margin is not in the data), profit after advertising per scenario, profit added and break-even margin per channel.
- **Help.** A panel at the top explains inputs, bands, the range and the warnings for managers.
- **Gain as a range.** From `effects="benchmark"` (advertising works as published studies find) to `effects="model"` (as we measured it), because our social and influencer effects are two to seven times larger than the literature.

## How it is built

- One file, `app/dashboard.py`. It contains no model logic: it builds plans with `baseline_plan`, `scale_plan` and `shift_budget`, calls `gain_range` once per change, `profit_view` and `profit_gain` for the margin, and formats the result. If you need a number the interface does not give you, add it in `src/arla_mmm/interface.py` with a test, not here.
- Interface documentation: `docs/part2/INTERFACE.md`.
- A cell edited in the week table keeps its value when a slider moves afterwards. "Reset to current plan" clears sliders, price and edits.
- `tests/test_app.py` runs the app headless and checks that the warning follows the inputs (`pytest`).

## Deploy on Streamlit Community Cloud

The repo is ready: `requirements.txt` at the root has every pinned dependency, `.streamlit/config.toml` sets the look, the model file and the data are committed, and the app finds `src/arla_mmm` by itself when the package is not installed (the cloud only runs `pip install -r requirements.txt`). Tested locally in a fresh environment built that way.

Steps in the browser (about five minutes):

1. Go to https://share.streamlit.io and sign in with GitHub. Allow access to the repository when asked.
2. **Create app** → **Deploy a public app from GitHub**.
3. Repository `heytuna10/Arla-Protein-UK-Mixed-Modelling`, branch `dashboard_starter` (or `main` once it is merged), main file path `app/dashboard.py`.
4. **Advanced settings** → Python version **3.12**. No secrets are needed.
5. Choose the app URL, press **Deploy**, and wait for the first build (a few minutes).

Things to know:

- The repository belongs to Quentin's account. If it does not show up in the list or the deploy is refused, Streamlit needs someone with admin rights on the repo: ask Quentin to deploy, or to add you as an admin collaborator. Deploying from a fork of your own also works.
- The app redeploys on every push to the chosen branch. Anyone with the link can open it; inputs are per visitor and nothing is stored.
- Free apps go to sleep after a period without visitors and take about half a minute to wake up. Open the link shortly before a presentation.

## Ideas and open points

See the entries "Dashboard starter" and "Dashboard, second round" in `docs/part2/LOG.md`.
