USE bigdata_lab;

SELECT
    hour(from_unixtime(CAST(tpep_pickup_datetime / 1000000 AS BIGINT))) AS pickup_hour,
    COUNT(*) AS total_trips
FROM taxi_yellow_raw
GROUP BY hour(from_unixtime(CAST(tpep_pickup_datetime / 1000000 AS BIGINT)))
ORDER BY total_trips DESC;