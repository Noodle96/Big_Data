# flink-jobs/

Jobs de Apache Flink (Java/Maven) — Fase 4 del `plan.md`. Se despliegan sobre el cluster real (JobManager + 3 TaskManagers en AWS), no en modo embebido como el laboratorio anterior del curso.

**Varios jobs separados por responsabilidad** (decisión del 2026-07-29), cada uno lee directo de Kafka y escribe directo a Postgres/TimescaleDB (sin topic intermedio):

| Job | Estado | Qué hace |
|---|---|---|
| `EventCountJob` | Implementado, sin probar | Consume `user-events` + `purchase-events`, cuenta eventos por tipo en ventanas de 30s, escribe a `eventos_por_tipo`. |
| `ProductRankingJob` | Pendiente | Productos más vistos / más comprados. |
| `RegionSalesJob` | Pendiente | Compras por región (ciudad). |

## Dependencias (versiones confirmadas en Maven Central para Flink 2.2.1)

- `flink-streaming-java` / `flink-clients` 2.2.1 — `provided` (ya están en el cluster).
- `flink-connector-kafka` 5.0.0-2.2 + `flink-connector-base` 2.2.1 explícito (mismo patrón validado en `kafka-flink-streaming-lab`).
- `flink-connector-jdbc-postgres` **4.1.0-2.2** — el conector JDBC se reorganizó en `jdbc-core` + un módulo por base de datos; este es el que trae el dialecto de Postgres, confirmado como la versión exacta para Flink 2.2.
- `postgresql` (driver JDBC) **42.7.13**.
- `jackson-databind` 2.18.2 — parseo del JSON de los eventos.

## Build y despliegue

```bash
cd flink-jobs
mvn clean package
```

Genera `target/flink-jobs-1.0.0.jar` (con shade plugin, incluye los conectores). Como hay varios jobs en el mismo jar, no hay una clase principal por defecto -- se indica cuál correr con `-c`:

```bash
flink run -c com.bigdata.audiencias.jobs.EventCountJob target/flink-jobs-1.0.0.jar
```

Verificar en la Web UI de Flink (`pulumi stack output flinkUiUrl`) que el job aparece como `RUNNING`.

## Sin validar todavía

- Los imports de `org.apache.flink.connector.jdbc.*` (`JdbcSink`, `JdbcExecutionOptions`, `JdbcConnectionOptions`) en `EventCountJob` son los históricos de la documentación del conector -- con el conector reorganizado en `jdbc-core`/`jdbc-postgres` (4.1.0-2.2) es posible que el path del paquete haya cambiado. No se ha compilado todavía; puede necesitar un ajuste en el primer `mvn package`, igual que pasó con el bootstrap de Flink/Postgres en la Fase 1.
- El esquema de la tabla destino (`dashboard/db/init.sql`) hay que ejecutarlo en la instancia `dashboard` antes de correr el job por primera vez.
