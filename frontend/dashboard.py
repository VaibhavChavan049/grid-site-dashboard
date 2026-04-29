"""
Grid Site Analysis & Deployment Intelligence Dashboard
Powertown-style smart grid site assessment tool.
Author: Vaibhav Chavan | WPI MS Data Science '26
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import os
import sys
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grid Site Intelligence Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
  }
  
  .main { background: #0a0f1e; }
  
  /* Header */
  .dash-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 50%, #0d1b2a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .dash-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #00d4ff, #0066ff, #6600ff, #00d4ff);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
  }
  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
  .dash-title {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .dash-subtitle {
    font-size: 14px;
    color: #7a9cc0;
    margin-top: 6px;
    font-weight: 400;
  }

  /* Metric cards */
  .metric-card {
    background: linear-gradient(145deg, #111827, #1a2535);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #00d4ff; }
  .metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #00d4ff;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
  }
  .metric-label {
    font-size: 12px;
    color: #7a9cc0;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 6px;
  }
  .metric-sub {
    font-size: 11px;
    color: #4a6080;
    margin-top: 4px;
  }

  /* Score badge */
  .score-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
  }
  
  /* Section headers */
  .section-header {
    font-size: 16px;
    font-weight: 600;
    color: #c8d8f0;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 24px 0 16px 0;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 8px;
  }

  /* Status pills */
  .status-active { background: #0d2e1a; color: #00c853; border: 1px solid #00c853; }
  .status-approved { background: #0d1e2e; color: #00b4d8; border: 1px solid #00b4d8; }
  .status-pending { background: #2e2400; color: #ffd600; border: 1px solid #ffd600; }
  .status-review { background: #2e1800; color: #ff9800; border: 1px solid #ff9800; }
  .status-rejected { background: #2e0d0d; color: #ff4444; border: 1px solid #ff4444; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #090e1c;
    border-right: 1px solid #1e3a5f;
  }
  
  /* Dataframe styling */
  .stDataFrame { border-radius: 10px; overflow: hidden; }
  
  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    color: #7a9cc0;
    border-radius: 6px;
  }
  .stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #00d4ff !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_sites(state=None, site_type=None, status=None, min_score=0):
    params = {"min_score": min_score, "limit": 200}
    if state and state != "All":    params["state"] = state
    if site_type and site_type != "All": params["site_type"] = site_type
    if status and status != "All":  params["status"] = status
    try:
        r = requests.get(f"{API_BASE}/api/sites", params=params, timeout=10)
        return pd.DataFrame(r.json())
    except Exception as e:
        st.error(f"API connection error: {e}. Make sure the FastAPI server is running.")
        return pd.DataFrame()

@st.cache_data(ttl=120)
def fetch_summary():
    try:
        r = requests.get(f"{API_BASE}/api/summary", timeout=10)
        return r.json()
    except:
        return {}

@st.cache_data(ttl=120)
def fetch_load_profile(site_id):
    try:
        r = requests.get(f"{API_BASE}/api/sites/{site_id}/load_profile", timeout=10)
        data = r.json()
        return pd.DataFrame(data.get("records", []))
    except:
        return pd.DataFrame()

def score_color(score):
    if score >= 85: return "#00c853"
    elif score >= 70: return "#00b4d8"
    elif score >= 55: return "#ffd600"
    elif score >= 40: return "#ff9800"
    else: return "#ff4444"

def score_label(score):
    if score >= 85: return "Excellent"
    elif score >= 70: return "Good"
    elif score >= 55: return "Moderate"
    elif score >= 40: return "Low"
    else: return "Critical"

def status_class(status):
    mapping = {
        "Active": "status-active", "Approved": "status-approved",
        "Pending": "status-pending", "Under Review": "status-review",
        "Rejected": "status-rejected"
    }
    return mapping.get(status, "status-pending")

# ── Sidebar Filters ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Grid Intelligence")
    st.markdown("<small style='color:#4a6080'>Deployment Feasibility Platform</small>", unsafe_allow_html=True)
    st.divider()

    st.markdown("#### 🔍 Filter Sites")
    states = ["All", "CA", "TX", "NY", "FL", "AZ", "NV", "CO", "WA", "OR", "MN"]
    site_types = ["All", "Solar", "Wind", "Battery Storage", "Solar+Storage", "Wind+Storage"]
    statuses = ["All", "Active", "Pending", "Under Review", "Approved", "Rejected"]

    sel_state = st.selectbox("State", states)
    sel_type = st.selectbox("Site Type", site_types)
    sel_status = st.selectbox("Deployment Status", statuses)
    min_score = st.slider("Min Viability Score", 0, 100, 0, 5)
    min_cap = st.slider("Min Capacity (MW)", 0, 250, 0, 10)

    st.divider()
    st.markdown("#### 📊 Sort By")
    sort_col = st.selectbox("Sort by", [
        "composite_viability_score", "capacity_mw", "irr_percent",
        "est_cost_million_usd", "payback_years"
    ])

    st.divider()
    st.markdown("#### 📥 Export")
    export_url = f"{API_BASE}/api/export/csv?min_score={min_score}"
    if sel_state != "All": export_url += f"&state={sel_state}"
    if sel_status != "All": export_url += f"&status={sel_status}"
    st.markdown(f"[⬇ Download CSV Report]({export_url})")

    st.divider()
    st.markdown(f"<small style='color:#4a6080'>Last updated: {datetime.now().strftime('%H:%M:%S')}</small>", unsafe_allow_html=True)


# ── Main Dashboard ─────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div class="dash-title">⚡ Grid Site Deployment Intelligence</div>
  <div class="dash-subtitle">End-to-end feasibility scoring & site analysis platform · 60 sites · Real-time filtering · Statistical ranking</div>
</div>
""", unsafe_allow_html=True)

# Fetch data
df = fetch_sites(sel_state, sel_type, sel_status, min_score)
if not df.empty and min_cap > 0:
    df = df[df["capacity_mw"] >= min_cap]

summary = fetch_summary()

if df.empty:
    st.warning("⚠️ No sites found with current filters, or API is not running.")
    st.info("Run the FastAPI server: `uvicorn backend.api:app --reload`")
    st.stop()

# ── KPI Row ────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, str(len(df)), "Sites Matched", f"of {summary.get('total_sites', '—')} total"),
    (c2, f"{df['composite_viability_score'].mean():.1f}", "Avg Viability Score", "0–100 composite"),
    (c3, f"{df['capacity_mw'].sum():.0f} MW", "Total Capacity", "across filtered sites"),
    (c4, f"${df['est_cost_million_usd'].sum():.0f}M", "Est. Investment", "total capital"),
    (c5, f"{df['irr_percent'].mean():.1f}%", "Avg IRR", "internal rate of return"),
]
for col, val, label, sub in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{val}</div>
          <div class="metric-label">{label}</div>
          <div class="metric-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺 Map View", "📊 Analytics", "📋 Site Table", "🔬 Site Deep Dive"])

# ════════════════════════════════════════════════════════
# TAB 1: MAP
# ════════════════════════════════════════════════════════
with tab1:
    col_map, col_top = st.columns([3, 1])

    with col_map:
        st.markdown('<div class="section-header">Geospatial Site Distribution</div>', unsafe_allow_html=True)
        fig_map = px.scatter_mapbox(
            df,
            lat="latitude", lon="longitude",
            color="composite_viability_score",
            size="capacity_mw",
            hover_name="site_name",
            hover_data={
                "state": True, "site_type": True, "status": True,
                "composite_viability_score": ":.1f",
                "capacity_mw": ":.1f",
                "irr_percent": ":.1f",
                "latitude": False, "longitude": False
            },
            color_continuous_scale=[(0, "#ff4444"), (0.4, "#ff9800"), (0.7, "#ffd600"), (1.0, "#00c853")],
            size_max=20,
            zoom=3.5,
            center={"lat": 38.5, "lon": -98},
            mapbox_style="carto-darkmatter",
            title=""
        )
        fig_map.update_layout(
            height=520,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(
                title="Viability Score",
                tickfont=dict(color="#7a9cc0"),
                titlefont=dict(color="#7a9cc0")
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_top:
        st.markdown('<div class="section-header">Top 10 Sites</div>', unsafe_allow_html=True)
        top10 = df.nlargest(10, "composite_viability_score")[
            ["site_id", "state", "composite_viability_score", "status"]
        ]
        for _, row in top10.iterrows():
            sc = row["composite_viability_score"]
            st.markdown(f"""
            <div style="background:#111827; border:1px solid #1e3a5f; border-radius:8px;
                        padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <span style="color:#c8d8f0; font-size:13px; font-weight:600;">{row['site_id']}</span>
                <span style="color:#4a6080; font-size:11px; margin-left:6px;">{row['state']}</span>
              </div>
              <span style="color:{score_color(sc)}; font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:700;">{sc}</span>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2: ANALYTICS
# ════════════════════════════════════════════════════════
with tab2:
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown('<div class="section-header">Viability Score Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df, x="composite_viability_score", nbins=20,
            color_discrete_sequence=["#00d4ff"]
        )
        fig_hist.update_layout(
            height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d1520",
            font_color="#7a9cc0", showlegend=False,
            xaxis=dict(gridcolor="#1e3a5f", title="Viability Score"),
            yaxis=dict(gridcolor="#1e3a5f", title="Count"),
            bargap=0.1
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with r1c2:
        st.markdown('<div class="section-header">Status Breakdown</div>', unsafe_allow_html=True)
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        colors = {"Active": "#00c853", "Approved": "#00b4d8", "Pending": "#ffd600",
                  "Under Review": "#ff9800", "Rejected": "#ff4444"}
        fig_pie = px.pie(
            status_counts, values="count", names="status",
            color="status", color_discrete_map=colors, hole=0.5
        )
        fig_pie.update_layout(
            height=300, paper_bgcolor="rgba(0,0,0,0)",
            font_color="#7a9cc0", legend=dict(font=dict(color="#7a9cc0"))
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown('<div class="section-header">IRR vs Viability Score</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df, x="composite_viability_score", y="irr_percent",
            color="site_type", size="capacity_mw",
            hover_name="site_name",
            labels={"composite_viability_score": "Viability Score", "irr_percent": "IRR (%)"}
        )
        fig_scatter.update_layout(
            height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d1520",
            font_color="#7a9cc0",
            xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f"),
            legend=dict(font=dict(color="#7a9cc0"), bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with r2c2:
        st.markdown('<div class="section-header">Avg Score by State</div>', unsafe_allow_html=True)
        state_avg = df.groupby("state")["composite_viability_score"].mean().sort_values(ascending=True).reset_index()
        fig_bar = px.bar(
            state_avg, y="state", x="composite_viability_score",
            orientation="h", color="composite_viability_score",
            color_continuous_scale=[(0, "#ff4444"), (0.5, "#ffd600"), (1.0, "#00c853")]
        )
        fig_bar.update_layout(
            height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d1520",
            font_color="#7a9cc0", showlegend=False,
            xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Scoring factor radar
    st.markdown('<div class="section-header">Average Scoring Factor Breakdown</div>', unsafe_allow_html=True)
    factors = [
        "land_availability_score", "grid_proximity_score", "load_demand_score",
        "environmental_score", "permit_ease_score", "infrastructure_readiness_score"
    ]
    labels = ["Land Availability", "Grid Proximity", "Load Demand",
              "Environmental", "Permit Ease", "Infrastructure"]
    avg_vals = [df[f].mean() for f in factors]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=avg_vals + [avg_vals[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(0, 212, 255, 0.15)",
        line=dict(color="#00d4ff", width=2),
        name="All Sites Avg"
    ))

    # Top 10 overlay
    top_df = df.nlargest(10, "composite_viability_score")
    top_vals = [top_df[f].mean() for f in factors]
    fig_radar.add_trace(go.Scatterpolar(
        r=top_vals + [top_vals[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(0, 200, 83, 0.15)",
        line=dict(color="#00c853", width=2, dash="dash"),
        name="Top 10 Sites"
    ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0d1520",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e3a5f", color="#4a6080"),
            angularaxis=dict(gridcolor="#1e3a5f", color="#7a9cc0")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#7a9cc0",
        legend=dict(font=dict(color="#7a9cc0"), bgcolor="rgba(0,0,0,0)"),
        height=380
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ════════════════════════════════════════════════════════
# TAB 3: SITE TABLE
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">All Sites · Filterable & Sortable</div>', unsafe_allow_html=True)

    display_cols = [
        "site_id", "site_name", "state", "site_type", "capacity_mw",
        "composite_viability_score", "irr_percent", "est_cost_million_usd",
        "payback_years", "status", "analyst", "assessment_date"
    ]
    display_df = df[display_cols].copy()
    display_df = display_df.rename(columns={
        "composite_viability_score": "viability_score",
        "est_cost_million_usd": "cost_M_usd",
        "irr_percent": "irr_%",
    })
    display_df = display_df.sort_values("viability_score", ascending=False)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        column_config={
            "viability_score": st.column_config.ProgressColumn(
                "Viability Score", min_value=0, max_value=100, format="%.1f"
            ),
            "irr_%": st.column_config.NumberColumn("IRR (%)", format="%.1f%%"),
            "cost_M_usd": st.column_config.NumberColumn("Cost ($M)", format="$%.1fM"),
            "capacity_mw": st.column_config.NumberColumn("Capacity (MW)", format="%.1f MW"),
        }
    )

    st.markdown(f"<small style='color:#4a6080'>Showing {len(display_df)} sites · Use sidebar to filter</small>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# TAB 4: SITE DEEP DIVE
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Site-Level Analysis</div>', unsafe_allow_html=True)

    site_options = df["site_id"].tolist()
    selected_site_id = st.selectbox("Select a Site to Analyze", site_options,
                                     format_func=lambda x: f"{x} · {df[df['site_id']==x]['site_name'].values[0]}")

    site_row = df[df["site_id"] == selected_site_id].iloc[0]
    sc = site_row["composite_viability_score"]

    # Site header
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#111827,#1a2535); border:1px solid #1e3a5f;
                border-radius:12px; padding:20px 28px; margin:12px 0;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:20px; font-weight:700; color:#fff;">{site_row['site_name']}</div>
          <div style="color:#7a9cc0; font-size:13px; margin-top:4px;">
            {site_row['site_type']} · {site_row['grid_zone']} · {site_row['state']} · Analyst: {site_row['analyst']}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:42px; font-weight:700; color:{score_color(sc)}; font-family:'JetBrains Mono',monospace; line-height:1;">{sc}</div>
          <div style="font-size:12px; color:{score_color(sc)}; text-transform:uppercase; letter-spacing:1px;">{score_label(sc)}</div>
          <span class="score-badge {status_class(site_row['status'])}" style="margin-top:6px; display:inline-block;">{site_row['status']}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    dc1, dc2, dc3, dc4 = st.columns(4)
    detail_kpis = [
        (dc1, f"{site_row['capacity_mw']:.1f} MW", "Capacity"),
        (dc2, f"${site_row['est_cost_million_usd']:.1f}M", "Est. Cost"),
        (dc3, f"{site_row['irr_percent']:.1f}%", "IRR"),
        (dc4, f"{site_row['payback_years']:.1f} yrs", "Payback"),
    ]
    for col, val, lbl in detail_kpis:
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-value" style="font-size:24px;">{val}</div>
              <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dd1, dd2 = st.columns(2)

    with dd1:
        st.markdown('<div class="section-header">Scoring Breakdown</div>', unsafe_allow_html=True)
        factors = [
            ("Grid Proximity", site_row["grid_proximity_score"]),
            ("Load Demand", site_row["load_demand_score"]),
            ("Land Availability", site_row["land_availability_score"]),
            ("Environmental", site_row["environmental_score"]),
            ("Permit Ease", site_row["permit_ease_score"]),
            ("Infrastructure", site_row["infrastructure_readiness_score"]),
        ]
        for label, val in factors:
            bar_color = score_color(val)
            st.markdown(f"""
            <div style="margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color:#c8d8f0; font-size:13px;">{label}</span>
                <span style="color:{bar_color}; font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:600;">{val:.1f}</span>
              </div>
              <div style="background:#1e3a5f; border-radius:4px; height:6px;">
                <div style="background:{bar_color}; width:{val}%; height:100%; border-radius:4px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with dd2:
        st.markdown('<div class="section-header">Load Profile (Last 30 Days)</div>', unsafe_allow_html=True)
        load_df = fetch_load_profile(selected_site_id)
        if not load_df.empty:
            load_df["timestamp"] = pd.to_datetime(load_df["timestamp"])
            fig_load = go.Figure()
            fig_load.add_trace(go.Scatter(
                x=load_df["timestamp"], y=load_df["load_mw"],
                mode="lines", name="Load (MW)", line=dict(color="#00d4ff", width=1.5)
            ))
            fig_load.add_trace(go.Scatter(
                x=load_df["timestamp"], y=load_df["generation_mw"],
                mode="lines", name="Generation (MW)", line=dict(color="#00c853", width=1.5)
            ))
            fig_load.update_layout(
                height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d1520",
                font_color="#7a9cc0", margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f"),
                legend=dict(font=dict(color="#7a9cc0"), bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_load, use_container_width=True)
        else:
            st.info("No load profile data for this site.")

# ── Footer ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:40px; padding:20px; border-top:1px solid #1e3a5f; color:#4a6080; font-size:12px;">
  Grid Site Intelligence Dashboard · Built by Vaibhav Chavan · WPI MS Data Science '26 · 
  <span style="color:#00d4ff;">Powertown Internship Project</span>
</div>
""", unsafe_allow_html=True)
