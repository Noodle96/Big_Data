import re
from typing import Iterable, Tuple

from pyspark import RDD
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import input_file_name, regexp_extract, col


INPUT_PATH: str = "hdfs:///datasets/wikipedia/raw"
OUTPUT_PATH: str = "hdfs:///outputs/spark/inverted-index"


def normalize_text(text: str) -> str:
    """
    Entrada:
        "Anarchism, Spark! Hadoop."

    Salida:
        "anarchism  spark  hadoop "
    """
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())


def row_to_document_line(row: object) -> Tuple[str, str]:
    """
    Entrada:
        Row(
            document_name="wiki_part_0001.txt",
            value="Anarchism is a political philosophy..."
        )

    Salida:
        (
            "wiki_part_0001.txt",
            "Anarchism is a political philosophy..."
        )
    """
    return row["document_name"], row["value"]


def line_to_word_document_pairs(
    record: Tuple[str, str]
) -> list[Tuple[str, str]]:
    """
    Entrada:
        (
            "wiki_part_0001.txt",
            "Hadoop Spark Hadoop"
        )

    Salida:
        [
            ("hadoop", "wiki_part_0001.txt"),
            ("spark", "wiki_part_0001.txt"),
            ("hadoop", "wiki_part_0001.txt")
        ]

    Nota:
        Si la línea está vacía, devuelve [].
    """
    document_name, line = record

    if line is None or line.strip() == "":
        return []

    clean_text: str = normalize_text(line)

    return [
        (word, document_name)
        for word in clean_text.split()
        if word != ""
    ]


def document_to_set(pair: Tuple[str, str]) -> Tuple[str, set[str]]:
    """
    Entrada:
        ("hadoop", "wiki_part_0001.txt")

    Salida:
        ("hadoop", {"wiki_part_0001.txt"})
    """
    word, document_name = pair
    return word, {document_name}


def merge_document_sets(left: set[str], right: set[str]) -> set[str]:
    """
    Entrada:
        {"wiki_part_0001.txt"} + {"wiki_part_0003.txt"}

    Salida:
        {"wiki_part_0001.txt", "wiki_part_0003.txt"}
    """
    return left.union(right)


def format_result(record: Tuple[str, set[str]]) -> str:
    """
    Entrada:
        ("hadoop", {"wiki_part_0001.txt", "wiki_part_0003.txt"})

    Salida:
        "hadoop    wiki_part_0001.txt, wiki_part_0003.txt"
    """
    word, documents = record
    sorted_documents: list[str] = sorted(documents)

    return f"{word}\t{', '.join(sorted_documents)}"


def main() -> None:
    spark: SparkSession = (
        SparkSession.builder
        .appName("Spark Inverted Index RDD")
        .getOrCreate()
    )

    # Lee los archivos línea por línea.
    # No carga archivos completos en memoria.
    #
    # Entrada HDFS:
    #   /datasets/wikipedia/raw/wiki_part_0001.txt
    #   /datasets/wikipedia/raw/wiki_part_0002.txt
    #
    # Salida DataFrame:
    #   value = línea de texto
    #   file_path = ruta completa del archivo
    #   document_name = nombre del archivo
    lines_df: DataFrame = (
        spark.read.text(INPUT_PATH)
        .withColumn("file_path", input_file_name())
        .withColumn(
            "document_name",
            regexp_extract(col("file_path"), r"([^/]+)$", 1)
        )
    )

    # Convertimos DataFrame a RDD para trabajar con map y flatMap.
    #
    # Entrada:
    #   Row(document_name="wiki_part_0001.txt", value="Hadoop Spark")
    #
    # Salida:
    #   ("wiki_part_0001.txt", "Hadoop Spark")
    document_lines: RDD[Tuple[str, str]] = lines_df.rdd.map(
        lambda row: row_to_document_line(row)
    )

    # flatMap:
    # Cada línea genera muchos pares (palabra, documento).
    #
    # Entrada:
    #   ("wiki_part_0001.txt", "Hadoop Spark Hadoop")
    #
    # Salida:
    #   ("hadoop", "wiki_part_0001.txt")
    #   ("spark", "wiki_part_0001.txt")
    #   ("hadoop", "wiki_part_0001.txt")
    word_document_pairs: RDD[Tuple[str, str]] = document_lines.flatMap(
        lambda record: line_to_word_document_pairs(record)
    )

    # map:
    # Convertimos cada documento a set para luego unir documentos únicos.
    #
    # Entrada:
    #   ("hadoop", "wiki_part_0001.txt")
    #
    # Salida:
    #   ("hadoop", {"wiki_part_0001.txt"})
    word_document_sets: RDD[Tuple[str, set[str]]] = word_document_pairs.map(
        lambda pair: document_to_set(pair)
    )

    # reduceByKey:
    # Une todos los documentos donde aparece cada palabra.
    #
    # Entrada:
    #   ("hadoop", {"wiki_part_0001.txt"})
    #   ("hadoop", {"wiki_part_0002.txt"})
    #
    # Salida:
    #   ("hadoop", {"wiki_part_0001.txt", "wiki_part_0002.txt"})
    inverted_index: RDD[Tuple[str, set[str]]] = word_document_sets.reduceByKey(
        lambda left, right: merge_document_sets(left, right)
    )

    # map:
    # Convertimos el resultado a texto final.
    #
    # Entrada:
    #   ("hadoop", {"wiki_part_0001.txt", "wiki_part_0002.txt"})
    #
    # Salida:
    #   "hadoop    wiki_part_0001.txt, wiki_part_0002.txt"
    formatted_result: RDD[str] = inverted_index.map(
        lambda record: format_result(record)
    )

    formatted_result.saveAsTextFile(OUTPUT_PATH)

    spark.stop()


if __name__ == "__main__":
    main()