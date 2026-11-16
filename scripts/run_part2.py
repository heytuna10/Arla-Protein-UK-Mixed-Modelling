"""Rebuild results/part2/ from scratch: evaluate every candidate in order (about 5 minutes)."""

import warnings

from arla_mmm.baseline import BASELINE, theta_method
from arla_mmm.candidates import STEP2_LADDER, STEP2_VARIANTS, make_spec
from arla_mmm.data import RESULTS_DIR, load_data
from arla_mmm.evaluate import evaluate, md_table, variants_table
from arla_mmm import robustness as rb
from arla_mmm.ladder import CHOSEN, SYNERGIES, carryover_table, final_config, step3_ladder, step3_variants, step4_ladder
from arla_mmm.tune import tune

VARIANT_ND = {"AIC": 1, "BIC": 1, "Breusch-Godfrey p": 3, "max VIF": 1}


def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    data = load_data()
    (RESULTS_DIR / "model_comparison.csv").unlink(missing_ok=True)
    candidates = [BASELINE] + [make_spec(c) for c in STEP2_LADDER] + step3_ladder(data) + step4_ladder(data)
    synergy_rows, chosen_row = [], None
    for spec in candidates:
        out = evaluate(spec, data)
        r = out["row"]
        if spec.name == CHOSEN:
            chosen_row = r
        ix = [c for c in out["fit"].params.index if c.startswith("ix_")]
        if len(ix) == 1:
            c, f, folds = ix[0], out["fit"], out["fold_params"][ix[0]]
            synergy_rows.append({
                "interaction": spec.config.interactions[0].replace(":", " × "),
                "coef": f.params[c], "t (HAC)": f.res_hac.tvalues[c], "p (HAC)": f.res_hac.pvalues[c],
                "range across training windows": f"{folds.min():.2f} to {folds.max():.2f}",
                "AIC vs M14": r["aic"] - chosen_row["aic"], "BIC vs M14": r["bic"] - chosen_row["bic"],
                f"hold-out MAPE % (M14: {chosen_row['ho26_mape']:.2f})": r["ho26_mape"],
                f"rolling MAPE % (M14: {chosen_row['cv_mape']:.2f})": r["cv_mape"],
                "kept": "no",
            })
        elif len(ix) > 1:
            all_row = r
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

    # ---- step 4: synergies
    import pandas as pd
    stories = "\n".join(f"- **{k.replace(':', ' × ')}**: {story}." for k, (_, story) in SYNERGIES.items())
    (RESULTS_DIR / "step4_synergies.md").write_text(
        "# Step 4 – synergies beyond the multiplicative structure\n\n"
        "The model is multiplicative: every driver already scales the effect of every other one (a week with TV on air "
        "has more sales for influencer spend to lift). The tests below ask whether a pair of drivers reinforces each "
        "other *more* than that. Four pairs were fixed before testing:\n\n" + stories + "\n\n"
        "Each interaction is the product of the two transformed media variables (centred at average spend; social = "
        "Instagram + TikTok; promo = promo depth), added to M14 with decays re-tuned. Rule: keep only if BIC and "
        "hold-out error improve and the sign is stable.\n\n"
        + md_table(pd.DataFrame(synergy_rows).set_index("interaction"), nd={"p (HAC)": 3, "AIC vs M14": 1, "BIC vs M14": 1})
        + f"\n\nAll four together: AIC {all_row['aic'] - chosen_row['aic']:+.1f}, BIC {all_row['bic'] - chosen_row['bic']:+.1f} vs M14, "
        f"hold-out MAPE {all_row['ho26_mape']:.2f}%, rolling {all_row['cv_mape']:.2f}%.\n\n"
        "Positive AIC/BIC differences = worse than M14. None is kept.\n"
    )

    # ---- step 5: robustness of the final model
    cfg, search = final_config(data)
    final = tune(cfg, search, data)[0]
    sens = rb.sensitivity(final, search, data)
    add, add_info = rb.additive_model(final, search, data)
    sub = rb.subperiods(final, search, data)
    lead, lead_p = rb.lead_test(final, data)
    infl, infl_weeks = rb.influence(final, data)
    se = rb.se_comparison(final, data)
    roi_cols = [c for c in sens.columns if c.startswith(("ROI", "mROI"))]
    rng = pd.DataFrame({"final": sens.iloc[0][roi_cols], "lowest": sens[roi_cols].min(), "highest": sens[roi_cols].max()})
    rng["spread % of final"] = (rng["highest"] - rng["lowest"]) / rng["final"] * 100
    (RESULTS_DIR / "step5_robustness.md").write_text(
        f"# Step 5 – robustness of the final model ({CHOSEN})\n\n"
        "ROI = revenue ROI above the observed floor (TV: vs zero); mROI = revenue per extra £ for +10% spend.\n\n"
        "## 1. Sensitivity to the carry-over and saturation choices\n\n"
        "One choice changed at a time, regression re-estimated.\n\n"
        + md_table(sens, nd={"AIC": 1}) + "\n\n"
        "Range over all rows above:\n\n" + md_table(rng.rename_axis("metric"), nd={"spread % of final": 0}) + "\n\n"
        "## 2. Multiplicative vs additive\n\n"
        "The same drivers in an additive model of units (no logs), decays re-tuned "
        f"({', '.join(f'{k} {v}' for k, v in add_info['decay'].items())}).\n\n"
        + md_table(add, nd={"AIC": 1}) + "\n\n"
        f"On a common scale (likelihood of units) the final model's AIC is {add_info['aic_final_units']:,.1f} against "
        f"{add_info['aic_additive_units']:,.1f} for the additive model, and the additive hold-out error is "
        f"{add_info['holdout_additive']:.1f}%. The ROI columns are not like for like (in an additive model the average and "
        "the marginal return coincide up to saturation); the marginal ROIs are the comparable numbers.\n\n"
        "## 3. Stability over time\n\n"
        "Model re-estimated on parts of the history (decays re-tuned for windows starting at week 1; "
        "windows starting later use the final decays).\n\n" + md_table(sub.rename_axis("sample"), nd=2) + "\n\n"
        "## 4. Placebo: does next week's spend 'explain' this week's sales?\n\n"
        "It cannot be causal. If budgets were raised ahead of expected demand, these coefficients would be positive and "
        "significant.\n\n" + md_table(lead.rename_axis("channel"), nd=3)
        + f"\n\nJoint test of all five (HAC F-test): p = {lead_p:.2f}.\n\n"
        "## 5. Influential weeks\n\n"
        f"Weeks with the largest Cook's distance: {', '.join(infl_weeks)}.\n\n"
        + md_table(infl.rename_axis("coefficient"), nd={"change %": 1, "all weeks": 3, infl.columns[1]: 3}) + "\n\n"
        "## 6. Standard errors\n\n"
        "Newey-West (4 lags) against plain OLS, with 95% intervals from the Newey-West errors.\n\n"
        + md_table(se.rename_axis("term"), nd=3) + "\n"
    )


if __name__ == "__main__":
    main()
