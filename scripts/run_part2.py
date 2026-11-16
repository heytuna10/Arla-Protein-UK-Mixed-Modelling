"""Rebuild results/part2/ from scratch: evaluate every candidate in order (about 3 minutes)."""

import warnings

from arla_mmm.baseline import BASELINE, theta_method
from arla_mmm.candidates import STEP2_LADDER, STEP2_VARIANTS, make_spec
from arla_mmm.data import RESULTS_DIR, load_data
from arla_mmm.evaluate import evaluate, md_table, variants_table
from arla_mmm.ladder import CHOSEN, carryover_table, step3_ladder, step3_variants

VARIANT_ND = {"AIC": 1, "BIC": 1, "Breusch-Godfrey p": 3, "max VIF": 1}


def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    data = load_data()
    (RESULTS_DIR / "model_comparison.csv").unlink(missing_ok=True)
    candidates = [BASELINE] + [make_spec(c) for c in STEP2_LADDER] + step3_ladder(data)
    for spec in candidates:
        out = evaluate(spec, data)
        r = out["row"]
        print(f"{spec.name}: R2 {r['r2']:.3f}  AIC {r['aic']:.1f}  BIC {r['bic']:.1f}  "
              f"hold-out MAPE {r['ho26_mape']:.1f}%  rolling {r['cv_mape']:.1f}%", flush=True)
        if spec is BASELINE:
            theta = theta_method(out["fit"].params, data)
            (RESULTS_DIR / "baseline_part1_method.md").write_text(
                "# Baseline with part 1's attribution method (reference only)\n\n"
                "Reproduces `notebooks/01_exploratory_analysis.ipynb` (theta = beta x mean sales / mean spend; "
                "contribution = theta x total spend; ROI at the average price).\n\n"
                + md_table(theta.rename_axis("channel"), nd={"beta": 4, "contribution_units": 0, "pct_of_total_sales": 1})
                + f"\n\nSum of channel contributions = {theta['pct_of_total_sales'].sum():.0f}% of total sales, "
                "before any base sales.\n"
            )
        if spec.name == CHOSEN:
            carry = carryover_table(spec.config, out["fit"].params["lagged_sales"])
            carry_md = md_table(carry.rename_axis("channel"), nd={"adstock decay": 1, "% of effect in week of spend": 0,
                                                                  "% within 4 weeks": 0, "weeks to 90% of effect": 0})

    table = variants_table([make_spec(c) for c in STEP2_VARIANTS], data)
    (RESULTS_DIR / "step2_controls.md").write_text(
        "# Step 2 – alternatives around the chosen controls (M5)\n\n"
        "Each row changes one thing in M5 (media still as in part 1: log(spend + 1), lagged sales). "
        "Same sample and error measures as `model_comparison.md`.\n\n" + md_table(table, nd=VARIANT_ND) + "\n"
    )
    table = variants_table(step3_variants(data), data)
    (RESULTS_DIR / "step3_media.md").write_text(
        f"# Step 3 – alternatives around the chosen media model ({CHOSEN})\n\n"
        "Each row changes one thing; decays (and scales where tuned) are re-searched for every row and inside every "
        "hold-out fold. `params` includes the grid-searched ones.\n\n" + md_table(table, nd=VARIANT_ND)
        + f"\n\n## How each channel's effect is spread over time ({CHOSEN})\n\n"
        "Response of log sales to one week of extra spend: the channel's own adstock decay combined with the "
        "lagged-sales term (repeat purchase), which applies to every channel.\n\n" + carry_md + "\n"
    )


if __name__ == "__main__":
    main()
