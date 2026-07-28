# infra/

Infraestructura como código (Pulumi, Python) para AWS Academy — Fase 1 del `plan.md`.

Reutiliza el patrón validado en `kafka-flink-streaming-lab`: VPC, subnet, security groups, IPs privadas estáticas por instancia, bootstrap completo en `user_data` (sin SSH manual). Se extiende con instancias para el cluster de Flink (JobManager + TaskManager), PostgreSQL/TimescaleDB y Grafana.

Pendiente de implementar:

- `__main__.py` — definición de todos los recursos (VPC, EC2 por rol).
- `Pulumi.yaml` / `Pulumi.<stack>.yaml` — configuración del stack.
- `requirements.txt` — dependencias Python (con type hints en todo el código).
- `keys/` — par de llaves EC2 (gitignored, no se versiona).

Recordatorio: actualizar credenciales de AWS Academy (`Start Lab`) antes de cada `pulumi up`/`preview`/`refresh`.
