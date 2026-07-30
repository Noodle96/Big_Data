# flink-jobs/

Jobs de Apache Flink (Java/Maven) — Fase 4 del `plan.md`. Se despliegan sobre el cluster real (JobManager + 3 TaskManagers en AWS), no en modo embebido como el laboratorio anterior del curso.

**Varios jobs separados por responsabilidad** (decisión del 2026-07-29), cada uno lee directo de Kafka y escribe directo a Postgres/TimescaleDB (sin topic intermedio):

| Job | Estado | Qué hace |
|---|---|---|
| `EventCountJob` | Compila OK, pendiente correr en el cluster | Consume `user-events` + `purchase-events`, cuenta eventos por tipo en ventanas de 30s, escribe a `eventos_por_tipo`. |
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

## Estado de validación

- **2026-07-29, primer `mvn clean package` en kafka-client: falló**, como se esperaba. `JdbcSink` no estaba en `org.apache.flink.connector.jdbc` (el paquete histórico de la documentación) y `org.apache.flink.streaming.api.windowing.time.Time` ya no existe en Flink 2.x. Corregido leyendo el código fuente real del conector (tag `v4.1.0` en GitHub): `JdbcSink` se movió a `org.apache.flink.connector.jdbc.core.datastream.sink` y usa la Sink API v2 (`JdbcSink.builder().withQueryStatement(...).withExecutionOptions(...).buildAtLeastOnce(...)`, aplicado con `.sinkTo()` en vez de `.addSink()`); las ventanas ahora se definen con `TumblingProcessingTimeWindows.of(Duration.ofSeconds(...))` directamente, sin la clase `Time`. `JdbcConnectionOptions`/`JdbcExecutionOptions` sí siguen en el paquete histórico. Segundo intento: `BUILD SUCCESS`.
- **2026-07-29, primera corrida real (24+ min, ~3,463 eventos procesados):** confirmó el pipeline end-to-end (Kafka → Flink → Postgres) funcionando, pero reveló que `window_start` en la tabla destino en realidad era la hora de inserción en Postgres (`LocalDateTime.now()` en el sink), no el límite real de la ventana de Flink -- `.sum(1)` no da acceso a los metadatos de la ventana. **Corregido**: se cambió a `.process(new CountEventsWindowFunction())` (una `ProcessWindowFunction` interna a `EventCountJob`), que sí tiene acceso a `context.window().getStart()`. El stream ahora es `Tuple3<Long, String, Long>` (inicio real de ventana en epoch millis, tipo de evento, conteo). Pendiente: recompilar, cancelar el job viejo (`JobID 932b20b4249f2cc792d045207bdfa79c`), limpiar la tabla (tiene filas con el `window_start` incorrecto) y volver a correr.
- El esquema de la tabla destino (`dashboard/db/init.sql`) ya se aplicó exitosamente contra Postgres en la instancia `dashboard` (tabla `eventos_por_tipo`, convertida a hypertable de TimescaleDB).
