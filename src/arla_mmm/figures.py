"""Slide-ready charts (PNG) for results/part2/figures/. One visual system for all of them:
fixed colour per channel, thin marks, light grid, labels in ink (never in the series colour)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

from .data import CHANNELS, RESULTS_DIR

FIG_DIR = RESULTS_DIR / "figures"
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a897f", "#e6e5df"
COLOR = {"tv": "#2a78d6", "instagram": "#eb6834", "tiktok": "#1baf7a", "influencer": "#eda100",
         "pos_promotion": "#e87ba4", "promotions": "#008300", "growth": "#9a998f", "base": "#c9c8bf"}
NAME = {"tv": "TV", "instagram": "Instagram", "tiktok": "TikTok", "influencer": "Influencer",
        "pos_promotion": "POS promotion", "promotions": "Price promotions", "growth": "Growth since Jan 2022",
        "base": "Base incl. minimum always-on media"}
BLUES = ["#86b6ef", "#2a78d6", "#104281"]            # ordinal ramp (light -> dark)

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "sans-serif", "font.size": 12, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2, "axes.titlesize": 15,
    "axes.titleweight": "semibold", "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1.0,
    "axes.axisbelow": True, "legend.frameon": False, "xtick.major.size": 0, "ytick.major.size": 0,
})


def _save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return path


def _title(ax, title: str, subtitle: str = "") -> None:
    ax.set_title(title, pad=(14 + 19 * (subtitle.count("\n") + 1)) if subtitle else 12)
    if subtitle:
        ax.text(0, 1.0, subtitle, transform=ax.transAxes, va="bottom", ha="left", fontsize=11.5, color=INK2,
                linespacing=1.3)


def _k(v, _=None) -> str:
    return f"{v / 1e3:,.0f}K" if abs(v) >= 1e3 else f"{v:,.0f}"


def decomposition(weekly: pd.DataFrame) -> Path:
    """Average weekly units per quarter, split into base, growth, promotions and channels."""
    order = ["base", "growth", "promotions", "pos_promotion", "tv", "tiktok", "instagram", "influencer"]
    q = weekly.set_index("week_beg")[order].resample("QS").mean()
    labels = [f"Q{d.quarter}\n{d.year}" if d.quarter == 1 else f"Q{d.quarter}" for d in q.index]
    fig, ax = plt.subplots(figsize=(12, 6.2))
    x, bottom = np.arange(len(q)), np.zeros(len(q))
    for c in order:
        ax.bar(x, q[c], bottom=bottom, width=0.5, color=COLOR[c], edgecolor=SURFACE, linewidth=2, label=NAME[c])
        bottom += q[c].to_numpy()
    for xi, tot in zip(x, bottom):
        ax.text(xi, tot + 12000, _k(tot), ha="center", va="bottom", fontsize=10.5, color=INK2)
    ax.set_xticks(x, labels)
    ax.yaxis.set_major_formatter(FuncFormatter(_k))
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Units per week (quarter average)")
    handles, lab = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], lab[::-1], loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=11, handlelength=1.1)
    _title(ax, "Where weekly sales come from", "Parts add up to actual sales. Channel parts = sales above what the lowest spend ever observed would deliver (TV: above zero).")
    return _save(fig, "decomposition.png")


def roi(summary: pd.DataFrame) -> Path:
    """ROI above the floor and marginal ROI per channel, with 5-95% intervals, on a log axis."""
    chans = sorted(CHANNELS, key=lambda c: summary.loc[_lab(c), "marginal ROI"])
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)
    spec = [("ROI", "ROI p5", "ROI p95", "Average return", "£ revenue per £ spent above the lowest level observed (TV: per £)"),
            ("marginal ROI", "mROI p5", "mROI p95", "Return on the next £", "£ revenue per extra £ (+10% spend in every week)")]
    for ax, (col, lo, hi, title, sub) in zip(axes, spec):
        for i, c in enumerate(chans):
            r = summary.loc[_lab(c)]
            ax.plot([r[lo], r[hi]], [i, i], color=COLOR[c], linewidth=2, solid_capstyle="round")
            ax.plot(r[col], i, "o", color=COLOR[c], markersize=10, markeredgecolor=SURFACE, markeredgewidth=2)
            ax.text(r[hi] * 1.18, i, f"£{r[col]:.2f}" if r[col] < 10 else f"£{r[col]:.0f}", va="center", fontsize=12, color=INK)
        ax.axvline(1, color=MUTED, linewidth=1)
        ax.text(1, len(chans) - 0.42, " £1 back per £1", fontsize=10, color=MUTED, va="bottom")
        ax.set_xscale("log")
        ax.set_xlim(0.5, 220)
        ax.set_xticks([1, 3, 10, 30, 100], ["£1", "£3", "£10", "£30", "£100"])
        ax.minorticks_off()
        ax.set_ylim(-0.6, len(chans) - 0.2)
        ax.set_yticks(range(len(chans)), [NAME[c] for c in chans])
        ax.grid(axis="y", visible=False)
        _title(ax, title, sub)
    fig.text(0.01, -0.03, "Revenue, not profit. Lines show the 5–95% range from coefficient uncertainty. Log scale.", fontsize=10.5, color=INK2)
    fig.tight_layout(w_pad=3)
    return _save(fig, "roi.png")


def _money(v, _=None) -> str:
    sign = "−" if v < 0 else ""
    v = abs(v)
    if v < 500:
        return "£0"
    return f"{sign}£{v / 1e6:.1f}M" if v >= 1e5 else f"{sign}£{v / 1e3:,.0f}K"


def _lab(c: str) -> str:
    return {"tv": "TV", "instagram": "Instagram", "tiktok": "TikTok", "influencer": "Influencer", "pos_promotion": "POS"}[c]


def response_curves(curves: pd.DataFrame, sustained: dict[str, tuple[float, float]]) -> Path:
    """Small multiples: weekly revenue gained vs weekly spend held constant, one panel per channel."""
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.6))
    axes = axes.ravel()
    for ax, c in zip(axes, CHANNELS):
        d = curves[curves["channel"] == c]
        lo, hi = (0.0 if c == "tv" else d["observed_min"].iloc[0]), d["observed_max"].iloc[0]
        s_lo, s_hi = sustained[c]
        ax.axvspan(lo, hi, color=GRID, alpha=0.55, linewidth=0)
        ax.axvspan(s_lo, s_hi, color="#d2d1c8", alpha=0.9, linewidth=0)
        inside = (d["weekly_spend"] >= s_lo) & (d["weekly_spend"] <= s_hi)
        ax.fill_between(d["weekly_spend"], d["p5"], d["p95"], color=COLOR[c], alpha=0.12, linewidth=0)
        ax.plot(d["weekly_spend"], d["incremental_revenue"], color=COLOR[c], linewidth=1.3, alpha=0.55)
        ax.plot(d.loc[inside, "weekly_spend"], d.loc[inside, "incremental_revenue"], color=COLOR[c], linewidth=2.6,
                solid_capstyle="round")
        ax.set_xlim(0, d["weekly_spend"].max())
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: "£0" if v == 0 else f"£{v / 1e3:,.0f}K"))
        ax.yaxis.set_major_formatter(FuncFormatter(_money))
        ax.xaxis.set_major_locator(plt.MaxNLocator(4))
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        ax.set_title(NAME[c], fontsize=13.5)
    ax = axes[-1]
    ax.axis("off")
    notes = [
        ("#d2d1c8", "Spend levels held for a quarter at some point (13-week averages observed)"),
        (GRID, "Spend levels seen in single weeks only"),
        (None, "Thick line: where the model has evidence.\nThin line: extrapolation."),
        (None, "Vertical axis: revenue per week once the spend level has been\nheld long enough to settle, against the lowest level observed\n(TV: against no TV). Band = 5–95% range."),
    ]
    y = 0.95
    for col, text in notes:
        if col:
            ax.add_patch(plt.Rectangle((0.0, y - 0.045), 0.07, 0.07, transform=ax.transAxes, color=col, clip_on=False))
        ax.text(0.1 if col else 0.0, y, text, transform=ax.transAxes, va="top" if not col else "center", fontsize=11, color=INK2)
        y -= 0.17 if col else 0.24
    fig.suptitle("What a sustained weekly spend level is worth, by channel", x=0.012, ha="left", fontsize=16, fontweight="semibold")
    fig.supxlabel("Weekly spend held constant", fontsize=12, color=INK2)
    fig.tight_layout(h_pad=2.2, w_pad=2)
    return _save(fig, "response_curves.png")


def model_ladder(comparison: pd.DataFrame) -> Path:
    steps = [("M0_baseline", "Part 1 baseline"), ("M1_trend", "+ trend"), ("M2_season", "+ seasonality"),
             ("M5_january", "+ shelf price / promo depth,\npost-promo dip, January"),
             ("M9_adstock_lag", "+ carry-over per channel\n(with repeat purchase)"),
             ("M14_hill", "+ diminishing-returns curve\n= final model")]
    t = comparison.set_index("model")
    vals = [t.loc[k, "ho26_mape"] for k, _ in steps]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    y = np.arange(len(steps))[::-1]
    ax.barh(y, vals, height=0.42, color=COLOR["tv"])
    for yi, v in zip(y, vals):
        ax.text(v + 0.15, yi, f"{v:.1f}%", va="center", fontsize=12.5)
    ax.set_yticks(y, [s for _, s in steps])
    ax.set_xlim(0, max(vals) * 1.12)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", visible=False)
    _title(ax, "Each extension makes the forecast better", "Average error when forecasting the last 26 weeks of unit sales from the weeks before (lower is better)")
    return _save(fig, "model_ladder.png")


def fit_holdout(weeks, actual, fitted, forecast, origin: int) -> Path:
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.axvspan(weeks[origin], weeks[-1], color=GRID, alpha=0.5, linewidth=0)
    ax.plot(weeks, actual, color=INK2, linewidth=2, label="Actual sales")
    ax.plot(weeks[:origin], fitted[:origin], color=COLOR["tv"], linewidth=2, label="Model one week ahead, weeks it was trained on")
    ax.plot(weeks[origin:], forecast, color=COLOR["instagram"], linewidth=2, label="Model forecast, weeks it never saw")
    ax.yaxis.set_major_formatter(FuncFormatter(_k))
    ax.set_ylabel("Units per week")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", ncols=3, fontsize=11, bbox_to_anchor=(0, 1.0))
    ax.set_ylim(0, max(actual) * 1.18)
    err = np.mean(np.abs(forecast - actual[origin:]) / actual[origin:]) * 100
    ax.text(weeks[-1], max(actual) * 0.05, f"Last 26 weeks: forecast from spend, price\nand promotions only. Average error {err:.1f}%.", fontsize=11, color=INK2, ha="right")
    _title(ax, "The model tracks sales, including weeks it was not trained on")
    return _save(fig, "fit_holdout.png")


SCENARIO_SUB = ("Replay of 2024 with a different media plan. Black line: 5–95% range from coefficient uncertainty only.\n"
                "These are what the model implies, not a forecast: the larger the change, the further it is from anything observed.")


def scenarios(table: pd.DataFrame, keys: list[str], name: str = "scenarios.png",
              title: str = "Model-implied revenue change vs the 2024 plan", subtitle: str = SCENARIO_SUB) -> Path:
    t = table.loc[keys]
    fig, ax = plt.subplots(figsize=(11.5, 0.9 * len(keys) + 2.2))
    y = np.arange(len(t))[::-1]
    ax.barh(y, t["Δ revenue £m"], height=0.3, color=COLOR["tv"])
    ax.hlines(y, t["Δ p5"], t["Δ p95"], color=INK, linewidth=1.5)
    for yi, (_, r) in zip(y, t.iterrows()):
        label = f"+£{r['Δ revenue £m']:.0f}m  ({r['Δ revenue %']:+.0f}%)" if abs(r["Δ revenue £m"]) > 1e-9 else "reference"
        ax.text(max(r["Δ p95"], 0) + 0.6, yi, label, va="center", fontsize=12)
    ax.set_yticks(y, [k.split(" · ")[1] if " · " in k else k for k in t.index])
    ax.set_xlim(0, t["Δ p95"].max() * 1.3)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v:.0f}m"))
    ax.grid(axis="y", visible=False)
    _title(ax, title, subtitle)
    return _save(fig, name)


def allocation(plans: dict[str, pd.Series], title_sub: str, name: str = "allocation.png", legend_below: bool = False) -> Path:
    """Annual spend per channel for up to three ordered plans (ordinal blue ramp, legend + value labels)."""
    names = list(plans)
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    h = 0.22
    y0 = np.arange(len(CHANNELS))[::-1]
    for j, n in enumerate(names):
        vals = plans[n][CHANNELS].to_numpy() / 1e6
        yy = y0 + (len(names) / 2 - 0.5 - j) * (h + 0.04)
        ax.barh(yy, vals, height=h, color=BLUES[j], label=n)
        for a, v in zip(yy, vals):
            ax.text(v + 0.03, a, f"£{v:.2f}m", va="center", fontsize=10.5, color=INK2)
    ax.set_yticks(y0, [NAME[c] for c in CHANNELS])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v:.1f}m"))
    ax.set_xlim(0, max(p[CHANNELS].max() for p in plans.values()) / 1e6 * 1.15)
    ax.grid(axis="y", visible=False)
    if legend_below:
        ax.legend(loc="upper left", bbox_to_anchor=(0, -0.08), ncol=len(names), fontsize=11, columnspacing=1.6)
    else:
        ax.legend(loc="lower right", fontsize=11)
    _title(ax, "Same budget, shifted from TV towards social and influencers", title_sub)
    return _save(fig, name)


def promotions(curve: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10.5, 5))
    x = np.arange(len(curve))
    w = 0.3
    ax.bar(x - w / 2 - 0.02, curve["total units %"], width=w, color=BLUES[0], label="Units")
    ax.bar(x + w / 2 + 0.02, curve["total revenue %"], width=w, color=BLUES[2], label="Revenue")
    ax.vlines(x + w / 2 + 0.02, curve["total revenue p5"], curve["total revenue p95"], color=INK2, linewidth=1.5)
    for xi, (_, r) in zip(x, curve.iterrows()):
        ax.text(xi - w / 2 - 0.02, r["total units %"] + 0.6, f"+{r['total units %']:.0f}%", ha="center", fontsize=11)
        ax.text(xi + w / 2 + 0.02, r["total revenue p5"] - 0.6, f"−{abs(r['total revenue %']):.0f}%", ha="center", va="top", fontsize=11)
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.set_xticks(x, curve.index)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: "0%" if v == 0 else f"{v:+.0f}%".replace("-", "−")))
    ax.set_ylim(curve["total revenue p5"].min() - 4, curve["total units %"].max() + 5)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", ncols=2, fontsize=11)
    _title(ax, "Price promotions sell more units but cost revenue", "Effect of one promotion week, incl. the weeks after, in % of a normal week. Line: 5–95% range.")
    return _save(fig, "promotions.png")


def forecast_fan(history: pd.DataFrame, forecasts: dict[str, pd.DataFrame], weeks_back: int = 26) -> Path:
    """Interface example: the last weeks of history and the forecast (median, 5-95% band) for up to three plans."""
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    h = history.tail(weeks_back)
    ax.plot(h["week_beg"], h["revenue"], color=INK, linewidth=2, label="Observed")
    last = h.iloc[-1]
    colours = [MUTED, COLOR["tv"], COLOR["influencer"]]
    for (name, w), c in zip(forecasts.items(), colours):
        x = np.r_[last["week_beg"].to_datetime64(), w["week_beg"].to_numpy()]
        ax.fill_between(x, np.r_[last["revenue"], w["revenue_p5"]], np.r_[last["revenue"], w["revenue_p95"]],
                        color=c, alpha=0.16, linewidth=0)
        ax.plot(x, np.r_[last["revenue"], w["revenue_p50"]], color=c, linewidth=2, label=name)
    ax.axvline(last["week_beg"], color=GRID, linewidth=1.5)
    ax.yaxis.set_major_locator(MultipleLocator(0.5e6))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v / 1e6:.1f}m"))
    ax.set_ylim(0, None)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower left", fontsize=11, title="Forecasts: median and 5–95% band", title_fontsize=10.5, alignment="left")
    _title(ax, "What the dashboard gets back: weekly revenue with an uncertainty band per plan",
           "Next 12 weeks after the data end. Bands cover coefficient and week-to-week uncertainty, "
           "not the risk of leaving the observed spend range.")
    return _save(fig, "forecast_example.png")


def anchored(sweep: pd.DataFrame, benchmark: float, part1_error: float) -> Path:
    """Benchmark-anchored regression: effect sizes and forecast error as the prior gets stronger."""
    x = np.arange(len(sweep))
    ticks = ["none"] + [i for i in sweep.index[1:-1]] + ["fixed"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.5, 5.6), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.2})
    for ch in CHANNELS:
        y = sweep[f"elasticity {_lab(ch)}"].to_numpy()
        a1.plot(x, y, color=COLOR[ch], linewidth=2, marker="o", markersize=4.5, label=NAME[ch])
    a1.axhline(benchmark, color=INK2, linewidth=1.2, linestyle=(0, (4, 3)))
    a1.text(x[0] - 0.1, benchmark + 0.035, f"literature average {benchmark}", color=INK2, fontsize=10.5, ha="left", va="bottom")
    a1.set_ylim(0, None)
    a1.set_ylabel("long-term advertising elasticity")
    a1.legend(loc="upper right", fontsize=10.5)
    a1.set_title("Effect sizes", fontsize=12.5, pad=8)
    err = sweep["hold-out error %"].to_numpy()
    a2.plot(x, err, color=INK, linewidth=2, marker="o", markersize=4.5)
    a2.axhline(part1_error, color=INK2, linewidth=1.2, linestyle=(0, (4, 3)))
    a2.text(x[0] - 0.1, part1_error - 0.25, f"part 1's model {part1_error:.1f}%", color=INK2, fontsize=10.5, ha="left", va="top")
    for i in (0, len(x) - 1):
        a2.annotate(f"{err[i]:.1f}%", (x[i], err[i]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=11)
    a2.set_ylim(0, max(err.max(), part1_error) * 1.15)
    a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    a2.set_title("Forecast error on 26 unseen weeks", fontsize=12.5, pad=8)
    for ax, label in ((a1, "how tightly effects are tied to the literature average (prior sd, % of benchmark)"), (a2, "same scale")):
        ax.set_xticks(x, ticks, fontsize=8.5)
        ax.grid(axis="x", visible=False)
        ax.set_xlabel(label, fontsize=10)
    fig.suptitle("The model can be forced to literature-sized effects, but then it stops forecasting",
                 x=0.07, y=1.02, ha="left", fontsize=15, fontweight="semibold")
    fig.text(0.07, 0.945, "Final model re-estimated with a prior on the five media effects, from no prior (left) to fixed at the benchmark (right).",
             fontsize=11.5, color=INK2, ha="left")
    return _save(fig, "anchored.png")
