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

# load.py

df.tosql(id_exists="replace")...Why? because we want idempotency, and if we run a pipeline multiple times, we dont want the same data to be duplicated many times to our database


# Hourly demand chart characterized by weekday and weekend
1. The chart suggests that people are staying out late on the weekends
2. The demand on the weekday starts increasing at around 5am, suggesting people going on with there normal workday
3. For weekday, the peak is around 18, which is usually the time, when people get back from work
4. For weekends, the peak is around 16


# FOR LATER: 
It could have this predictive feature, where we could analyse the cost for a taxi ride, based on pickup and dropoff location and time of the day and a user can directly query it and get an answer
