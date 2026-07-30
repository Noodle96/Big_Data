# dashboard/

Dashboard en tiempo real — Fase 6 del `plan.md`. Grafana + PostgreSQL/TimescaleDB, con provisioning as code (nada de configuración manual por clicks, para que el informe pueda documentar el proceso paso a paso).

## Estructura

- `grafana/provisioning/datasources/postgres.yaml` — datasource de Grafana apuntando al Postgres local de la instancia `dashboard` (as code).
- `grafana/provisioning/dashboards/dashboards.yaml` — provider que le dice a Grafana dónde buscar los `.json` de dashboards.
- `grafana/dashboards/*.json` — definiciones de dashboards/paneles, uno por cada métrica pedida en el enunciado.
- `db/init.sql` — esquema de PostgreSQL/TimescaleDB (tablas que alimentan cada panel).

## Estado de los paneles (Fase 6, iniciado 2026-07-30)

`audiencias-eventos.json` cubre los 4 paneles que ya se pueden alimentar con datos reales de `eventos_por_tipo` (Job 1, `EventCountJob`):

| Métrica pedida | Estado |
|---|---|
| Eventos por tipo | Listo (`audiencias-eventos.json`) |
| Tendencias temporales | Listo (`audiencias-eventos.json`) |
| Eventos por segundo | Listo, aproximado (`audiencias-eventos.json`) |
| Conversión de compras | Listo, aproximado (`audiencias-eventos.json`) |
| Usuarios activos | Pendiente |
| Audiencias detectadas | Pendiente (Fase 5) |
| Productos más visitados/comprados | Pendiente (Job 2, `ProductRankingJob`) |
| Compras por región | Pendiente (Job 3, `RegionSalesJob`) |
| Alertas | Pendiente |

## Desplegar a la instancia `dashboard`

No se toca `infra/__main__.py` para esto (evita otro ciclo de reasignación de IPs en las demás instancias) — se sube por `rsync` igual que `flink-jobs/` a kafka-client, y se copia a las rutas reales de Grafana:

```bash
# 1. desde tu laptop: sube el proyecto actualizado a la instancia dashboard
rsync -avz --progress -e "ssh -i keys/audiencias-lab-key.pem" \
  --filter=":- .gitignore" --exclude='.git/' \
  ./ ubuntu@<IP-dashboard>:/home/ubuntu/digital-audience-streaming-platform/

# 2. entra a la instancia dashboard y copia los archivos a donde Grafana los espera
ssh -i keys/audiencias-lab-key.pem ubuntu@<IP-dashboard>
sudo cp digital-audience-streaming-platform/dashboard/grafana/provisioning/datasources/postgres.yaml \
  /etc/grafana/provisioning/datasources/
sudo cp digital-audience-streaming-platform/dashboard/grafana/provisioning/dashboards/dashboards.yaml \
  /etc/grafana/provisioning/dashboards/
sudo cp digital-audience-streaming-platform/dashboard/grafana/dashboards/audiencias-eventos.json \
  /etc/grafana/provisioning/dashboards/

# 3. reinicia Grafana para que cargue el datasource + dashboard
sudo systemctl restart grafana-server
sudo systemctl status grafana-server
```

Después entra a `http://<IP-dashboard>:3000` (usuario/clave por defecto `admin`/`admin`, pide cambiarla al primer login) y el dashboard "Audiencias Digitales - Eventos (Fase 4)" ya debería aparecer solo, sin haberlo creado a mano.
