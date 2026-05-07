payment_type:

1 = Credit card
2 = Cash
3 = No charge
4 = Dispute

RatecodeID:

1 = Standard rate
2 = JFK airport
3 = Newark airport
4 = Nassau/Westchester
5 = Negotiated fare
6 = Group ride

VendorID:

1 = Creative Mobile Technologies
2 = VeriFone Inc

#  EDA
I performed exploratory data analysis to identify data quality issues, then encoded those decisions as modular cleaning functions.
"I found negative fares, impossible trip distances, and dates going back to 2002 in a January 2024 dataset — all of which would corrupt downstream KPI calculations.


Findings & Cleaning Decisions:

Negative financial values — ~1.27% of rows had negative fare_amount, total_amount, etc. You cross-checked and found most of these had payment_type=4 (Dispute). Without a transaction ID to confirm refunds, you removed them all.
DateTime outliers — 18 rows had pickup/dropoff dates outside January 2024 (earliest was 2002-12-31). Removed.
Trip duration anomalies — 56 negative durations, 814 zero-duration trips, and 1,651 trips over 10 hours. All removed.
Passenger count issues — 31,465 rows with 0 passengers and 60 rows exceeding the legal limit of 6. Removed.
Trip distance problems — 60,371 rows with zero distance (of which 56,569 had positive fares — likely GPS failures), and 59 trips over 100 miles. Removed.
Null value pattern — 140,162 rows had nulls in the same 5 columns (passenger_count, RatecodeID, store_and_fwd_flag, congestion_surcharge, Airport_fee). These were already caught by your passenger_count > 0 filter.
Result: 242,271 rows removed (8.17%), leaving 2,722,353 clean rows.

The approach was methodical — you investigated each anomaly category independently, checked for correlations (like the dispute/negative-value link), and encoded each decision as a modular cleaning function for the ETL pipeline.

# load.py

df.tosql(id_exists="replace")...Why? because we want idempotency, and if we run a pipeline multiple times, we dont want the same data to be duplicated many times to our database


# Hourly demand chart characterized by weekday and weekend
1. The chart suggests that people are staying out late on the weekends
2. The demand on the weekday starts increasing at around 5am, suggesting people going on with there normal workday
3. For weekday, the peak is around 18, which is usually the time, when people get back from work
4. For weekends, the peak is around 16


# FOR LATER: 
It could have this predictive feature, where we could analyse the cost for a taxi ride, based on pickup and dropoff location and time of the day and a user can directly query it and get an answer
