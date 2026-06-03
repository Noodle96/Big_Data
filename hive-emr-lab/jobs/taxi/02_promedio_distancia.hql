USE bigdata_lab;
SELECT
    AVG(trip_distance) AS avg_trip_distance
FROM taxi_yellow_raw
WHERE trip_distance >= 0;