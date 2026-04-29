import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
warnings.filterwarnings("ignore")

# Always resolve CSV path relative to this script file
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "HHS_Unaccompanied_Alien_Children_Program.csv")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HHS UAC Care System Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #1e2a3a;
    }
    [data-testid="stSidebar"] * { color: #c9d1d9 !important; }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #161b27 0%, #1a2035 100%);
        border: 1px solid #1e2a3a;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #2563eb; }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #f0f6fc;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 11px;
        color: #6b7280;
        margin-top: 4px;
    }
    .kpi-pos { color: #22c55e !important; }
    .kpi-neg { color: #ef4444 !important; }
    .kpi-warn { color: #f59e0b !important; }
    .kpi-blue { color: #60a5fa !important; }

    /* Section Headers */
    .section-header {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6b7280;
        border-bottom: 1px solid #1e2a3a;
        padding-bottom: 8px;
        margin-bottom: 16px;
        margin-top: 8px;
    }

    /* Stress band */
    .stress-band {
        display: flex;
        height: 24px;
        border-radius: 6px;
        overflow: hidden;
        width: 100%;
    }

    /* Phase badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-critical { background: rgba(239,68,68,0.15); color: #ef4444; }
    .badge-high     { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge-moderate { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-recovery { background: rgba(34,197,94,0.15);  color: #22c55e; }
    .badge-low      { background: rgba(99,102,241,0.15); color: #818cf8; }

    /* Plotly chart background */
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }

    /* Hide streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* Metric delta */
    [data-testid="stMetricDelta"] { font-size: 12px; }

    /* Divider */
    hr { border-color: #1e2a3a; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ──────────────────────────────────────────────────────────────
PLOT_BG   = "#0f1117"
PAPER_BG  = "#0f1117"
GRID_CLR  = "rgba(255,255,255,0.05)"
TEXT_CLR  = "#c9d1d9"
FONT_FAM  = "Inter, sans-serif"

def base_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(size=14, color=TEXT_CLR, family=FONT_FAM), x=0.01),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_CLR, family=FONT_FAM, size=11),
        margin=dict(l=50, r=20, t=40, b=50),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(size=11),
        ),
        xaxis=dict(showgrid=False, color=TEXT_CLR, linecolor="#1e2a3a", tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_CLR, color=TEXT_CLR, linecolor="#1e2a3a", tickfont=dict(size=10)),
    )

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df.columns = ["Date","Apprehended","CBP_Custody","Transferred","HHS_Care","Discharged"]
    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    for col in ["Apprehended","CBP_Custody","Transferred","HHS_Care","Discharged"]:
        df[col] = df[col].astype(str).str.replace(",","").str.strip()
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df = df.sort_values("Date").reset_index(drop=True)
    # Derived columns
    df["Total_Load"]    = df["CBP_Custody"] + df["HHS_Care"]
    df["Net_Intake"]    = df["Transferred"] - df["Discharged"]
    df["Year"]          = df["Date"].dt.year
    df["Month"]         = df["Date"].dt.to_period("M")
    df["MonthStr"]      = df["Date"].dt.strftime("%b %Y")
    df["YearMonth"]     = df["Date"].dt.strftime("%Y-%m")
    df["Discharge_Ratio"] = (df["Discharged"] / df["Transferred"].replace(0, np.nan)).round(2)
    return df

@st.cache_data
def monthly_agg(df):
    m = df.groupby("YearMonth").agg(
        Apprehended=("Apprehended","sum"),
        Transferred=("Transferred","sum"),
        Discharged=("Discharged","sum"),
        Avg_HHS=("HHS_Care","mean"),
        Avg_CBP=("CBP_Custody","mean"),
        Max_HHS=("HHS_Care","max"),
    ).reset_index()
    m["Net_Intake"] = m["Transferred"] - m["Discharged"]
    m["Discharge_Ratio"] = (m["Discharged"] / m["Transferred"].replace(0, np.nan)).round(2)
    m["Label"] = pd.to_datetime(m["YearMonth"]).dt.strftime("%b '%y")
    return m

df_all = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 UAC Care System")
    st.markdown("**HHS Analytics Dashboard**")
    st.markdown("---")

    year_opts = ["All Years"] + sorted(df_all["Year"].unique().tolist(), reverse=True)
    sel_year  = st.selectbox("📅 Filter by Year", year_opts)

    granularity = st.radio("📊 Granularity", ["Monthly", "Daily"], index=0)

    st.markdown("---")
    st.markdown("**Chart Toggles**")
    show_cbp    = st.checkbox("Show CBP Custody layer", value=True)
    show_7day   = st.checkbox("Show 7-day rolling avg", value=True)
    show_stress = st.checkbox("Show Stress Timeline",   value=True)

    st.markdown("---")
    st.markdown("**Dataset Info**")
    st.caption(f"📆 {df_all['Date'].min().strftime('%b %d, %Y')} → {df_all['Date'].max().strftime('%b %d, %Y')}")
    st.caption(f"📋 {len(df_all):,} reporting days")
    st.caption(f"🏛 Source: HHS / ORR")

# ── FILTER ────────────────────────────────────────────────────────────────────
if sel_year == "All Years":
    df = df_all.copy()
else:
    df = df_all[df_all["Year"] == int(sel_year)].copy()

monthly = monthly_agg(df)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
  <div>
    <h1 style="margin:0;font-size:26px;font-weight:700;color:#f0f6fc;">
      🏥 HHS Unaccompanied Children Care System
    </h1>
    <p style="margin:4px 0 0;font-size:13px;color:#6b7280;">
      U.S. Department of Health and Human Services · Operational Analytics Dashboard
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI SECTION ───────────────────────────────────────────────────────────────
last       = df.iloc[-1]
total_load = int(last["Total_Load"])
hhs_latest = int(last["HHS_Care"])
cbp_latest = int(last["CBP_Custody"])
peak_hhs   = int(df["HHS_Care"].max())
peak_date  = df.loc[df["HHS_Care"].idxmax(), "Date"].strftime("%b %d, %Y")
tot_trans  = int(df["Transferred"].sum())
tot_disc   = int(df["Discharged"].sum())
net_press  = tot_trans - tot_disc
ratio_avg  = round(tot_disc / max(tot_trans, 1), 2)

def fmt(n): return f"{n:,}"

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

kpis = [
    (col1, "Total System Load", fmt(total_load), "CBP + HHS combined", "kpi-blue"),
    (col2, "HHS In Care", fmt(hhs_latest), "Latest reported day", ""),
    (col3, "CBP Custody", fmt(cbp_latest), "Latest reported day", ""),
    (col4, "Peak HHS Population", fmt(peak_hhs), peak_date, "kpi-warn"),
    (col5, "Total Transferred", fmt(tot_trans), "Into HHS system", "kpi-blue"),
    (col6, "Total Discharged", fmt(tot_disc), "To sponsors", "kpi-pos"),
    (col7, "Net Intake Pressure",
     ("+" if net_press >= 0 else "") + fmt(net_press),
     "Backlog accumulating" if net_press > 0 else "System relieving load",
     "kpi-neg" if net_press > 0 else "kpi-pos"),
]

for col, label, val, sub, cls in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value {cls}">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# ── ROW 1: System Load + Net Intake ──────────────────────────────────────────
st.markdown('<div class="section-header">System Care Load Over Time</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])

with c1:
    fig = go.Figure()
    # HHS care fill
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["HHS_Care"],
        name="HHS In Care",
        line=dict(color="#3b82f6", width=2),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.12)",
        mode="lines",
    ))
    if show_cbp:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["CBP_Custody"],
            name="CBP Custody",
            line=dict(color="#f97316", width=1.5, dash="dot"),
            fill="tozeroy", fillcolor="rgba(249,115,22,0.08)",
            mode="lines",
        ))
    if show_7day:
        df["HHS_7d"] = df["HHS_Care"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["HHS_7d"],
            name="7-day Rolling Avg (HHS)",
            line=dict(color="#a78bfa", width=1.5, dash="dash"),
            mode="lines",
        ))
    # Annotate peak
    fig.add_annotation(
        x=df.loc[df["HHS_Care"].idxmax(), "Date"],
        y=peak_hhs,
        text=f"Peak: {fmt(peak_hhs)}",
        showarrow=True, arrowhead=2,
        arrowcolor="#ef4444", font=dict(color="#ef4444", size=11),
        bgcolor="rgba(239,68,68,0.1)", bordercolor="#ef4444",
        ax=40, ay=-40,
    )
    layout = base_layout("HHS & CBP Care Load")
    layout["xaxis"]["title"] = "Date"
    layout["yaxis"]["title"] = "Children"
    fig.update_layout(**layout, height=300)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    # Monthly net intake bar
    colors_net = ["#ef4444" if v >= 0 else "#22c55e" for v in monthly["Net_Intake"]]
    fig2 = go.Figure(go.Bar(
        x=monthly["Label"], y=monthly["Net_Intake"],
        marker_color=colors_net, marker_line_width=0,
        name="Net Intake",
        text=monthly["Net_Intake"].apply(lambda v: f"+{v:,}" if v >= 0 else f"{v:,}"),
        textposition="outside", textfont=dict(size=8),
    ))
    layout2 = base_layout("Net Monthly Intake Pressure")
    layout2["yaxis"]["title"] = "Transferred − Discharged"
    layout2["xaxis"]["tickangle"] = -45
    layout2["xaxis"]["tickfont"] = dict(size=8)
    fig2.update_layout(**layout2, height=300, showlegend=False)
    fig2.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

# ── ROW 2: Flow + Discharge Ratio ────────────────────────────────────────────
st.markdown('<div class="section-header">Intake & Discharge Flow Analysis</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    if granularity == "Monthly":
        x_data = monthly["Label"]
        trans_data = monthly["Transferred"]
        disc_data  = monthly["Discharged"]
    else:
        x_data = df["Date"]
        trans_data = df["Transferred"]
        disc_data  = df["Discharged"]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=x_data, y=trans_data, name="Transferred to HHS",
                          marker_color="#0ea5e9", marker_line_width=0))
    fig3.add_trace(go.Bar(x=x_data, y=disc_data, name="Discharged to Sponsors",
                          marker_color="#f59e0b", marker_line_width=0))
    layout3 = base_layout("Transfers vs Discharges")
    layout3["yaxis"]["title"] = "Children"
    layout3["xaxis"]["tickangle"] = -45
    layout3["xaxis"]["tickfont"] = dict(size=9)
    layout3["barmode"] = "group"
    fig3.update_layout(**layout3, height=300)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    ratio_colors = ["#22c55e" if v >= 1 else "#f59e0b" for v in monthly["Discharge_Ratio"].fillna(0)]
    fig4 = go.Figure(go.Bar(
        x=monthly["Label"],
        y=monthly["Discharge_Ratio"].fillna(0),
        marker_color=ratio_colors, marker_line_width=0,
        name="Discharge Ratio",
        text=monthly["Discharge_Ratio"].fillna(0).apply(lambda v: f"{v:.2f}×"),
        textposition="outside", textfont=dict(size=8),
    ))
    layout4 = base_layout("Discharge Offset Ratio (Discharges ÷ Transfers)")
    layout4["yaxis"]["title"] = "Ratio"
    layout4["xaxis"]["tickangle"] = -45
    layout4["xaxis"]["tickfont"] = dict(size=8)
    fig4.update_layout(**layout4, height=300, showlegend=False)
    fig4.add_hline(y=1, line_color="rgba(255,255,255,0.3)", line_width=1,
                   annotation_text="Break-even (1×)",
                   annotation_font=dict(color="rgba(255,255,255,0.5)", size=10))
    st.plotly_chart(fig4, use_container_width=True)

# ── ROW 3: Apprehensions + CBP vs HHS scatter ─────────────────────────────────
st.markdown('<div class="section-header">Apprehensions & Capacity Correlation</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    if granularity == "Monthly":
        x_app  = monthly["Label"]
        y_app  = monthly["Apprehended"]
        mode_t = "bar"
    else:
        x_app  = df["Date"]
        y_app  = df["Apprehended"]
        mode_t = "line"

    fig5 = go.Figure()
    if mode_t == "bar":
        fig5.add_trace(go.Bar(x=x_app, y=y_app, name="Apprehended",
                               marker_color="#8b5cf6", marker_line_width=0))
    else:
        fig5.add_trace(go.Scatter(x=x_app, y=y_app, name="Apprehended",
                                  line=dict(color="#8b5cf6", width=1.5),
                                  fill="tozeroy", fillcolor="rgba(139,92,246,0.1)"))
    layout5 = base_layout("Daily/Monthly Apprehensions into CBP Custody")
    layout5["yaxis"]["title"] = "Children Apprehended"
    layout5["xaxis"]["tickangle"] = -45
    layout5["xaxis"]["tickfont"] = dict(size=9)
    fig5.update_layout(**layout5, height=280)
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    fig6 = go.Figure(go.Scatter(
        x=df["CBP_Custody"], y=df["HHS_Care"],
        mode="markers",
        marker=dict(
            color=df["Date"].astype(np.int64),
            colorscale="Viridis",
            size=5, opacity=0.7,
            colorbar=dict(title="Time →", tickfont=dict(size=9), len=0.6),
        ),
        text=df["Date"].dt.strftime("%b %d, %Y"),
        hovertemplate="<b>%{text}</b><br>CBP: %{x:,}<br>HHS: %{y:,}<extra></extra>",
        name="Daily snapshot"
    ))
    layout6 = base_layout("CBP Custody vs HHS Care Load")
    layout6["xaxis"]["title"] = "CBP Custody count"
    layout6["yaxis"]["title"] = "HHS In Care count"
    fig6.update_layout(**layout6, height=280)
    st.plotly_chart(fig6, use_container_width=True)

# ── ROW 4: Stress Timeline ────────────────────────────────────────────────────
if show_stress:
    st.markdown('<div class="section-header">Monthly Capacity Stress Classification</div>', unsafe_allow_html=True)

    peak_hhs_all = monthly["Avg_HHS"].max()
    def classify(v):
        r = v / peak_hhs_all
        if r > 0.80: return "Critical"
        if r > 0.60: return "High"
        if r > 0.40: return "Moderate"
        if r > 0.20: return "Recovery"
        return "Low"

    monthly["Phase"] = monthly["Avg_HHS"].apply(classify)
    phase_colors = {"Critical":"#ef4444","High":"#f59e0b","Moderate":"#3b82f6","Recovery":"#22c55e","Low":"#818cf8"}

    fig7 = go.Figure()
    for phase, color in phase_colors.items():
        m_sub = monthly[monthly["Phase"] == phase]
        fig7.add_trace(go.Bar(
            x=m_sub["Label"], y=m_sub["Avg_HHS"],
            name=phase, marker_color=color, marker_line_width=0,
        ))
    layout7 = base_layout("Average HHS Population by Stress Phase")
    layout7["yaxis"]["title"] = "Avg HHS In Care"
    layout7["xaxis"]["tickangle"] = -45
    layout7["xaxis"]["tickfont"] = dict(size=9)
    layout7["barmode"] = "stack"
    fig7.update_layout(**layout7, height=280)
    st.plotly_chart(fig7, use_container_width=True)

    # Phase summary badges
    phase_counts = monthly["Phase"].value_counts()
    badge_cols = st.columns(5)
    for i, (phase, color) in enumerate(phase_colors.items()):
        count = phase_counts.get(phase, 0)
        badge_cols[i].markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid #1e2a3a;border-radius:10px;padding:12px 16px;text-align:center;">
            <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.08em;">{phase}</div>
            <div style="font-size:24px;font-weight:700;color:{color};margin:4px 0;">{count}</div>
            <div style="font-size:11px;color:#6b7280;">months</div>
        </div>""", unsafe_allow_html=True)

# ── ROW 5: Cumulative + Rolling ───────────────────────────────────────────────
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown('<div class="section-header">Cumulative Trends & Rolling Averages</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)

with c7:
    df["Cum_Transferred"] = df["Transferred"].cumsum()
    df["Cum_Discharged"]  = df["Discharged"].cumsum()
    df["Cum_Backlog"]     = df["Net_Intake"].cumsum()
    fig8 = go.Figure()
    fig8.add_trace(go.Scatter(x=df["Date"], y=df["Cum_Transferred"], name="Cumulative Transferred",
                               line=dict(color="#0ea5e9", width=2)))
    fig8.add_trace(go.Scatter(x=df["Date"], y=df["Cum_Discharged"], name="Cumulative Discharged",
                               line=dict(color="#22c55e", width=2)))
    fig8.add_trace(go.Scatter(x=df["Date"], y=df["Cum_Backlog"],
                               name="Cumulative Backlog",
                               line=dict(color="#ef4444", width=1.5, dash="dash"),
                               fill="tozeroy", fillcolor="rgba(239,68,68,0.05)"))
    layout8 = base_layout("Cumulative System Flows")
    layout8["yaxis"]["title"] = "Children (cumulative)"
    fig8.update_layout(**layout8, height=280)
    st.plotly_chart(fig8, use_container_width=True)

with c8:
    df["HHS_14d"]   = df["HHS_Care"].rolling(14, min_periods=1).mean()
    df["HHS_30d"]   = df["HHS_Care"].rolling(30, min_periods=1).mean()
    df["HHS_std14"] = df["HHS_Care"].rolling(14, min_periods=1).std().fillna(0)
    fig9 = go.Figure()
    fig9.add_trace(go.Scatter(
        x=pd.concat([df["Date"], df["Date"][::-1]]),
        y=pd.concat([df["HHS_14d"] + df["HHS_std14"], (df["HHS_14d"] - df["HHS_std14"])[::-1]]),
        fill="toself", fillcolor="rgba(59,130,246,0.08)", line=dict(color="rgba(0,0,0,0)"),
        name="±1σ (14-day)", showlegend=True,
    ))
    fig9.add_trace(go.Scatter(x=df["Date"], y=df["HHS_Care"], name="Daily HHS",
                               line=dict(color="rgba(59,130,246,0.3)", width=1), mode="lines"))
    fig9.add_trace(go.Scatter(x=df["Date"], y=df["HHS_14d"], name="14-day Avg",
                               line=dict(color="#3b82f6", width=2)))
    fig9.add_trace(go.Scatter(x=df["Date"], y=df["HHS_30d"], name="30-day Avg",
                               line=dict(color="#a78bfa", width=2, dash="dash")))
    layout9 = base_layout("HHS Care Load — Rolling Averages & Volatility")
    layout9["yaxis"]["title"] = "Children in HHS Care"
    fig9.update_layout(**layout9, height=280)
    st.plotly_chart(fig9, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-size:11px;color:#4b5563;padding:12px 0;">
    HHS UAC Care System Analytics · Data Source: Office of Refugee Resettlement (ORR) ·
    Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
