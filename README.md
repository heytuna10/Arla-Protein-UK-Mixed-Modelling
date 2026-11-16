# Arla-Protein-UK-Mixed-Modelling

## Part 2 – model extension

The extended marketing mix model, its results and the interface for the dashboard.

- Summary for the slides: [results/part2/SUMMARY.md](results/part2/SUMMARY.md)
- How the dashboard calls the model: [docs/part2/INTERFACE.md](docs/part2/INTERFACE.md)
- The story with charts: [notebooks/02_model_extension.ipynb](notebooks/02_model_extension.ipynb)
- Critical review (what we can claim, profit view, test design): [results/part2/step9_critical_review.md](results/part2/step9_critical_review.md)
- Every decision with its reason: [docs/part2/LOG.md](docs/part2/LOG.md)

```bash
pip install -r requirements.txt && pip install -e .
python scripts/run_part2.py && python scripts/run_insights.py && python scripts/run_interface.py && python scripts/run_review.py   # rebuilds results/part2/
pytest
```
