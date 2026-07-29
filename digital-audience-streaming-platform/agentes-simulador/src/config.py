"""Configuración compartida del simulador de agentes + productores Kafka."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

# TODO(Fase 1): reemplazar por las IPs privadas de nuestros brokers una vez
# que la infraestructura (Pulumi) esté desplegada. Estas son del cluster de
# prueba del compañero.
# BOOTSTRAP_SERVERS: str = "172.31.26.203:9092,172.31.23.20:9092,172.31.26.204:9092"
BOOTSTRAP_SERVERS: str = "10.30.1.11:9092,10.30.1.12:9092,10.30.1.13:9092"

# Topics separados por SEMÁNTICA DE NEGOCIO (no por canal de origen), tal
# como sugiere el diagrama de referencia del enunciado. "user-events"
# concentra la navegación (SEARCH, VIEW_PRODUCT); "purchase-events"
# concentra la conversión (ADD_CART, PURCHASE, PAYMENT_REJECTED). Ver
# plan.md, Fase 3, y el análisis de este mismo chat sobre por qué no usamos
# un único topic "eventos".
TOPIC_USER_EVENTS: str = "user-events"
TOPIC_PURCHASE_EVENTS: str = "purchase-events"

CITIES: list[str] = ["Arequipa", "Lima", "Cusco", "Trujillo", "Piura"]


@dataclass(frozen=True)
class Product:
    """Un producto del catálogo simulado."""

    product: str
    category: str
    price: int


PRODUCTS: list[Product] = [
    Product("Laptop Lenovo", "Electronics", 3200),
    Product("Laptop Dell", "Electronics", 4100),
    Product("iPhone 15", "Electronics", 5200),
    Product("Mouse Logitech", "Accesorios", 90),
    Product("Teclado HyperX", "Accesorios", 250),
    Product("Monitor LG", "Electronics", 1200),
    Product("Audifonos Sony", "Audio", 700),
    Product("Smartwatch Garmin", "Wearables", 1500),
]

# Fuerza un escenario específico sin depender de la fecha real del sistema
# (por defecto, None => se detecta la temporada por la fecha real, ver
# escenarios/seasons.py). Se lee de una variable de entorno para poder
# cambiar de escenario en cada corrida sin editar este archivo:
#
#   FORCED_SEASON=navidad python3 main.py
#
# Valores válidos: las keys de SEASONS en escenarios/seasons.py
# (cyber_monday, black_friday, navidad, fiestas_patrias, dia_del_padre,
# campaña_escolar, normal).
FORCED_SEASON: Optional[str] = os.environ.get("FORCED_SEASON")
