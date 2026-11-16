"""Step 9: diagnostics behind results/part2/step9_critical_review.md (about 10 seconds)."""

import warnings

import numpy as np
import pandas as pd

from arla_mmm import anchored as an
from arla_mmm import figures as fg
from arla_mmm import insights as ins
from arla_mmm import review as rv
from arla_mmm.data import CHANNELS, RESULTS_DIR
from arla_mmm.evaluate import md_table
from arla_mmm.final import final_model
from arla_mmm.interface import backtest, baseline_plan, compare_scenarios, load_model, scale_plan

L = ins.LABEL


def main() -> None:
    warnings.filterwarnings("ignore")
    m = final_model()
    d = m.data
    roi, el = ins.roi_summary(m), ins.elasticities(m)
    bench = ins.BENCHMARK["long"]

    sp = rv.spend_process(m).rename(index=L)
    lead = rv.lead_placebo(m).rename(columns={f"{c} p": f"{L[c]} p" for c in CHANNELS})
    fs = rv.frequency_split(m).rename(index=L)
    agg, corr = rv.digital_aggregate(m)
    corr = corr.rename(index=L, columns=L)
    spend_corr = d[CHANNELS].corr().rename(index=L, columns=L)
    noise = rv.forecast_noise(m)
    bt = backtest(horizon=13, origins=(91, 104, 117, 130, 143))
    oos = np.log(bt["actual_units"] / bt["units_p50"]).groupby(bt["origin"]).mean()
    oos_sd = float(np.sqrt((oos ** 2).mean()))
    profit = rv.profit_view(roi, el, bench)

    model = load_model()
    base = baseline_plan(model, 13)
    moves = {"TV −10%": {"tv": 0.9}, "Instagram +10%": {"instagram": 1.1}, "TikTok +10%": {"tiktok": 1.1},
             "Influencer +10%": {"influencer": 1.1},
             "all four (the first-step plan)": {"tv": 0.9, "instagram": 1.1, "tiktok": 1.1, "influencer": 1.1}}
    comp, _ = compare_scenarios(model, {"current": base, **{k: scale_plan(base, v) for k, v in moves.items()}}, "current")
    lt = el["long-term"]
    bench_world = {"TV −10%": -0.1 * lt["TV"], "Instagram +10%": 0.1 * bench, "TikTok +10%": 0.1 * bench, "Influencer +10%": 0.1 * bench}
    bench_world["all four (the first-step plan)"] = sum(bench_world.values())
    test = pd.DataFrame({"model: units over 13 weeks %": comp.loc[list(moves), "delta_units_pct"],
                         "if digital effects were benchmark-sized %": pd.Series(bench_world) * 100})

    total_el = float(lt.sum())
    ad_ratio = float(d[CHANNELS].sum().sum() / d["revenue"].sum() * 100)
    k = 2.49
    lines = [
        "# Step 9 – diagnostics for the critical review",
        "",
        "Tables behind `step9_critical_review.md`. Final model M14 unless stated; p-values use Newey-West errors. Rebuild: `python scripts/run_review.py`.",
        "",
        "## 1. Does spend follow demand?",
        "",
        "### 1a. How weekly spend behaves",
        "",
        "Log spend (TV: on air yes/no) regressed on the model's demand drivers and last week's log sales.",
        "",
        md_table(sp.T.rename_axis(""), nd=3),
        "",
        "- Digital spend does not rise in promotion weeks (when demand is about 13% higher) and does not respond to last week's sales. "
        "Influencer spend is unrelated to anything in the data (R² 0.03) and close to random from week to week.",
        "- POS spend is the exception: it is clearly higher in promotion weeks (coefficient 0.95 on promotion depth: about +30% spend in a 24%-off week). "
        "The model controls for promotion depth, so the POS effect is measured on the remaining variation, but POS and price promotions are run together and their effects are harder to separate than the others.",
        "- TV, Instagram and TikTok follow a seasonal calendar; the model has seasonal terms.",
        "",
        "### 1b. Placebo at longer horizons: does future spend 'explain' current sales?",
        "",
        md_table(lead.rename_axis("average spend over the"), nd=3),
        "",
        "- No signal for any always-on channel at 1, 4 or 8 weeks. TV at 8 weeks is significant (p 0.005) with a small negative sign "
        "(sales are slightly *lower* before TV-heavy periods); the joint tests are not significant, and adding the leads leaves every media coefficient unchanged.",
        "",
        "### 1c. Slow and fast movements of spend",
        "",
        "Each always-on regressor split into its 13-week average (budget level) and the week-to-week deviation.",
        "",
        md_table(fs.rename_axis("channel"), nd={"share of the regressor's variance that is fast %": 0, "p (slow = fast)": 3}),
        "",
        "- The coefficients on the slow and the fast part do not differ for any channel; for influencer they are identical (4.32 and 4.33). "
        "The effect is identified almost entirely from week-to-week movements (74–97% of the variation), which quarterly or monthly budget planning cannot produce.",
        f"- The split does not improve the fit (AIC {fs.attrs['aic'] + 12:.1f} against {fs.attrs['aic_final'] + 12:.1f}).",
        "",
        "## 2. One shared digital effect?",
        "",
        "Correlation of weekly spend between channels:",
        "",
        md_table(spend_corr.rename_axis(""), nd=2),
        "",
        "Correlation between the estimated media coefficients:",
        "",
        md_table(corr.rename_axis(""), nd=2),
        "",
        "The model with Instagram, TikTok and influencer spend added into one digital channel:",
        "",
        md_table(agg.rename_axis(""), nd=2),
        "",
        "- The three digital budgets are uncorrelated (largest |r| 0.12), so there is no common movement to split, and the coefficient for influencer is uncorrelated with those of Instagram and TikTok.",
        f"- Forcing one digital effect makes the model far worse (AIC {agg.iloc[1, 1]:.0f} against {agg.iloc[1, 0]:.0f}, hold-out error {agg.iloc[3, 1]:.1f}% against {agg.iloc[3, 0]:.1f}%). "
        "The data insist on three different effects. The return on digital as a whole stays of the same order (£38 against £47 per extra £).",
        "",
        "## 3. Sizes in context",
        "",
        f"- Sum of the five long-term elasticities: **{total_el:.2f}**. The benchmark of {bench} is for a brand's advertising, so the total is about {total_el / bench:.0f} times it.",
        f"- Media spend is {ad_ratio:.0f}% of revenue over the three years.",
        f"- With the floor reference the model credits media with {100 - roi.attrs['base']['estimate']:.0f}% of sales (five channels; step 6).",
        "",
        "## 4. Test design: what can a test detect?",
        "",
        "Spread of the average multi-week forecast error (model given the actual inputs), and the smallest change in sales a test of that length can detect (one-sided 5%, 80% power):",
        "",
        md_table(noise.rename_axis("test length"), nd={"forecasts compared": 0}),
        "",
        f"- These use coefficients fitted on all weeks. Five out-of-sample 13-week forecasts (step-8 back-test method) have a spread of {oos_sd * 100:.1f}%, "
        f"which gives a minimum detectable change of {(np.exp(k * oos_sd) - 1) * 100:.0f}%. Plan with 3–6% for 13 weeks.",
        "",
        "What the first-step plan should do over 13 weeks, by component:",
        "",
        md_table(test.rename_axis("change"), nd=1),
        "",
        "## 5. Profit view",
        "",
        "Profit per extra £ of spend = margin × revenue per extra £ − 1. Right-hand block: the same with every channel above the benchmark scaled down to a long-term elasticity of 0.24.",
        "",
        md_table(profit.T.rename_axis(""), nd=2),
        "",
    ]
    (RESULTS_DIR / "step9_diagnostics.md").write_text("\n".join(lines))

    # ------------------------------------------------------------ benchmark-anchored regression
    sw = an.sweep(m)
    target = an.benchmark_coefficients(m)
    part1 = float(pd.read_csv(RESULTS_DIR / "model_comparison.csv").set_index("model").loc["M0_baseline", "ho26_mape"])
    fg.anchored(sw, bench, part1)
    names = [L[c] for c in CHANNELS]
    fit_md = sw[["R²", "residual sd %", "Δ AIC vs final model", "hold-out error %", "lagged sales", "first-step plan, Δ revenue %"]]
    el_md = sw[[f"elasticity {n}" for n in names]].rename(columns=lambda c: c.replace("elasticity ", ""))
    roi_md = sw[[f"mROI {n}" for n in names]].rename(columns=lambda c: c.replace("mROI ", ""))
    roi_md["ranking"] = sw["ranking by return on the next £"]
    first, last = sw.iloc[0], sw.iloc[-1]
    half = sw.loc["±25%"]
    coef = pd.DataFrame({"estimated": m.fit.params[CHANNELS].to_numpy(), "benchmark-sized": target.to_numpy(),
                         "standard error (Newey-West)": m.fit.res_hac.bse[CHANNELS].to_numpy()}, index=names)
    lines = [
        "# Step 9 – benchmark-anchored regression: what does plausibility cost?",
        "",
        "The final model (M14, carry-over rates and curve scales fixed) re-estimated with a normal prior on each of the five media "
        f"coefficients, centred on the value that gives the channel the literature's average long-term elasticity of {bench} "
        "(Sethuraman, Tellis & Briesch 2011). All other coefficients are free. The prior's strength is one number: its standard "
        "deviation as a percentage of the benchmark-sized coefficient. \"±100%\" is a loose belief that the true effect is "
        "somewhere between zero and twice the benchmark; \"±10%\" is a firm one; \"fixed\" forces the benchmark. "
        "Closed form (a ridge penalty towards a target), no sampling. Code: `src/arla_mmm/anchored.py`. Figure: `figures/anchored.png`.",
        "",
        "Media coefficients:",
        "",
        md_table(coef.rename_axis("channel"), nd=3),
        "",
        "## Fit and forecast along the sweep",
        "",
        "Hold-out error: coefficients re-estimated with the same prior on the weeks before the last 26, then a 26-week forecast. "
        "First-step plan: TV −10%, Instagram, TikTok and influencer +10%, replay of 2024.",
        "",
        md_table(fit_md.rename_axis("prior"), nd={"R²": 3, "Δ AIC vs final model": 1, "first-step plan, Δ revenue %": 1}),
        "",
        "## Long-term elasticity per channel",
        "",
        md_table(el_md.rename_axis("prior"), nd=2),
        "",
        "## Revenue per extra £",
        "",
        md_table(roi_md.rename_axis("prior"), nd=1),
        "",
        "## Reading",
        "",
        f"- **An honest prior changes nothing.** Up to ±100% the estimates do not move (influencer {first['elasticity Influencer']:.2f} → "
        f"{sw.loc['±100%', 'elasticity Influencer']:.2f}). The data are too informative: the influencer coefficient is measured to within 3%.",
        f"- **Plausible sizes have to be forced, and forcing them breaks the model.** Even a prior of ±25% leaves influencer at "
        f"{half['elasticity Influencer']:.2f} and already costs {half['Δ AIC vs final model']:.0f} AIC points. Fixed at the benchmark, "
        f"R² falls from {first['R²']:.2f} to {last['R²']:.2f} and the forecast error on unseen weeks rises from {first['hold-out error %']:.1f}% to "
        f"{last['hold-out error %']:.1f}%, worse than part 1's model ({part1:.1f}%). The large effects are a property of the data, not of our specification.",
        f"- **The ranking digital > POS > TV holds at every strength.** At the benchmark an extra £ returns about "
        f"£{last['mROI Instagram']:.0f}–{last['mROI TikTok']:.0f} on each digital channel, £{last['mROI POS']:.1f} on POS and £{last['mROI TV']:.1f} on TV, "
        "although the prior doubles TV's effect. Equal elasticities give the higher return to the smaller budget.",
        "- **The order among the three digital channels does not hold.** Influencer leads without a prior, TikTok at the benchmark.",
        f"- **The gain from the first-step plan ranges from {last['first-step plan, Δ revenue %']:.0f}% to {first['first-step plan, Δ revenue %']:.0f}%** "
        "of revenue between the two ends. That range, not either number, is what we know before a test.",
        "",
        "This differs slightly from the arithmetic in `step9_critical_review.md` (about +6%), which scaled only the three digital "
        "channels and left TV as estimated; here all five channels are tied to the benchmark and the rest of the model is re-estimated.",
        "",
    ]
    (RESULTS_DIR / "step9_anchored.md").write_text("\n".join(lines))
    print("written", RESULTS_DIR / "step9_diagnostics.md", "and step9_anchored.md")


if __name__ == "__main__":
    main()
