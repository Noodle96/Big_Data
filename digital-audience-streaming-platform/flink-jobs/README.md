# flink-jobs/

Jobs de Apache Flink (Java/Maven) — Fase 4 del `plan.md`. Se despliegan sobre un cluster real (JobManager + TaskManager en AWS), no en modo embebido.

Reutiliza el stack validado en `kafka-flink-streaming-lab`: Flink 2.2.1 (`flink-streaming-java`, `flink-clients`) + `flink-connector-kafka` 5.0.0-2.2 + `flink-connector-base` explícito (evita `NoClassDefFoundError`) + `jackson-databind` 2.18.2, Java 11. Para cluster real: dependencias core de Flink en scope `provided`, `maven-shade-plugin` para el jar de conectores, envío con `flink run` (no `java -jar`).

## Estructura prevista

- `pom.xml` — dependencias y shade plugin.
- `src/main/java/.../consumo/` — consumo de topics Kafka.
- `src/main/java/.../filtrado/` — filtrado de eventos (purchase, add_cart, etc.).
- `src/main/java/.../enriquecimiento/` — enriquecimiento (hora, día, mes, fin de semana).
- `src/main/java/.../agregacion/` — ventanas de tiempo, conteos, agregaciones.
- `src/main/java/.../audiencias/` — clasificación en audiencias digitales según reglas de negocio.
- `src/main/java/.../sink/` — sink JDBC hacia PostgreSQL/TimescaleDB.
