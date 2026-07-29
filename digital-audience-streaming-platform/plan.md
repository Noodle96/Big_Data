# Plan de trabajo — Plataforma Inteligente para Simulación y Análisis de Audiencias Digitales en Tiempo Real

**Curso:** BigData 2026A — UNSA · **Trabajo:** Unidad II (Arquitecturas Orientadas a Eventos) · **Entregable oficial:** PDF (`requerimientos/requerimientos.pdf`)

Este documento es el plan de trabajo, no el informe. Sirve para no perder de vista el alcance completo y para que el `informe/` (LaTeX, template de Pablo Pizarro) se vaya llenando en el mismo orden en que se construye el sistema. Se actualiza a medida que avanzamos.

---

## 0. Decisiones de arquitectura ya tomadas

| Decisión | Elegido | Motivo |
|---|---|---|
| Despliegue de Flink | **Cluster real** (JobManager + TaskManager en EC2) | Más fiel a un entorno productivo, permite mostrar Web UI, checkpoints y paralelismo real en el informe |
| Infraestructura | **AWS Academy + Pulumi** | Reutiliza el patrón ya validado en `kafka-flink-streaming-lab` (VPC, IPs privadas estáticas, bootstrap en `user_data`, KRaft) |
| Dashboard | **Grafana + base de series de tiempo** | Menos código propio, paneles y alertas por umbral ya integrados, se ve profesional rápido |
| Base de datos para el dashboard | **PostgreSQL + extensión TimescaleDB** (a confirmar si se usa InfluxDB en su lugar) | Postgres es más universal que Influx para documentar en una guía, tiene sink JDBC directo desde Flink, y TimescaleDB da lo esencial de series de tiempo sin aprender un lenguaje de consulta nuevo (Flux) |
| Lenguaje del simulador/producers | **Python, con type hints obligatorios en todo** (variables, estructuras, funciones, clases) | Regla explícita de Russell, ver memoria `feedback-python-type-annotations` |
| Lenguaje de los jobs de Flink | **Java** (Maven), igual que en `kafka-flink-streaming-lab` | Stack ya validado (Flink 2.2.1, `flink-connector-kafka` 5.0.0-2.2, `flink-connector-base` explícito, Java 11) |
| Convención comando + evidencia en el informe | `\inlinesourcecodeboxed[cmdbg]{bash}{<comando>}` seguido de `\insertimage[...]{...}{...}{<descripción con el comando>}`, sin prefijo `$` | Definida y probada en esta misma sesión — ver plantilla al inicio de `informe/contenido.tex` |
| Regla de imágenes en el informe | Diagramas genéricos/conceptuales los genero yo (tikz); evidencia real (capturas de consola AWS, terminal, Grafana en vivo) las coloca Russell | Ya establecida en el laboratorio anterior |

---

## 1. Arquitectura general del sistema

```
Agentes autónomos (8 perfiles)
        │  generan eventos (login, view, cart, purchase, ...)
        ▼
Productores Kafka (Python)
        │  publican JSON en topics particionados
        ▼
Apache Kafka (cluster, 3 brokers KRaft)
        │  topics: user-events, purchase-events, iot/system-events, ...
        ▼
Apache Flink (cluster: JobManager + TaskManager)
        │  filtra, enriquece, agrega por ventanas, clasifica audiencias
        ▼
PostgreSQL/TimescaleDB
        │  tablas de métricas y audiencias, actualizadas continuamente
        ▼
Grafana
        │  paneles con auto-refresh + alertas por umbral
        ▼
Usuario / evaluador (navegador)
```

Este diagrama (versión más elaborada, con VPC/EC2 por componente) es el primer gráfico que preparo para el informe, sección "Arquitectura de la solución".

---

## 2. Fases de implementación

### Fase 1 — Infraestructura base (Pulumi / AWS Academy) ✅ (desplegada y verificada 2026-07-28)

`pulumi up` corrió sin problemas: 8 instancias creadas, y tras esperar el cloud-init, los 8 servicios confirmados `active` por SSH (3× `kafka`, `flink-jobmanager`, 3× `flink-taskmanager`, `postgresql`, `grafana-server`). El JobManager registró correctamente los 3 TaskManagers (verificado en su log). Único hallazgo: los TaskManagers 2 y 3 mostraron reintentos de conexión al arrancar antes que el JobManager (condición de carrera normal en cloud-init paralelo), resuelto solo por el mecanismo de reintento de Flink — sin intervención manual. Pendiente confirmar la extensión TimescaleDB con `psql -c '\dx'`. Todo el detalle de comandos + outputs de esta verificación ya está listo para pasar al informe.

- Scaffold creado manualmente por Russell con `pulumi new aws-python` en `infra/` (stack `academy2`, región `us-east-1`), `__main__.py` reemplazado con el cluster completo.
- Topología final (8 EC2, todas `t3.small`): 3 brokers Kafka KRaft (patrón validado, reutilizado tal cual), 1 JobManager + **3 TaskManagers de Flink de una** (decisión explícita de Russell: no arrancar con 1 y escalar después), 1 instancia con PostgreSQL 16 + TimescaleDB + Grafana co-ubicados (aceptado: Grafana es liviano, Postgres no se expone a Internet).
- Bootstrap 100% en `user_data` (nada de SSH manual). El de Kafka está probado; el de Flink (usa `config.yaml`, el formato YAML anidado nuevo de Flink 2.x, no el viejo `flink-conf.yaml`) y el de Postgres/TimescaleDB/Grafana son nuevos, sin validar contra un cluster real todavía — esperar debug en el primer `pulumi up`.
- Detalle completo en `infra/README.md`.
- Actualizar credenciales de AWS Academy antes de cada sesión de trabajo (gotcha ya conocido).
- **Va al informe:** diagrama de red, tabla de instancias (rol / tipo / IP privada), comandos `pulumi up`/`preview` con su evidencia — TODOS los comandos ejecutados, sin excepción (regla reforzada 2026-07-24).

### Fase 2 — Simulador de agentes + Productores Kafka ✅ (avance inicial integrado 2026-07-24)

- Base de código aportada por un compañero de equipo, integrada en `agentes-simulador/src/` con type hints completos, `key=user_id` en el producer, override `FORCED_SEASON` y los 6 escenarios del enunciado. Detalle en `agentes-simulador/README.md` y en la memoria `project-companero-simulador`. Pendiente: apuntar `BOOTSTRAP_SERVERS` a nuestros brokers reales (Fase 1) y correrlo contra un cluster real.
- Implementar los 8 perfiles obligatorios como clases Python con type hints completos:

  | Agente | Comportamiento clave a modelar |
  |---|---|
  | Comprador compulsivo | Compra rápido, pocos productos consultados, alta probabilidad de compra, poco tiempo de navegación |
  | Comparador | Consulta muchos productos, compara precios, compra ocasional |
  | Comprador nocturno | Actividad solo en horario nocturno |
  | Cliente Premium | Compras poco frecuentes pero de alto valor |
  | Cliente frecuente | Compra constantemente |
  | Usuario explorador | Navega mucho, nunca compra |
  | Cliente indeciso | Agrega/elimina productos del carrito repetidamente |
  | Cliente estacional | Cambia de comportamiento según el evento comercial activo (Navidad, Cyber Monday, Black Friday, Día del Padre, Fiestas Patrias, Campaña Escolar) |

- Motor de simulación: bucle temporal, N agentes concurrentes (asyncio o threads), reloj simulado o real, capacidad de "activar" un escenario/evento comercial que module el comportamiento global (no solo del agente estacional).
- Productores Kafka: serializan a JSON, publican según el tipo de evento al topic correspondiente.
- **Va al informe:** tabla de perfiles (arriba), diagrama de flujo del simulador, fragmentos de código relevantes (no el código completo — eso va a Anexos si aplica), evidencia de eventos llegando a Kafka.

### Fase 3 — Kafka: topics y particiones ✅ (decidido 2026-07-24)

- Esquema final: **2 topics por semántica de negocio** (no por canal ni uno solo), decidido tras integrar el simulador:

  | Topic | Contenido | Particiones | Clave de partición |
  |---|---|---|---|
  | `user-events` | SEARCH, VIEW_PRODUCT (navegación) | 3 | `user_id` |
  | `purchase-events` | ADD_CART, PURCHASE, PAYMENT_REJECTED (conversión) | 3 | `user_id` |

  `iot-events`/`system-events` quedan descartados por ahora: los canales IoT/Vehicle del simulador son canales de *compra*, no telemetría real de sensores — crear un topic vacío no aporta al informe. Se agregaría solo si más adelante se generan eventos de sensores de verdad.

- **Va al informe:** tabla final de topics/particiones/claves (arriba), comandos `kafka-topics.sh --create`/`--describe` con evidencia, y una breve justificación de por qué 2 topics y no 1 ni 4 (buen contenido de análisis).

### Fase 4 — Apache Flink: cluster y jobs

- Deploy del cluster: `start-cluster.sh` o EC2 dedicados a JobManager/TaskManager, verificación por Web UI.
- Jobs (uno o varios, a definir): consumo de topics → filtrado (purchase/add_cart, etc.) → enriquecimiento (hora, día, mes, fin de semana) → ventanas de tiempo → conteo/agregación → clasificación en audiencias.
- Sink hacia PostgreSQL/TimescaleDB (vía `flink-connector-jdbc`).
- **Va al informe:** diagrama JobManager/TaskManager, descripción de cada job, evidencia de envío (`flink run`), capturas de la Web UI, logs relevantes.

### Fase 5 — Audiencias digitales (reglas de negocio)

- Reglas a definir con tabla explícita, por ejemplo:

  | Audiencia | Regla (borrador, ajustar en la fase) | Umbral |
  |---|---|---|
  | Usuarios con alta intención de compra | ≥N vistas de producto + ≥1 carrito en ventana de M minutos | a definir |
  | Clientes frecuentes | ≥N compras en ventana de M días/horas simuladas | a definir |
  | Usuarios que abandonaron el carrito | Evento `add_cart` sin `purchase` en ventana de M minutos | a definir |
  | Clientes Premium | Compra de monto ≥ X | a definir |
  | Usuarios con riesgo de abandono | Navegación sin interacción reciente | a definir |

- **Va al informe:** tabla final de reglas, evidencia de clasificación (registros/consultas mostrando usuarios etiquetados).

### Fase 6 — Dashboard en tiempo real (Grafana)

- Modelo de datos en Postgres/TimescaleDB: una tabla o vista por bloque de métrica pedido.
- Provisioning de Grafana as code (datasources + dashboards en JSON/YAML, no clicks manuales — mejor para la guía).
- Paneles requeridos por el enunciado, uno a uno:

  | Métrica pedida | Tipo de panel sugerido |
  |---|---|
  | Usuarios activos | Stat / contador |
  | Eventos por segundo | Gráfico de línea |
  | Eventos por tipo | Barras o pie |
  | Audiencias detectadas | Tabla |
  | Productos más visitados | Barras horizontales (top N) |
  | Productos más comprados | Barras horizontales (top N) |
  | Compras por región | Mapa o barras por ciudad |
  | Tendencias temporales | Serie de tiempo |
  | Conversión de compras | Gauge / stat con porcentaje |
  | Alertas | Panel de alertas de Grafana (umbral) |

- **Va al informe:** diagrama ER simple de las tablas en Postgres, tabla métrica→panel (arriba), capturas del dashboard en vivo (varias, agrupadas por bloque de métricas).

### Fase 7 — Ejecución de escenarios y análisis

- Definir al menos 3–4 corridas: día normal, Navidad, Cyber Monday, Fiestas Patrias (mínimo indicado por el enunciado; se puede sumar Black Friday/Día del Padre/Campaña Escolar si el tiempo alcanza).
- Cada corrida: activar el escenario en el simulador, dejar correr un tiempo fijo, capturar el dashboard, exportar métricas clave.
- **Va al informe:** tabla comparativa entre escenarios, gráficos exportados de Grafana por escenario, análisis/discusión en prosa.

### Fase 8 — Cierre del informe

- Redacción de introducción/marco conceptual (breve, en palabras propias, citando lo necesario).
- Revisión de índices (Índice de Códigos/Figuras/Tablas del template).
- Conclusiones.
- Exportar PDF final, subir a classroom/aula virtual antes del plazo del profesor.

---

## 3. Índice propuesto del informe (`informe/contenido.tex`)

1. **Introducción / Marco conceptual** — resumen breve de EDA, Event Streaming, Kafka, Flink, Audiencias digitales (en palabras propias). 1 diagrama conceptual genérico.
2. **Arquitectura de la solución** — diagrama general (sección 1 de este plan), tabla de componentes y su rol, justificación de decisiones (cluster real, Grafana, etc.).
3. **Infraestructura (Pulumi/AWS)** — diagrama de red, tabla de instancias EC2, evidencia de despliegue.
4. **Simulador de agentes** — tabla de los 8 perfiles, diagrama de flujo del simulador, fragmentos de código, evidencia de ejecución.
5. **Productores y esquema de eventos** — esquema JSON documentado (tabla de campos), evidencia de eventos en Kafka.
6. **Kafka: topics y particiones** — tabla topic/particiones/clave, evidencia de creación y verificación.
7. **Apache Flink: cluster y jobs** — diagrama JobManager/TaskManager, descripción de jobs, evidencia de despliegue y ejecución.
8. **Audiencias digitales (reglas de negocio)** — tabla regla→audiencia→umbral, evidencia de clasificación.
9. **Dashboard en tiempo real (Grafana)** — diagrama ER, tabla métrica→panel, capturas del dashboard en vivo.
10. **Escenarios ejecutados y análisis de resultados** — tabla comparativa, gráficos por escenario, discusión.
11. **Conclusiones**
12. **Anexos** (si aplica: código completo de piezas clave)
13. **Referencias**

Cada sección de la 3 a la 9 se escribe siguiendo la convención comando+evidencia ya definida (plantilla al inicio de `contenido.tex`), de modo que el informe funcione como guía reproducible paso a paso.

---

## 4. Gráficos a preparar (quién los hace)

| Gráfico/diagrama | Quién lo genera | Notas |
|---|---|---|
| Arquitectura general (Agentes→Kafka→Flink→DB→Grafana) | Yo (tikz) | Genérico, no depende de una corrida específica |
| Diagrama de red/infra (VPC, EC2 por rol) | Yo (tikz) | Basado en lo que finalmente se despliegue |
| Diagrama de flujo del simulador de agentes | Yo (tikz) | Conceptual |
| Diagrama JobManager/TaskManager | Yo (tikz) | Conceptual |
| Diagrama ER de Postgres/TimescaleDB | Yo (tikz o tabla) | Depende del modelo final de datos |
| Capturas de consola AWS, terminal, Web UI de Flink, Grafana en vivo | Russell | Evidencia real de una corrida — no se fabrica |

---

## 5. Reglas ya establecidas (no repetir en cada fase, aplican siempre)

- **No modificar** `template.tex` ni `template_config.tex` del informe — solo `main.tex` (metadata/paquetes extra) y `contenido.tex` (contenido).
- Lenguaje de `sourcecode` para texto plano/log es `plaintext`, nunca `text`.
- Comando + evidencia: `\inlinesourcecodeboxed[cmdbg]{bash}{<comando>}` + `\insertimage[...]{...}{scale=0.12}{<descripción con el comando>}`, **sin** prefijo `$`.
- Todo el código Python lleva type hints completos (variables, estructuras de datos, funciones, clases).
- Diagramas genéricos los hago yo; evidencia real la coloca Russell.

---

## 6. Próximos pasos inmediatos

1. Crear la estructura base de carpetas del proyecto (sección siguiente de este mensaje).
2. Empezar por la Fase 1 (infraestructura) reutilizando el `__main__.py` de Pulumi validado en `kafka-flink-streaming-lab`, extendiéndolo con Flink/Postgres/Grafana.
3. En paralelo, se puede avanzar la Fase 2 (simulador de agentes) sin depender de que la infraestructura esté arriba, usando Kafka local (Docker) para probar antes de desplegar en AWS.
