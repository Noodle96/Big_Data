from pyspark.sql import SparkSession, DataFrame


CURATED_HDFS_PATH: str = "hdfs:///datasets/taxi/yellow_curated"


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Taxi Spark Total Trips Curated")
        .getOrCreate()
    )


def read_curated_dataset(spark: SparkSession) -> DataFrame:
    return spark.read.parquet(CURATED_HDFS_PATH)


def main() -> None:
    spark: SparkSession = create_spark_session()

    df: DataFrame = read_curated_dataset(spark)

    total_trips: int = df.count()

    print("\n=== TOTAL TRIPS CURATED ===")
    print(f"Total trips curated: {total_trips}")

    spark.stop()


if __name__ == "__main__":
    main()  