"""Estructuras de datos compartidas entre simulator/agents/producers."""

from __future__ import annotations

from typing import TypedDict


class Event(TypedDict):
    """Evento JSON tal como se publica en Kafka (ver requerimientos.pdf, I.3)."""

    timestamp: str
    user_id: str
    event: str
    product: str
    category: str
    city: str
    price: int
    agent_type: str
    source: str  # lo completa el producer (web/mobile/iot/vehicle/pos) en send()


class SimulatedUser(TypedDict):
    """Un usuario sintético del simulador."""

    user_id: str
    agent: str
