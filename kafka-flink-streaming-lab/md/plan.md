# Plan: Laboratorio Kafka (rehecho) + Laboratorio 07 Flink

Curso: Big Data (UNSA) — Entrega combinada en un solo informe (template Pablo Pizarro, `informe/`).

## Contexto

- El laboratorio de Kafka se rehace desde cero porque la vez anterior se instaló y configuró Kafka manualmente por SSH y no quedó documentado (el docente preguntó por un detalle específico y no se pudo responder).
- El laboratorio de Flink es nuevo (`especificaciones/especificaciones.pdf`, Laboratorio 07).
- No es necesario mantener consistencia entre el esquema de eventos de ambos labs; se tratan como entregables independientes dentro del mismo informe.
- Ejecución manual: Russell corre todo (Pulumi, SSH, scripts); Claude entrega código e instrucciones.

## Requisitos a demostrar

**Kafka (EC2, pedido original del docente):** Producer, Consumer, Topic, Partition, Offset, Consumer Group.

**Flink (especificaciones.pdf, Laboratorio 07):**
- 2.1 Preparar Flink para consumir eventos desde Kafka (proyecto Maven, dependencias Flink + conector Kafka, Consumer).
- 2.2 Filtrar eventos de compra (`purchase`, `add_cart`).
- 2.3 Transformar: agregar atributos derivados (hora, día, mes, fin de semana).
- 2.4 Conteo de eventos (búsquedas, compras, vistas, agregados al carrito).
- 2.5 Agrupamiento por producto (mayor actividad).

Entregable final: PDF con nombre del alumno, subido manualmente al aula virtual/classroom.

## Estructura de carpetas acordada

```
kafka-flink-streaming-lab/
├── especificaciones/        # PDFs de los enunciados
├── informe/                 # LaTeX (template intacto, solo main.tex + contenido.tex)
├── infrastructure/          # Proyecto Pulumi (Python) — VPC, SG, 3 brokers + cliente EC2
├── keys/                    # kafka-lab-key.pem
├── topics.yaml              # Definición declarativa de topics (nombre, particiones, réplicas)
├── producer/                # producer.py
├── consumer/                # consumer.py (parametrizable --group-id para demo de consumer groups)
├── flink-job/                # Proyecto Maven para el Laboratorio 07
├── scripts/                  # Utilidades CLI (crear topics, describir, monitorear grupos)
├── docs/
│   └── images/                # Diagramas generados (arquitectura, flujo) — no evidencia
├── md/                        # Notas y planes (este archivo)
└── README.md
```

**Nota sobre evidencia (capturas):** el template LaTeX carga imágenes desde `informe/img/` (`\defaultimagefolder {img/}`). Para que `\insertimage{...}` nunca falle por ruta incorrecta, **toda** captura/evidencia que vaya a citarse en el informe se guarda directamente en `informe/img/kafka/` (ya creada), no en `docs/evidence/`. `docs/images/` queda solo para diagramas genéricos fuera del informe (ej. README).

## Plan paso a paso

### Fase 0 — Scaffolding
1. Crear `infrastructure/` y correr `pulumi new aws-python` (crea venv, `Pulumi.yaml`, `__main__.py`, `requirements.txt` automáticamente).
2. Adaptar el `main.py` existente (arquitectura VPC/subnet/SG/instancias con IP privada fija se mantiene igual) y **extender `user_data`** para que además:
   - Instale Java (Kafka 3.9.0 requiere Java 11+; se usará Java 17).
   - Descargue e instale el binario de Kafka.
   - Genere `server.properties` por nodo en modo KRaft (`broker.id`, `process.roles`, `controller.quorum.voters` con las 3 IPs privadas ya conocidas, listeners 9092/9093).
   - Formatee el storage (`kafka-storage.sh format`) con un `CLUSTER_ID` fijo generado una sola vez (para que sea reproducible y quede documentado).
   - Registre Kafka como servicio `systemd`.
3. Mover `kafka-lab-key.pem` a `keys/` (Russell) y ajustar la referencia en el código.
4. Crear `topics.yaml` con el topic principal (`ecommerce-events`, 3 particiones, factor de replicación 3) y su script de creación.

### Fase 1 — Deploy
5. Correr `pulumi up`.
6. Verificar por SSH que el servicio Kafka esté activo en los 3 brokers (`systemctl status kafka`) — primera evidencia documentada.

### Fase 2 — Demostrar conceptos Kafka
7. Crear el topic → evidencia de **Topic** y **Partition**.
8. Correr `producer.py` en el cliente → evidencia de **Producer**.
9. Correr `consumer.py` → evidencia de **Consumer**; usar `kafka-consumer-groups.sh --describe` → evidencia de **Offset**.
10. Levantar 2 instancias de `consumer.py` con el mismo `--group-id` → evidencia de **Consumer Group** (rebalanceo de particiones).

### Fase 3 — Informe (sección Kafka)
11. Con la evidencia guardada en `informe/img/kafka/`, escribir la sección Kafka en `informe/contenido.tex`. Diagramas genéricos (arquitectura) los genera Claude; capturas específicas (consola AWS, terminal) las inserta Russell manualmente en esa misma carpeta.

### Fase 4 — Flink
12. Implementar el proyecto Maven en `flink-job/` cubriendo 2.1 a 2.5 de la guía.
13. Escribir la sección Flink del informe.

### Fase 5 — Cierre
14. Compilar el PDF final y revisar contra ambas guías antes de que Russell suba manualmente a GitHub y al aula virtual.

## Defaults asumidos (corregir si no aplican)

- Kafka 3.9.0 (Scala 2.13), Java 17.
- Topic principal: `ecommerce-events`, 3 particiones, factor de replicación 3.
- `CLUSTER_ID` fijo, generado una vez y hardcodeado en el código de infraestructura: `X2k7a_8UT5i145WnsLy8qQ`.

## Registro de ejecución (se va actualizando)

- **Infraestructura desplegada** con `pulumi up` (stack `academy`, región `us-east-1`), 15 recursos creados.
  - VPC `vpc-0ac7a74587bd395fe`, subnet `subnet-0f7d37a4f1af56e30`, SG `sg-0f0a0b786b3352275`.
  - broker-1: privada `10.20.1.11` / pública `50.16.10.123`
  - broker-2: privada `10.20.1.12` / pública `54.89.42.95`
  - broker-3: privada `10.20.1.13` / pública `54.90.152.95`
  - client: privada `10.20.1.20` / pública `100.54.236.99`
  - `controller.quorum.voters`: `1@10.20.1.11:9093,2@10.20.1.12:9093,3@10.20.1.13:9093`
- **Pendiente:** verificar `systemctl status kafka` en los 3 brokers y capturar evidencia en `informe/img/kafka/` (`brokerN-systemctl-status.png`, `brokerN-journalctl.png`).

Nota: las IPs públicas cambian si se destruye/recrea el stack (`pulumi destroy` + `pulumi up`); las privadas son fijas mientras no se cambie el código.
