"""Scenario planner for Arla Protein UK (part 3, starter).

Run from the repo root:  streamlit run app/dashboard.py

The app holds no model logic. Everything it shows comes from arla_mmm.interface
(docs/part2/INTERFACE.md): baseline_plan, scale_plan, shift_budget, gain_range, profit_view,
profit_gain and the Forecast objects.
"""

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

try:
    import arla_mmm  # noqa: F401
except ModuleNotFoundError:      # not installed with `pip install -e .` (e.g. Streamlit Community Cloud)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arla_mmm.interface import baseline_plan, gain_range, load_model, profit_gain, profit_view, scale_plan, shift_budget

CHANNELS = {  # interface column -> name shown to the user
    "tv": "TV",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "influencer": "Influencers",
    "pos_promotion": "In-store promotion",
}
PRICE_COL, PROMO_COL, WEEK_COL = "Shelf price", "Promotion (% off)", "Week starting"
BASELINE = "Current plan"
# Starting points for the scenarios: % change of each channel's weekly spend against the current plan,
# and a budget move (from, to, % of the source channel's budget).
DEFAULTS = [
    ("Shift to digital", {"tv": -10, "instagram": 10, "tiktok": 10, "influencer": 10}, ("tv", "influencer", 0)),
    ("TV to influencers", {}, ("tv", "influencer", 10)),        # the codebook's example
    ("Scenario C", {}, ("tv", "influencer", 0)),
]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]         # current plan first, then the scenarios in order

st.set_page_config(page_title="Arla Protein scenario planner", layout="wide")


# ------------------------------------------------------------------ model calls (cached)

@st.cache_resource
def get_model():
    return load_model()


@st.cache_data(show_spinner=False)
def get_baseline(weeks: int) -> pd.DataFrame:
    return baseline_plan(get_model(), weeks=weeks)


@st.cache_data(show_spinner="Running the scenarios…")
def run(plans: dict[str, pd.DataFrame]):
    """Both effect sizes for every plan: the table of gain ranges and the full results per mode."""
    return gain_range(get_model(), plans, baseline=BASELINE)


# ------------------------------------------------------------------ formatting

def money(x: float, signed: bool = False) -> str:
    sign = "−" if x < 0 else ("+" if signed else "")
    x = abs(x)
    if x >= 1e6:
        return f"{sign}£{x / 1e6:.2f}m"
    if x >= 1e3:
        return f"{sign}£{x / 1e3:.0f}k"
    return f"{sign}£{x:.0f}"


def count(x: float) -> str:
    return f"{x / 1e6:.2f}m" if abs(x) >= 1e6 else f"{x / 1e3:.0f}k"


def pct(x: float) -> str:
    return f"{'−' if x < 0 else '+'}{abs(x):.0f}%"


def money_range(low: float, high: float) -> str:
    if abs(low) < 500 and abs(high) < 500:
        return "no change"
    return f"{money(low, signed=True)} to {money(high, signed=True)}"


def with_range(row, prefix: str, fmt) -> str:
    return f"{fmt(row[prefix + '_p50'])}  ({fmt(row[prefix + '_p5'])} to {fmt(row[prefix + '_p95'])})"


def plain_warning(sentence: str) -> str:
    """The interface's warning sentences start with the column name; show the channel's name instead."""
    key, _, rest = sentence.partition(": ")
    label = {**CHANNELS, "regular_price": "Shelf price", "promo_discount": "Promotion discount"}.get(key, key)
    return f"**{label}:** {rest[0].upper()}{rest[1:]}"


# ------------------------------------------------------------------ inputs

def set_scenario(i: int, shelf_price: float, move: int = 0) -> None:
    """Button callback: back to the current plan (move=0) or to the codebook example (move=10)."""
    for ch in CHANNELS:
        st.session_state[f"s{i}_{ch}"] = 0
    st.session_state[f"s{i}_from"], st.session_state[f"s{i}_to"], st.session_state[f"s{i}_move"] = "tv", "influencer", move
    st.session_state[f"s{i}_price"] = shelf_price
    st.session_state[f"s{i}_version"] = st.session_state.get(f"s{i}_version", 0) + 1     # drops the week edits


def week_table(plan: pd.DataFrame) -> pd.DataFrame:
    """A plan in the form shown to the user."""
    table = pd.DataFrame({WEEK_COL: plan["week_beg"].dt.strftime("%d %b %Y")})
    for ch, label in CHANNELS.items():
        table[label] = plan[ch].to_numpy()
    table[PRICE_COL] = plan["regular_price"].to_numpy()
    table[PROMO_COL] = plan["promo_discount"].to_numpy() * 100
    return table


def table_to_plan(table: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    plan = base[["week_beg"]].copy()
    for ch, label in CHANNELS.items():
        plan[ch] = table[label].to_numpy(dtype=float)
    plan["regular_price"] = table[PRICE_COL].to_numpy(dtype=float)
    plan["promo_discount"] = table[PROMO_COL].to_numpy(dtype=float) / 100
    return plan


SHORT = {"In-store promotion": "In-store"}          # column header in the week table


def table_height(rows: int) -> int:
    return min(35 * (rows + 1) + 3, 528)


TABLE_CONFIG = {
    WEEK_COL: st.column_config.TextColumn(width="small"),
    **{label: st.column_config.NumberColumn(SHORT.get(label, label) + " (£)", min_value=0, step=1000, format="£%d", width="small")
       for label in CHANNELS.values()},
    PRICE_COL: st.column_config.NumberColumn(min_value=0.5, max_value=5.0, step=0.01, format="£%.2f", width="small"),
    PROMO_COL: st.column_config.NumberColumn(min_value=0, max_value=90, step=1, format="%.0f%%", width="small",
                                             help="0 = no promotion that week. Promotions in the data were 20% to 32% off."),
}


def scenario_inputs(i: int, base: pd.DataFrame, weeks: int) -> pd.DataFrame:
    default_name, default_pct, default_move = DEFAULTS[i]
    shelf_price = float(base["regular_price"].iloc[0])
    for ch in CHANNELS:
        st.session_state.setdefault(f"s{i}_{ch}", default_pct.get(ch, 0))
    for key, value in zip(("from", "to", "move"), default_move):
        st.session_state.setdefault(f"s{i}_{key}", value)
    st.session_state.setdefault(f"s{i}_price", shelf_price)

    top = st.columns([3, 2, 1.4])
    top[0].text_input("Scenario name", value=default_name, key=f"s{i}_name")
    top[1].button("Example: move 10% of TV to influencers", key=f"s{i}_example", on_click=set_scenario,
                  args=(i, shelf_price, 10), width="stretch", help="The example from the project brief.")
    top[2].button("Reset to current plan", key=f"s{i}_reset", on_click=set_scenario, args=(i, shelf_price),
                  width="stretch")

    st.markdown("**1. Spend more or less on a channel** (% against the current plan, every week)")
    cols = st.columns(len(CHANNELS))
    factors = {}
    for col, (ch, label) in zip(cols, CHANNELS.items()):
        change = col.slider(label, min_value=-50, max_value=100, step=5, format="%+d%%", key=f"s{i}_{ch}")
        factors[ch] = 1 + change / 100
    plan = scale_plan(base, factors)

    st.markdown("**2. Move budget from one channel to another** (total budget stays the same)")
    cols = st.columns([1, 1, 2])
    source = cols[0].selectbox("Take from", list(CHANNELS), format_func=CHANNELS.get, key=f"s{i}_from")
    target = cols[1].selectbox("Give to", list(CHANNELS), format_func=CHANNELS.get, key=f"s{i}_to")
    share = cols[2].slider(f"Share of the {CHANNELS[source]} budget to move", min_value=0, max_value=50, step=1,
                           format="%d%%", key=f"s{i}_move")
    if share > 0:
        try:
            moved = share / 100 * plan[source].sum()
            plan = shift_budget(plan, source, target, share / 100)
            st.caption(f"Moves **{money(moved)}** from {CHANNELS[source]} to {CHANNELS[target]}, spread over the weeks "
                       "in proportion to each channel's spend.")
        except ValueError as err:
            st.warning(f"Nothing was moved: {err}.")

    st.markdown("**3. Shelf price** (the price without a promotion)")
    plan["regular_price"] = st.number_input(
        "Shelf price (£ per unit)", min_value=0.5, max_value=5.0, step=0.01, format="%.2f", key=f"s{i}_price",
        label_visibility="collapsed")

    st.markdown("**4. Edit single weeks**: spend, shelf price, and promotion weeks. "
                "A cell you edit keeps your value even if you change the controls above afterwards.")
    version = st.session_state.get(f"s{i}_version", 0)
    edited = st.data_editor(week_table(plan), key=f"s{i}_weeks_{weeks}_{version}", hide_index=True, num_rows="fixed",
                            disabled=[WEEK_COL], column_config=TABLE_CONFIG, width="stretch", height=table_height(weeks))
    if edited.drop(columns=WEEK_COL).isna().any().any():
        st.error("A cell in the table is empty. Empty cells are filled with the slider value for now.")
        edited = edited.fillna(week_table(plan))
    plan = table_to_plan(edited, base)

    spend, spend0 = plan[list(CHANNELS)].sum().sum(), base[list(CHANNELS)].sum().sum()
    promo, promo0 = int((plan["promo_discount"] > 0).sum()), int((base["promo_discount"] > 0).sum())
    st.caption(f"Advertising budget over {weeks} weeks: **{money(spend)}** ({money(spend - spend0, signed=True)} "
               f"against the current plan). Promotion weeks: **{promo}** (current plan: {promo0}).")
    return plan


# ------------------------------------------------------------------ charts

def scenario_color(colors: dict, legend: bool = True) -> alt.Color:
    return alt.Color("scenario:N", title=None, sort=list(colors),
                     scale=alt.Scale(domain=list(colors), range=list(colors.values())),
                     legend=alt.Legend(orient="top", symbolOpacity=1) if legend else None)


def weekly_chart(forecasts: dict, measure: str, bands: bool, colors: dict) -> alt.Chart:
    data = pd.concat([
        fc.weekly[["week_beg", f"{measure}_p5", f"{measure}_p50", f"{measure}_p95"]]
        .set_axis(["week", "low", "likely", "high"], axis=1).assign(scenario=name)
        for name, fc in forecasts.items()], ignore_index=True)
    title = "Revenue per week (£)" if measure == "revenue" else "Units sold per week"
    unit = " (£)" if measure == "revenue" else ""
    base = alt.Chart(data).encode(x=alt.X("week:T", title=None, axis=alt.Axis(format="%d %b", grid=False)))
    tooltip = [alt.Tooltip("scenario:N", title="Scenario"), alt.Tooltip("week:T", title="Week starting", format="%d %b %Y"),
               alt.Tooltip("likely:Q", title=f"Most likely{unit}", format=",.0f"),
               alt.Tooltip("low:Q", title=f"Low, 5%{unit}", format=",.0f"),
               alt.Tooltip("high:Q", title=f"High, 95%{unit}", format=",.0f")]
    y = alt.Y("likely:Q", title=title, scale=alt.Scale(zero=False), axis=alt.Axis(format="~s"))
    hover = alt.selection_point(fields=["week"], nearest=True, on="pointerover", clear="pointerout", empty=False)
    layers = []
    if bands:
        layers.append(base.mark_area(opacity=0.13).encode(y=alt.Y("low:Q", title=title), y2="high:Q",
                                                          color=scenario_color(colors)))
    layers.append(base.mark_rule(color="#8a8984", strokeDash=[3, 3]).encode(opacity=alt.condition(hover, alt.value(1), alt.value(0))))
    layers.append(base.mark_line(strokeWidth=2.5, interpolate="monotone").encode(y=y, color=scenario_color(colors)))
    layers.append(base.mark_point(filled=True, opacity=1, stroke="white", strokeWidth=1.5).encode(
        y=y, color=scenario_color(colors), tooltip=tooltip,
        size=alt.condition(hover, alt.value(110), alt.value(28))).add_params(hover))
    return alt.layer(*layers).properties(height=380)


def gain_chart(gains: pd.DataFrame, names: list[str], colors: dict) -> alt.Chart:
    """One bar per scenario from the study-sized gain (ring) to the gain as measured (dot)."""
    data = pd.DataFrame({"scenario": names,
                         "low": gains.loc[names, "delta_revenue_pct_low"].to_numpy(),
                         "high": gains.loc[names, "delta_revenue_pct_high"].to_numpy(),
                         "studies": gains.loc[names, "delta_revenue_pct_benchmark"].to_numpy(),
                         "measured": gains.loc[names, "delta_revenue_pct_model"].to_numpy()})
    color = alt.Color("scenario:N", legend=None, scale=alt.Scale(domain=list(colors), range=list(colors.values())))
    tooltip = [alt.Tooltip("scenario:N", title="Scenario"),
               alt.Tooltip("studies:Q", title="If advertising works as studies find (%)", format="+.1f"),
               alt.Tooltip("measured:Q", title="If it works as our model measured (%)", format="+.1f")]
    base = alt.Chart(data).encode(
        y=alt.Y("scenario:N", title=None, sort=names, scale=alt.Scale(paddingInner=0.5),
                axis=alt.Axis(labelLimit=220, ticks=False, domain=False, labelPadding=10, labelFontSize=13)),
        color=color, tooltip=tooltip)
    x = alt.X("low:Q", title="Revenue against the current plan (%)", axis=alt.Axis(format="+.0f", tickCount=8))
    bar = base.mark_bar(height=8, cornerRadius=4, opacity=0.4).encode(x=x, x2="high:Q")
    ring = base.mark_point(size=190, fill="white", opacity=1, strokeWidth=3).encode(x="studies:Q")
    dot = base.mark_point(size=190, filled=True, opacity=1).encode(x="measured:Q")
    return (bar + ring + dot).properties(height=alt.Step(46))


def profit_chart(profits: dict, colors: dict) -> alt.Chart:
    rows = []
    for name, (_, ch) in profits.items():
        for key, label in CHANNELS.items():
            rows.append({"scenario": name, "channel": label, "profit": ch.loc[key, "incremental_profit_p50"],
                         "low": ch.loc[key, "incremental_profit_p5"], "high": ch.loc[key, "incremental_profit_p95"]})
    data = pd.DataFrame(rows)
    order = list(colors)
    x = alt.X("channel:N", title=None, sort=list(CHANNELS.values()), axis=alt.Axis(labelAngle=0))
    offset = alt.XOffset("scenario:N", sort=order)
    tooltip = [alt.Tooltip("scenario:N", title="Scenario"), alt.Tooltip("channel:N", title="Channel"),
               alt.Tooltip("profit:Q", title="Profit added (£)", format=",.0f"),
               alt.Tooltip("low:Q", title="Low, 5% (£)", format=",.0f"), alt.Tooltip("high:Q", title="High, 95% (£)", format=",.0f")]
    bars = alt.Chart(data).mark_bar(cornerRadius=3).encode(
        x=x, xOffset=offset, y=alt.Y("profit:Q", title="Profit added over the period (£)", axis=alt.Axis(format="~s")),
        color=scenario_color(colors), tooltip=tooltip)
    whiskers = alt.Chart(data).mark_rule(color="#52514e", strokeWidth=1.5).encode(x=x, xOffset=offset, y="low:Q", y2="high:Q", tooltip=tooltip)
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#52514e").encode(y="y:Q")
    return (bars + whiskers + zero).properties(height=340)


def breakeven_chart(profits: dict, margin: float, colors: dict) -> alt.Chart:
    rows = [{"scenario": name, "channel": label, "breakeven": ch.loc[key, "breakeven_margin"] * 100}
            for name, (_, ch) in profits.items() for key, label in CHANNELS.items()]
    data = pd.DataFrame(rows)
    top = max(100.0, data["breakeven"].max() * 1.05)
    y = alt.Y("channel:N", title=None, sort=list(CHANNELS.values()), axis=alt.Axis(labelLimit=200, ticks=False, domain=False, labelPadding=8))
    x = alt.X("breakeven:Q", title="Margin needed for the channel to pay for itself (%)", scale=alt.Scale(domain=[0, top]), axis=alt.Axis(tickCount=10))
    dots = alt.Chart(data).mark_point(size=130, filled=True, opacity=0.95, stroke="white", strokeWidth=1.5).encode(
        y=y, x=x, color=scenario_color(colors),
        tooltip=[alt.Tooltip("scenario:N", title="Scenario"), alt.Tooltip("channel:N", title="Channel"),
                 alt.Tooltip("breakeven:Q", title="Break-even margin (%)", format=".0f")])
    line = alt.Chart(pd.DataFrame({"x": [margin * 100], "label": [f"Assumed margin {margin:.0%}"]}))
    rule = line.mark_rule(color="#0b0b0b", strokeWidth=1.5, strokeDash=[5, 4]).encode(x="x:Q")
    text = line.mark_text(align="left", dx=6, dy=-4, baseline="top", color="#0b0b0b", fontWeight=600).encode(
        x="x:Q", y=alt.value(0), text="label:N")
    return (rule + dots + text).properties(height=alt.Step(42))


def channel_chart(forecasts: dict, colors: dict) -> alt.Chart:
    rows = []
    for name, fc in forecasts.items():
        ch = fc.channels
        for key, label in CHANNELS.items():
            rows.append({"scenario": name, "channel": label, "added": ch.loc[key, "incremental_revenue_p50"],
                         "low": ch.loc[key, "incremental_revenue_p5"], "high": ch.loc[key, "incremental_revenue_p95"]})
    data = pd.DataFrame(rows)
    order = list(colors)
    x = alt.X("channel:N", title=None, sort=list(CHANNELS.values()), axis=alt.Axis(labelAngle=0))
    offset = alt.XOffset("scenario:N", sort=order)
    tooltip = [alt.Tooltip("scenario:N", title="Scenario"), alt.Tooltip("channel:N", title="Channel"),
               alt.Tooltip("added:Q", title="Revenue added (£)", format=",.0f"),
               alt.Tooltip("low:Q", title="Low, 5% (£)", format=",.0f"), alt.Tooltip("high:Q", title="High, 95% (£)", format=",.0f")]
    bars = alt.Chart(data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=x, xOffset=offset, y=alt.Y("added:Q", title="Revenue added over the period (£)", axis=alt.Axis(format="~s")),
        color=scenario_color(colors), tooltip=tooltip)
    whiskers = alt.Chart(data).mark_rule(color="#52514e", strokeWidth=1.5).encode(
        x=x, xOffset=offset, y="low:Q", y2="high:Q", tooltip=tooltip)
    return (bars + whiskers).properties(height=360)


# ------------------------------------------------------------------ page

model = get_model()

with st.sidebar:
    st.header("Settings")
    weeks = st.slider("Weeks to plan", min_value=12, max_value=52, value=12,
                      help="The plan starts in the week after the data end (30 Dec 2024).")
    n_scenarios = st.radio("Scenarios to compare with the current plan", [2, 3], horizontal=True)
    bands = st.checkbox("Show the likely range in the weekly chart", value=True)
    st.divider()
    st.caption(f"Model fitted on {model.meta['weeks']} weeks of sales, {model.meta['first_week']} to "
               f"{model.meta['last_week']}. Starter dashboard: a working base for part 3, not the final product.")

base = get_baseline(weeks)

st.title("Arla Protein UK: what happens if we change the plan?")
st.markdown(
    f"Set the weekly advertising spend, shelf price and promotion weeks for the next **{weeks} weeks** and compare "
    "the result with the current plan. The **current plan** repeats the spend and promotions of the same weeks a "
    "year ago at today's shelf price.")

with st.expander("How to use this tool, and what it cannot tell you", icon="📖"):
    how, read, limits = st.columns(3)
    how.markdown(
        "**What you set**\n"
        "- **Weekly spend per channel** in £: TV, Instagram, TikTok, influencers and in-store promotion.\n"
        "- **Shelf price**: the price on the shelf when there is no promotion.\n"
        "- **Price promotions**: in which weeks, and how many % off.\n\n"
        "Each scenario starts from the current plan. Change a channel for all weeks, move budget from one channel "
        "to another, or edit single weeks in the table.")
    read.markdown(
        "**How to read the results**\n"
        "- **Low, most likely, high.** Sales are never certain. Nine times out of ten the result should land "
        "between low and high.\n"
        "- **The gain is a range**, for example +4% to +28%. One end assumes advertising works as well as "
        "published studies find, the other as well as our model measured on Arla's data. Plan with the lower "
        "figure and treat the higher one as the upside.\n"
        "- **Revenue per £** is revenue, not profit. The Profit tab applies a margin you choose.")
    limits.markdown(
        "**Warnings and limits**\n"
        "- 🚨 **Red**: the scenario holds a spend level for months that the brand has never held. The tool still "
        "shows numbers, but **they are not a forecast**.\n"
        "- ⚠️ **Yellow**: single weeks, a price or a discount are outside what the data contain. Read with care.\n"
        "- The model learned from three years of Arla's own data. It shows the direction and ranking of the "
        "channels reliably; the size of a gain should be tested in the market before the budget is moved for good.\n"
        "- Growth and seasonal patterns are assumed to continue as in 2022 to 2024.")

st.header("Your scenarios")
names = []
for i in range(n_scenarios):
    name = (st.session_state.get(f"s{i}_name") or DEFAULTS[i][0]).strip() or DEFAULTS[i][0]
    while name in names or name == BASELINE:
        name += " (2)"
    names.append(name)

plans = {BASELINE: base}
tabs = st.tabs(names + [BASELINE])
for i, tab in enumerate(tabs[:-1]):
    with tab:
        plans[names[i]] = scenario_inputs(i, base, weeks)
with tabs[-1]:
    st.caption("The plan every scenario is compared with. It cannot be edited here.")
    st.dataframe(week_table(base), hide_index=True, column_config=TABLE_CONFIG, width="stretch", height=table_height(weeks))

try:
    gains, detail = run(plans)
except ValueError as err:
    st.error(f"This plan cannot be calculated: {err}")
    st.stop()
table, forecasts = detail["model"]              # levels and bands: effects as estimated
colors = dict(zip([BASELINE] + names, COLORS))

# ---- warnings first
st.header("Results")
flagged = {}
for name, fc in forecasts.items():
    sustained = bool(fc.flags["sustained_out"].any())
    if fc.warnings:
        flagged[name] = sustained
        text = "\n".join(f"- {plain_warning(w)}" for w in fc.warnings)
        if sustained:
            st.error(f"**{name}: outside anything the brand has done before. Do not read its numbers as a forecast.**\n\n"
                     f"{text}", icon="🚨")
        else:
            st.warning(f"**{name}: single weeks outside the range seen in the data.**\n\n{text}", icon="⚠️")
if not flagged:
    st.success("All scenarios stay inside the spend levels, prices and promotions seen in three years of data.", icon="✅")

# ---- the gain as a range
st.subheader("Revenue against the current plan")
st.caption("Why a range: our model measures social and influencer advertising as two to seven times more effective "
           "than published studies do, so each gain runs from *effects as large as the studies find* to *effects as "
           "our model measured them*. The truth is most likely in between.")
for col, name in zip(st.columns(n_scenarios), names):
    g = gains.loc[name]
    with col.container(border=True):
        mark = " 🚨" if flagged.get(name) else ""
        unchanged = max(abs(g["delta_revenue_pct_low"]), abs(g["delta_revenue_pct_high"])) < 0.5
        st.metric(f"{name}{mark}", "No change" if unchanged else
                  f"{pct(g['delta_revenue_pct_low'])} to {pct(g['delta_revenue_pct_high'])}")
        st.markdown(f"{money_range(g['delta_revenue_low'], g['delta_revenue_high']).capitalize()} over {weeks} weeks  \n"
                    f"Advertising budget: {money(g['delta_spend'], signed=True) if abs(g['delta_spend']) >= 500 else 'unchanged'}")
        if flagged.get(name):
            st.caption("Outside past spend levels: a what-if, not a forecast.")
st.altair_chart(gain_chart(gains, names, colors), width="stretch")
st.caption("○ if advertising works as published studies find  ·  ● if it works as our model measured")

tab_totals, tab_channels, tab_profit, tab_numbers = st.tabs(["Sales and revenue", "Channels", "Profit", "Weekly numbers"])

# ---- totals with bands, week by week
with tab_totals:
    st.subheader(f"Totals over {weeks} weeks")
    summary = pd.DataFrame({
        "Scenario": [f"{n} 🚨" if flagged.get(n) else n for n in table.index],
        "Advertising budget": [money(v) for v in table["media_spend"]],
        "Units sold": [with_range(r, "units", count) for _, r in table.iterrows()],
        "Revenue": [with_range(r, "revenue", money) for _, r in table.iterrows()],
        "Revenue per £ of advertising": [with_range(r, "media_roi", lambda v: f"£{v:.1f}") for _, r in table.iterrows()],
    })
    st.dataframe(summary, hide_index=True, width="stretch")
    st.caption("Each cell: most likely value (low to high), with advertising effects as our model measured them. "
               "*Revenue per £ of advertising* is the revenue all channels add together, divided by what is spent "
               "above the minimum level the brand has always kept. It is revenue, not profit.")

    st.subheader("Week by week")
    measure = st.radio("Show", ["Revenue", "Units sold"], horizontal=True, label_visibility="collapsed")
    st.altair_chart(weekly_chart(forecasts, "revenue" if measure == "Revenue" else "units", bands, colors), width="stretch")
    st.caption("Lines: most likely value. Shaded area: the range from low to high.")

# ---- channels
with tab_channels:
    st.subheader("What each channel adds")
    st.altair_chart(channel_chart(forecasts, colors), width="stretch")
    st.caption("Bars: revenue the channel adds over the period. Thin lines: low to high. TV is measured against no "
               "TV; the other channels against the lowest weekly spend the brand has ever had, because they were "
               "never switched off.")

    st.markdown("**Revenue per £ spent on the channel** (most likely, low to high)")
    roi = pd.DataFrame({"Channel": list(CHANNELS.values())})
    for name, fc in forecasts.items():
        roi[name] = [with_range(fc.channels.loc[ch], "roi", lambda v: f"£{v:.1f}") for ch in CHANNELS]
    st.dataframe(roi, hide_index=True, width="stretch")
    note = "Counted on the spend above the channel's minimum level (for TV: on all TV spend)."
    ch0 = forecasts[BASELINE].channels
    moved = [(CHANNELS[ch], name) for name in names for ch in CHANNELS
             if abs(forecasts[name].channels.loc[ch, "spend"] - ch0.loc[ch, "spend"]) < 1
             and abs(forecasts[name].channels.loc[ch, "roi_mean"] / ch0.loc[ch, "roi_mean"] - 1) > 0.02]
    if moved:
        note += (f" Why does the return of {moved[0][0]} change in *{moved[0][1]}* although its spend does not? In the "
                 "model the channels reinforce each other: when one channel lifts sales, every £ on the others works "
                 "on a larger base.")
    st.caption(note)

    st.markdown("**Where the revenue comes from**")
    source = pd.DataFrame({"Source": ["Base sales"] + list(CHANNELS.values())})
    for name, fc in forecasts.items():
        by = fc.contributions.groupby("component")["revenue_mean"].sum()
        source[name] = [money(by[c]) for c in ["base"] + list(CHANNELS)]
    st.dataframe(source, hide_index=True, width="stretch")
    st.caption("Base sales: what would be sold with every channel at its minimum level. Includes growth, season, "
               "price, promotions and the after-effect of earlier advertising.")

# ---- profit at an assumed margin
with tab_profit:
    st.subheader("Profit at an assumed margin")
    margin = st.slider("Gross margin: an assumption, not a number from the data", min_value=5, max_value=60, value=20,
                       step=1, format="%d%%", help="The share of revenue left after the cost of making and delivering "
                       "the product. Arla's real margin is not in our data, so set the one you believe.") / 100
    profits = {name: profit_view(fc, margin) for name, fc in forecasts.items()}
    pgain = profit_gain(gains, margin)
    st.dataframe(pd.DataFrame({
        "Scenario": [f"{n} 🚨" if flagged.get(n) else n for n in profits],
        "Advertising budget": [money(t["media_spend"]) for t, _ in profits.values()],
        "Profit after advertising": [with_range(t, "profit_after_media", money) for t, _ in profits.values()],
        "Against the current plan": ["" if n == BASELINE else money_range(pgain.loc[n, "delta_profit_low"], pgain.loc[n, "delta_profit_high"])
                                     for n in profits],
    }), hide_index=True, width="stretch")
    st.caption(f"Profit after advertising = {margin:.0%} of revenue minus the advertising budget; other costs are not "
               "in the data. Cells show most likely (low to high). *Against the current plan* is a range for the "
               "same reason as the revenue gain.")

    st.markdown("**Does each channel pay for itself?**")
    st.altair_chart(breakeven_chart(profits, margin, colors), width="stretch")
    st.caption("Each dot is the margin a channel needs to earn back its own spend. Dots left of the dashed line pay "
               "for themselves at the assumed margin; dots right of it do not. Where the dots sit does not depend "
               "on the margin you choose.")
    st.altair_chart(profit_chart(profits, colors), width="stretch")
    st.caption(f"Profit a channel adds = {margin:.0%} of the revenue it adds minus its spend above the minimum level. "
               "Bars below zero cost more than they bring in at this margin. Thin lines: low to high.")
    be = pd.DataFrame({"Channel": list(CHANNELS.values())})
    for name, (_, ch) in profits.items():
        be[name] = [f"{ch.loc[c, 'breakeven_margin']:.0%}  ({'pays back' if ch.loc[c, 'pays_back'] else 'does not pay back'})"
                    for c in CHANNELS]
    st.markdown("**Margin needed to break even**")
    st.dataframe(be, hide_index=True, width="stretch")

# ---- details
with tab_numbers:
    weekly = pd.concat([
        fc.weekly.assign(scenario=name, week_beg=fc.weekly["week_beg"].dt.date)
        [["scenario", "week_beg", *CHANNELS, "regular_price", "promo_discount", "units_p5", "units_p50", "units_p95",
          "revenue_p5", "revenue_p50", "revenue_p95"]] for name, fc in forecasts.items()], ignore_index=True)
    st.dataframe(weekly.round(2), hide_index=True, width="stretch")
    st.download_button("Download as CSV", weekly.to_csv(index=False), file_name="arla_scenarios_weekly.csv", mime="text/csv")
