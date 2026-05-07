import streamlit as st
import plotly.express as px
import pandas as pd 
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from etl.load import get_engine



st.title("NYC YELLOW TAXIS")



@st.cache_data
def run_query(query):
    engine = get_engine()
    df = pd.read_sql(query, engine)
    return df

# --- KPI Queries ---
kpi_df = run_query("""
    SELECT 
        COUNT(*) as total_trips,
        ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
        ROUND(AVG(total_amount)::numeric, 2) as avg_fare,
        ROUND((SUM(total_amount)/SUM(trip_distance))::numeric, 2) as revenue_per_mile
    FROM taxi_trips
""")

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Trips", f"{kpi_df['total_trips'][0]:,}")
col2.metric("Total Revenue", f"${kpi_df['total_revenue'][0]:,.2f}")
col3.metric("Avg Fare", f"${kpi_df['avg_fare'][0]:,.2f}")
col4.metric("Revenue per Mile", f"${kpi_df['revenue_per_mile'][0]:,.2f}")



# --- Hourly Demand Chart ---
hourly_df = run_query("""
    WITH base AS (
        SELECT 
            EXTRACT(HOUR FROM tpep_pickup_datetime) as hour,
            CASE 
                WHEN (EXTRACT(DOW FROM tpep_pickup_datetime) = 0 OR EXTRACT(DOW FROM tpep_pickup_datetime) = 6) THEN 'WEEKEND'
                ELSE 'WEEKDAY' 
            END as day_type
        FROM taxi_trips
    ),
    grouped AS (
        SELECT 
            hour,
            day_type,
            COUNT(*) as trip_count
        FROM base
        GROUP BY hour, day_type
    )
    SELECT 
        hour,
        day_type,
        CASE 
            WHEN day_type = 'WEEKEND' THEN trip_count / 2
            ELSE trip_count / 5
        END as avg_daily_trips
    FROM grouped
    ORDER BY hour
""")


weekday_df = hourly_df[hourly_df['day_type'] == 'WEEKDAY']
weekend_df = hourly_df[hourly_df['day_type'] == 'WEEKEND']
peak_weekday = weekday_df.sort_values('avg_daily_trips', ascending=False).head(3).to_dict('records')
peak_weekend = weekend_df.sort_values('avg_daily_trips', ascending=False).head(3).to_dict('records')
peak_hours = {"weekday": peak_weekday, "weekend": peak_weekend}


st.subheader("Trips by Hour of Day")
fig = px.line(hourly_df, x='hour', y='avg_daily_trips', color='day_type',
              labels={'hour': 'Hour of Day', 'avg_daily_trips': 'Number of Trips'})
st.plotly_chart(fig, use_container_width=True)


# --- Top 10 pickup zones chart --

top10_pz_df = run_query("""
    SELECT CAST(pulocationid AS TEXT) as pulocationid , COUNT(*) AS total_trips, ROUND(SUM(total_amount)::numeric,2) as total_sales, zone_lookup."Zone"
    FROM taxi_trips JOIN zone_lookup on pulocationid = "LocationID"
    GROUP BY CAST(pulocationid AS TEXT), zone_lookup."Zone"
    ORDER BY total_sales DESC
    LIMIT 10;
""")
top_zones = top10_pz_df[['Zone', 'total_sales']].to_dict('records')

st.subheader("Top 10 pickup zones")
fig = px.bar(top10_pz_df, x='total_sales', y='Zone',
            labels={'total_sales': 'Total Sales', 'Zone': 'Zones'},
            orientation='h')
fig.update_yaxes(type='category')
st.plotly_chart(fig)
st.caption("JFK Airport commands a $70 flat rate to/from Manhattan, driving significantly higher revenue than other zones.")


# -- -- 4. Daily Revenue with cumulative sum
st.subheader("DAILY REVENUE AND CUMULATIVE SUM FOR JAN 2024")

cum_rev_df = run_query("""
    WITH day_info as (SELECT
                        total_amount,
                        EXTRACT(DAY FROM tpep_dropoff_datetime) as day_of_month
                        FROM taxi_trips),

    revenue_per_day as (SELECT day_of_month ,SUM(total_amount) as daily_revenue 
                        FROM day_info
                        GROUP BY day_of_month
                        ORDER BY day_of_month ASC)

    SELECT day_of_month, daily_revenue, SUM(daily_revenue) OVER (ORDER BY day_of_month) as cumulative_daily_revenue
    FROM revenue_per_day;
""")

fig = px.line(cum_rev_df, x='day_of_month', y='cumulative_daily_revenue', labels={'cumulative_daily_revenue' : 'Cumulative Daily Revenue'})
fig.add_scatter(x=cum_rev_df['day_of_month'], y=cum_rev_df['daily_revenue'], 
                name='daily_revenue', yaxis='y2')
fig.update_layout(
    yaxis2=dict(overlaying='y', side='right', title='Daily Revenue')
)
st.plotly_chart(fig)

st.caption("We could see the weekly pattern - revnue going down every 7 days and increasing again. The cumulative sum is linear however and we reach half the revenue in 15days.")


# --- 5. Payment Breakdown 

payment_df = run_query("""
    SELECT payment_type, SUM(total_amount) as total_revenue, COUNT(*) as total_trips,
    CASE 
        WHEN payment_type = '1' THEN 'Credit Card'
        WHEN payment_type = '2' THEN 'Cash'
        WHEN payment_type = '3' THEN 'No Charge'
        WHEN payment_type = '4' THEN 'Dispute'
    END as payment_label
    FROM taxi_trips
    GROUP BY payment_type, payment_label
    ORDER BY payment_type   
""")

payment_breakdown = payment_df[['payment_label', 'total_revenue']].to_dict('records')

fig = px.pie(payment_df, names='payment_label', values='total_revenue')
st.plotly_chart(fig)

# Generate KIP summary --

from llm import generate_kpi_summary


st.subheader("AI Insight")
if st.button("Generate AI Insight"):
    with st.spinner("Generating insight..."):
        summary = generate_kpi_summary(
            total_trips=kpi_df['total_trips'][0],
            total_revenue=kpi_df['total_revenue'][0],
            avg_fare=kpi_df['avg_fare'][0],
            revenue_per_mile=kpi_df['revenue_per_mile'][0],
            top_zones=top_zones,
            payment_mix=payment_breakdown,
            peak_hour=peak_hours
        )
        st.markdown(summary.replace('`', ''))


from llm import text_to_sql

schema_df = run_query("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    ORDER BY table_name, ordinal_position
""")
schema_str = schema_df.to_string(index=False)


st.subheader("Database query")
question = st.text_input("Ask a question about the data")
if st.button("Ask"):
    with st.spinner("Working on it..."):
        response = text_to_sql(question, schema_str)
        if response['status'] == 'ok':
            try:
                query = response['sql']
                df = run_query(query)
                st.dataframe(df)
                chart_type = response['chart']['type']
                x = response['chart']['x']
                y = response['chart']['y']
                color = response['chart']['color']
                title = response['chart']['title']
                if chart_type == 'bar':
                    fig = px.bar(df, x=x, y=y, color=color, title=title)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == 'line':
                    fig = px.line(df, x=x, y=y, color=color, title=title)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == 'pie':
                    fig = px.pie(df, names=x, values=y, color=color, title=title)
                    st.plotly_chart(fig)
                elif chart_type == 'bar_horizontal':
                    fig = px.bar(df, x=y, y=x, orientation='h', color=color, title=title)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == 'kpi_card':
                    st.metric(label=title, value=df[y][0])
            except Exception as e:
                st.error(f"Query failed: {str(e)}")
                st.code(query, language='sql')
        elif response['status'] == 'clarify':
             st.warning(response['question'])
        elif response['status'] == 'refuse':
             st.error(response['message'])
        elif response['status'] == 'error':
             st.error(response['message'])
