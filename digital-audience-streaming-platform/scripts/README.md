# scripts/

Scripts auxiliares del proyecto (no forman parte del informe entregable, pero sí se documentan/referencian desde él).

## kafka/

Creación declarativa de topics: `topics.yaml` define nombre, particiones, factor de replicación y config (retention, cleanup policy) de cada topic con una descripción de qué eventos recibe. `create_topics.py` lee ese YAML y los crea vía `kafka-python` (protocolo de Kafka directo, no necesita SSH a ningún broker ni tener el CLI de Kafka instalado localmente). Mismo patrón usado en `kafka-flink-streaming-lab` para no perder de vista qué se configuró.

```bash
cd scripts/kafka
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 create_topics.py --bootstrap-servers 10.30.1.11:9092,10.30.1.12:9092,10.30.1.13:9092
```
