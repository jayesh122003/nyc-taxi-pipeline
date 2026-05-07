import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from etl.load import get_engine

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NYC Yellow Taxis",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color palette ────────────────────────────────────────────────────────────

YELLOW = "#F7C948"
YELLOW_LIGHT = "#FFE08A"
YELLOW_DIM = "#B8960F"
DARK_BG = "#0E1117"
TEXT = "#FAFAFA"
TEXT_MUTED = "#9CA3AF"
ACCENT_BLUE = "#60A5FA"
ACCENT_GREEN = "#34D399"
ACCENT_RED = "#F87171"
ACCENT_PURPLE = "#A78BFA"

CHART_COLORS = [YELLOW, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_PURPLE, YELLOW_LIGHT]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="Inter, sans-serif", size=13),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED, size=11),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis=dict(gridcolor="#2A2D35", zerolinecolor="#2A2D35"),
    yaxis=dict(gridcolor="#2A2D35", zerolinecolor="#2A2D35"),
)

# ── Minimal CSS (only what native Streamlit can't do) ────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, p, h1, h2, h3, h4, h5, h6, span, div, label, input, textarea, button, a {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar dark background */
    [data-testid="stSidebar"] {
        background-color: #0B0E13;
        border-right: 1px solid #1E2128;
    }

    /* Sidebar brand */
    .sidebar-brand {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid #1E2128;
        margin-bottom: 1.5rem;
    }
    .sidebar-brand h2 {
        color: #F7C948;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .sidebar-brand p {
        color: #9CA3AF;
        font-size: 0.7rem;
        margin: 0.25rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Sidebar nav radio styling */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: #9CA3AF;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.15s;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: #1A1D23;
        color: #FAFAFA;
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, #1A1D23 0%, #22262E 100%);
        border-color: #F7C948;
        color: #F7C948;
        font-weight: 600;
    }

    /* Page header */
    .page-header {
        padding: 1rem 0 0.75rem 0;
        border-bottom: 2px solid #F7C948;
        margin-bottom: 1.5rem;
    }
    .page-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #FAFAFA;
        margin: 0;
    }
    .page-header p {
        color: #9CA3AF;
        font-size: 0.85rem;
        margin: 0.2rem 0 0 0;
    }

    /* Section labels */
    .section-label {
        color: #F7C948;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
    }

    /* Insight captions */
    .insight-caption {
        color: #9CA3AF;
        font-size: 0.8rem;
        font-style: italic;
        padding: 0.5rem 0 0.5rem 0.75rem;
        border-left: 3px solid #F7C948;
        margin-top: 0.5rem;
    }

    /* Primary buttons */
    .stButton > button {
        background-color: #F7C948;
        color: #0E1117;
        font-weight: 600;
        border: none;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: #FFE08A;
        color: #0E1117;
    }

    /* About card */
    .about-card {
        background: linear-gradient(135deg, #1A1D23 0%, #1E2128 100%);
        border: 1px solid #2A2D35;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-top: 2rem;
    }
    .about-card h3 {
        color: #F7C948;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 0 1rem 0;
    }
    .about-name {
        color: #FAFAFA;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .about-links {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin: 1rem 0;
    }
    .about-links a {
        color: #F7C948;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 0.4rem 1rem;
        border: 1px solid #F7C948;
        border-radius: 20px;
        transition: all 0.15s;
    }
    .about-links a:hover {
        background: #F7C948;
        color: #0E1117;
    }
    .about-note {
        color: #6B7280;
        font-size: 0.75rem;
        margin-top: 1rem;
        line-height: 1.6;
    }

    /* Coming soon */
    .coming-soon-container {
        text-align: center;
        padding: 4rem 2rem;
    }
    .coming-soon-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
    }
    .coming-soon-badge {
        display: inline-block;
        background: linear-gradient(135deg, #F7C948 0%, #B8960F 100%);
        color: #0E1117;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 0.4rem 1.25rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
    }
    .coming-soon-title {
        color: #FAFAFA;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .coming-soon-desc {
        color: #9CA3AF;
        font-size: 0.95rem;
        line-height: 1.7;
        max-width: 520px;
        margin: 0 auto 2.5rem auto;
    }
    .mock-form {
        background: linear-gradient(135deg, #1A1D23 0%, #1E2128 100%);
        border: 1px solid #2A2D35;
        border-radius: 12px;
        padding: 2rem;
        max-width: 480px;
        margin: 0 auto;
        opacity: 0.45;
    }
    .mock-form-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .mock-field {
        flex: 1;
        background: #0E1117;
        border: 1px solid #2A2D35;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        color: #555;
        font-size: 0.85rem;
    }
    .mock-btn {
        width: 100%;
        background: #2A2D35;
        color: #555;
        border: none;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    .stPlotlyChart {
        border-radius: 8px;
    }

    /* Fix expander icon overlapping label text */
    [data-testid="stExpander"] summary {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    [data-testid="stExpander"] summary span[data-testid="stExpanderToggleIcon"] {
        min-width: 1.5rem;
        flex-shrink: 0;
        overflow: hidden;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────

@st.cache_data
def run_query(query):
    engine = get_engine()
    df = pd.read_sql(query, engine)
    return df


# ── Sidebar navigation ──────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🚕 NYC Yellow Taxis</h2>
        <p>Trip Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["📋  Overview", "📊  Analytics", "🤖  AI Assistant", "🔮  Fare Predictor"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Data: TLC Trip Record · Jan 2024\nBuilt with Streamlit & Plotly")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if page == "📋  Overview":

    st.markdown("""
    <div class="page-header">
        <h1>Project Overview</h1>
        <p>End-to-end data pipeline &amp; analytics for NYC Yellow Taxi trips</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Data Source / Pipeline / What I Built ──
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        with st.container(border=True):
            st.markdown("##### 🗂️ Data Source")
            st.markdown(
                "**NYC Taxi & Limousine Commission**\n\n"
                "Yellow taxi trip records for **January 2024**, published by the "
                "TLC as part of their public trip record data program.\n\n"
                "- ~2.7 million trip records\n"
                "- 19 fields per trip\n"
                "- Pickup/dropoff times & locations\n"
                "- Fare, tips, tolls & payment type"
            )

    with c2:
        with st.container(border=True):
            st.markdown("##### ⚙️ Pipeline Architecture")
            st.markdown(
                "A modular **ETL pipeline** built in Python, loading into PostgreSQL:\n\n"
                "- :blue[**Extract**] — pull Parquet data from TLC\n"
                "- :green[**Transform**] — clean negatives, impossible distances, date outliers\n"
                "- :orange[**Load**] — idempotent upsert to PostgreSQL (replace strategy)\n\n"
                "Zone lookup table joined for human-readable location names."
            )

    with c3:
        with st.container(border=True):
            st.markdown("##### 🔍 What I Built")
            st.markdown(
                "Performed **exploratory data analysis** to surface quality issues, then "
                "encoded cleaning rules as modular transform functions.\n\n"
                "- Removed negative fares & impossible trip distances\n"
                "- Filtered date outliers (records from 2002 in a 2024 dataset)\n"
                "- Built interactive dashboard with Plotly\n"
                "- Added AI-powered natural language querying\n"
                "- LLM-generated KPI summaries"
            )

    st.space("large")

    # ── Key Findings ──
    st.markdown('<p class="section-label">Key Findings from EDA</p>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4, gap="medium")
    f1.metric("Peak Weekday Hour", "6 PM", border=True)
    f2.metric("Peak Weekend Hour", "4 PM", border=True)
    f3.metric("Top Revenue Zone", "JFK Airport", border=True)
    f4.metric("Dominant Payment", "Credit Card", border=True)

    st.space("medium")

    # ── Observations ──
    with st.container(border=True):
        st.markdown("##### Observations")
        st.markdown(
            "- Weekend riders stay out later — demand stays elevated past midnight compared to weekdays.\n"
            "- Weekday demand ramps at 5 AM (commuters), peaking at 6 PM (end of workday).\n"
            "- JFK Airport's $70 flat-rate fare to Manhattan drives outsized revenue despite moderate trip volume.\n"
            "- Revenue follows a weekly cycle — dips every 7 days then recovers. "
            "Cumulative growth is roughly linear, hitting the midpoint around day 15."
        )

    # ── About ──
    st.markdown("""
    <div class="about-card">
        <h3>Built By</h3>
        <div class="about-name">Jayesh Agrawal</div>
        <div class="about-links">
            <a href="https://github.com/jayesh122003" target="_blank">GitHub</a>
            <a href="https://www.linkedin.com/in/jayesh-agrawal-32b5a9238" target="_blank">LinkedIn</a>
        </div>
        <p class="about-note">
            All data engineering (ETL pipeline, SQL queries, EDA) and AI features (text-to-SQL, KPI summaries)
            built independently.<br>
            Dashboard styling assisted by Claude Code — currently building a custom dashboard framework from scratch.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📊  Analytics":

    kpi_df = run_query("""
        SELECT
            COUNT(*) as total_trips,
            ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
            ROUND(AVG(total_amount)::numeric, 2) as avg_fare,
            ROUND((SUM(total_amount)/SUM(trip_distance))::numeric, 2) as revenue_per_mile
        FROM taxi_trips
    """)

    hourly_df = run_query("""
        WITH base AS (
            SELECT EXTRACT(HOUR FROM tpep_pickup_datetime) as hour,
                CASE WHEN (EXTRACT(DOW FROM tpep_pickup_datetime) IN (0,6)) THEN 'Weekend' ELSE 'Weekday' END as day_type
            FROM taxi_trips
        ),
        grouped AS (
            SELECT hour, day_type, COUNT(*) as trip_count FROM base GROUP BY hour, day_type
        )
        SELECT hour, day_type,
            CASE WHEN day_type = 'Weekend' THEN trip_count / 2 ELSE trip_count / 5 END as avg_daily_trips
        FROM grouped ORDER BY hour
    """)

    top10_pz_df = run_query("""
        SELECT CAST(pulocationid AS TEXT) as pulocationid, COUNT(*) AS total_trips,
               ROUND(SUM(total_amount)::numeric, 2) as total_sales, zone_lookup."Zone"
        FROM taxi_trips JOIN zone_lookup ON pulocationid = "LocationID"
        GROUP BY CAST(pulocationid AS TEXT), zone_lookup."Zone"
        ORDER BY total_sales DESC LIMIT 10;
    """)

    cum_rev_df = run_query("""
        WITH day_info AS (
            SELECT total_amount, EXTRACT(DAY FROM tpep_dropoff_datetime) as day_of_month FROM taxi_trips
        ),
        revenue_per_day AS (
            SELECT day_of_month, SUM(total_amount) as daily_revenue
            FROM day_info GROUP BY day_of_month ORDER BY day_of_month ASC
        )
        SELECT day_of_month, daily_revenue,
               SUM(daily_revenue) OVER (ORDER BY day_of_month) as cumulative_daily_revenue
        FROM revenue_per_day;
    """)

    payment_df = run_query("""
        SELECT payment_type, SUM(total_amount) as total_revenue, COUNT(*) as total_trips,
        CASE WHEN payment_type = '1' THEN 'Credit Card' WHEN payment_type = '2' THEN 'Cash'
             WHEN payment_type = '3' THEN 'No Charge' WHEN payment_type = '4' THEN 'Dispute'
        END as payment_label
        FROM taxi_trips GROUP BY payment_type, payment_label ORDER BY payment_type
    """)

    # ── Header ──
    st.markdown("""
    <div class="page-header">
        <h1>Analytics</h1>
        <p>Trip metrics and revenue breakdown for January 2024</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards ──
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    k1.metric("Total Trips", f"{kpi_df['total_trips'][0]:,}", border=True)
    k2.metric("Total Revenue", f"${kpi_df['total_revenue'][0]:,.0f}", border=True)
    k3.metric("Avg Fare", f"${kpi_df['avg_fare'][0]:,.2f}", border=True)
    k4.metric("Revenue / Mile", f"${kpi_df['revenue_per_mile'][0]:,.2f}", border=True)

    st.space("large")

    # ── Row 1: Hourly Demand + Top Zones ──
    st.markdown('<p class="section-label">Demand & Geography</p>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="medium")

    with col_left:
        with st.container(border=True):
            st.markdown("**Trips by Hour of Day**")
            st.caption("Average daily trips — weekday vs weekend")

            weekday_h = hourly_df[hourly_df['day_type'] == 'Weekday'].sort_values('hour')
            weekend_h = hourly_df[hourly_df['day_type'] == 'Weekend'].sort_values('hour')

            fig_hourly = go.Figure()
            fig_hourly.add_trace(go.Scatter(
                x=weekend_h['hour'], y=weekend_h['avg_daily_trips'],
                name='Weekend', fill='tozeroy', mode='lines',
                line=dict(color=ACCENT_BLUE, width=2.5),
                fillcolor='rgba(96,165,250,0.25)',
            ))
            fig_hourly.add_trace(go.Scatter(
                x=weekday_h['hour'], y=weekday_h['avg_daily_trips'],
                name='Weekday', fill='tozeroy', mode='lines',
                line=dict(color=YELLOW, width=2.5),
                fillcolor='rgba(247,201,72,0.25)',
            ))
            fig_hourly.update_layout(**PLOTLY_LAYOUT, height=380)
            fig_hourly.update_xaxes(dtick=2)
            st.plotly_chart(fig_hourly, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown("**Top 10 Pickup Zones**")
            st.caption("By total revenue generated")

            top10_sorted = top10_pz_df.sort_values('total_sales', ascending=True)
            fig_zones = px.bar(
                top10_sorted, x='total_sales', y='Zone', orientation='h',
                labels={'total_sales': 'Revenue ($)', 'Zone': ''},
                color_discrete_sequence=[YELLOW],
            )
            fig_zones.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False)
            fig_zones.update_yaxes(type='category')
            fig_zones.update_traces(marker=dict(cornerradius=4))
            st.plotly_chart(fig_zones, use_container_width=True)

        st.markdown(
            '<p class="insight-caption">JFK Airport commands a $70 flat rate to/from Manhattan, '
            'driving significantly higher revenue than other zones.</p>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Row 2: Daily Revenue + Payment Breakdown ──
    st.markdown('<p class="section-label">Revenue & Payments</p>', unsafe_allow_html=True)

    col_left2, col_right2 = st.columns([3, 2], gap="medium")

    with col_left2:
        with st.container(border=True):
            st.markdown("**Daily Revenue Trend**")
            st.caption("Daily revenue (bars) and cumulative total (line) — January 2024")

            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(
                x=cum_rev_df['day_of_month'], y=cum_rev_df['daily_revenue'],
                name='Daily Revenue', marker_color=YELLOW_DIM, marker_cornerradius=4, opacity=0.7,
            ))
            fig_rev.add_trace(go.Scatter(
                x=cum_rev_df['day_of_month'], y=cum_rev_df['cumulative_daily_revenue'],
                name='Cumulative Revenue', line=dict(color=YELLOW, width=3), yaxis='y2',
            ))
            rev_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
            fig_rev.update_layout(
                **rev_layout, height=380, barmode='overlay',
                yaxis=dict(title='Daily Revenue ($)', gridcolor='#2A2D35', zerolinecolor='#2A2D35'),
                yaxis2=dict(title='Cumulative ($)', overlaying='y', side='right',
                            gridcolor='rgba(0,0,0,0)', zerolinecolor='rgba(0,0,0,0)'),
                xaxis=dict(title='Day of Month', dtick=2, gridcolor='#2A2D35', zerolinecolor='#2A2D35'),
            )
            st.plotly_chart(fig_rev, use_container_width=True)

        st.markdown(
            '<p class="insight-caption">Weekly pattern visible — revenue dips every 7 days then recovers. '
            'Cumulative growth is roughly linear, reaching the midpoint around day 15.</p>',
            unsafe_allow_html=True,
        )

    with col_right2:
        with st.container(border=True):
            st.markdown("**Payment Breakdown**")
            st.caption("Revenue share by payment method")

            fig_pay = px.pie(
                payment_df, names='payment_label', values='total_revenue',
                color_discrete_sequence=[YELLOW, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED],
                hole=0.5,
            )
            pay_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('legend',)}
            fig_pay.update_layout(
                **pay_layout, height=380,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED, size=11),
                            orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            )
            fig_pay.update_traces(
                textinfo='percent+label', textfont_size=12, textfont_color=TEXT,
                marker=dict(line=dict(color=DARK_BG, width=2)),
            )
            st.plotly_chart(fig_pay, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🤖  AI Assistant":

    from llm import generate_kpi_summary, text_to_sql

    st.markdown("""
    <div class="page-header">
        <h1>AI Assistant</h1>
        <p>AI-powered insights and natural language data exploration</p>
    </div>
    """, unsafe_allow_html=True)

    tab_insight, tab_query = st.tabs(["💡 KPI Insights", "💬 Ask the Data"])

    # ── Tab 1: AI Insight ──
    with tab_insight:
        st.space("small")

        with st.container(border=True):
            st.markdown("##### How it works")
            st.markdown(
                "Generates a concise executive summary by feeding the dashboard's KPIs, peak hours, "
                "top zones, and payment mix into an LLM. The model identifies patterns and surfaces "
                "actionable takeaways you might miss scanning charts alone."
            )

        st.space("small")

        kpi_df = run_query("""
            SELECT COUNT(*) as total_trips,
                   ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
                   ROUND(AVG(total_amount)::numeric, 2) as avg_fare,
                   ROUND((SUM(total_amount)/SUM(trip_distance))::numeric, 2) as revenue_per_mile
            FROM taxi_trips
        """)
        hourly_df = run_query("""
            WITH base AS (
                SELECT EXTRACT(HOUR FROM tpep_pickup_datetime) as hour,
                    CASE WHEN (EXTRACT(DOW FROM tpep_pickup_datetime) IN (0,6)) THEN 'Weekend' ELSE 'Weekday' END as day_type
                FROM taxi_trips
            ),
            grouped AS (
                SELECT hour, day_type, COUNT(*) as trip_count FROM base GROUP BY hour, day_type
            )
            SELECT hour, day_type,
                CASE WHEN day_type = 'Weekend' THEN trip_count / 2 ELSE trip_count / 5 END as avg_daily_trips
            FROM grouped ORDER BY hour
        """)
        top10_pz_df = run_query("""
            SELECT CAST(pulocationid AS TEXT) as pulocationid, COUNT(*) AS total_trips,
                   ROUND(SUM(total_amount)::numeric, 2) as total_sales, zone_lookup."Zone"
            FROM taxi_trips JOIN zone_lookup ON pulocationid = "LocationID"
            GROUP BY CAST(pulocationid AS TEXT), zone_lookup."Zone"
            ORDER BY total_sales DESC LIMIT 10;
        """)
        payment_df = run_query("""
            SELECT payment_type, SUM(total_amount) as total_revenue, COUNT(*) as total_trips,
            CASE WHEN payment_type = '1' THEN 'Credit Card' WHEN payment_type = '2' THEN 'Cash'
                 WHEN payment_type = '3' THEN 'No Charge' WHEN payment_type = '4' THEN 'Dispute'
            END as payment_label
            FROM taxi_trips GROUP BY payment_type, payment_label ORDER BY payment_type
        """)

        weekday_df = hourly_df[hourly_df['day_type'] == 'Weekday']
        weekend_df = hourly_df[hourly_df['day_type'] == 'Weekend']
        peak_hours = {
            "weekday": weekday_df.sort_values('avg_daily_trips', ascending=False).head(3).to_dict('records'),
            "weekend": weekend_df.sort_values('avg_daily_trips', ascending=False).head(3).to_dict('records'),
        }
        top_zones = top10_pz_df[['Zone', 'total_sales']].to_dict('records')
        payment_breakdown = payment_df[['payment_label', 'total_revenue']].to_dict('records')

        if st.button("Generate KPI Summary", use_container_width=True):
            with st.spinner("Analyzing data..."):
                summary = generate_kpi_summary(
                    total_trips=kpi_df['total_trips'][0],
                    total_revenue=kpi_df['total_revenue'][0],
                    avg_fare=kpi_df['avg_fare'][0],
                    revenue_per_mile=kpi_df['revenue_per_mile'][0],
                    top_zones=top_zones,
                    payment_mix=payment_breakdown,
                    peak_hour=peak_hours,
                )
                with st.container(border=True):
                    clean = summary.replace('`', '').replace('$', r'\$')
                    st.markdown(f"##### AI Summary\n\n{clean}")

    # ── Tab 2: Ask the Data ──
    with tab_query:
        st.space("small")

        with st.container(border=True):
            st.markdown("##### How it works")
            st.markdown(
                "Type a question in plain English. The LLM translates it into SQL, runs it against "
                "the database, and auto-selects the best chart type to visualize the results."
            )

        st.space("small")

        schema_df = run_query("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        schema_str = schema_df.to_string(index=False)

        EXAMPLE_QUESTIONS = [
            "Average fare by hour of day",
            "Top 5 zones by trip count",
            "Revenue by payment type",
            "Busiest day of the month by revenue",
        ]

        def set_example(q):
            st.session_state.ask_input = q

        st.caption("TRY AN EXAMPLE")
        chip_cols = st.columns(len(EXAMPLE_QUESTIONS))
        for i, eq in enumerate(EXAMPLE_QUESTIONS):
            with chip_cols[i]:
                st.button(eq, key=f"chip_{i}", use_container_width=True,
                          on_click=set_example, args=(eq,))

        question = st.text_area(
            "Your question",
            placeholder="Or type your own question here...",
            height=100,
            key="ask_input",
        )

        if st.button("Run Query", use_container_width=True):
            active_question = question.strip()
            if not active_question:
                st.warning("Please enter a question first.")
            else:
                with st.spinner("Translating to SQL and querying..."):
                    response = text_to_sql(active_question, schema_str)

                if response['status'] == 'ok':
                    try:
                        sql = response['sql']
                        df = run_query(sql)
                        chart_type = response['chart']['type']
                        x = response['chart']['x']
                        y = response['chart']['y']
                        color = response['chart']['color']
                        title = response['chart']['title']

                        with st.container(border=True):
                            st.markdown(f"##### 📊 {title}")

                            fig = None
                            if chart_type == 'bar':
                                fig = px.bar(df, x=x, y=y, color=color, title=title,
                                             color_discrete_sequence=CHART_COLORS)
                            elif chart_type == 'line':
                                fig = px.line(df, x=x, y=y, color=color, title=title,
                                              color_discrete_sequence=CHART_COLORS)
                            elif chart_type == 'pie':
                                fig = px.pie(df, names=x, values=y, color=color, title=title,
                                             color_discrete_sequence=CHART_COLORS, hole=0.4)
                                fig.update_traces(
                                    textinfo='label+percent', textposition='outside',
                                    textfont_size=12, textfont_color=TEXT,
                                    marker=dict(line=dict(color=DARK_BG, width=2)),
                                )
                            elif chart_type == 'bar_horizontal':
                                fig = px.bar(df, x=y, y=x, orientation='h', color=color, title=title,
                                             color_discrete_sequence=CHART_COLORS)
                            elif chart_type == 'kpi_card':
                                st.metric(title, df[y][0], border=True)

                            if fig:
                                chart_height = 480 if chart_type == 'pie' else 420
                                base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('legend', 'margin')}
                                fig.update_layout(
                                    **base,
                                    height=chart_height,
                                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED, size=11)),
                                    margin=dict(l=40, r=40, t=60, b=40),
                                )
                                if chart_type in ('bar', 'bar_horizontal'):
                                    fig.update_traces(marker=dict(cornerradius=4))
                                st.plotly_chart(fig, use_container_width=True)

                        with st.expander("View raw data"):
                            st.dataframe(df, use_container_width=True)
                        with st.expander("View generated SQL"):
                            st.code(sql, language='sql')

                    except Exception as e:
                        st.error(f"Query failed: {str(e)}")
                        st.code(response.get('sql', ''), language='sql')

                elif response['status'] == 'clarify':
                    st.warning(response['question'])
                elif response['status'] == 'refuse':
                    st.error(response['message'])
                elif response['status'] == 'error':
                    st.error(response['message'])


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: FARE PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔮  Fare Predictor":

    st.markdown("""
    <div class="page-header">
        <h1>Fare Predictor</h1>
        <p>ML-powered fare estimation based on route and time</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="coming-soon-container">
        <div class="coming-soon-icon">🔮</div>
        <div class="coming-soon-badge">Coming Soon</div>
        <div class="coming-soon-title">Predictive Fare Estimation</div>
        <div class="coming-soon-desc">
            Enter a pickup zone, dropoff zone, and time of day — and get an estimated fare
            powered by a machine learning model trained on millions of historical taxi trips.
        </div>
        <div class="mock-form">
            <div class="mock-form-row">
                <div class="mock-field">📍 Pickup zone</div>
                <div class="mock-field">📍 Dropoff zone</div>
            </div>
            <div class="mock-form-row">
                <div class="mock-field">🕐 Time of day</div>
                <div class="mock-field">📅 Day of week</div>
            </div>
            <div class="mock-btn">Estimate Fare</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
