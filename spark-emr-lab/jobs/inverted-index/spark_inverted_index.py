import re
from operator import add
from typing import Iterable, Tuple

from pyspark import RDD, SparkConf, SparkContext


INPUT_PATH: str = "hdfs:///datasets/wikipedia/raw"
OUTPUT_PATH: str = "hdfs:///outputs/spark/inverted-index"


def normalize_line(line: str) -> str:
    """
    Entrada:
        "Hadoop, Spark! HIVE"

    Salida:
        "hadoop  spark  hive"
    """
    return re.sub(r"[^a-z0-9 ]", " ", line.lower())


def get_document_name(file_path: str) -> str:
    """
    Entrada:
        "hdfs://.../wiki_part_0001.txt"

    Salida:
        "wiki_part_0001.txt"
    """
    return file_path.split("/")[-1]


def line_to_word_document_pairs(record: Tuple[str, str]) -> list[Tuple[str, str]]:
    """
    Entrada:
        (
            "hdfs://.../wiki_part_0001.txt",
            "Hadoop Spark Hadoop"
        )

    Salida:
        [
            ("hadoop", "wiki_part_0001.txt"),
            ("spark", "wiki_part_0001.txt"),
            ("hadoop", "wiki_part_0001.txt")
        ]
    """
    file_path, line = record
    document_name: str = get_document_name(file_path)
    clean_line: str = normalize_line(line)

    return [
        (word, document_name)
        for word in clean_line.split()
        if word
    ]


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
        "hadoop\twiki_part_0001.txt, wiki_part_0003.txt"
    """
    word, documents = record
    sorted_documents: list[str] = sorted(documents)

    return f"{word}\t{', '.join(sorted_documents)}"


def main() -> None:
    conf: SparkConf = (
        SparkConf()
        .setAppName("Spark Inverted Index RDD")
    )

    sc: SparkContext = SparkContext(conf=conf)

    # wholeTextFiles:
    # Lee cada archivo como:
    # ("ruta_del_archivo", "contenido_completo")
    files: RDD[Tuple[str, str]] = sc.wholeTextFiles(INPUT_PATH)

    # flatMap:
    # (archivo, texto) -> múltiples pares:
    # ("hadoop", "wiki_part_0001.txt")
    word_document_pairs: RDD[Tuple[str, str]] = files.flatMap(
        lambda record: line_to_word_document_pairs(record)
    )

    # map:
    # ("hadoop", "wiki_part_0001.txt")
    # -> ("hadoop", {"wiki_part_0001.txt"})
    word_document_sets: RDD[Tuple[str, set[str]]] = word_document_pairs.map(
        lambda pair: (pair[0], {pair[1]})
    )

    # reduceByKey:
    # ("hadoop", [{"doc1"}, {"doc2"}])
    # -> ("hadoop", {"doc1", "doc2"})
    inverted_index: RDD[Tuple[str, set[str]]] = word_document_sets.reduceByKey(
        lambda left, right: merge_document_sets(left, right)
    )

    # map:
    # ("hadoop", {"doc1", "doc2"})
    # -> "hadoop\tdoc1, doc2"
    formatted_result: RDD[str] = inverted_index.map(
        lambda record: format_result(record)
    )

    formatted_result.saveAsTextFile(OUTPUT_PATH)

    sc.stop()


if __name__ == "__main__":
    main()