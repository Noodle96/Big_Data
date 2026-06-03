USE bigdata_lab;
SELECT
    year,
    month,
    COUNT(*) AS total_trips,
    AVG(trip_distance) AS avg_distance,
    AVG(total_amount) AS avg_total_amount
FROM taxi_yellow_raw
WHERE year = 2024
  AND month = 1
GROUP BY year, month;