import re
from operator import add
from typing import Iterable, Tuple

from pyspark import RDD, SparkConf, SparkContext


INPUT_PATH: str = "hdfs:///datasets/wikipedia/raw"
OUTPUT_PATH: str = "hdfs:///outputs/spark/wordcount"


def normalize_line(line: str) -> str:
    """
    Entrada:
        "Hadoop, Spark! HIVE"

    Salida:
        "hadoop  spark  hive"
    """
    return re.sub(r"[^a-z0-9 ]", " ", line.lower())


def split_words(line: str) -> list[str]:
    """
    Entrada:
        "hadoop spark hive"

    Salida:
        ["hadoop", "spark", "hive"]
    """
    return line.split()


def main() -> None:
    conf: SparkConf = (
        SparkConf()
        .setAppName("Spark WordCount RDD")
    )

    sc: SparkContext = SparkContext(conf=conf)

    lines: RDD[str] = sc.textFile(INPUT_PATH)

    # map:
    # "Hadoop, Spark!" -> "hadoop  spark "
    clean_lines: RDD[str] = lines.map(lambda line: normalize_line(line))

    # flatMap:
    # "hadoop spark" -> "hadoop", "spark"
    words: RDD[str] = clean_lines.flatMap(lambda line: split_words(line))

    # map:
    # "hadoop" -> ("hadoop", 1)
    word_pairs: RDD[Tuple[str, int]] = words.map(lambda word: (word, 1))

    # reduceByKey:
    # ("hadoop", [1, 1, 1]) -> ("hadoop", 3)
    word_counts: RDD[Tuple[str, int]] = word_pairs.reduceByKey(lambda a, b: a + b)

    # Salida:
    # hadoop    1532
    # spark     921
    word_counts.saveAsTextFile(OUTPUT_PATH)

    sc.stop()


if __name__ == "__main__":
    main()