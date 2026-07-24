#!/usr/bin/env python3
"""
Crea (o verifica) los topics definidos en topics.yaml, usando las
herramientas CLI de Kafka (kafka-topics.sh).

Se ejecuta en la máquina cliente (kafka-client), donde ya está el
binario de Kafka instalado (mismo que en los brokers).

Uso:
    python3 create_topics.py --bootstrap-server 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092

Este script existe para que la creación de topics quede documentada y
sea reproducible, en vez de comandos sueltos ejecutados a mano y luego
olvidados.
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Falta PyYAML. Instala con: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

KAFKA_TOPICS_BIN = "kafka-topics.sh"
# Se asume que topics.yaml vive junto a este script (así se copian juntos
# por scp a la máquina cliente, que no tiene el resto del repositorio).
TOPICS_FILE = Path(__file__).resolve().parent / "topics.yaml"


def load_topics(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["topics"]


def create_topic(bootstrap_server: str, topic: dict) -> None:
    name = topic["name"]
    partitions = str(topic["partitions"])
    replication_factor = str(topic["replication_factor"])

    cmd = [
        KAFKA_TOPICS_BIN,
        "--create",
        "--if-not-exists",
        "--bootstrap-server", bootstrap_server,
        "--topic", name,
        "--partitions", partitions,
        "--replication-factor", replication_factor,
    ]

    for key, value in (topic.get("config") or {}).items():
        cmd += ["--config", f"{key}={value}"]

    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    describe_cmd = [
        KAFKA_TOPICS_BIN,
        "--describe",
        "--bootstrap-server", bootstrap_server,
        "--topic", name,
    ]
    print(f"\n$ {' '.join(describe_cmd)}")
    subprocess.run(describe_cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bootstrap-server",
        required=True,
        help="Lista de brokers, ej: 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092",
    )
    args = parser.parse_args()

    topics = load_topics(TOPICS_FILE)
    print(f"Topics definidos en {TOPICS_FILE}: {[t['name'] for t in topics]}")

    for topic in topics:
        create_topic(args.bootstrap_server, topic)


if __name__ == "__main__":
    main()
