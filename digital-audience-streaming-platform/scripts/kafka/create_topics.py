"""Crea los topics de Kafka declarados en topics.yaml.

No usa el CLI kafka-topics.sh (no hace falta SSH a ningún broker ni tener
Kafka instalado localmente) -- habla el protocolo de Kafka directamente vía
kafka-python, igual que el simulador de agentes. Corre desde cualquier
máquina con acceso de red al puerto 9092 de los brokers.

Uso:

    python3 create_topics.py --bootstrap-servers 10.30.1.11:9092,10.30.1.12:9092,10.30.1.13:9092

Requiere: pip install kafka-python pyyaml
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

TOPICS_YAML_PATH: Path = Path(__file__).parent / "topics.yaml"


def load_topic_definitions(path: Path) -> list[dict[str, Any]]:
    """Lee y parsea topics.yaml."""
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return data["topics"]


def build_new_topics(definitions: list[dict[str, Any]]) -> list[NewTopic]:
    """Convierte las definiciones del YAML en objetos NewTopic de kafka-python."""
    new_topics: list[NewTopic] = []
    for topic in definitions:
        topic_config: dict[str, str] = {
            key: str(value) for key, value in topic.get("config", {}).items()
        }
        new_topics.append(
            NewTopic(
                name=topic["name"],
                num_partitions=topic["partitions"],
                replication_factor=topic["replication_factor"],
                topic_configs=topic_config,
            )
        )
    return new_topics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crea los topics definidos en topics.yaml.")
    parser.add_argument(
        "--bootstrap-servers",
        required=True,
        help=(
            "IPs:puerto de uno o más brokers, separadas por coma "
            "(ej: 10.30.1.11:9092,10.30.1.12:9092,10.30.1.13:9092)."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args: argparse.Namespace = parse_args()
    definitions: list[dict[str, Any]] = load_topic_definitions(TOPICS_YAML_PATH)
    new_topics: list[NewTopic] = build_new_topics(definitions)

    admin: KafkaAdminClient = KafkaAdminClient(
        bootstrap_servers=args.bootstrap_servers.split(","),
        client_id="create-topics-script",
    )

    print(f"Creando {len(new_topics)} topic(s) desde {TOPICS_YAML_PATH.name}...")
    try:
        admin.create_topics(new_topics=new_topics, validate_only=False)
        for topic in new_topics:
            print(
                f"  [OK] {topic.name} "
                f"(particiones={topic.num_partitions}, replicacion={topic.replication_factor})"
            )
    except TopicAlreadyExistsError:
        print("  Al menos un topic ya existía -- verificando de a uno...")
        for topic in new_topics:
            try:
                admin.create_topics(new_topics=[topic], validate_only=False)
                print(f"  [OK] {topic.name} creado")
            except TopicAlreadyExistsError:
                print(f"  [SKIP] {topic.name} ya existía, no se toca")
    finally:
        admin.close()


if __name__ == "__main__":
    main()
