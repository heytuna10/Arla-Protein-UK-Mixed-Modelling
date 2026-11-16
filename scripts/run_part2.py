"""Rebuild results/part2/ from scratch: evaluate every candidate in order."""

from arla_mmm.baseline import BASELINE, theta_method
from arla_mmm.data import RESULTS_DIR, load_data
from arla_mmm.evaluate import evaluate, md_table

CANDIDATES = [BASELINE]


def main() -> None:
    data = load_data()
    for stale in (RESULTS_DIR / "model_comparison.csv",):
        stale.unlink(missing_ok=True)
    for spec in CANDIDATES:
        out = evaluate(spec, data)
        r = out["row"]
        print(f"{spec.name}: R2 {r['r2']:.3f}  AIC {r['aic']:.1f}  BIC {r['bic']:.1f}  "
              f"hold-out MAPE {r['ho26_mape']:.1f}%  rolling {r['cv_mape']:.1f}%")
        if spec is BASELINE:
            theta = theta_method(out["fit"].params, data)
            path = RESULTS_DIR / "baseline_part1_method.md"
            path.write_text(
                "# Baseline with part 1's attribution method (reference only)\n\n"
                "Reproduces `notebooks/01_exploratory_analysis.ipynb` (theta = beta x mean sales / mean spend; "
                "contribution = theta x total spend; ROI at the average price).\n\n"
                + md_table(theta.rename_axis("channel"), nd={"beta": 4, "contribution_units": 0, "pct_of_total_sales": 1})
                + f"\n\nSum of channel contributions = {theta['pct_of_total_sales'].sum():.0f}% of total sales, "
                "before any base sales.\n"
            )


if __name__ == "__main__":
    main()
