# NYC Yellow Taxi Analytics Pipeline
🔗 [Live Dashboard](https://nyc-taxi-pipeline-itmmxawiwp7lsfsg5hzkmc.streamlit.app/)

## What is it?
An end-to-end data pipeline and analytics dashboard for NYC Yellow Taxi trip data (January 2024). Built with a modular ETL pipeline in Python, a PostgreSQL backend, and an interactive Streamlit dashboard. Features LLM-powered KPI summaries and natural language querying via Text-to-SQL.


## What I built?

### 1. Exploratory Data Analysis (Findings and Decisions):

**1.Negative Financial Values:** Observed around ~1.27% of rows had negative fare_amount, total_amount, etc. Cross-Checked to find out if they are related to any transaction ID,which might suggest reversals, but as there is no transaction ID, i concluded that it is misentry in the dataset and decided to remove these rows.
**2.Date-Time Problem:** Observed negative trip durations (dropoff time < pickup time>), trips over 10 hours (which is highly unlikely for a taxi ride), dates outside of january 2024, and all of these consisted of less than ~0.1% of the dataset. I decided to remove these rows as well
**3.Invalid Passenger Count** The legal limit for NYC Yellow Taxi is 6, and there were rows including passenger more than 6 and even 0. Decided to remove these rows.
**4.Trip Distance Problem:** ~2.04% of the dataset, had rows with trip_distance = 0. Zero Distance Trips corrupts the distance based KPIs. I also suspected outliers with trip distance exceeding 100miles, unrealistic for NYC taxi. Removed all these rows.
**5.Null Value Pattern:** 140,162 rows had nulls in the same 5 columns (passenger_count, RatecodeID, store_and_fwd_flag, congestion_surcharge, Airport_fee). These were already caught by passenger_count > 0 filter.
**Result:** Removed ~8.17% of the dataset, which included all the problematic rows and null values.


### 2. ETL Pipeline:

**1.Extract:** Extracted the data from https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet, downloaded it and loaded the raw data as a dataframe. Also downloaded taxi_zone_lookup.csv to look up the pickup and dropoff location IDs.  
**2. Transform:** Cleaned the data by applying all the findings in EDA. 
**3.Load:** Chose PostgreSQL as my main database, because it handles large database and complex queries well. Loaded both the trip data and zone lookup data into the database. 

### 3. SQL queries:

Find out what key metrics I wanna investigate on. 
1. KPIs includes Total Revenue, Total Trips, Average Fare and Revenue per mile. 
2. Top 10 Pickup zones by total revenue generate 
3. Daily Revenue Trend and Cumulative Daily Revenue. 
4. Payment Breakdown: Card, Cash, Dispute and No Charge

### 4. LLM integration:
*Used OpenAI API with model gpt-4o-mini, because it's cost effective and sufficient for the current use case.*

**1. Generating KPI summary:** Generates a summary and a business insight based on the KPIs.  The system prompt was well thought, so that the insights would be quick to read (140-160 words), would be impact and business driven. The prompt was engineered and put together with the help of Claude AI.
**2. Text to SQL:** User can ask complex queries related to the database in the text box and get response with chart if needed. I restricted queries to read-only SELECT statements to prevent any data modification. Here the prompt was also well engineered, which fed, domain knowledge, schema structure, and output contract to the API. Each response from the API is in json format which could be any of the four cases:
    1. OK: It returns an sql query and the type of chart.
    2. Clarify: If the user asked question is not clear - it gives a suggestion, as to what makes the question clear. 
    3. Refuse: If the question is off-topic.
    4. Error: If asked column or table doesnt exist. 
The prompt was written with the help of Claude AI after giving it a well thought procedure on how to write the prompt and the requirements that's needed. 

### 5. Dashboard:

All the KPIs, Charts and AI insight was built from scratch independently. Used Claude AI to design the dashboard.

### Tech Stack
Python, pandas, PostgreSQL, SQLAlchemy, Streamlit, Plotly, OpenAI API (gpt-4o-mini)


### How to Run Locally
1. Clone the repo
2. Create a virtual environment and install requirements
3. Add a `.env` file with your PostgreSQL and OpenAI credentials
4. Run `python etl/load.py` to populate the database
5. Run `streamlit run dashboard/app.py`


