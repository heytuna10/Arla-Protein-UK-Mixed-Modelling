# Arla Protein UK – Marketing Mix Model (DSBA term project, ESSEC × CentraleSupélec)

Weekly marketing mix model for Arla Protein UK (156 weeks, Jan 2022 – Dec 2024) plus a Streamlit scenario dashboard.
Data: `data/arla_protein_mmm_weekly.csv` (variables are described in `docs/part2/BRIEF.md`).
Team parts: 1 baseline + data prep (Ketan, Quentin) · 2 model extension (Jakob, Elvira) · 3 forecasting dashboard (Quentin, Ketan, Paola) · 4 slides · 5 pitch video.

## Working on part 2 (model extension)
1. Read `docs/part2/BRIEF.md` (goal, steps, acceptance criteria, decisions) and the latest entries of `docs/part2/LOG.md` before you start.
2. Do only the steps you were asked to do, then stop at the next checkpoint.
3. Before you finish, append an entry to `docs/part2/LOG.md` (format at the top of that file) and commit.
4. `BRIEF.md` is written by the planning side (Jakob + Claude in the desktop app). Don't edit it; put questions and proposed changes under "Open questions" in your LOG entry.

## Conventions (whole repo)
- Python ≥ 3.11, dependencies pinned in `requirements.txt`, package installed with `pip install -e .`.
- Reusable logic lives in `src/arla_mmm/`. Notebooks only call it and draw charts; they must run top to bottom from a fresh kernel with relative paths.
- Tables someone else needs to read go to `results/part2/` as small `.md`/`.csv` files; charts for the slides go to `results/part2/figures/` (PNG, readable at slide size).
- Never commit to `main` or to someone else's branch. Work on your own branch and merge via pull request.
- Commit messages: imperative and prefixed with the part, e.g. `part2: add geometric adstock`.
