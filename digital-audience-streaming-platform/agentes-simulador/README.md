# agentes-simulador/

Simulador de agentes autónomos + productores Kafka (Python). Fase 2 del `plan.md`. Código base aportado por un compañero de equipo, integrado y tipado en esta sesión (2026-07-24). Todo el código lleva type hints completos (variables, estructuras de datos, funciones, clases).

## Estructura

```
src/
├── config.py              # brokers, topics, catálogo, override de escenario (FORCED_SEASON)
├── schema.py               # tipos compartidos: Event, SimulatedUser
├── agentes/
│   ├── __init__.py
│   └── agents.py            # los 8 perfiles (AgentProfile) + pick_event/pick_product
├── escenarios/
│   ├── __init__.py
│   └── seasons.py           # los 6 escenarios del enunciado + "Normal"
├── productores/
│   ├── __init__.py
│   └── producers.py         # 5 canales (Web, Mobile, IoT, Vehicle, POS)
└── main.py                  # bucle principal (50 usuarios sintéticos)
```

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt   # o: pip install kafka-python
```

## Configuración obligatoria antes de correr

En `src/config.py`:

- `BOOTSTRAP_SERVERS` — IPs de **nuestros** brokers Kafka (privadas si el simulador corre dentro de la misma VPC). Todavía tiene las IPs del cluster de prueba del compañero, hay que reemplazarlas cuando la Fase 1 (infra) esté lista.
- Los topics `user-events` (navegación) y `purchase-events` (conversión) deben existir en el cluster antes de correr, o tener auto-create activado:

```bash
bin/kafka-topics.sh --create --topic user-events \
  --bootstrap-server localhost:9092 --partitions 3 --replication-factor 3
bin/kafka-topics.sh --create --topic purchase-events \
  --bootstrap-server localhost:9092 --partitions 3 --replication-factor 3
```

## Probar SIN Kafka (mientras la Fase 1 no esté lista)

No hace falta tener ningún cluster levantado para validar que los agentes y los escenarios funcionan. `--dry-run` evita conectarse a Kafka por completo y solo imprime en consola lo que se habría enviado:

```bash
cd src
python3 main.py --dry-run
python3 main.py --dry-run --escenario navidad
```

Esto es lo único que se puede probar hoy de punta a punta sin infraestructura: la lógica de agentes (perfiles, horarios, intensidad), la selección de escenario y el ruteo a topic/producer. Todavía no existe nada de Kafka, Flink ni el dashboard (ver `plan.md`) — eso empieza en la Fase 1.

## Cómo ejecutar (contra Kafka real)

```bash
cd src
python3 main.py
```

Con la fecha real del sistema, hoy (2026-07-28) cae en la ventana de "Fiestas Patrias" — para probar cualquier otro escenario hay que forzarlo explícitamente con `--escenario`:

```bash
python3 main.py --escenario navidad
python3 main.py --escenario cyber_monday
```

Escenarios válidos: `cyber_monday`, `black_friday`, `navidad`, `fiestas_patrias`, `dia_del_padre`, `campaña_escolar`, `normal`. Ver más ejemplos (incluido cómo correr varios escenarios seguidos para comparar, Fase 7) en el docstring de `main.py`.

> También existe la variable de entorno `FORCED_SEASON` (ej. `FORCED_SEASON=navidad python3 main.py`) con el mismo efecto que `--escenario` — se mantiene como alternativa para scripts, pero `--escenario` es el recomendado por ser un argumento explícito y aparecer en `python3 main.py --help`.

Detener con **Ctrl+C**.

## Verificar que los eventos llegan a Kafka

```bash
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic user-events --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic purchase-events --from-beginning
```

## Decisiones de diseño (por qué se ve así)

- **2 topics por semántica de negocio, no 1 ni por canal**: `user-events` (SEARCH, VIEW_PRODUCT) y `purchase-events` (ADD_CART, PURCHASE, PAYMENT_REJECTED). Sigue el diagrama de referencia del enunciado y le da a Flink una separación natural entre "análisis de navegación" y "análisis de conversión" sin tener que filtrar un único topic. No se creó un tercer topic `iot-events` porque hoy el simulador no genera telemetría real de sensores (IoT/Vehicle son canales de compra, no sensores) — se agrega el día que eso exista.
- **`key=user_id` en cada mensaje**: garantiza que los eventos de un mismo usuario queden en la misma partición (orden preservado). El riesgo de desbalance por usuarios muy activos existe en teoría, pero con 50 usuarios repartidos en 3 particiones y perfiles asignados al azar, cada partición mezcla varios perfiles y el desbalance se diluye en la práctica. Si en pruebas reales se ve una partición mucho más cargada que las otras, la alternativa es no mandar `key` (round-robin) y dejar que Flink agrupe por `user_id` internamente con `keyBy` (que hace su propio shuffle, independiente del particionado de Kafka).
- **`FORCED_SEASON` en `config.py`, leído de una variable de entorno**: mantiene la configuración en un solo lugar (junto a `BOOTSTRAP_SERVERS`, etc.) pero permite cambiar de escenario en cada corrida sin editar el archivo — necesario para la Fase 7 (ejecutar bajo distintos escenarios), ya que la detección automática por fecha real no sirve para probar "Navidad" en julio.
- **`--escenario` (CLI, argparse) sobre `FORCED_SEASON` (env var)**: ambos hacen lo mismo, pero `--escenario` es más explícito para alguien siguiendo la guía (aparece en `--help`, no depende de la sintaxis `VAR=valor comando` de bash que no es igual en Windows). Prioridad si se usan ambos: `--escenario` > `FORCED_SEASON` > fecha real.
- **`--dry-run`**: evita conectar a Kafka (el constructor de `KafkaProducer` intentaría conectarse igual, y fallaría si no hay cluster). Permite validar toda la lógica de agentes/escenarios/ruteo sin depender de que la Fase 1 (infra) ya exista.
