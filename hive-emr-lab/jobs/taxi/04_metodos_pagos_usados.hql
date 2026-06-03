USE bigdata_lab;
SELECT
    payment_type,
    COUNT(*) AS total_trips
FROM taxi_yellow_raw
GROUP BY payment_type
ORDER BY total_trips DESC;