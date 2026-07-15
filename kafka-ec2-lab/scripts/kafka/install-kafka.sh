#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# CONFIGURACIÓN
# ============================================================

KAFKA_VERSION="4.3.1"
SCALA_VERSION="2.13"

KAFKA_ARCHIVE="kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz"
KAFKA_DOWNLOAD_URL="https://downloads.apache.org/kafka/${KAFKA_VERSION}/${KAFKA_ARCHIVE}"

KAFKA_INSTALL_DIR="/opt/kafka"
KAFKA_DATA_DIR="/var/lib/kafka/data"
KAFKA_LOG_DIR="/var/log/kafka"
KAFKA_USER="kafka"
KAFKA_GROUP="kafka"


# ============================================================
# VALIDACIÓN
# ============================================================

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: Este script debe ejecutarse con sudo."
    exit 1
fi


echo "============================================================"
echo "Instalando Java y Apache Kafka"
echo "Hostname: $(hostname)"
echo "============================================================"


# ============================================================
# INSTALAR JAVA Y HERRAMIENTAS
# ============================================================

export DEBIAN_FRONTEND=noninteractive

apt-get update -y

apt-get install -y \
    openjdk-17-jdk-headless \
    curl \
    wget \
    tar \
    jq


echo
echo "Versión de Java:"
java -version


# ============================================================
# CREAR USUARIO KAFKA
# ============================================================

if ! getent group "${KAFKA_GROUP}" >/dev/null; then
    groupadd --system "${KAFKA_GROUP}"
fi

if ! id "${KAFKA_USER}" >/dev/null 2>&1; then
    useradd \
        --system \
        --gid "${KAFKA_GROUP}" \
        --home-dir "${KAFKA_INSTALL_DIR}" \
        --shell /usr/sbin/nologin \
        "${KAFKA_USER}"
fi


# ============================================================
# DESCARGAR E INSTALAR KAFKA
# ============================================================

if [[ ! -x "${KAFKA_INSTALL_DIR}/bin/kafka-server-start.sh" ]]; then
    echo
    echo "Descargando ${KAFKA_DOWNLOAD_URL}"

    cd /tmp

    wget \
        --progress=dot:giga \
        --output-document="${KAFKA_ARCHIVE}" \
        "${KAFKA_DOWNLOAD_URL}"

    rm -rf "/tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION}"

    tar -xzf "${KAFKA_ARCHIVE}"

    rm -rf "${KAFKA_INSTALL_DIR}"

    mv \
        "/tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION}" \
        "${KAFKA_INSTALL_DIR}"

    rm -f "/tmp/${KAFKA_ARCHIVE}"
else
    echo "Kafka ya está instalado en ${KAFKA_INSTALL_DIR}."
fi


# ============================================================
# CREAR DIRECTORIOS
# ============================================================

mkdir -p \
    "${KAFKA_DATA_DIR}" \
    "${KAFKA_LOG_DIR}" \
    "${KAFKA_INSTALL_DIR}/config/kraft"


chown -R "${KAFKA_USER}:${KAFKA_GROUP}" \
    "${KAFKA_INSTALL_DIR}" \
    "${KAFKA_DATA_DIR}" \
    "${KAFKA_LOG_DIR}"


# ============================================================
# AGREGAR BINARIOS AL PATH
# ============================================================

cat > /etc/profile.d/kafka.sh <<EOF
export KAFKA_HOME=${KAFKA_INSTALL_DIR}
export PATH=\${PATH}:\${KAFKA_HOME}/bin
EOF

chmod 644 /etc/profile.d/kafka.sh


# ============================================================
# RESULTADO
# ============================================================

echo
echo "============================================================"
echo "Instalación finalizada correctamente"
echo "Kafka: ${KAFKA_VERSION}"
echo "Directorio: ${KAFKA_INSTALL_DIR}"
echo "Datos: ${KAFKA_DATA_DIR}"
echo "============================================================"

"${KAFKA_INSTALL_DIR}/bin/kafka-topics.sh" --version