"""Los 8 perfiles de agente requeridos por el enunciado (sección 3)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from config import PRODUCTS, Product

PricePreference = Literal["any", "high", "low"]


@dataclass(frozen=True)
class AgentProfile:
    """Perfil de comportamiento de un tipo de agente."""

    weights: dict[str, float]
    hours: list[int]
    price: PricePreference
    intensity: float
    seasonal: bool = False


AGENTS: dict[str, AgentProfile] = {
    # Compra impulsivamente, mucho PURCHASE, poca comparación
    "comprador_compulsivo": AgentProfile(
        weights={"SEARCH": 1, "VIEW_PRODUCT": 2, "ADD_CART": 3, "PURCHASE": 5},
        hours=list(range(0, 24)),
        price="any",
        intensity=1.5,
    ),
    # Investiga mucho antes de comprar: mucho SEARCH/VIEW, poco PURCHASE
    "comparador": AgentProfile(
        weights={"SEARCH": 5, "VIEW_PRODUCT": 5, "ADD_CART": 2, "PURCHASE": 1},
        hours=list(range(8, 23)),
        price="any",
        intensity=1.0,
    ),
    # Activo de madrugada
    "nocturno": AgentProfile(
        weights={"SEARCH": 3, "VIEW_PRODUCT": 4, "ADD_CART": 2, "PURCHASE": 2},
        hours=list(range(22, 24)) + list(range(0, 5)),
        price="any",
        intensity=1.0,
    ),
    # Compra productos caros
    "premium": AgentProfile(
        weights={"SEARCH": 2, "VIEW_PRODUCT": 3, "ADD_CART": 2, "PURCHASE": 4},
        hours=list(range(9, 23)),
        price="high",
        intensity=0.8,
    ),
    # Muy activo, compra seguido
    "frecuente": AgentProfile(
        weights={"SEARCH": 3, "VIEW_PRODUCT": 4, "ADD_CART": 3, "PURCHASE": 3},
        hours=list(range(6, 24)),
        price="any",
        intensity=2.0,
    ),
    # Navega mucho, compra poco
    "explorador": AgentProfile(
        weights={"SEARCH": 5, "VIEW_PRODUCT": 6, "ADD_CART": 1, "PURCHASE": 0.5},
        hours=list(range(8, 24)),
        price="any",
        intensity=1.2,
    ),
    # Llena el carrito pero abandona (mucho ADD_CART, casi sin PURCHASE)
    "indeciso": AgentProfile(
        weights={"SEARCH": 3, "VIEW_PRODUCT": 4, "ADD_CART": 5, "PURCHASE": 0.5},
        hours=list(range(9, 24)),
        price="low",
        intensity=1.0,
    ),
    # Su comportamiento depende de la temporada activa (ver escenarios/seasons.py)
    "estacional": AgentProfile(
        weights={"SEARCH": 2, "VIEW_PRODUCT": 3, "ADD_CART": 2, "PURCHASE": 2},
        hours=list(range(8, 24)),
        price="any",
        intensity=1.0,
        seasonal=True,
    ),
}


def pick_event(weights: dict[str, float]) -> str:
    """Elige un tipo de evento al azar, ponderado por los pesos del perfil."""
    return random.choices(list(weights), weights=list(weights.values()), k=1)[0]


def pick_product(price_pref: PricePreference) -> Product:
    """Elige un producto del catálogo acorde a la preferencia de precio del agente."""
    pool: list[Product]
    if price_pref == "high":
        pool = [p for p in PRODUCTS if p.price >= 1500]
    elif price_pref == "low":
        pool = [p for p in PRODUCTS if p.price < 1000]
    else:
        pool = PRODUCTS
    return random.choice(pool or PRODUCTS)
