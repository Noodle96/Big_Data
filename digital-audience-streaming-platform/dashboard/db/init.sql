-- Esquema de PostgreSQL/TimescaleDB para el dashboard.
-- Una tabla por bloque de métrica (Fase 6 del plan.md). Se ejecuta contra la
-- base "audiencias" ya creada por el bootstrap de la instancia dashboard
-- (ver infra/__main__.py, POSTGRES_DB).
--
-- Fase 4: job único de Flink (AudienciasDigitalesJob, adaptado del diseño del
-- compañero de equipo -- ver jobsCompa/ -- cambiando sus sinks de Kafka por
-- sinks JDBC a estas tablas, para mantener el dashboard sobre Postgres/Grafana
-- ya construido). Ventanas tumbling de 10s (tiempo de procesamiento).
--
-- TIMESTAMPTZ (no TIMESTAMP) y TEXT (no VARCHAR(n)) en todas las columnas,
-- siguiendo las recomendaciones de TimescaleDB -- el sink JDBC no cambia,
-- java.sql.Timestamp/String funcionan igual con ambos tipos.

-- Eventos por tipo, por ventana.
CREATE TABLE IF NOT EXISTS eventos_por_tipo (
    window_start TIMESTAMPTZ NOT NULL,
    event_type   TEXT NOT NULL,
    event_count  BIGINT NOT NULL
);
SELECT create_hypertable('eventos_por_tipo', 'window_start', if_not_exists => TRUE);

-- Métricas escalares por ventana: usuarios activos, eventos/segundo, conversión.
CREATE TABLE IF NOT EXISTS resumen_ventana (
    window_start        TIMESTAMPTZ NOT NULL,
    window_end          TIMESTAMPTZ NOT NULL,
    total_events         BIGINT NOT NULL,
    usuarios_activos     BIGINT NOT NULL,
    eventos_por_segundo  DOUBLE PRECISION NOT NULL,
    conversion           DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('resumen_ventana', 'window_start', if_not_exists => TRUE);

-- Productos más vistos, por ventana.
CREATE TABLE IF NOT EXISTS productos_vistos (
    window_start TIMESTAMPTZ NOT NULL,
    product      TEXT NOT NULL,
    views_count  BIGINT NOT NULL
);
SELECT create_hypertable('productos_vistos', 'window_start', if_not_exists => TRUE);

-- Productos más comprados, por ventana.
CREATE TABLE IF NOT EXISTS productos_comprados (
    window_start     TIMESTAMPTZ NOT NULL,
    product          TEXT NOT NULL,
    purchases_count  BIGINT NOT NULL
);
SELECT create_hypertable('productos_comprados', 'window_start', if_not_exists => TRUE);

-- Compras por región (ciudad), por ventana.
CREATE TABLE IF NOT EXISTS compras_por_region (
    window_start     TIMESTAMPTZ NOT NULL,
    city             TEXT NOT NULL,
    purchases_count  BIGINT NOT NULL
);
SELECT create_hypertable('compras_por_region', 'window_start', if_not_exists => TRUE);

-- Clasificación de audiencia por usuario, evaluada en cada evento (estado
-- acumulado de Flink, no ventaneado).
CREATE TABLE IF NOT EXISTS audiencias (
    event_time    TIMESTAMPTZ NOT NULL,
    user_id       TEXT NOT NULL,
    agent_type    TEXT,
    audiencia     TEXT NOT NULL,
    total_events  BIGINT NOT NULL
);
SELECT create_hypertable('audiencias', 'event_time', if_not_exists => TRUE);

-- Alertas: anomalías de ventana (ADD_CART sin PURCHASE) + transiciones de
-- audiencia a un estado de riesgo/interés.
CREATE TABLE IF NOT EXISTS alertas (
    created_at  TIMESTAMPTZ NOT NULL,
    tipo        TEXT NOT NULL,
    mensaje     TEXT NOT NULL,
    user_id     TEXT
);
SELECT create_hypertable('alertas', 'created_at', if_not_exists => TRUE);

-- Productos vistos y comprados en la misma ventana (join informativo, no es
-- uno de los 10 paneles pedidos, pero se conserva del diseño original).
CREATE TABLE IF NOT EXISTS productos_relacionados (
    detected_at   TIMESTAMPTZ NOT NULL,
    product       TEXT NOT NULL,
    viewed_by     TEXT NOT NULL,
    purchased_by  TEXT NOT NULL
);
SELECT create_hypertable('productos_relacionados', 'detected_at', if_not_exists => TRUE);
