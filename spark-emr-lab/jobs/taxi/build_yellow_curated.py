from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col


RAW_PATH: str = "s3://bigdata-russell-academy/datasets/taxi/yellow/"
CURATED_PATH: str = "s3://bigdata-russell-academy/datasets/taxi/yellow_curated/"


def create_spark_session() -> SparkSession:
    """
    Output:
        SparkSession para ejecutar el ETL distribuido.
    """
    return (
        SparkSession.builder
        .appName("Build Yellow Taxi Curated")
        .getOrCreate()
    )


def read_raw_dataset(spark: SparkSession) -> DataFrame:
    """
    Input:
        S3 raw:
        s3://bigdata-russell-academy/datasets/taxi/yellow/

    Output:
        DataFrame con los viajes raw de 2023 y 2024.
    """
    return spark.read.parquet(RAW_PATH)


def build_curated_dataset(raw_df: DataFrame) -> DataFrame:
    """
    Input:
        DataFrame raw con registros válidos e inválidos.

    Reglas aplicadas:
        fare_amount >= 0
        total_amount >= 0
        tpep_dropoff_datetime >= tpep_pickup_datetime

    Output:
        DataFrame curated con registros consistentes para análisis.
    """
    curated_df: DataFrame = (
        raw_df
        .filter(col("fare_amount").isNotNull())
        .filter(col("total_amount").isNotNull())
        .filter(col("tpep_pickup_datetime").isNotNull())
        .filter(col("tpep_dropoff_datetime").isNotNull())
        .filter(col("fare_amount") >= 0)
        .filter(col("total_amount") >= 0)
        .filter(col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime"))
    )

    return curated_df


def show_etl_summary(raw_df: DataFrame, curated_df: DataFrame) -> None:
    """
    Input:
        raw_df: dataset original
        curated_df: dataset limpio

    Output:
        Métricas básicas del proceso ETL.
    """
    raw_count: int = raw_df.count()
    curated_count: int = curated_df.count()
    removed_count: int = raw_count - curated_count
    removed_percentage: float = (removed_count / raw_count) * 100

    print("\n=== RESUMEN DEL ETL CURATED ===")
    print(f"RAW rows: {raw_count}")
    print(f"CURATED rows: {curated_count}")
    print(f"REMOVED rows: {removed_count}")
    print(f"REMOVED percentage: {removed_percentage:.4f}%")


def write_curated_dataset(curated_df: DataFrame) -> None:
    """
    Input:
        DataFrame curated.

    Output:
        Dataset Parquet en S3, particionado por year y month:

        s3://bigdata-russell-academy/datasets/taxi/yellow_curated/
            year=2023/month=01/
            year=2023/month=02/
            ...
            year=2024/month=12/
    """
    (
        curated_df
        .write
        .mode("overwrite")
        .partitionBy("year", "month")
        .parquet(CURATED_PATH)
    )


def main() -> None:
    spark: SparkSession = create_spark_session()

    print("\n=== LEYENDO DATASET RAW ===")
    raw_df: DataFrame = read_raw_dataset(spark)

    print("\n=== CONSTRUYENDO DATASET CURATED ===")
    curated_df: DataFrame = build_curated_dataset(raw_df)

    show_etl_summary(raw_df, curated_df)

    print("\n=== ESCRIBIENDO DATASET CURATED EN S3 ===")
    write_curated_dataset(curated_df)

    print(f"\nDataset curated creado en: {CURATED_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()