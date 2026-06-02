from pathlib import Path
import random


OUTPUT_DIR: Path = Path("data/text-corpus/raw")

NUM_FILES: int = 16
TARGET_SIZE_MB: int = 2048
LINES_PER_BATCH: int = 5000

VOCABULARY: list[str] = [
    "hadoop", "hive", "hdfs", "mapreduce", "spark", "emr", "aws", "s3",
    "cluster", "master", "worker", "namenode", "datanode", "yarn",
    "resourcemanager", "nodemanager", "application", "container",
    "distributed", "parallel", "scalable", "storage", "compute", "pipeline",
    "batch", "streaming", "processing", "query", "analytics", "dataset",
    "table", "partition", "bucket", "schema", "metadata", "warehouse",
    "database", "column", "row", "record", "field", "format", "text",
    "parquet", "csv", "json", "orc", "compression", "snappy", "gzip",
    "sql", "hiveql", "select", "where", "group", "order", "join",
    "count", "sum", "avg", "min", "max", "distinct", "explode",
    "split", "regexp", "lower", "token", "word", "document", "index",
    "inverted", "wordcount", "frequency", "occurrence", "term",
    "search", "retrieval", "ranking", "result", "output", "input",
    "file", "block", "replication", "fault", "tolerance", "availability",
    "latency", "throughput", "memory", "cpu", "disk", "network",
    "resource", "execution", "runtime", "performance", "optimization",
    "cost", "cloud", "region", "instance", "node", "service", "log",
    "taxi", "trip", "pickup", "dropoff", "distance", "fare", "payment",
    "passenger", "yellow", "green", "zone", "location", "datetime",
    "hour", "month", "year", "driver", "route", "traffic", "city",
    "newyork", "analysis", "report", "dashboard", "visualization",
    "experiment", "laboratory", "comparison", "complexity", "scalability",
    "implementation", "algorithm", "mapper", "reducer", "shuffle",
    "sort", "aggregate", "filter", "transform", "load", "extract",
    "clean", "prepare", "validate", "inspect", "sample", "raw",
    "processed", "persistent", "temporary", "s3distcp", "academy",
    "learner", "lab", "infrastructure", "pulumi", "terraform", "ansible",
    "linux", "shell", "terminal", "command", "script", "notebook",
    "python", "java", "maven", "jar", "class", "package", "compile",
    "deploy", "destroy", "preview", "credential", "token", "session",
    "security", "permission", "role", "iam", "keypair", "ssh",
    "tunnel", "browser", "interface", "namenodeui", "yarnui", "history",
    "metastore", "external", "internal", "managed", "location",
    "serde", "delimiter", "line", "sentence", "paragraph", "corpus",
    "synthetic", "generated", "random", "repeat", "variable", "constant",
]


def generate_line(file_id: int) -> str:
    words: list[str] = random.choices(
        VOCABULARY,
        k=random.randint(8, 20),
    )

    return " ".join(words) + "\n"

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    target_total_bytes: int = TARGET_SIZE_MB * 1024 * 1024
    target_file_bytes: int = target_total_bytes // NUM_FILES

    print(f"Generating {NUM_FILES} files")
    print(f"Target total size: {TARGET_SIZE_MB} MB")
    print(f"Target per file: {target_file_bytes / (1024 * 1024):.2f} MB")

    for file_id in range(1, NUM_FILES + 1):
        file_path: Path = OUTPUT_DIR / f"doc_{file_id:04d}.txt"
        written: int = 0

        with file_path.open("w", encoding="utf-8") as file:
            while written < target_file_bytes:
                batch_lines: list[str] = [
                    generate_line(file_id)
                    for _ in range(LINES_PER_BATCH)
                ]

                content: str = "".join(batch_lines)
                file.write(content)
                written += len(content.encode("utf-8"))

        print(f"Created {file_path} ({written / (1024 * 1024):.2f} MB)")

    print("Done.")


if __name__ == "__main__":
    main()