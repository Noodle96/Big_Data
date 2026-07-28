# Plataforma Inteligente para Simulación y Análisis de Audiencias Digitales en Tiempo Real

Trabajo Unidad II — Curso BigData 2026A, UNSA. Ver `plan.md` para el plan de trabajo completo (arquitectura, fases, índice del informe) y `requerimientos/requerimientos.pdf` para el enunciado original.

## Estructura del proyecto

- `requerimientos/` — enunciado oficial del trabajo (PDF).
- `informe/` — informe final en LaTeX (template de Pablo Pizarro). **No modificar** `template.tex` ni `template_config.tex`; solo `main.tex` y `contenido.tex`.
- `infra/` — infraestructura como código (Pulumi/Python) para el cluster de Kafka, Flink, PostgreSQL/TimescaleDB y Grafana en AWS Academy.
- `agentes-simulador/` — simulador de agentes autónomos + productores Kafka (Python, con type hints completos en todo).
- `flink-jobs/` — jobs de Apache Flink (Java/Maven): consumo, filtrado, enriquecimiento, agregación, clasificación de audiencias.
- `dashboard/` — provisioning de Grafana (datasources/paneles as code) y esquema de la base de datos.
- `scripts/` — scripts auxiliares (creación de topics, despliegue, utilidades).
- `docs/` — notas internas de desarrollo (decisiones, aprendizajes) que no forman parte del informe entregable.

## Reglas del proyecto

- Todo el código Python lleva anotaciones de tipo completas (variables, estructuras de datos, funciones, clases).
- El `informe/` nunca modifica el template — solo su contenido.
- Los diagramas genéricos/conceptuales del informe los genera el asistente; la evidencia real (capturas de consola, terminal, dashboard) la coloca Russell.
