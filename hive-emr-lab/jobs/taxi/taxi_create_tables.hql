SET hive.execution.engine=mr;

CREATE DATABASE IF NOT EXISTS bigdata_lab;

USE bigdata_lab;

DROP TABLE IF EXISTS taxi_yellow_raw;

CREATE EXTERNAL TABLE taxi_yellow_raw (
    VendorID BIGINT,
    tpep_pickup_datetime BIGINT,
    tpep_dropoff_datetime BIGINT,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    RatecodeID BIGINT,
    store_and_fwd_flag STRING,
    PULocationID BIGINT,
    DOLocationID BIGINT,
    payment_type BIGINT,
    fare_amount DOUBLE,
    extra DOUBLE,
    mta_tax DOUBLE,
    tip_amount DOUBLE,
    tolls_amount DOUBLE,
    improvement_surcharge DOUBLE,
    total_amount DOUBLE,
    congestion_surcharge DOUBLE,
    airport_fee DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT
)
STORED AS PARQUET
LOCATION '/datasets/taxi/yellow/raw';

MSCK REPAIR TABLE taxi_yellow_raw;

SHOW PARTITIONS taxi_yellow_raw;