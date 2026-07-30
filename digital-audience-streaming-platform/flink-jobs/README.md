# flink-jobs/

Fase 4 del `plan.md`. **Un solo job de Flink** (`AudienciasDigitalesJob`), adaptado del diseño original de un compañero de equipo (carpeta `jobsCompa/`, ya retirada del proyecto). Se despliega sobre el cluster real (JobManager + 3 TaskManagers en AWS).

## Historia de esta decisión (2026-07-30)

El diseño original era del compañero encargado de esa parte, y sus sinks eran 3 tópicos de Kafka (`metrics`, `alertas`, `audiencias`) en vez de Postgres. Se analizó su código y se decidió **mantenerlo como un solo job** (no partirlo en varios, aunque tiene desventajas de acoplamiento -- punto único de falla, `windowAll()` no escala con el paralelismo, no se puede redesplegar por partes) porque es la parte que él va a explicar/sustentar tal cual la diseñó. Lo único que se adaptó fue el **destino de los datos**: se cambiaron los 3 sinks de Kafka por sinks JDBC a Postgres/TimescaleDB, para que alimente el dashboard de Grafana ya construido (Fase 6, ver `dashboard/`) en vez de requerir un consumidor de Kafka aparte.

## Qué hace (una sola clase, `AudienciasDigitalesJob`, varias ramas)

Consume `user-events` + `purchase-events` (2 tópicos -- el original leía de un solo tópico `eventos`, se adaptó a `.setTopics(...)` con los 2 nuestros, sin tocar la lógica de procesamiento). Ventanas tumbling de **10 segundos** (tiempo de procesamiento, distinto de los 30s que se usaban antes en el job propio que este reemplaza).

| Rama | Tabla(s) destino | Cubre del enunciado |
|---|---|---|
| Agregación por ventana (`windowAll`) | `resumen_ventana` | Usuarios activos, eventos/segundo, conversión |
| ↳ mismo resumen, explotado por mapa | `eventos_por_tipo` | Eventos por tipo |
| ↳ | `productos_vistos` | Productos más visitados |
| ↳ | `productos_comprados` | Productos más comprados |
| ↳ | `compras_por_region` | Compras por región |
| ↳ alerta ADD_CART sin PURCHASE | `alertas` | Alertas (parte 1) |
| Clasificación de audiencia (`keyBy` + estado) | `audiencias` | Audiencias detectadas |
| ↳ alerta de transición a estado de riesgo | `alertas` | Alertas (parte 2) |
| Join vista/compra por ventana | `productos_relacionados` | Extra, no pedido por el enunciado |

Con esto las 10 métricas del enunciado ya tienen tabla real en Postgres. **Tendencias temporales** no tiene tabla propia -- se resuelve graficando cualquiera de las anteriores contra `window_start`, ya lo hacíamos así en el dashboard de la Fase 6.

## Build y despliegue

Mismo procedimiento ya validado (ver `dashboard/README.md` y las notas de Fase 4 en memoria del proyecto): `rsync` a kafka-client, `mvn clean package` ahí, `scp` en dos saltos al JobManager, `flink run -c com.bigdata.audiencias.jobs.AudienciasDigitalesJob target/flink-jobs-1.0.0.jar`.

Antes de correrlo por primera vez: aplicar el esquema completo de `dashboard/db/init.sql` (ya tiene las 7 tablas nuevas) contra Postgres en la instancia `dashboard`.

## Estado

- **2026-07-30: `BUILD SUCCESS` en kafka-client.** Primer intento de compilación falló con 2 errores esperables de una adaptación: `ClassifyAudienceFunction` usaba `open(Configuration parameters)`, eliminado por completo en Flink 2.x (no solo deprecado) -- corregido a `open(OpenContext openContext)`, confirmado contra la documentación oficial. El otro error era el propio `EventCountJob.java` (ya retirado) rompiendo la compilación por acceder a campos de `Event` que ahora son privados -- se eliminó el archivo.
- **Primer `flink run`: falló** con `PSQLException: remaining connection slots are reserved for roles with the SUPERUSER attribute` -- `max_connections` de Postgres (25, tuneado bajo por `timescaledb-tune` para el t3.small) no alcanzaba para 8 sinks JDBC x parallelism 3. Subido a 100 en `postgresql.conf` (manual en la instancia + agregado a `infra/__main__.py` para que quede en el bootstrap real).
- **Segundo intento: job corriendo, validado de punta a punta.** Grafo de la Web UI confirmado igual al diseño (8 sinks JDBC visibles). Corrido el simulador ~3.5 min, las 8 tablas de Postgres con datos reales y coherentes (`audiencias` mostrando clasificaciones correctas por estado acumulado, `alertas` con transiciones reales sin spam).
- Pendiente: extender el dashboard de Grafana (`dashboard/grafana/dashboards/audiencias-eventos.json`) con paneles para las 6 tablas nuevas -- hoy el dashboard solo tiene los 4 paneles que ya existían sobre `eventos_por_tipo`.
