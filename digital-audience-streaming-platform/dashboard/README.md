# dashboard/

Dashboard en tiempo real — Fase 6 del `plan.md`. Grafana + PostgreSQL/TimescaleDB, con provisioning as code (nada de configuración manual por clicks, para que el informe pueda documentar el proceso paso a paso).

## Estructura

- `grafana/provisioning/datasources/postgres.yaml` — datasource de Grafana apuntando al Postgres local de la instancia `dashboard` (as code).
- `grafana/provisioning/dashboards/dashboards.yaml` — provider que le dice a Grafana dónde buscar los `.json` de dashboards.
- `grafana/dashboards/*.json` — definiciones de dashboards/paneles, uno por cada métrica pedida en el enunciado.
- `db/init.sql` — esquema de PostgreSQL/TimescaleDB (tablas que alimentan cada panel).

## Estado de los paneles (actualizado 2026-07-30 -- las 10 métricas del enunciado)

Con el job adaptado del compañero (ver `flink-jobs/README.md`), **`audiencias-eventos.json` ya tiene los 10 paneles pedidos**, todos alimentados por tablas reales de `dashboard/db/init.sql`:

| Métrica pedida | Tabla en Postgres | Tipo de panel |
|---|---|---|
| Eventos por tipo | `eventos_por_tipo` | Pie |
| Tendencias temporales | `eventos_por_tipo`, contra `window_start` | Serie de tiempo |
| Eventos por segundo | `resumen_ventana` | Serie de tiempo |
| Conversión de compras | `resumen_ventana` | Gauge |
| Usuarios activos | `resumen_ventana` | Stat |
| Audiencias detectadas | `audiencias` | Tabla (usuarios distintos por audiencia) |
| Productos más visitados | `productos_vistos` | Barras horizontales |
| Productos más comprados | `productos_comprados` | Barras horizontales |
| Compras por región | `compras_por_region` | Barras horizontales |
| Alertas | `alertas` | Tabla (alertas recientes) |

**Nota sobre "Alertas":** el enunciado sugiere un "panel de alertas de Grafana (umbral)" -- es decir, una regla de alerta nativa de Grafana, no solo una tabla mostrando filas de la tabla `alertas`. Lo que hay ahora es una tabla con las alertas más recientes (dato real, sí cumple la métrica), pero configurar además una regla de alerta nativa (ej. umbral sobre `riesgo_abandono` o `PAYMENT_REJECTED`) queda como mejora pendiente si hay tiempo.

**Ya no aproximados:** "Eventos por segundo" y "Conversión de compras" ahora leen directo de `resumen_ventana` (calculados por el job, precisos) en vez de recalcularse desde `eventos_por_tipo` como en la primera versión.

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
