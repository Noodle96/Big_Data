#!/usr/bin/env python3
"""
Consumidor de eventos de e-commerce para el laboratorio de Kafka.

Se suscribe al topic indicado dentro de un consumer group y va imprimiendo
cada mensaje recibido (partición, offset, key, valor). Pensado para
ejecutarse una o varias veces en simultáneo con el mismo --group-id, para
demostrar el rebalanceo de particiones entre consumidores de un mismo grupo.

Uso (una sola instancia):
    python3 consumer.py --bootstrap-server 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092 \
        --group-id demo-group

Uso (demo de consumer group, en 2 terminales/SSH distintas, mismo --group-id):
    # Terminal A
    python3 consumer.py --bootstrap-server ... --group-id demo-group --consumer-name C1
    # Terminal B
    python3 consumer.py --bootstrap-server ... --group-id demo-group --consumer-name C2
"""

import argparse

from kafka import ConsumerRebalanceListener, KafkaConsumer

DEFAULT_TOPIC = "ecommerce-events"


class PrintingRebalanceListener(ConsumerRebalanceListener):
    """Imprime explícitamente cada vez que este consumer gana o pierde
    particiones, para que el rebalanceo del consumer group quede visible
    en pantalla en el momento exacto en que ocurre."""

    def __init__(self, name: str) -> None:
        self.name = name

    def on_partitions_revoked(self, revoked) -> None:
        if revoked:
            partitions = sorted(p.partition for p in revoked)
            print(f"[{self.name}] >>> REBALANCEO: se le quitan las particiones {partitions}")

    def on_partitions_assigned(self, assigned) -> None:
        partitions = sorted(p.partition for p in assigned)
        print(f"[{self.name}] >>> REBALANCEO: quedan asignadas las particiones {partitions}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-server", required=True, help="Lista de brokers, ej: 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092")
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--group-id", required=True, help="Consumer group id. Usa el MISMO valor en varias instancias para ver el rebalanceo.")
    parser.add_argument("--consumer-name", default="consumer", help="Solo para identificar los prints en pantalla, no es parte del protocolo de Kafka.")
    parser.add_argument("--from-beginning", action="store_true", help="Lee desde el offset más antiguo disponible en vez de solo mensajes nuevos.")
    args = parser.parse_args()

    consumer = KafkaConsumer(
        bootstrap_servers=args.bootstrap_server.split(","),
        group_id=args.group_id,
        auto_offset_reset="earliest" if args.from_beginning else "latest",
        enable_auto_commit=True,
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
        value_deserializer=lambda v: v.decode("utf-8"),
        consumer_timeout_ms=-1,
    )
    consumer.subscribe(topics=[args.topic], listener=PrintingRebalanceListener(args.consumer_name))

    print(f"[{args.consumer_name}] Conectado a {args.bootstrap_server}")
    print(f"[{args.consumer_name}] group_id='{args.group_id}' topic='{args.topic}'\n")

    try:
        for message in consumer:
            print(
                f"[{args.consumer_name}] partition={message.partition} offset={message.offset} "
                f"key={message.key} value={message.value}"
            )
    except KeyboardInterrupt:
        print(f"\n[{args.consumer_name}] Detenido por el usuario.")
    finally:
        print(f"[{args.consumer_name}] Particiones asignadas al cerrar: {consumer.assignment()}")
        consumer.close()


if __name__ == "__main__":
    main()
