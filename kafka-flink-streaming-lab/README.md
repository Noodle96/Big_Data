# Kafka + Flink Streaming Lab

## Descripción

Este proyecto tiene como objetivo implementar una arquitectura distribuida para el procesamiento de eventos en tiempo real utilizando Apache Kafka y Apache Flink sobre infraestructura desplegada en AWS mediante Pulumi.

Durante el desarrollo del laboratorio no solo se implementará la solución funcional, sino que también se documentará detalladamente cada componente, su configuración y la interacción entre ellos, con el propósito de comprender el funcionamiento interno de una arquitectura de procesamiento de datos en streaming.

---

## Tecnologías

- Apache Kafka
- Apache Flink
- AWS EC2
- Pulumi
- Python
- Java
- Maven

---

## Arquitectura objetivo

- 3 Brokers Apache Kafka (KRaft)
- 1 Cliente Kafka
- 1 JobManager Flink
- 2 TaskManagers Flink


La solución implementará una arquitectura distribuida para el procesamiento de eventos en tiempo real.

```text
Producer / Client
        │
        ▼
Apache Kafka Cluster
 (3 Brokers)
        │
        ▼
Apache Flink Cluster
(JobManager + 2 TaskManagers)
        │
        ▼

---

## Objetivos

- Implementar un clúster distribuido de Apache Kafka.
- Implementar un clúster distribuido de Apache Flink.
- Integrar Apache Flink con Apache Kafka.
- Procesar eventos en tiempo real.
- Aplicar transformaciones sobre flujos de datos.
- Comprender la arquitectura completa de procesamiento de eventos.

---

## Estado del proyecto

### ✔ Etapa 1

- [x] Definición de la arquitectura.
- [x] Organización del proyecto.
- [ ] Infraestructura AWS.
- [ ] Instalación de Kafka.
- [ ] Configuración de Kafka.
- [ ] Instalación de Flink.
- [ ] Integración Kafka + Flink.
- [ ] Procesamiento de eventos.

---

## Estructura del proyecto

```text
kafka-flink-streaming-lab/

├── infrastructure/
├── producer/
├── consumer/
├── flink-job/
├── scripts/
│   ├── kafka/
│   └── flink/
├── docs/
└── README.md
```

---

## Autor

Proyecto desarrollado como laboratorio de procesamiento distribuido de eventos utilizando Apache Kafka y Apache Flink.