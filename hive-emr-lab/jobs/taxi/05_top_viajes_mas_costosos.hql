USE bigdata_lab;

SELECT
    year,
    month,
    from_unixtime(CAST(tpep_pickup_datetime / 1000000 AS BIGINT)) AS pickup_datetime,
    from_unixtime(CAST(tpep_dropoff_datetime / 1000000 AS BIGINT)) AS dropoff_datetime,
    trip_distance,
    fare_amount,
    tip_amount,
    tolls_amount,
    total_amount,
    payment_type
FROM taxi_yellow_raw
WHERE total_amount IS NOT NULL
ORDER BY total_amount DESC
LIMIT 20;