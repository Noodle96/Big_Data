"""Productores Kafka: 5 canales de ingesta (Web, Mobile, IoT, Vehicle, POS)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional

from config import BOOTSTRAP_SERVERS, TOPIC_PURCHASE_EVENTS, TOPIC_USER_EVENTS
from schema import Event

if TYPE_CHECKING:
    # Solo se importa de verdad para chequeo de tipos (mypy/IDE). En
    # tiempo de ejecución el import real vive dentro de __init__, y solo
    # ocurre si dry_run=False -- así "--dry-run" funciona aunque el
    # paquete kafka-python no esté instalado (ver ModuleNotFoundError que
    # tuviste: eso pasaba porque este import estaba a nivel de módulo y se
    # ejecutaba siempre, incluso en dry-run).
    from kafka import KafkaProducer

# Eventos de "conversión" -> purchase-events; el resto (navegación) -> user-events.
_PURCHASE_EVENT_TYPES: frozenset[str] = frozenset({"ADD_CART", "PURCHASE", "PAYMENT_REJECTED"})


def topic_for_event(event_type: str) -> str:
    """Decide a qué topic va un evento según su tipo (ver config.py)."""
    return TOPIC_PURCHASE_EVENTS if event_type in _PURCHASE_EVENT_TYPES else TOPIC_USER_EVENTS


class BaseProducer:
    source: str = "generic"
    allowed_events: Optional[list[str]] = None  # None = permite todos

    def __init__(self, dry_run: bool = False) -> None:
        # dry_run=True: no intenta conectar a Kafka en absoluto (útil si
        # todavía no existe el cluster -- Fase 1 -- o si ni siquiera está
        # instalado kafka-python) y solo se quiere validar la lógica de
        # agentes/escenarios. Ver main.py --dry-run.
        self.dry_run: bool = dry_run
        self.kafka: Optional[Any] = None  # Optional["KafkaProducer"] en tiempo de tipos
        if not dry_run:
            from kafka import KafkaProducer  # import perezoso, ver nota arriba

            self.kafka = KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
            )

    def send(self, event: Event) -> None:
        event["source"] = self.source
        topic: str = topic_for_event(event["event"])
        if self.dry_run or self.kafka is None:
            print(f"  [DRY-RUN] -> topic={topic} key={event['user_id']} value={event}")
            return
        # key=user_id: mismo usuario siempre a la misma partición (orden
        # garantizado por usuario). Ver análisis de skew en el chat / plan.md.
        self.kafka.send(topic, key=event["user_id"], value=event)


class WebProducer(BaseProducer):
    source = "web"  # todo el flujo


class MobileProducer(BaseProducer):
    source = "mobile"  # todo el flujo


class IoTProducer(BaseProducer):
    source = "iot"
    allowed_events = ["ADD_CART", "PURCHASE"]  # reposición automática


class VehicleProducer(BaseProducer):
    source = "vehicle"
    allowed_events = ["SEARCH", "PURCHASE"]  # compras en ruta


class POSProducer(BaseProducer):
    source = "pos"
    allowed_events = ["PURCHASE"]  # tienda física
