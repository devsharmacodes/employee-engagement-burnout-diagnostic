"""
dashboard/app.py
Streamlit dashboard for the Employee Engagement, Satisfaction & Burnout
Diagnostic project (Palo Alto Networks HR dataset).

Run locally with:
    streamlit run dashboard/app.py

Reuses the exact same cleaning / scoring logic as the notebooks via the
src/ modules, so the numbers here always match the analysis notebooks.
Visual language (colors, type, badges) mirrors the companion HTML
dashboard so both deliverables read as one product.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import data_loader
import engagement
import burnout
import metrics
import textwrap


# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Workforce Pulse — PAN Engagement & Burnout Diagnostic",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Theme + design system
# ---------------------------------------------------------------------
# Streamlit itself cannot directly persist arbitrary Python state in the
# browser across a hard refresh, so the selected theme is also reflected in
# the URL query parameter. This keeps the preference when the page is reloaded.
query_theme = st.query_params.get("theme", "dark").lower()
if query_theme not in {"light", "dark"}:
    query_theme = "dark"

if "theme" not in st.session_state:
    st.session_state.theme = query_theme

DARK_MODE = st.session_state.theme == "dark"

if DARK_MODE:
    BG = "#080B10"
    SURFACE = "#0F141B"
    SURFACE_2 = "#141A22"
    SURFACE_3 = "#1A212B"
    BORDER = "#252D38"
    TEXT = "#F4F7FA"
    TEXT_MUTED = "#8F9BAB"
    TEXT_SOFT = "#B5BFCC"
    ACCENT = "#35C6D2"
    ACCENT_STRONG = "#67DCE4"
    GRID = "rgba(231,236,242,0.08)"
else:
    BG = "#F5F7FA"
    SURFACE = "#FFFFFF"
    SURFACE_2 = "#F8FAFC"
    SURFACE_3 = "#EEF2F6"
    BORDER = "#E3E8EF"
    TEXT = "#141922"
    TEXT_MUTED = "#687386"
    TEXT_SOFT = "#475365"
    ACCENT = "#0B8F9C"
    ACCENT_STRONG = "#08757F"
    GRID = "rgba(30,41,59,0.10)"

RISK_LOW = "#3FB47A"
RISK_MEDIUM = "#D99A2B"
RISK_HIGH = "#DE5C5A"

CHART_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT_MUTED, size=12),
        colorway=[ACCENT, RISK_MEDIUM, RISK_HIGH, RISK_LOW, ACCENT_STRONG],
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=BORDER),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED)),
        margin=dict(t=28, b=28, l=8, r=8),
    )
)

# ---------------------------------------------------------------------
# Premium UI styling
# ---------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --bg: {BG};
    --surface: {SURFACE};
    --surface2: {SURFACE_2};
    --surface3: {SURFACE_3};
    --border: {BORDER};
    --text: {TEXT};
    --muted: {TEXT_MUTED};
    --soft: {TEXT_SOFT};
    --accent: {ACCENT};
    --accent-strong: {ACCENT_STRONG};
}}

html, body, [class*="css"] {{ font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
.stApp {{ background: var(--bg); color: var(--text); }}
.block-container {{ max-width: 1540px; padding: 1.25rem 2rem 3rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}

section[data-testid="stSidebar"] {{
    background: var(--surface);
    border-right: 1px solid var(--border);
}}
section[data-testid="stSidebar"] > div {{ padding-top: 1rem; }}
[data-testid="stSidebar"] .block-container {{ padding-left: 1rem; padding-right: 1rem; }}

/* Premium cards */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 15px;
    box-shadow: 0 1px 2px rgba(0,0,0,.025);
}}

.pulse-intro {{
    background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 7%, var(--surface)), var(--surface));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 22px;
    margin: 8px 0 16px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    box-shadow: 0 8px 28px rgba(0,0,0,.035);
}}
.pulse-intro .icon {{
    width: 38px; height: 38px; flex: 0 0 38px;
    border-radius: 11px; background: var(--surface3);
    display: flex; align-items: center; justify-content: center;
    font-size: 19px;
}}
.pulse-intro h3 {{ margin: 0 0 4px; font-size: 14px; font-weight: 700; color: var(--text); }}
.pulse-intro p {{ margin: 0; font-size: 13px; color: var(--muted); line-height: 1.6; max-width: 100ch; }}

/* KPI system */
.kpi-row {{ display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 12px; margin: 14px 0 18px; }}
.kpi-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 16px 17px; min-height: 128px; position: relative;
    transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
}}
.kpi-card:hover {{ transform: translateY(-2px); border-color: color-mix(in srgb, var(--accent) 48%, var(--border)); box-shadow: 0 10px 28px rgba(0,0,0,.07); }}
.kpi-label {{ font-size: 11.5px; color: var(--muted); font-weight: 600; display: flex; align-items: center; gap: 5px; }}
.kpi-value {{ font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 25px; font-weight: 650; color: var(--text); margin-top: 9px; letter-spacing: -.025em; }}
.kpi-value.accent {{ color: var(--accent); }}
.kpi-value.risk-high {{ color: #DE5C5A; }}
.kpi-help {{ font-size: 10.5px; color: var(--muted); margin-top: 5px; line-height: 1.4; }}

.pulse-h {{ font-size: 14px; font-weight: 700; color: var(--text); margin: 3px 0 2px; letter-spacing: -.01em; }}
.pulse-sub {{ font-size: 12px; color: var(--muted); margin-bottom: 10px; }}

.badge {{ display:inline-flex; align-items:center; gap:5px; font-size:11px; font-weight:650; padding:4px 9px; border-radius:999px; margin-top:8px; }}
.badge::before {{ content:""; width:6px; height:6px; border-radius:50%; background:currentColor; }}
.badge.low {{ background: rgba(63,180,122,.13); color:#3FB47A; }}
.badge.medium {{ background: rgba(217,154,43,.14); color:#D99A2B; }}
.badge.high {{ background: rgba(222,92,90,.13); color:#DE5C5A; }}
.badge.active {{ background: color-mix(in srgb, var(--accent) 12%, transparent); color:var(--accent); }}
.badge.left {{ background:var(--surface3); color:var(--muted); }}

/* Sidebar */
.sidebar-brand {{ display:flex; align-items:center; gap:10px; padding:3px 3px 16px; }}
.brand-mark {{ width:35px; height:35px; border-radius:10px; background:var(--accent); color:white; display:flex; align-items:center; justify-content:center; font-weight:800; box-shadow:0 5px 16px color-mix(in srgb, var(--accent) 20%, transparent); }}
.brand-name {{ color:var(--text); font-size:15px; font-weight:700; letter-spacing:-.02em; }}
.brand-sub {{ color:var(--muted); font-size:10.5px; margin-top:2px; }}
.nav-caption {{ color:var(--muted); font-size:10px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; padding:9px 4px 6px; }}

section[data-testid="stSidebar"] .stButton > button {{
    width:100%; border:1px solid transparent; background:transparent; color:var(--muted);
    text-align:left; border-radius:9px; min-height:37px; font-size:12.5px; font-weight:600;
    transition:all .15s ease;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{ background:var(--surface3); color:var(--text); border-color:var(--border); transform:none; }}

/* Streamlit controls */
.stButton > button {{ border-radius:9px; border:1px solid var(--border); background:var(--surface); color:var(--text); transition:all .15s ease; }}
.stButton > button:hover {{ border-color:var(--accent); color:var(--accent); transform:translateY(-1px); }}
.stButton > button[kind="primary"] {{ background:var(--accent); border-color:var(--accent); color:white; }}
.stButton > button[kind="primary"]:hover {{ filter:brightness(1.05); color:white; }}
div[data-baseweb="select"] > div {{ background:var(--surface); border-color:var(--border); color:var(--text); border-radius:9px; }}
input, textarea {{ background:var(--surface) !important; color:var(--text) !important; }}
.stTextInput label, .stSelectbox label, .stSlider label, .stMultiSelect label {{ color:var(--muted) !important; font-size:11.5px !important; }}

/* Tabs */
button[data-baseweb="tab"] {{ color:var(--muted); font-size:12.5px; font-weight:650; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color:var(--accent); }}
div[data-baseweb="tab-highlight"] {{ background:var(--accent); }}

/* Dataframes */
div[data-testid="stDataFrame"] {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; }}

/* Responsive */
@media (max-width: 1050px) {{
    .kpi-row {{ grid-template-columns:repeat(3, minmax(0,1fr)); }}
    .block-container {{ padding-left:1rem; padding-right:1rem; }}
}}
@media (max-width: 650px) {{
    .kpi-row {{ grid-template-columns:repeat(2, minmax(0,1fr)); }}
    .page-title {{ font-size:1.5rem !important; }}
    .pulse-intro {{ padding:15px; }}
}}
</style>
""", unsafe_allow_html=True)


def set_theme(theme):
    st.session_state.theme = theme
    st.query_params["theme"] = theme



def risk_emoji(risk):
    return {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}.get(risk, risk)


def status_emoji(status):
    return {"Active": "🟢 Active", "Left": "⚪ Left"}.get(status, status)


# ---------------------------------------------------------------------
# Data loading (cached so filters don't reprocess the whole pipeline)
# ---------------------------------------------------------------------
@st.cache_data
def load_scored_data():
    raw_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "Palo_Alto_Networks.csv")
    df = data_loader.load_clean(raw_path)
    df = engagement.score(df)
    df = burnout.score(df)
    bins = [0, 2, 5, 10, 20, 100]
    labels = ["0-2", "3-5", "6-10", "11-20", "20+"]
    df["TenureBand"] = pd.cut(df["YearsAtCompany"], bins=bins, labels=labels, right=True)
    return df


df_full = load_scored_data()


# ---------------------------------------------------------------------
# Sidebar — product navigation + filters
# ---------------------------------------------------------------------
st.sidebar.markdown(
    f"""
    <div class="sidebar-brand">
        <div class="brand-mark">W</div>
        <div>
            <div class="brand-name">Workforce Pulse</div>
            <div class="brand-sub">People Analytics</div>
        </div>
    </div>
    <div class="nav-caption">Workspace</div>
    """,
    unsafe_allow_html=True,
)

nav_help = {
    "Overview": "Engagement health, satisfaction, workforce KPIs and department trends.",
    "Burnout": "Burnout risk patterns across overtime, travel and departments.",
    "Career": "Explore engagement by job level, tenure and promotion history.",
    "Manager": "Review the priority watchlist and intervention signals.",
}

# The existing analytical tabs remain the main content navigation; these
# buttons provide a polished product-style navigation cue and can be used to
# jump to the corresponding section via session state.
if "active_section" not in st.session_state:
    st.session_state.active_section = "Overview"

for item, icon in [("Overview", "⌂"), ("Burnout", "◉"), ("Career", "⌁"), ("Manager", "! ")]:
    if st.sidebar.button(f"{icon}  {item}", key=f"nav_{item}", help=nav_help[item], use_container_width=True):
        st.session_state.active_section = item
        st.rerun()

st.sidebar.markdown('<div class="nav-caption">Filters</div>', unsafe_allow_html=True)

departments = ["All"] + sorted(df_full["Department"].unique().tolist())
selected_dept = st.sidebar.selectbox(
    "Department", departments,
    help="Filter the dashboard to one department or keep all departments selected."
)

roles = ["All"] + sorted(df_full["JobRole"].unique().tolist())
selected_role = st.sidebar.selectbox(
    "Job role", roles,
    help="Filter the dashboard to a specific job role."
)

overtime_only = st.sidebar.toggle(
    "Overtime employees only", value=False,
    help="Limit the analysis to employees whose OverTime field is Yes."
)

engagement_threshold = st.sidebar.slider(
    "Minimum Engagement Index", min_value=0.0, max_value=1.0, value=0.0, step=0.05,
    help="Show only employees at or above this Engagement Index score.",
)

min_tenure, max_tenure = int(df_full["YearsAtCompany"].min()), int(df_full["YearsAtCompany"].max())
tenure_range = st.sidebar.slider(
    "Years at company", min_value=min_tenure, max_value=max_tenure,
    value=(min_tenure, max_tenure),
    help="Limit results to employees within the selected tenure range."
)

# Apply filters
df = df_full.copy()
if selected_dept != "All":
    df = df[df["Department"] == selected_dept]
if selected_role != "All":
    df = df[df["JobRole"] == selected_role]
if overtime_only:
    df = df[df["OverTime"] == "Yes"]
df = df[df["EngagementIndex"] >= engagement_threshold]
df = df[df["YearsAtCompany"].between(tenure_range[0], tenure_range[1])]

st.sidebar.divider()

# Theme control — persisted through URL query parameters.
theme_choice = st.sidebar.radio(
    "Appearance",
    ["dark", "light"],
    index=0 if DARK_MODE else 1,
    format_func=lambda x: "Dark mode" if x == "dark" else "Light mode",
    horizontal=True,
    help="Switch the complete dashboard between light and dark themes. The choice is preserved on refresh."
)
if theme_choice != st.session_state.theme:
    set_theme(theme_choice)
    st.rerun()

st.sidebar.markdown(
    f"""
    <div style="padding:9px 2px 2px;color:var(--muted);font-size:11px;line-height:1.5;">
        <b style="color:var(--text);">{len(df):,}</b> of {len(df_full):,} employees match the current filters.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Header + product introduction
# ---------------------------------------------------------------------
head_a, head_b = st.columns([5, 1.2])
with head_a:
    st.markdown(
        """
        <div style="color:var(--accent);font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px;">
            PEOPLE ANALYTICS / WORKFORCE INTELLIGENCE
        </div>
        <div style="font-size:30px;line-height:1.1;font-weight:750;letter-spacing:-.045em;color:var(--text);">
            Workforce Pulse
        </div>
        <div style="font-size:13px;color:var(--muted);margin-top:6px;">
            Engagement, satisfaction and burnout diagnostic for workforce decision-making.
        </div>
        """,
        unsafe_allow_html=True,
    )
with head_b:
    st.markdown(
        f"""
        <div style="margin-top:6px;text-align:right;color:var(--muted);font-size:10.5px;">
            <div style="display:inline-flex;align-items:center;gap:6px;border:1px solid var(--border);background:var(--surface);padding:7px 10px;border-radius:999px;">
                <span style="width:7px;height:7px;border-radius:50%;background:#3FB47A;"></span>
                Live analysis
            </div>
            <div style="margin-top:8px;">{len(df_full):,} employees · filtered view</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="pulse-intro">
        <span class="icon">✦</span>
        <div>
            <h3>What this dashboard does</h3>
            <p>
                Turns raw HR survey data into an early-warning system by combining involvement,
                satisfaction and work-life balance into an Engagement Index, identifying burnout
                signals from overtime and workload patterns, and surfacing teams and career stages
                that may need attention.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if df.empty:
    st.warning("No employees match the current filters. Try widening them in the sidebar.")
    st.stop()

tab_overview, tab_burnout, tab_career, tab_manager = st.tabs(
    ["📊  Engagement Health Overview", "🔥  Burnout Risk Dashboard",
     "🧭  Role & Career Stage Analysis", "🚨  Manager Action Panel"]
)

# Product-style sidebar navigation is intentionally paired with the original
# analytical tabs so every existing analysis remains available.
if st.session_state.active_section != "Overview":
    st.info(f"Showing the full dashboard. Use the {st.session_state.active_section} tab below to focus on that analysis.")



# ---------------------------------------------------------------------
# TAB 1 — Engagement Health Overview
# ---------------------------------------------------------------------
with tab_overview:
    kpis = metrics.kpi_summary(df)

    eng_val = kpis['Engagement Index']
    eng_tier = "Low" if eng_val < 0.34 else ("High" if eng_val >= 0.67 else "Medium")
    wlb_val = kpis['Work-Life Balance Index']
    wlb_tag = "Below org avg" if wlb_val < 2.76 else ("Above org avg" if wlb_val > 2.76 else "At org avg")
    high_risk_n = int((df["BurnoutRisk"] == "High").sum())
    stress_n = int(((df["OverTime"] == "Yes") & (df["BusinessTravel"] == "Travel_Frequently")).sum())
    pct_of_total = f" ({len(df) / len(df_full) * 100:.0f}% of {len(df_full):,} total)" if len(df) != len(df_full) else ""

    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-card"><div class="kpi-label">👥 Employees</div>
                <div class="kpi-value">{len(df):,}</div>
                <div class="kpi-help">In current filtered view{pct_of_total}</div></div>
            <div class="kpi-card"><div class="kpi-label">⚡ Engagement Index</div>
                <div class="kpi-value accent">{eng_val:.3f}</div>
                <span class="badge {eng_tier.lower()}">{eng_tier} tier</span>
                <div class="kpi-help">Mean of involvement, job, environment &amp; relationship satisfaction, normalized 0–1. Tiers: &lt;0.34 Low · 0.34–0.67 Medium · ≥0.67 High.</div></div>
            <div class="kpi-card"><div class="kpi-label">⚖️ Work-Life Balance</div>
                <div class="kpi-value">{wlb_val:.2f} / 4</div>
                <div class="kpi-help">{wlb_tag} (org mean 2.76). Self-reported, 1 = poor, 4 = excellent.</div></div>
            <div class="kpi-card"><div class="kpi-label">🔥 High Burnout Risk</div>
                <div class="kpi-value risk-high">{kpis['High Burnout Risk (%)']:.1f}%</div>
                <div class="kpi-help">{high_risk_n:,} employees — overtime + low work-life balance + low engagement combined.</div></div>
            <div class="kpi-card"><div class="kpi-label">🧳 Workload Stress</div>
                <div class="kpi-value">{kpis['Workload Stress Indicator (%)']:.1f}%</div>
                <div class="kpi-help">{stress_n:,} employees travel frequently AND work overtime — the highest-concentration risk combo.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown('<div class="pulse-h">Engagement tier distribution</div>', unsafe_allow_html=True)
            st.markdown('<div class="pulse-sub">Employees bucketed by their 0–1 Engagement Index score</div>', unsafe_allow_html=True)
            tier_counts = df["EngagementTier"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
            fig = px.pie(
                values=tier_counts.values, names=tier_counts.index, hole=0.62,
                color=tier_counts.index,
                color_discrete_map={"Low": RISK_HIGH, "Medium": RISK_MEDIUM, "High": RISK_LOW},
            )
            fig.update_traces(textfont_size=12, marker=dict(line=dict(color=SURFACE, width=2)))
            fig.update_layout(template=CHART_TEMPLATE, height=280, showlegend=True,
                               legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.markdown('<div class="pulse-h">Satisfaction distribution</div>', unsafe_allow_html=True)
            st.markdown('<div class="pulse-sub">Spread of the 4 satisfaction dimensions (1–4 scale)</div>', unsafe_allow_html=True)
            sat_cols = ["JobInvolvement", "JobSatisfaction", "EnvironmentSatisfaction", "RelationshipSatisfaction"]
            sat_long = df[sat_cols].melt(var_name="Dimension", value_name="Score")
            fig = px.histogram(sat_long, x="Score", color="Dimension", barmode="group", nbins=4)
            fig.update_layout(template=CHART_TEMPLATE, height=280, legend=dict(orientation="h", y=-0.15),
                               bargap=0.15)
            st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown('<div class="pulse-h">Engagement Index by department</div>', unsafe_allow_html=True)
        st.markdown('<div class="pulse-sub">Average score (0–1) across each department</div>', unsafe_allow_html=True)
        dept_eng = df.groupby("Department")["EngagementIndex"].mean().sort_values()
        fig = go.Figure(go.Bar(x=dept_eng.values, y=dept_eng.index, orientation="h",
                                marker_color=ACCENT, marker_line_width=0))
        fig.update_layout(template=CHART_TEMPLATE, height=220, xaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------
# TAB 2 — Burnout Risk Dashboard
# ---------------------------------------------------------------------
with tab_burnout:
    risk_counts = df["BurnoutRisk"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
    risk_pct = (risk_counts / len(df) * 100).round(1) if len(df) else risk_counts

    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-card"><div class="kpi-label">🟢 Low risk</div>
                <div class="kpi-value">{int(risk_counts['Low']):,}</div>
                <div class="kpi-help">{risk_pct['Low']:.1f}% of filtered employees — no overtime/balance/engagement flags triggered.</div></div>
            <div class="kpi-card"><div class="kpi-label">🟡 Medium risk</div>
                <div class="kpi-value">{int(risk_counts['Medium']):,}</div>
                <div class="kpi-help">{risk_pct['Medium']:.1f}% — one risk factor present, worth monitoring.</div></div>
            <div class="kpi-card"><div class="kpi-label">🔴 High risk</div>
                <div class="kpi-value risk-high">{int(risk_counts['High']):,}</div>
                <div class="kpi-help">{risk_pct['High']:.1f}% — multiple factors combined; prioritize for the Manager Action Panel watchlist.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown('<div class="pulse-h">Overtime vs. engagement</div>', unsafe_allow_html=True)
            st.markdown('<div class="pulse-sub">Do overtime employees show lower engagement?</div>', unsafe_allow_html=True)
            fig = px.box(df, x="OverTime", y="EngagementIndex", color="OverTime",
                         color_discrete_map={"Yes": RISK_HIGH, "No": RISK_LOW})
            fig.update_layout(template=CHART_TEMPLATE, height=290, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.markdown('<div class="pulse-h">Burnout risk by travel frequency</div>', unsafe_allow_html=True)
            st.markdown('<div class="pulse-sub">Risk-level mix within each travel category</div>', unsafe_allow_html=True)
            travel_risk = pd.crosstab(df["BusinessTravel"], df["BurnoutRisk"], normalize="index") * 100
            travel_risk = travel_risk.reindex(columns=["Low", "Medium", "High"]).fillna(0)
            fig = go.Figure()
            colors = {"Low": RISK_LOW, "Medium": RISK_MEDIUM, "High": RISK_HIGH}
            for level in ["Low", "Medium", "High"]:
                fig.add_bar(name=level, x=travel_risk.index, y=travel_risk[level], marker_color=colors[level])
            fig.update_layout(barmode="stack", template=CHART_TEMPLATE, height=290,
                               legend=dict(orientation="h", y=-0.2), yaxis_title="% of employees")
            st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown('<div class="pulse-h">High burnout risk share by department</div>', unsafe_allow_html=True)
        dept_burnout = df.groupby("Department")["BurnoutRisk"].apply(lambda s: (s == "High").mean() * 100).sort_values()
        fig = go.Figure(go.Bar(x=dept_burnout.values, y=dept_burnout.index, orientation="h",
                                marker_color=RISK_HIGH, marker_line_width=0))
        fig.update_layout(template=CHART_TEMPLATE, height=220, xaxis_title="% High risk")
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------
# TAB 3 — Role & Career Stage Analysis
# ---------------------------------------------------------------------
with tab_career:
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown('<div class="pulse-h">Engagement by job level</div>', unsafe_allow_html=True)
            level_eng = df.groupby("JobLevel")["EngagementIndex"].mean()
            fig = go.Figure(go.Bar(x=level_eng.index.astype(str), y=level_eng.values,
                                    marker_color=ACCENT, marker_line_width=0))
            fig.update_layout(template=CHART_TEMPLATE, height=260, yaxis_range=[0, 1])
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.markdown('<div class="pulse-h">Engagement by tenure band</div>', unsafe_allow_html=True)
            tenure_eng = df.groupby("TenureBand", observed=True)["EngagementIndex"].mean()
            fig = go.Figure(go.Scatter(x=tenure_eng.index.astype(str), y=tenure_eng.values,
                                        mode="lines+markers", line=dict(color=ACCENT, width=2.5),
                                        marker=dict(size=7, color=ACCENT), fill="tozeroy",
                                        fillcolor="rgba(43,193,205,0.12)"))
            fig.update_layout(template=CHART_TEMPLATE, height=260, yaxis_range=[0, 1])
            st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown('<div class="pulse-h">Stagnation check: years since last promotion vs. engagement</div>', unsafe_allow_html=True)
        st.markdown('<div class="pulse-sub">Does engagement fade the longer someone waits for a promotion?</div>', unsafe_allow_html=True)
        promo_eng = df.groupby("YearsSinceLastPromotion")["EngagementIndex"].mean()
        fig = go.Figure(go.Scatter(x=promo_eng.index, y=promo_eng.values, mode="lines+markers",
                                    line=dict(color=ACCENT_STRONG, width=2.5),
                                    marker=dict(size=6, color=ACCENT_STRONG)))
        fig.update_layout(template=CHART_TEMPLATE, height=250,
                           xaxis_title="Years since last promotion", yaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown('<div class="pulse-h">Engagement by job role</div>', unsafe_allow_html=True)
        role_eng = df.groupby("JobRole")["EngagementIndex"].mean().sort_values()
        fig = go.Figure(go.Bar(x=role_eng.values, y=role_eng.index, orientation="h",
                                marker_color=ACCENT, marker_line_width=0))
        fig.update_layout(template=CHART_TEMPLATE, height=340, xaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------
# TAB 4 — Manager Action Panel
# ---------------------------------------------------------------------
with tab_manager:
    st.markdown('<div class="pulse-h">Priority watchlist</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pulse-sub">High burnout risk employees with the lowest Engagement Index — prioritize for a check-in</div>',
        unsafe_allow_html=True,
    )

    watchlist = (
        df[df["BurnoutRisk"] == "High"]
        .sort_values("EngagementIndex")
        .head(8)
    )

    with st.container(border=True):
        if watchlist.empty:
            st.info("No High burnout risk employees match the current filters.")
        else:
            rows_html = ""
            for _, w in watchlist.iterrows():
                rows_html += f"""
                <div class="watch-row">
                    <div><div class="watch-role">{w['JobRole']}</div>
                        <div class="watch-meta">{w['Department']}</div></div>
                    <div class="watch-meta">{w['BusinessTravel'].replace('_',' ')} · Overtime: {w['OverTime']}</div>
                    <div class="watch-meta">WLB {w['WorkLifeBalance']} · {w['YearsAtCompany']} yrs tenure</div>
                    <div><span class="badge high">Engagement {w['EngagementIndex']:.2f}</span></div>
                </div>
                """
            st.markdown(rows_html, unsafe_allow_html=True)

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="pulse-h">Priority intervention areas</div>', unsafe_allow_html=True)
        attr_by_tier = (df.groupby("EngagementTier")["Attrition"].mean() * 100).reindex(["Low", "Medium", "High"])
        freq_travel_ot = df[(df["OverTime"] == "Yes") & (df["BusinessTravel"] == "Travel_Frequently")]
        freq_high_risk_pct = (freq_travel_ot["BurnoutRisk"] == "High").mean() * 100 if len(freq_travel_ot) else 0

        st.markdown(
            f"""
            <ul style="font-size:13px; color:#93A1B0; line-height:1.7; margin:0; padding-left:18px;">
                <li><b style="color:#E7ECF2;">{freq_high_risk_pct:.1f}%</b> of employees who both travel
                    frequently and work overtime are at High burnout risk within the current filters.</li>
                <li>Low-engagement employees show a <b style="color:#E7ECF2;">{attr_by_tier.get('Low', 0):.1f}%</b>
                    attrition rate, versus <b style="color:#E7ECF2;">{attr_by_tier.get('High', 0):.1f}%</b>
                    for highly engaged employees.</li>
                <li>Use the sidebar filters to narrow this panel to a specific department or role before
                    sharing with a manager.</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="pulse-h">Full filtered employee table</div>', unsafe_allow_html=True)
        table_df = df[["Department", "JobRole", "Age", "OverTime", "WorkLifeBalance",
                        "EngagementIndex", "EngagementTier", "BurnoutRisk", "YearsAtCompany", "Attrition"]].copy()
        table_df["EngagementIndex"] = table_df["EngagementIndex"].round(3)
        table_df["BurnoutRisk"] = table_df["BurnoutRisk"].apply(risk_emoji)
        table_df["Attrition"] = table_df["Attrition"].apply(
            lambda a: status_emoji("Left" if a == 1 else "Active")
        )
        st.dataframe(table_df, use_container_width=True, hide_index=True)
