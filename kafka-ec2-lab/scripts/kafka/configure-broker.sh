#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# ARGUMENTOS
# ============================================================

if [[ "$#" -ne 3 ]]; then
    echo "Uso:"
    echo "  sudo $0 NODE_ID PRIVATE_IP CLUSTER_ID"
    echo
    echo "Ejemplo:"
    echo "  sudo $0 1 10.20.1.11 abcdefghijklmnopqrstuv"
    exit 1
fi


NODE_ID="$1"
PRIVATE_IP="$2"
CLUSTER_ID="$3"


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

KAFKA_HOME="/opt/kafka"
KAFKA_CONFIG_FILE="${KAFKA_HOME}/config/kraft/server.properties"
KAFKA_DATA_DIR="/var/lib/kafka/data"

KAFKA_USER="kafka"
KAFKA_GROUP="kafka"

BROKER_1_IP="10.20.1.11"
BROKER_2_IP="10.20.1.12"
BROKER_3_IP="10.20.1.13"

CONTROLLER_QUORUM_VOTERS="1@${BROKER_1_IP}:9093,2@${BROKER_2_IP}:9093,3@${BROKER_3_IP}:9093"


# ============================================================
# VALIDACIONES
# ============================================================

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: Este script debe ejecutarse con sudo."
    exit 1
fi

if [[ ! "${NODE_ID}" =~ ^[123]$ ]]; then
    echo "ERROR: NODE_ID debe ser 1, 2 o 3."
    exit 1
fi

if [[ ! -x "${KAFKA_HOME}/bin/kafka-storage.sh" ]]; then
    echo "ERROR: Kafka no se encuentra instalado en ${KAFKA_HOME}."
    exit 1
fi


echo "============================================================"
echo "Configurando Broker Kafka"
echo "Node ID: ${NODE_ID}"
echo "Private IP: ${PRIVATE_IP}"
echo "Cluster ID: ${CLUSTER_ID}"
echo "============================================================"


# ============================================================
# CONFIGURACIÓN KRAFT
# ============================================================

cat > "${KAFKA_CONFIG_FILE}" <<EOF
# ============================================================
# IDENTIDAD Y ROLES DEL NODO
# ============================================================

process.roles=broker,controller
node.id=${NODE_ID}


# ============================================================
# QUORUM KRAFT
# ============================================================

controller.quorum.voters=${CONTROLLER_QUORUM_VOTERS}
controller.listener.names=CONTROLLER


# ============================================================
# LISTENERS
# ============================================================

listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093

advertised.listeners=PLAINTEXT://${PRIVATE_IP}:9092

listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT

inter.broker.listener.name=PLAINTEXT


# ============================================================
# ALMACENAMIENTO
# ============================================================

log.dirs=${KAFKA_DATA_DIR}

num.partitions=3

default.replication.factor=3
min.insync.replicas=2


# ============================================================
# TOPICS INTERNOS
# ============================================================

offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2


# ============================================================
# RETENCIÓN Y SEGMENTOS
# ============================================================

log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000


# ============================================================
# RENDIMIENTO ADECUADO PARA LABORATORIO
# ============================================================

num.network.threads=3
num.io.threads=4
num.recovery.threads.per.data.dir=1
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600


# ============================================================
# CONFIGURACIONES GENERALES
# ============================================================

auto.create.topics.enable=false
delete.topic.enable=true
group.initial.rebalance.delay.ms=0
EOF


chown "${KAFKA_USER}:${KAFKA_GROUP}" "${KAFKA_CONFIG_FILE}"
chmod 640 "${KAFKA_CONFIG_FILE}"


# ============================================================
# FORMATEAR ALMACENAMIENTO KRAFT
# ============================================================

mkdir -p "${KAFKA_DATA_DIR}"

chown -R "${KAFKA_USER}:${KAFKA_GROUP}" "${KAFKA_DATA_DIR}"


if [[ -f "${KAFKA_DATA_DIR}/meta.properties" ]]; then
    echo
    echo "El almacenamiento ya está formateado."
    echo "No se volverá a ejecutar kafka-storage.sh format."
else
    echo
    echo "Formateando almacenamiento KRaft..."

    sudo -u "${KAFKA_USER}" \
        "${KAFKA_HOME}/bin/kafka-storage.sh" format \
        --cluster-id "${CLUSTER_ID}" \
        --config "${KAFKA_CONFIG_FILE}"
fi


# ============================================================
# SERVICIO SYSTEMD
# ============================================================

cat > /etc/systemd/system/kafka.service <<'EOF'
[Unit]
Description=Apache Kafka Server
Documentation=https://kafka.apache.org/
After=network-online.target
Wants=network-online.target

[Service]
Type=simple

User=kafka
Group=kafka

Environment="KAFKA_HEAP_OPTS=-Xms512m -Xmx512m"
Environment="KAFKA_JVM_PERFORMANCE_OPTS=-server"

ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/kraft/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh

Restart=on-failure
RestartSec=10

LimitNOFILE=100000

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF


systemctl daemon-reload
systemctl enable kafka


echo
echo "============================================================"
echo "Broker ${NODE_ID} configurado correctamente"
echo "Todavía no se iniciará Kafka automáticamente en este script."
echo "============================================================"