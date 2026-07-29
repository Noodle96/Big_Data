"""Simulador de agentes: bucle principal.

Ejecutar SIEMPRE desde esta carpeta (los imports dependen de eso):

    cd agentes-simulador/src

Ejemplos:

    # Probar la lógica de agentes/escenarios SIN Kafka (no necesita que
    # exista ningún cluster todavía -- útil mientras la Fase 1 no está lista)
    python3 main.py --dry-run

    # Igual que arriba, pero forzando el escenario "Navidad" en vez de la
    # fecha real del sistema
    python3 main.py --dry-run --escenario navidad

    # Corrida real contra Kafka (necesita BOOTSTRAP_SERVERS válido en
    # config.py y los topics ya creados), con la fecha real -> hoy
    # (2026-07-28) cae en la ventana de "Fiestas Patrias"
    python3 main.py

    # Corrida real forzando un escenario puntual
    python3 main.py --escenario cyber_monday

    # Forzar que TODOS los perfiles estén activos sin importar la hora real
    # del servidor (por defecto, solo comprador_compulsivo lo está siempre;
    # el resto depende de AgentProfile.hours) -- útil para capturar evidencia
    # con variedad de perfiles para el informe
    python3 main.py --escenario navidad --ignore-horario

    # Ver todos los escenarios disponibles
    python3 main.py --help

    # Correr varios escenarios en secuencia para comparar (Fase 7): una
    # corrida por escenario, cada una un tiempo fijo (aquí 2 minutos),
    # deteniéndose sola con `timeout`
    for esc in navidad cyber_monday black_friday fiestas_patrias; do
        echo "=== $esc ==="
        timeout 120 python3 main.py --escenario "$esc"
    done

Nota sobre la sintaxis `FORCED_SEASON=navidad python3 main.py` (variable de
entorno antes del comando, no después): así es como funciona en bash/zsh --
el shell arranca el proceso de Python con esa variable ya puesta en su
entorno. Python la lee con `os.environ.get(...)`, no como argumento de
línea de comandos, por eso NO se escribe `python3 main.py FORCED_SEASON=...`
(eso llegaría como texto suelto a sys.argv y no lo estamos leyendo). Para
evitar esta confusión se agregó `--escenario`, que sí es un argumento común
y corriente y hace exactamente lo mismo -- se recomienda usar `--escenario`
en la guía del informe por ser más explícito; FORCED_SEASON queda como
alternativa para scripts.
"""

from __future__ import annotations

import argparse
import random
import time
from datetime import datetime
from typing import Optional

from agentes.agents import AGENTS, AgentProfile, pick_event, pick_product
from config import CITIES, FORCED_SEASON
from escenarios.seasons import SEASONS, Season, get_season
from productores.producers import (
    BaseProducer,
    IoTProducer,
    MobileProducer,
    POSProducer,
    VehicleProducer,
    WebProducer,
)
from schema import Event, SimulatedUser

# 50 usuarios sintéticos, cada uno con un tipo de agente
USERS: list[SimulatedUser] = [
    {"user_id": f"USR{i:03d}", "agent": random.choice(list(AGENTS))}
    for i in range(1, 51)
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulador de agentes autónomos + productores Kafka."
    )
    parser.add_argument(
        "--escenario",
        choices=sorted(SEASONS),
        default=None,
        help=(
            "Fuerza un escenario puntual en vez de detectarlo por la fecha "
            "real. Si no se indica, usa FORCED_SEASON (variable de entorno) "
            "o, si tampoco está, la fecha real del sistema."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No conecta a Kafka: solo imprime en consola los eventos que se enviarían.",
    )
    parser.add_argument(
        "--ignore-horario",
        action="store_true",
        help=(
            "Ignora AgentProfile.hours: todos los perfiles quedan activos sin "
            "importar la hora real del servidor. Solo comprador_compulsivo "
            "está activo 24/7 por defecto -- este flag es útil para generar "
            "evidencia con variedad de perfiles sin depender de a qué hora "
            "se corre el simulador."
        ),
    )
    return parser.parse_args()


def build_event(user: SimulatedUser, now: datetime, season: Season) -> Event:
    profile: AgentProfile = AGENTS[user["agent"]]
    weights: dict[str, float] = dict(profile.weights)
    weights["PURCHASE"] *= season.purchase_boost  # efecto estacional
    prod = pick_product(profile.price)
    return {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "user_id": user["user_id"],
        "event": pick_event(weights),
        "product": prod.product,
        "category": prod.category,
        "city": random.choice(CITIES),
        "price": prod.price,
        "agent_type": user["agent"],
        "source": "",  # lo completa el producer elegido en send()
    }


def main() -> None:
    args: argparse.Namespace = parse_args()

    # Prioridad: --escenario (CLI) > FORCED_SEASON (env var) > fecha real.
    forced_season: Optional[str] = args.escenario or FORCED_SEASON

    producers: list[BaseProducer] = [
        WebProducer(dry_run=args.dry_run),
        MobileProducer(dry_run=args.dry_run),
        IoTProducer(dry_run=args.dry_run),
        VehicleProducer(dry_run=args.dry_run),
        POSProducer(dry_run=args.dry_run),
    ]

    modo: str = "DRY-RUN (sin Kafka)" if args.dry_run else "real (publicando a Kafka)"
    print(f"Simulador iniciado en modo {modo}. Ctrl+C para detener.")
    if forced_season:
        print(f"Escenario forzado: {forced_season}")
    else:
        print("Escenario: se detecta por la fecha real del sistema.")

    while True:
        now: datetime = datetime.now()
        season: Season = get_season(now.date(), forced=forced_season)
        for user in USERS:
            profile: AgentProfile = AGENTS[user["agent"]]
            if not args.ignore_horario and now.hour not in profile.hours:
                continue  # respeta horario del agente, salvo --ignore-horario
            if random.random() > 0.3 * profile.intensity * season.intensity:
                continue  # frecuencia según intensidad
            ev: Event = build_event(user, now, season)
            valid: list[BaseProducer] = [
                pr for pr in producers
                if pr.allowed_events is None or ev["event"] in pr.allowed_events
            ]
            pr: BaseProducer = random.choice(valid)
            pr.send(ev)
            print(
                f"[{pr.source}] {ev['event']} | {ev['product']} | "
                f"{user['agent']} | {season.name}"
            )
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulador detenido (Ctrl+C).")
