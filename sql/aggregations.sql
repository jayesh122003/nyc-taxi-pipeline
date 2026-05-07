-- 1. Overall KPIs -- 
SELECT 
    Count(*) as Total_Trips,
    SUM(total_amount) as Total_Sales,
    ROUND(AVG(total_amount)::numeric,2) as Avg_Fare,
    ROUND(AVG(trip_distance)::numeric,2) as Avg_Distance
FROM taxi_trips;

-- 2. CALCULATING TOTAL TRIPS PER HOUR AND DIFFERENCE FROM PREVIOUS HOUR ---

WITH trips AS (
    SELECT 
    COUNT(*) as trip_count,
    EXTRACT(HOUR FROM tpep_dropoff_datetime) as hour_dropoff
    FROM taxi_trips
    GROUP BY hour_dropoff
    ORDER BY hour_dropoff
),
prev_trips AS (
    SELECT * , 
     LAG(trip_count, 1) OVER (ORDER BY hour_dropoff) as prev_hour_trips
    FROM trips )

SELECT trip_count, hour_dropoff,
    (trip_count - prev_hour_trips) as trip_count_difference
FROM prev_trips;


-- 3. Top 10 pickup zones by revenue --

--a. Checking Distinct Locations:

SELECT COUNT(DISTINCT pulocationid)
FROM taxi_trips;


--b. Ranking the top 10 pickup locations--
SELECT pulocationid , COUNT(*) AS total_trips, ROUND(SUM(total_amount)::numeric,2) as Total_Sales
FROM taxi_trips
GROUP BY pulocationid
ORDER BY Total_Sales DESC
LIMIT 10;

-- Zone 132 = JFK Airport (high revenue due to $70 flat rate)

--c. Ranking the bottom 10 pickup locations ---

SELECT pulocationid , COUNT(*) AS total_trips, ROUND(SUM(total_amount)::numeric,2) as Total_Sales
FROM taxi_trips
GROUP BY pulocationid
HAVING COUNT(*) >= (SELECT COUNT(*)/(SELECT COUNT(DISTINCT pulocationid) FROM taxi_trips) FROM taxi_trips)
ORDER BY Total_Sales ASC
LIMIT 10;

-- d. Calculating Average Trip per pickup location

SELECT COUNT(*)/(SELECT COUNT(DISTINCT pulocationid) FROM taxi_trips) as avg_trips
FROM taxi_trips;

---East Harlem has the lowest revenue despite above-average trip volume

-- 4. Revenue by day of week with cumulative sum

WITH week_info as (SELECT
                    total_amount,
                    EXTRACT(DAY FROM tpep_dropoff_datetime) as day_of_week
                FROM taxi_trips),

revenue_per_week as (SELECT day_of_week ,SUM(total_amount) as daily_revenue 
                    FROM week_info
                    GROUP BY day_of_week
                    ORDER BY day_of_week ASC)

SELECT day_of_week, daily_revenue, SUM(daily_revenue) OVER (ORDER BY day_of_week) as cumulative_daily_revenue
FROM revenue_per_week;

-- When i run the query, i see the demand is constant throughtout the month. We already reach half the total revenue in half the month. 


-- 5. Revenue per mile

SELECT SUM(total_amount)/SUM(trip_distance) as revenue_per_mile
FROM taxi_trips;

-- 6. Average tip percentage (I used fare_amount as the base because tips are a reward for service, not for government surcharges the driver doesn't control.)

SELECT ROUND((AVG(tip_amount/fare_amount)*100)::numeric, 2) as avg_tip
FROM taxi_trips
WHERE fare_amount>0;

-- 7. Payment Type Breakdown ----

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