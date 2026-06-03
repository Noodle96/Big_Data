USE bigdata_lab;
SELECT
    year,
    month,
    COUNT(*) AS total_trips
FROM taxi_yellow_raw
GROUP BY year, month
ORDER BY year, month;