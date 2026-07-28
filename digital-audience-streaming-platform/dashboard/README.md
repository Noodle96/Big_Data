# dashboard/

Dashboard en tiempo real — Fase 6 del `plan.md`. Grafana + PostgreSQL/TimescaleDB, con provisioning as code (nada de configuración manual por clicks, para que el informe pueda documentar el proceso paso a paso).

## Estructura prevista

- `grafana/provisioning/` — datasources y configuración de Grafana como código (YAML).
- `grafana/dashboards/` — definiciones de dashboards/paneles (JSON), uno por cada métrica pedida en el enunciado (usuarios activos, eventos por segundo, eventos por tipo, audiencias detectadas, productos más visitados/comprados, compras por región, tendencias temporales, conversión de compras, alertas).
- `db/init.sql` — esquema inicial de PostgreSQL/TimescaleDB (tablas/vistas que alimentan cada panel).
