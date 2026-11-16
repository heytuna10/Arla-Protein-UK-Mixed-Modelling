"""Scenario planner for Arla Protein UK (part 3, starter).

Run from the repo root:  streamlit run app/dashboard.py

The app holds no model logic. Everything it shows comes from arla_mmm.interface
(docs/part2/INTERFACE.md): baseline_plan, scale_plan, gain_range and the Forecast objects.
"""

import altair as alt
import pandas as pd
import streamlit as st

from arla_mmm.interface import baseline_plan, gain_range, load_model, scale_plan

CHANNELS = {  # interface column -> name shown to the user
    "tv": "TV",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "influencer": "Influencers",
    "pos_promotion": "In-store promotion",
}
PRICE_COL, PROMO_COL, WEEK_COL = "Shelf price", "Promotion (% off)", "Week starting"
BASELINE = "Current plan"
# Starting points for the scenarios: % change of each channel's weekly spend against the current plan.
DEFAULTS = [
    ("Shift to digital", {"tv": -10, "instagram": 10, "tiktok": 10, "influencer": 10}),
    ("TV to influencers", {"tv": -10, "influencer": 30}),      # the codebook's example: 10% of the TV budget
    ("Scenario C", {}),
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


def with_range(row, prefix: str, fmt) -> str:
    return f"{fmt(row[prefix + '_p50'])}  ({fmt(row[prefix + '_p5'])} to {fmt(row[prefix + '_p95'])})"


def plain_warning(sentence: str) -> str:
    """The interface's warning sentences start with the column name; show the channel's name instead."""
    key, _, rest = sentence.partition(": ")
    label = {**CHANNELS, "regular_price": "Shelf price", "promo_discount": "Promotion discount"}.get(key, key)
    return f"**{label}:** {rest[0].upper()}{rest[1:]}"


# ------------------------------------------------------------------ inputs

def reset_scenario(i: int, shelf_price: float) -> None:
    for ch in CHANNELS:
        st.session_state[f"s{i}_{ch}"] = 0
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
    default_name, default_pct = DEFAULTS[i]
    shelf_price = float(base["regular_price"].iloc[0])
    for ch in CHANNELS:
        st.session_state.setdefault(f"s{i}_{ch}", default_pct.get(ch, 0))
    st.session_state.setdefault(f"s{i}_price", shelf_price)

    top = st.columns([3, 1])
    top[0].text_input("Scenario name", value=default_name, key=f"s{i}_name")
    top[1].button("Reset to current plan", key=f"s{i}_reset", on_click=reset_scenario, args=(i, shelf_price),
                  width="stretch")

    st.markdown("**1. Change the weekly spend of a channel** (% against the current plan, every week)")
    cols = st.columns(len(CHANNELS))
    factors = {}
    for col, (ch, label) in zip(cols, CHANNELS.items()):
        change = col.slider(label, min_value=-50, max_value=100, step=5, format="%+d%%", key=f"s{i}_{ch}")
        factors[ch] = 1 + change / 100
    plan = scale_plan(base, factors)

    st.markdown("**2. Shelf price** (the price without a promotion)")
    plan["regular_price"] = st.number_input(
        "Shelf price (£ per unit)", min_value=0.5, max_value=5.0, step=0.01, format="%.2f", key=f"s{i}_price",
        label_visibility="collapsed")

    st.markdown("**3. Edit single weeks**: spend, shelf price, and promotion weeks. "
                "A cell you edit keeps your value even if you move a slider afterwards.")
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

def weekly_chart(forecasts: dict, measure: str, bands: bool, colors: dict) -> alt.Chart:
    data = pd.concat([
        fc.weekly[["week_beg", f"{measure}_p5", f"{measure}_p50", f"{measure}_p95"]]
        .set_axis(["week", "low", "likely", "high"], axis=1).assign(scenario=name)
        for name, fc in forecasts.items()], ignore_index=True)
    title = "Revenue per week (£)" if measure == "revenue" else "Units sold per week"
    unit = " (£)" if measure == "revenue" else ""
    color = alt.Color("scenario:N", title=None, sort=list(colors),
                      scale=alt.Scale(domain=list(colors), range=list(colors.values())),
                      legend=alt.Legend(orient="top"))
    base = alt.Chart(data).encode(x=alt.X("week:T", title=None, axis=alt.Axis(format="%d %b", grid=False)))
    tooltip = [alt.Tooltip("scenario:N", title="Scenario"), alt.Tooltip("week:T", title="Week starting", format="%d %b %Y"),
               alt.Tooltip("likely:Q", title=f"Most likely{unit}", format=",.0f"),
               alt.Tooltip("low:Q", title=f"Low, 5%{unit}", format=",.0f"),
               alt.Tooltip("high:Q", title=f"High, 95%{unit}", format=",.0f")]
    y = alt.Y("likely:Q", title=title, scale=alt.Scale(zero=False), axis=alt.Axis(format="~s"))
    layers = []
    if bands:
        layers.append(base.mark_area(opacity=0.13).encode(y=alt.Y("low:Q", title=title), y2="high:Q",
                                                          color=color.copy().legend(None)))
    layers.append(base.mark_line(strokeWidth=2).encode(y=y, color=color))
    layers.append(base.mark_point(size=70, filled=True, opacity=1).encode(y=y, color=color, tooltip=tooltip))
    return alt.layer(*layers).properties(height=360)


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
        color=alt.Color("scenario:N", title=None, sort=order, legend=alt.Legend(orient="top"),
                        scale=alt.Scale(domain=order, range=list(colors.values()))),
        tooltip=tooltip)
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
        st.markdown(f"{money(g['delta_revenue_low'], signed=True)} to {money(g['delta_revenue_high'], signed=True)} "
                    f"over {weeks} weeks  \nAdvertising budget: {money(table.loc[name, 'delta_spend'], signed=True)}")
        st.caption(f"With study-sized effects: {pct(g['delta_revenue_pct_benchmark'])}. "
                   f"As our model measured them: {pct(g['delta_revenue_pct_model'])}.")
        if flagged.get(name):
            st.caption("Outside past spend levels: treat as a what-if, not a forecast.")

# ---- totals with bands
st.subheader(f"Totals over {weeks} weeks")
summary = pd.DataFrame({
    "Scenario": [f"{n} 🚨" if flagged.get(n) else n for n in table.index],
    "Advertising budget": [money(v) for v in table["media_spend"]],
    "Units sold": [with_range(r, "units", count) for _, r in table.iterrows()],
    "Revenue": [with_range(r, "revenue", money) for _, r in table.iterrows()],
    "Revenue per £ of advertising": [with_range(r, "media_roi", lambda v: f"£{v:.1f}") for _, r in table.iterrows()],
})
st.dataframe(summary, hide_index=True, width="stretch")
st.caption("Each cell: most likely value (low to high). Nine times out of ten the result should fall between low and "
           "high, if the model's measured effects are right. *Revenue per £ of advertising* is the revenue all "
           "channels add together, divided by what is spent above the minimum level the brand has always kept. "
           "It is revenue, not profit.")

# ---- week by week
st.subheader("Week by week")
measure = st.radio("Show", ["Revenue", "Units sold"], horizontal=True, label_visibility="collapsed")
st.altair_chart(weekly_chart(forecasts, "revenue" if measure == "Revenue" else "units", bands, colors), width="stretch")
st.caption("Lines: most likely value. Shaded area: the range from low (5%) to high (95%).")

# ---- channels
st.subheader("What each channel adds")
st.altair_chart(channel_chart(forecasts, colors), width="stretch")
st.caption("Bars: revenue the channel adds over the period. Thin lines: low to high. TV is measured against no TV; "
           "the other channels against the lowest weekly spend the brand has ever had, because they were never "
           "switched off.")

st.markdown("**Revenue per £ spent on the channel** (most likely, low to high)")
roi = pd.DataFrame({"Channel": list(CHANNELS.values())})
for name, fc in forecasts.items():
    roi[name] = [with_range(fc.channels.loc[ch], "roi", lambda v: f"£{v:.1f}") for ch in CHANNELS]
st.dataframe(roi, hide_index=True, width="stretch")
st.caption("Counted on the spend above the channel's minimum level (for TV: on all TV spend).")

st.markdown("**Where the revenue comes from**")
source = pd.DataFrame({"Source": ["Base sales"] + list(CHANNELS.values())})
for name, fc in forecasts.items():
    by = fc.contributions.groupby("component")["revenue_mean"].sum()
    source[name] = [money(by[c]) for c in ["base"] + list(CHANNELS)]
st.dataframe(source, hide_index=True, width="stretch")
st.caption("Base sales: what would be sold with every channel at its minimum level. Includes growth, season, price, "
           "promotions and the after-effect of earlier advertising.")

# ---- details
with st.expander("Weekly numbers (table and download)"):
    weekly = pd.concat([
        fc.weekly.assign(scenario=name, week_beg=fc.weekly["week_beg"].dt.date)
        [["scenario", "week_beg", *CHANNELS, "regular_price", "promo_discount", "units_p5", "units_p50", "units_p95",
          "revenue_p5", "revenue_p50", "revenue_p95"]] for name, fc in forecasts.items()], ignore_index=True)
    st.dataframe(weekly.round(2), hide_index=True, width="stretch")
    st.download_button("Download as CSV", weekly.to_csv(index=False), file_name="arla_scenarios_weekly.csv", mime="text/csv")

with st.expander("What these numbers can and cannot tell you"):
    st.markdown(
        "- **Direction yes, size to be tested.** The ranking of the channels is stable; the size of the social and "
        "influencer effects is far above what published studies find. That is why gains are shown as a range.\n"
        "- **The red warning matters most.** The model has only seen spend levels the brand actually held. Beyond "
        "them it still produces numbers, and they are not evidence.\n"
        "- **Revenue, not profit.** Margin is not in the data.\n"
        "- **Price promotions sell more units and bring in less revenue** at every discount in the data.\n"
        "- **Low to high covers** normal week-to-week swings and how precisely the effects are measured. It does not "
        "cover the risk of leaving past spend levels.\n"
        "- **Growth and season are assumed to continue** as in the last three years.")
