"""Lógica estacional: los 6 escenarios de ejemplo del enunciado + 'Normal'."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from config import FORCED_SEASON


@dataclass(frozen=True)
class Season:
    """Una temporada/escenario comercial y su efecto sobre los agentes."""

    name: str
    purchase_boost: float
    intensity: float


SEASONS: dict[str, Season] = {
    "cyber_monday": Season("Cyber Monday", purchase_boost=3.0, intensity=3.0),
    "black_friday": Season("Black Friday", purchase_boost=2.5, intensity=2.5),
    "navidad": Season("Navidad", purchase_boost=2.0, intensity=2.0),
    "fiestas_patrias": Season("Fiestas Patrias", purchase_boost=1.8, intensity=1.8),
    "dia_del_padre": Season("Día del Padre", purchase_boost=1.5, intensity=1.5),
    "campaña_escolar": Season("Campaña Escolar", purchase_boost=1.4, intensity=1.4),
    "normal": Season("Normal", purchase_boost=1.0, intensity=1.0),
}


def _season_by_calendar_date(d: date) -> Season:
    """Detecta la temporada según la fecha real. Ventanas ilustrativas."""
    # Black Friday (última semana de noviembre) y Cyber Monday (el lunes
    # siguiente) ya no se solapan como en la versión original.
    if d.month == 11 and 28 <= d.day <= 30:
        return SEASONS["cyber_monday"]
    if d.month == 11 and 24 <= d.day <= 27:
        return SEASONS["black_friday"]
    if d.month == 12 and 1 <= d.day <= 25:
        return SEASONS["navidad"]
    if d.month == 7 and 25 <= d.day <= 29:
        return SEASONS["fiestas_patrias"]
    # Día del Padre (Perú): tercer domingo de junio, aproximado como ventana
    if d.month == 6 and 15 <= d.day <= 21:
        return SEASONS["dia_del_padre"]
    # Campaña Escolar (Perú): temporada previa al inicio de clases (marzo)
    if (d.month == 2 and d.day >= 15) or (d.month == 3 and d.day <= 15):
        return SEASONS["campaña_escolar"]
    return SEASONS["normal"]


def get_season(d: date, forced: Optional[str] = FORCED_SEASON) -> Season:
    """Devuelve la temporada activa.

    `forced` (si viene, sea por `--escenario` en main.py o por la variable de
    entorno FORCED_SEASON) fuerza esa temporada sin importar la fecha real --
    necesario para poder correr cada escenario a demanda (Fase 7 del
    plan.md) en vez de esperar a que llegue la fecha calendario real. Si no
    se fuerza nada, se detecta por la fecha real del sistema.
    """
    if forced:
        key = forced.strip().lower()
        if key not in SEASONS:
            valid = ", ".join(SEASONS)
            raise ValueError(f"Escenario {forced!r} inválido. Opciones: {valid}")
        return SEASONS[key]
    return _season_by_calendar_date(d)
