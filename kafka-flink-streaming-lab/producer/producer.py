#!/usr/bin/env python3
"""
Productor de eventos de e-commerce para el laboratorio de Kafka.

Genera continuamente eventos (VIEW_PRODUCT, SEARCH, ADD_CART, PURCHASE) con
el esquema:
    {user, event, product, category, city, price, timestamp}

y los envía al topic indicado. Se ejecuta en kafka-client.

Uso:
    python3 producer.py --bootstrap-server 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092
    python3 producer.py --bootstrap-server ... --rate 2 --count 50
"""

import argparse
import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

DEFAULT_TOPIC = "ecommerce-events"

USERS = [f"USR{n:03d}" for n in range(1, 21)]

CITIES = ["Arequipa", "Lima", "Cusco", "Trujillo", "Piura"]

PRODUCTS = [
    ("Laptop Lenovo", "Electronics", 3200),
    ("Laptop Dell", "Electronics", 3500),
    ("Mouse Logitech", "Electronics", 80),
    ("Zapatillas Nike", "Footwear", 350),
    ("Polera Adidas", "Clothing", 120),
    ("Cafetera Oster", "Home", 450),
    ("Audifonos Sony", "Electronics", 600),
]

# Distribución realista: más vistas que compras.
EVENT_TYPES = (
    ["VIEW_PRODUCT"] * 5
    + ["SEARCH"] * 3
    + ["ADD_CART"] * 2
    + ["PURCHASE"] * 1
)


def build_event() -> dict:
    product, category, price = random.choice(PRODUCTS)
    return {
        "user": random.choice(USERS),
        "event": random.choice(EVENT_TYPES),
        "product": product,
        "category": category,
        "city": random.choice(CITIES),
        "price": price,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-server", required=True, help="Lista de brokers, ej: 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092")
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--rate", type=float, default=2.0, help="Eventos por segundo")
    parser.add_argument("--count", type=int, default=0, help="Cantidad de eventos a enviar (0 = infinito, Ctrl+C para detener)")
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap_server.split(","),
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
    )

    print(f"Productor conectado a {args.bootstrap_server}, enviando a topic '{args.topic}'")
    print("Ctrl+C para detener.\n")

    sent = 0
    try:
        while args.count == 0 or sent < args.count:
            event = build_event()
            # La key es el user: eventos del mismo usuario van a la misma partición.
            future = producer.send(args.topic, key=event["user"], value=event)
            metadata = future.get(timeout=10)  # bloquea hasta tener la confirmación del broker

            sent += 1
            print(
                f"[{sent}] topic={metadata.topic} partition={metadata.partition} "
                f"offset={metadata.offset} key={event['user']} event={event['event']} "
                f"product={event['product']}"
            )

            time.sleep(1.0 / args.rate)
    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        producer.flush()
        producer.close()
        print(f"Total de eventos enviados: {sent}")


if __name__ == "__main__":
    main()
