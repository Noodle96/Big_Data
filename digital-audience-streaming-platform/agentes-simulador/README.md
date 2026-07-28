# agentes-simulador/

Simulador de agentes autónomos + productores Kafka (Python). Fase 2 del `plan.md`. Todo el código lleva type hints completos (variables, estructuras de datos, funciones, clases).

## Estructura prevista

- `src/agentes/` — un módulo por perfil (o una clase base + 8 subclases): comprador compulsivo, comparador, comprador nocturno, cliente premium, cliente frecuente, usuario explorador, cliente indeciso, cliente estacional.
- `src/productores/` — wrapper del productor Kafka (serialización JSON, ruteo a topics).
- `src/escenarios/` — definición de escenarios comerciales (Navidad, Cyber Monday, Black Friday, Día del Padre, Fiestas Patrias, Campaña Escolar) que modulan el comportamiento global de los agentes.
- `src/main.py` — punto de entrada: arranca N agentes concurrentes bajo un escenario dado.
- `tests/` — pruebas unitarias del motor de simulación y de cada perfil.
- `requirements.txt` — dependencias (ej. `confluent-kafka` o `kafka-python`, `pydantic` para el esquema de eventos).
