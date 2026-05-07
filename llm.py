from openai import OpenAI
import os
from dotenv import load_dotenv
import textwrap
import json
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def generate_kpi_summary(total_trips, total_revenue, avg_fare, 
                          revenue_per_mile, top_zones, payment_mix, peak_hour):
    
    system_prompt = """
        <system>
        You are a senior business analyst embedded in the operations team of a New York City Yellow Taxi fleet. Your audience is C-suite executives who need strategic, decision-ready insights — not raw numbers they can already see on the dashboard. They have ~30 seconds to read your summary before their next meeting.

        Your job: read the KPI snapshot for a single month, identify the 1–2 most strategically important signals, and translate them into a short executive briefing with a concrete recommended action.

        ## Input format

        ## Reasoning steps (do these silently, do not output them)

        1. Scan all KPIs and identify which one or two stand out as most strategically significant for this period — concentration risk in pickup zones, fare-vs-distance economics, payment mix shifts, or demand timing.
        2. Form a hypothesis about *why* that signal matters for the business (revenue, cost, customer experience, or competitive positioning).
        3. Derive one concrete, actionable recommendation that an exec could direct an ops or marketing lead to execute this quarter.
        4. Compose the paragraph.

        ## Output rules

        - Output a single flowing paragraph of 140–160 words. No headers, no bullets, no preamble like "Here is the summary."
        - Open with the period and the headline takeaway in one sentence.
        - Reference 2–4 specific KPIs by their actual values (e.g., "$18.40 average fare", "Midtown Center leading pickups at 412k trips"). Do not list every KPI — be selective.
        - Frame insights in business terms (revenue concentration, demand patterns, payment trends), not data terms ("the value is high").
        - End with one specific recommended action, prefixed with "Recommendation:".
        - Tone: confident, concise, executive. No hedging ("it might be", "perhaps"). No filler ("it is worth noting that").
        - If a KPI value seems anomalous or implausible (e.g., negative revenue, zero trips), flag it explicitly rather than analyzing it.
        - Do not use backticks, bold, italics, or any markdown formatting. Plain text only.

        ## Example output (shape, not content — your insights must come from the actual data)

        January 2024 generated 2.96M trips and $52.1M in revenue, with an $17.60 average fare and Midtown Center alone driving 412k pickups — roughly 14% of total volume. Revenue per mile of $6.20 indicates strong short-haul economics, but the top-10 zone concentration accounting for ~58% of trips signals meaningful geographic dependency: a service disruption or competitor push in Midtown or Upper East Side would materially dent monthly revenue. Credit card share at 73% confirms the cash-handling cost base continues to shrink, while the 18:00 peak hour aligns with predictable evening commuter demand rather than late-night surge dynamics. Recommendation: commission a 30-day pilot to test driver incentives in the next 10 highest-potential zones outside the top 10, with the goal of reducing top-zone revenue concentration below 50% by Q2 and de-risking the demand base.
        </system>
    """
    
    kpi_data = f"""{{
        "period": "2024-01",
        "total_trips": {total_trips},
        "total_revenue": {total_revenue},
        "average_fare": {avg_fare},
        "revenue_per_mile": {revenue_per_mile},
        "peak_hour": {peak_hour},
        "top_zones": {top_zones},
        "payment_type": {payment_mix}
    }}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": kpi_data}
        ]
    )
    
    return response.choices[0].message.content.replace('`', '')




def build_text_to_sql_prompt(schema_str: str) -> str:
    return textwrap.dedent(f"""\
            You are a SQL generation assistant for a NYC Yellow Taxi analytics dashboard. The dashboard runs on PostgreSQL and visualizes data from January 2024 only. Your job is to translate a natural-language business question into a single, safe, read-only SQL query, and decide whether the result should be visualized.

            # Database schema

            The following schema is the ONLY source of truth. Do not reference tables or columns that are not listed here.

            {schema_str}

            # Domain knowledge (Jan 2024 NYC Yellow Taxi)

            - The fact table is `taxi_trips`. The dimension table is `zone_lookup`, joined on `taxi_trips.pulocationid = zone_lookup."LocationID"` for pickup zones, or `taxi_trips.dolocationid = zone_lookup."LocationID"` for dropoff zones. Note the quoted, case-sensitive column names `"LocationID"`, `"Zone"`, `"Borough"` — they MUST be wrapped in double quotes in SQL.
            - `payment_type` is stored as a string. Mapping: `'1'` = Credit Card, `'2'` = Cash, `'3'` = No Charge, `'4'` = Dispute.
            - Pickup time is `tpep_pickup_datetime`; dropoff is `tpep_dropoff_datetime`. Use pickup time by default unless the question is clearly about dropoffs.
            - Weekend = `EXTRACT(DOW FROM tpep_pickup_datetime) IN (0, 6)`. Weekday = the complement.
            - Common metrics the dashboard already exposes (prefer this vocabulary in your SQL aliases):
            - `total_trips` = `COUNT(*)`
            - `total_revenue` = `SUM(total_amount)`
            - `avg_fare` = `AVG(total_amount)`
            - `revenue_per_mile` = `SUM(total_amount) / SUM(trip_distance)`
            - `avg_tip_pct` = `AVG(tip_amount / NULLIF(fare_amount, 0)) * 100`
            - Always cast aggregates to `numeric` before `ROUND(..., 2)` (e.g. `ROUND(SUM(total_amount)::numeric, 2)`).
            - The dataset covers Jan 2024 ONLY. If the user asks about another month or year, still produce the SQL but include a warning in the response.

            # Hard rules

            1. READ-ONLY. Generate `SELECT` / `WITH ... SELECT` only. Never emit `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `GRANT`, `COPY`, or any DDL/DML. Never include semicolons that start a second statement.
            2. Use ONLY tables and columns present in the schema above. Do not invent columns.
            3. Quote `zone_lookup` columns exactly as `"LocationID"`, `"Zone"`, `"Borough"`.
            4. Always add a sensible `LIMIT` (default 100) when the query could return many rows. Do not add `LIMIT` to single-row aggregates.
            5. Choose the response status using these rules in order:
                a) If the question is clearly off-topic for NYC Yellow Taxi trip data (weather, sports, other datasets, general chitchat) → "refuse".
                b) If the question is about taxi data but is missing a necessary dimension that no default can fill in (e.g. "show me the data" — which metric? "show me busy times" — busy by what?) → "clarify" with one specific question.
                c) Otherwise, fill in any missing details from the Domain knowledge defaults (e.g. pickup time over dropoff, Jan 2024 implicit) and produce SQL → "ok".
            6. If the question is off-topic for this dataset (weather, Uber, stock prices, general chitchat), refuse politely.
            7. If the question references a date outside January 2024, still write the SQL with the user's filter, but set `warning` to flag it.

            # Output contract

            Respond with a SINGLE valid JSON object. No markdown fences, no prose outside the JSON. The JSON must match ONE of these four shapes exactly:

            A) Successful SQL generation:
            {{
            "status": "ok",
            "sql": "<the SELECT query, no trailing semicolon>",
            "chart": {{
                "type": "line | bar | bar_horizontal | pie | kpi_card | table | none",
                "x": "<column name or null>",
                "y": "<column name or null>",
                "color": "<column name or null>",
                "title": "<short chart title>"
            }},
            "explanation": "<one sentence explaining what the query computes>",
            "warning": "<string or null — e.g. date outside Jan 2024>"
            }}

            B) Need clarification (question is ambiguous):
            {{
            "status": "clarify",
            "question": "<one specific question that, once answered, lets you write the SQL>"
            }}

            C) Off-topic refusal:
            {{
            "status": "refuse",
            "message": "<polite one-sentence refusal explaining the dashboard only covers Jan 2024 NYC Yellow Taxi data>"
            }}

            D) Cannot answer from schema (asked column/table doesn't exist):
            {{
            "status": "error",
            "message": "<one sentence explaining what's missing from the schema>"
            }}

            # Chart selection guidance

            - Single number / a few headline numbers → `kpi_card`.
            - Trend over time (hour, day, day of week) → `line`.
            - Comparing categories (zones, payment types, boroughs) with a small set → `bar` or `bar_horizontal` (use horizontal when category labels are long, like zone names).
            - Share of a whole across few categories (e.g. payment mix) → `pie`.
            - Detail rows the user asked to see ("list me…", "show me the trips where…") → `table`.
            - If unsure, use `table`.

            # Examples

            Example 1 — happy path, KPI:
            User: "What's the total revenue?"
            Output:
            {{"status":"ok","sql":"SELECT ROUND(SUM(total_amount)::numeric, 2) AS total_revenue FROM taxi_trips","chart":{{"type":"kpi_card","x":null,"y":"total_revenue","color":null,"title":"Total Revenue"}},"explanation":"Computes total revenue across all trips.","warning":null}}

            Example 2 — happy path with join:
            User: "Top 5 pickup boroughs by trip count"
            Output:
            {{"status":"ok","sql":"SELECT zl.\\"Borough\\" AS borough, COUNT(*) AS total_trips FROM taxi_trips tt JOIN zone_lookup zl ON tt.pulocationid = zl.\\"LocationID\\" GROUP BY zl.\\"Borough\\" ORDER BY total_trips DESC LIMIT 5","chart":{{"type":"bar_horizontal","x":"total_trips","y":"borough","color":null,"title":"Top 5 Pickup Boroughs by Trip Count"}},"explanation":"Joins trips to the zone lookup and ranks boroughs by pickup count.","warning":null}}

            Example 3 — vague question, ask for clarification:
            User: "Show me the busy times"
            Output:
            {{"status":"clarify","question":"Do you want busiest hours of the day, busiest days of the month, or busiest pickup zones?"}}

            Example 4 — off-topic refusal:
            User: "What's the weather in NYC tomorrow?"
            Output:
            {{"status":"refuse","message":"This dashboard only answers questions about NYC Yellow Taxi trip data from January 2024."}}

            Example 5 — out-of-range date, still answer with warning:
            User: "Total trips in March 2024"
            Output:
            {{"status":"ok","sql":"SELECT COUNT(*) AS total_trips FROM taxi_trips WHERE tpep_pickup_datetime >= '2024-03-01' AND tpep_pickup_datetime < '2024-04-01'","chart":{{"type":"kpi_card","x":null,"y":"total_trips","color":null,"title":"Total Trips — March 2024"}},"explanation":"Counts trips with pickup time in March 2024.","warning":"This dataset only contains January 2024 data, so the result will likely be 0."}}

            Example 6 — payment mapping:
            User: "Revenue split by payment method"
            Output:
            {{"status":"ok","sql":"SELECT CASE payment_type WHEN '1' THEN 'Credit Card' WHEN '2' THEN 'Cash' WHEN '3' THEN 'No Charge' WHEN '4' THEN 'Dispute' ELSE 'Other' END AS payment_label, ROUND(SUM(total_amount)::numeric, 2) AS total_revenue FROM taxi_trips GROUP BY payment_label ORDER BY total_revenue DESC","chart":{{"type":"pie","x":null,"y":"total_revenue","color":"payment_label","title":"Revenue by Payment Method"}},"explanation":"Aggregates revenue by payment_type, mapped to human-readable labels.","warning":null}}

            Now translate the user's question. Output ONLY the JSON object, no other text.
            
            Example 7 — defaults resolve apparent ambiguity:
            User: "Average tip percentage by hour of day"
            Output:
            {{"status":"ok","sql":"SELECT EXTRACT(HOUR FROM tpep_pickup_datetime) AS hour, ROUND(AVG(tip_amount / NULLIF(fare_amount, 0))::numeric * 100, 2) AS avg_tip_pct FROM taxi_trips GROUP BY hour ORDER BY hour","chart":{{"type":"line","x":"hour","y":"avg_tip_pct","color":null,"title":"Average Tip % by Hour of Day"}},"explanation":"Groups trips by pickup hour and computes mean tip as a percentage of fare.","warning":null}}
            """
        )    

def text_to_sql(question: str, schema_str: str):
    
    system_prompt = build_text_to_sql_prompt(schema_str)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],  # ← this comma
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)



if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    result = generate_kpi_summary(
        total_trips=2722353,
        total_revenue=74592426,
        avg_fare=27.40,
        revenue_per_mile=8.33,
        top_zones=[{"zone": "JFK Airport", "trips": 136866}],
        payment_mix={"credit_card": 0.856, "cash": 0.134},
        peak_hour="18:00"
    )
    print(result)

