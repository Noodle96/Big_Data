-- Esquema de PostgreSQL/TimescaleDB para el dashboard.
-- Una tabla por bloque de métrica (Fase 6 del plan.md). Se ejecuta contra la
-- base "audiencias" ya creada por el bootstrap de la instancia dashboard
-- (ver infra/__main__.py, POSTGRES_DB).

-- Job 1 (EventCountJob, Fase 4): eventos por tipo, en ventanas de 30s.
CREATE TABLE IF NOT EXISTS eventos_por_tipo (
    window_start TIMESTAMP NOT NULL,
    event_type   VARCHAR(32) NOT NULL,
    event_count  BIGINT NOT NULL
);
-- Convertir a hypertable de TimescaleDB (particiona automáticamente por tiempo)
SELECT create_hypertable('eventos_por_tipo', 'window_start', if_not_exists => TRUE);

-- TODO (Job 2, ProductRankingJob): productos_vistos, productos_comprados
-- TODO (Job 3, RegionSalesJob): compras_por_region
