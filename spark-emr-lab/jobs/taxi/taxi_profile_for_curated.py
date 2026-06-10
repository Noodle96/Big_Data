from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    count,
    min,
    max,
    avg,
    when
)

INPUT_PATH: str = "s3://bigdata-russell-academy/datasets/taxi/yellow/"

def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Taxi Profile For Curated")
        .getOrCreate()
    )


def read_dataset(
    spark: SparkSession
) -> DataFrame:

    return spark.read.parquet(INPUT_PATH)


def profile_numeric_column(
    df: DataFrame,
    column_name: str
) -> None:

    print(f"\n===== PERFIL DE {column_name} =====")

    df.select(
        count("*").alias("total_rows"),
        count(
            when(col(column_name).isNull(), True)
        ).alias("null_values"),
        count(
            when(col(column_name) < 0, True)
        ).alias("negative_values"),
        count(
            when(col(column_name) == 0, True)
        ).alias("zero_values"),
        min(column_name).alias("min_value"),
        max(column_name).alias("max_value"),
        avg(column_name).alias("avg_value")
    ).show(truncate=False)

def main() -> None:

    spark: SparkSession = create_spark_session()
    df: DataFrame = read_dataset(spark)
    profile_numeric_column(
        df,
        "trip_distance"
    )
    profile_numeric_column(
        df,
        "fare_amount"
    )
    profile_numeric_column(
        df,
        "total_amount"
    )
    spark.stop()


if __name__ == "__main__":
    main()