# infra/

Infraestructura como código (Pulumi, Python) — Fase 1 del `plan.md`. Scaffold creado manualmente con `pulumi new aws-python` (stack `academy2`, región `us-east-1`), `__main__.py` reemplazado con el cluster real.

## Topología (9 instancias EC2, todas `t3.small`, misma VPC/Security Group)

| Instancia | Rol | IP privada |
|---|---|---|
| kafka-broker-1/2/3 | Kafka KRaft (broker+controller) | 10.30.1.11-13 |
| flink-jobmanager | Flink JobManager | 10.30.1.21 |
| flink-taskmanager-1/2/3 | Flink TaskManager | 10.30.1.22-24 |
| dashboard | PostgreSQL 16 + TimescaleDB + Grafana (co-ubicados) | 10.30.1.30 |
| kafka-client | Simulador de agentes + `scripts/kafka/create_topics.py` (Python, repo clonado en el bootstrap) | 10.30.1.40 |

Decisiones (ver conversación 2026-07-24/2026-07-29): sin réplica de "empezar con 1 TaskManager y escalar después" — se despliegan los 3 TaskManagers de una. Postgres/TimescaleDB y Grafana comparten instancia (Grafana es liviano, Postgres no se expone a Internet, solo Grafana en el puerto 3000 y Flink UI en el 8081). El cliente (productor + verificación de consumo) es una sola instancia, no dos separadas como en `kafka-flink-streaming-lab`, para no sumar más EC2.

## Prerrequisitos

- Pulumi CLI y AWS CLI instalados.
- Credenciales de AWS Academy actualizadas en `~/.aws/credentials` (vencen cada "Start Lab").
- Un Key Pair llamado `audiencias-lab-key` creado en la consola de AWS (EC2 → Key Pairs), con el `.pem` guardado en `../keys/audiencias-lab-key.pem` (gitignored).

## Comandos

```bash
cd infra
pulumi preview
pulumi up
```

Para no reescribir la passphrase de secrets en cada comando:

```bash
export PULUMI_CONFIG_PASSPHRASE="tu-passphrase"
```

Al terminar `pulumi up`, revisa los outputs:

```bash
pulumi stack output
pulumi stack output flinkUiUrl
pulumi stack output grafanaUrl
```

Para destruir todo al terminar una sesión de trabajo (evitar consumir horas del Learner Lab sin usar):

```bash
pulumi destroy
```

## Estado del bootstrap

- **Kafka (KRaft):** idéntico al patrón validado en `kafka-flink-streaming-lab` — probado, funciona.
- **Flink:** nuevo en esta sesión. Usa `config.yaml` (formato YAML anidado de Flink 2.x, reemplaza al antiguo `flink-conf.yaml`). No validado todavía contra un cluster real — esperar necesitar debug la primera corrida.
- **Postgres/TimescaleDB + Grafana:** nuevo en esta sesión, instalación vía los repositorios oficiales (`apt.postgresql.org`, `packagecloud.io/timescale`, `apt.grafana.com`). Tampoco validado todavía.

Cada comando que se ejecute para levantar/depurar esto debe quedar documentado en el informe (`informe/`), con su evidencia — es la regla del proyecto.
