from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, when


INPUT_PATH: str = "s3://bigdata-russell-academy/datasets/taxi/yellow/"


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Taxi Datetime Diagnosis")
        .getOrCreate()
    )


def read_dataset(spark: SparkSession) -> DataFrame:
    return spark.read.parquet(INPUT_PATH)


def show_datetime_quality(df: DataFrame) -> None:
    print("\n=== DIAGNÓSTICO DE FECHAS PICKUP/DROPOFF ===")

    df.select(
        count("*").alias("total_rows"),

        count(
            when(col("tpep_pickup_datetime").isNull(), True)
        ).alias("pickup_null"),

        count(
            when(col("tpep_dropoff_datetime").isNull(), True)
        ).alias("dropoff_null"),

        count(
            when(col("tpep_dropoff_datetime") < col("tpep_pickup_datetime"), True)
        ).alias("dropoff_before_pickup"),

        count(
            when(col("tpep_dropoff_datetime") == col("tpep_pickup_datetime"), True)
        ).alias("zero_duration_trips"),

        count(
            when(col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime"), True)
        ).alias("valid_datetime_order"),
    ).show(truncate=False)


def main() -> None:
    spark: SparkSession = create_spark_session()

    df: DataFrame = read_dataset(spark)

    show_datetime_quality(df)

    spark.stop()


if __name__ == "__main__":
    main()