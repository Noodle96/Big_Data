from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    count,
    when
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_PATH: str = "s3://bigdata-russell-academy/datasets/taxi/yellow/"


# ============================================================
# CREAR SPARK SESSION
#
# Input:
#   Ninguno
#
# Output:
#   SparkSession lista para ejecutar el análisis
# ============================================================

def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Taxi Quality Report")
        .getOrCreate()
    )


# ============================================================
# LEER DATASET DE TAXIS
#
# Input:
#   Dataset Parquet particionado por:
#       year=2023/month=01
#       year=2023/month=02
#       ...
#       year=2024/month=12
#
# Output:
#   DataFrame con todos los viajes
# ============================================================

def read_taxi_dataset(
    spark: SparkSession
) -> DataFrame:

    return spark.read.parquet(INPUT_PATH)


# ============================================================
# REPORTE GENERAL DE CALIDAD
#
# Input:
#   Dataset completo
#
# Output:
#   Conteo de:
#       - filas totales
#       - distancias negativas
#       - montos negativos
#       - valores nulos
# ============================================================

def build_quality_report(
    df: DataFrame
) -> DataFrame:

    return df.select(

        count("*").alias("total_rows"),

        count(
            when(col("trip_distance") < 0, True)
        ).alias("trip_distance_negative"),

        count(
            when(col("fare_amount") < 0, True)
        ).alias("fare_amount_negative"),

        count(
            when(col("total_amount") < 0, True)
        ).alias("total_amount_negative"),

        count(
            when(col("trip_distance").isNull(), True)
        ).alias("trip_distance_null"),

        count(
            when(col("fare_amount").isNull(), True)
        ).alias("fare_amount_null"),

        count(
            when(col("total_amount").isNull(), True)
        ).alias("total_amount_null")
    )


# ============================================================
# EJEMPLOS DE VIAJES CON FARE NEGATIVO
#
# Objetivo:
#   Inspeccionar registros sospechosos.
#
# Input:
#   Dataset completo
#
# Output:
#   Primeros 20 registros con fare_amount < 0
# ============================================================

def show_negative_fares(
    df: DataFrame
) -> None:

    print("\n=== EJEMPLOS DE fare_amount NEGATIVO ===")

    df.filter(
        col("fare_amount") < 0
    ).select(
        "tpep_pickup_datetime",
        "fare_amount",
        "total_amount",
        "payment_type",
        "trip_distance",
        "year",
        "month"
    ).show(
        20,
        truncate=False
    )


# ============================================================
# EJEMPLOS DE VIAJES CON TOTAL NEGATIVO
#
# Objetivo:
#   Verificar si los montos totales negativos
#   son consistentes con los fares negativos.
#
# Input:
#   Dataset completo
#
# Output:
#   Primeros 20 registros con total_amount < 0
# ============================================================

def show_negative_totals(
    df: DataFrame
) -> None:

    print("\n=== EJEMPLOS DE total_amount NEGATIVO ===")

    df.filter(
        col("total_amount") < 0
    ).select(
        "tpep_pickup_datetime",
        "fare_amount",
        "total_amount",
        "payment_type",
        "trip_distance",
        "year",
        "month"
    ).show(
        20,
        truncate=False
    )


# ============================================================
# EJECUCIÓN PRINCIPAL
#
# Flujo:
#   1. Crear Spark Session
#   2. Leer dataset
#   3. Mostrar esquema
#   4. Ejecutar reporte de calidad
#   5. Mostrar ejemplos de anomalías
# ============================================================

def main() -> None:

    spark: SparkSession = create_spark_session()

    df: DataFrame = read_taxi_dataset(
        spark
    )

    print("\n=== ESQUEMA DEL DATASET ===")
    df.printSchema()

    print("\n=== REPORTE GENERAL DE CALIDAD ===")

    quality_report: DataFrame = build_quality_report(
        df
    )

    quality_report.show(
        truncate=False
    )

    show_negative_fares(df)

    show_negative_totals(df)

    spark.stop()


if __name__ == "__main__":
    main()