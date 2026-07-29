from typing import Final

import pulumi
import pulumi_aws as aws


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_NAME: Final[str] = "audiencias-streaming-infra"
AWS_REGION: Final[str] = aws.config.region or "us-east-1"

# Este nombre debe coincidir con el Key Pair registrado en AWS.
# El archivo privado local va en ../keys/audiencias-lab-key.pem (gitignored)
# TODO: crear este Key Pair en la consola de AWS Academy antes de `pulumi up`.
KEY_NAME: Final[str] = "audiencias-lab-key"

INSTANCE_TYPE: Final[str] = "t3.small"

VPC_CIDR: Final[str] = "10.30.0.0/16"
PUBLIC_SUBNET_CIDR: Final[str] = "10.30.1.0/24"

# IPs privadas estáticas — mismo patrón que kafka-flink-streaming-lab
BROKER_1_PRIVATE_IP: Final[str] = "10.30.1.11"
BROKER_2_PRIVATE_IP: Final[str] = "10.30.1.12"
BROKER_3_PRIVATE_IP: Final[str] = "10.30.1.13"

JOBMANAGER_PRIVATE_IP: Final[str] = "10.30.1.21"
TASKMANAGER_1_PRIVATE_IP: Final[str] = "10.30.1.22"
TASKMANAGER_2_PRIVATE_IP: Final[str] = "10.30.1.23"
TASKMANAGER_3_PRIVATE_IP: Final[str] = "10.30.1.24"
TASKMANAGER_PRIVATE_IPS: Final[list[str]] = [
    TASKMANAGER_1_PRIVATE_IP,
    TASKMANAGER_2_PRIVATE_IP,
    TASKMANAGER_3_PRIVATE_IP,
]

# Postgres/TimescaleDB + Grafana, co-ubicados en la misma instancia
DASHBOARD_PRIVATE_IP: Final[str] = "10.30.1.30"

# Cliente: corre el simulador de agentes (Fase 2) y scripts/kafka/create_topics.py.
# Rol único (productor + verificación de consumo), no separado en dos
# instancias como en kafka-flink-streaming-lab, para no sumar más EC2.
CLIENT_PRIVATE_IP: Final[str] = "10.30.1.40"

# Repositorio del proyecto -- se clona en la instancia cliente durante el
# bootstrap para tener el simulador y los scripts listos sin copiarlos a mano.
PROJECT_REPO_URL: Final[str] = "https://github.com/Noodle96/Big_Data.git"
PROJECT_REPO_SUBDIR: Final[str] = "digital-audience-streaming-platform"

COMMON_TAGS: Final[dict[str, str]] = {
    "Project": PROJECT_NAME,
    "Environment": "academy-lab",
    "ManagedBy": "Pulumi",
}


# ============================================================
# CONFIGURACIÓN DE KAFKA (KRaft, sin Zookeeper)
# Idéntico al patrón validado en kafka-flink-streaming-lab.
# ============================================================

KAFKA_VERSION: Final[str] = "3.9.0"
KAFKA_SCALA_VERSION: Final[str] = "2.13"
KAFKA_DIST_NAME: Final[str] = f"kafka_{KAFKA_SCALA_VERSION}-{KAFKA_VERSION}"
KAFKA_DOWNLOAD_URL: Final[str] = (
    f"https://archive.apache.org/dist/kafka/{KAFKA_VERSION}/{KAFKA_DIST_NAME}.tgz"
)

BROKER_PORT: Final[int] = 9092
CONTROLLER_PORT: Final[int] = 9093

# Generado UNA sola vez con:
#   python3 -c "import uuid,base64; print(base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip('='))"
KAFKA_CLUSTER_ID: Final[str] = "Q9m3p_7XKt825FpQrTn4wZ"

BROKER_NODE_IDS: Final[dict[str, int]] = {
    BROKER_1_PRIVATE_IP: 1,
    BROKER_2_PRIVATE_IP: 2,
    BROKER_3_PRIVATE_IP: 3,
}


def _controller_quorum_voters() -> str:
    return ",".join(
        f"{node_id}@{ip}:{CONTROLLER_PORT}"
        for ip, node_id in BROKER_NODE_IDS.items()
    )


CONTROLLER_QUORUM_VOTERS: Final[str] = _controller_quorum_voters()


# ============================================================
# CONFIGURACIÓN DE FLINK (cluster real: JobManager + TaskManagers)
# ============================================================
# IMPORTANTE: Flink 2.x cambió el archivo de configuración de
# "flink-conf.yaml" (pares clave-valor planos) a "config.yaml" (YAML
# anidado). Ver https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/config/

FLINK_VERSION: Final[str] = "2.2.1"
FLINK_SCALA_VERSION: Final[str] = "2.12"
FLINK_DIST_NAME: Final[str] = f"flink-{FLINK_VERSION}"
FLINK_DOWNLOAD_URL: Final[str] = (
    f"https://archive.apache.org/dist/flink/{FLINK_DIST_NAME}/"
    f"{FLINK_DIST_NAME}-bin-scala_{FLINK_SCALA_VERSION}.tgz"
)

FLINK_RPC_PORT: Final[int] = 6123
FLINK_UI_PORT: Final[int] = 8081
FLINK_TASKMANAGER_SLOTS: Final[int] = 2
FLINK_JOBMANAGER_MEMORY: Final[str] = "1600m"
FLINK_TASKMANAGER_MEMORY: Final[str] = "1728m"


# ============================================================
# CONFIGURACIÓN DE POSTGRES/TIMESCALEDB + GRAFANA
# ============================================================
# NOTA: password en texto plano a propósito, para mantener el mismo
# patrón de templating simple (.replace()) que el resto del archivo, sin
# mezclar pulumi.Config secrets (que devuelven Output y requieren
# .apply()). Aceptable acá porque Postgres NO se expone a Internet, solo
# es alcanzable dentro de la VPC. Cámbiala si haces esto en un contexto real.
POSTGRES_PORT: Final[int] = 5432
POSTGRES_DB: Final[str] = "audiencias"
POSTGRES_USER: Final[str] = "flink"
POSTGRES_PASSWORD: Final[str] = "AudienciasLab2026!"

GRAFANA_PORT: Final[int] = 3000


# ============================================================
# AMI UBUNTU 24.04 LTS
# ============================================================

ubuntu_ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"],
        ),
        aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
        aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
        aws.ec2.GetAmiFilterArgs(name="root-device-type", values=["ebs"]),
    ],
)


# ============================================================
# VPC, INTERNET GATEWAY, SUBRED, TABLA DE RUTAS
# ============================================================

vpc = aws.ec2.Vpc(
    resource_name="audiencias-lab-vpc",
    cidr_block=VPC_CIDR,
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={**COMMON_TAGS, "Name": "audiencias-lab-vpc"},
)

internet_gateway = aws.ec2.InternetGateway(
    resource_name="audiencias-lab-internet-gateway",
    vpc_id=vpc.id,
    tags={**COMMON_TAGS, "Name": "audiencias-lab-internet-gateway"},
)

availability_zones = aws.get_availability_zones(state="available")

public_subnet = aws.ec2.Subnet(
    resource_name="audiencias-lab-public-subnet",
    vpc_id=vpc.id,
    cidr_block=PUBLIC_SUBNET_CIDR,
    availability_zone=availability_zones.names[0],
    map_public_ip_on_launch=True,
    tags={**COMMON_TAGS, "Name": "audiencias-lab-public-subnet"},
)

public_route_table = aws.ec2.RouteTable(
    resource_name="audiencias-lab-public-route-table",
    vpc_id=vpc.id,
    tags={**COMMON_TAGS, "Name": "audiencias-lab-public-route-table"},
)

default_internet_route = aws.ec2.Route(
    resource_name="audiencias-lab-default-internet-route",
    route_table_id=public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id,
)

public_route_table_association = aws.ec2.RouteTableAssociation(
    resource_name="audiencias-lab-public-route-table-association",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id,
)


# ============================================================
# SECURITY GROUP
# ============================================================

lab_security_group = aws.ec2.SecurityGroup(
    resource_name="audiencias-lab-security-group",
    name="audiencias-lab-security-group",
    description="Security Group para la plataforma de audiencias digitales",
    vpc_id=vpc.id,
    revoke_rules_on_delete=True,
    tags={**COMMON_TAGS, "Name": "audiencias-lab-security-group"},
)

ssh_ingress_rule = aws.ec2.SecurityGroupRule(
    resource_name="audiencias-lab-ssh-ingress",
    type="ingress",
    protocol="tcp",
    from_port=22,
    to_port=22,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=lab_security_group.id,
    description="Temporary SSH access from Internet",
)

# Flink Web UI, accesible desde Internet para verla sin túnel SSH.
flink_ui_ingress_rule = aws.ec2.SecurityGroupRule(
    resource_name="audiencias-lab-flink-ui-ingress",
    type="ingress",
    protocol="tcp",
    from_port=FLINK_UI_PORT,
    to_port=FLINK_UI_PORT,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=lab_security_group.id,
    description="Flink JobManager Web UI",
)

# Grafana, accesible desde Internet para ver el dashboard en el navegador.
grafana_ingress_rule = aws.ec2.SecurityGroupRule(
    resource_name="audiencias-lab-grafana-ingress",
    type="ingress",
    protocol="tcp",
    from_port=GRAFANA_PORT,
    to_port=GRAFANA_PORT,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=lab_security_group.id,
    description="Grafana dashboard",
)

# Todo el tráfico interno entre nodos del laboratorio (Kafka 9092/9093,
# Flink 6123/8081, Postgres 5432, etc.) -- NO expone Postgres a Internet,
# solo es alcanzable desde otras instancias de este mismo Security Group.
internal_ingress_rule = aws.ec2.SecurityGroupRule(
    resource_name="audiencias-lab-internal-ingress",
    type="ingress",
    protocol="-1",
    from_port=0,
    to_port=0,
    source_security_group_id=lab_security_group.id,
    security_group_id=lab_security_group.id,
    description="Internal communication between lab nodes",
)

outbound_rule = aws.ec2.SecurityGroupRule(
    resource_name="audiencias-lab-outbound",
    type="egress",
    protocol="-1",
    from_port=0,
    to_port=0,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=lab_security_group.id,
    description="Allow all outbound traffic",
)


# ============================================================
# CLOUD-INIT COMÚN (paquetes base + hostname + /etc/hosts)
# ============================================================

ALL_HOSTS_ENTRIES: Final[str] = f"""
10.30.1.11 kafka-broker-1
10.30.1.12 kafka-broker-2
10.30.1.13 kafka-broker-3
{JOBMANAGER_PRIVATE_IP} flink-jobmanager
{TASKMANAGER_1_PRIVATE_IP} flink-taskmanager-1
{TASKMANAGER_2_PRIVATE_IP} flink-taskmanager-2
{TASKMANAGER_3_PRIVATE_IP} flink-taskmanager-3
{DASHBOARD_PRIVATE_IP} dashboard
{CLIENT_PRIVATE_IP} kafka-client
"""

COMMON_BOOTSTRAP: Final[str] = """#!/bin/bash
set -euxo pipefail

hostnamectl set-hostname "__HOSTNAME__"

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl jq net-tools unzip vim wget gnupg2

cat >> /etc/hosts <<'EOF'
""" + ALL_HOSTS_ENTRIES + """EOF

mkdir -p /opt/lab
cat > /opt/lab/node-info.txt <<EOF
hostname=__HOSTNAME__
private_ip=__PRIVATE_IP__
role=__ROLE__
EOF
"""

COMPLETION_MARKER: Final[str] = """
touch /opt/lab/cloud-init-complete
"""


def _render_common(hostname: str, private_ip: str, role: str) -> str:
    return (
        COMMON_BOOTSTRAP
        .replace("__HOSTNAME__", hostname)
        .replace("__PRIVATE_IP__", private_ip)
        .replace("__ROLE__", role)
    )


# ============================================================
# BOOTSTRAP DE KAFKA (idéntico al patrón validado)
# ============================================================

KAFKA_INSTALL_BOOTSTRAP: Final[str] = """
mkdir -p /opt/kafka
cd /opt/kafka
curl -fsSL "__KAFKA_DOWNLOAD_URL__" -o kafka.tgz
tar -xzf kafka.tgz
ln -sfn "/opt/kafka/__KAFKA_DIST_NAME__" /opt/kafka/current
rm kafka.tgz

cat > /etc/profile.d/kafka.sh <<'EOF'
export PATH="/opt/kafka/current/bin:$PATH"
EOF
"""

BROKER_BOOTSTRAP: Final[str] = """
id -u kafka &>/dev/null || useradd --system --home-dir /opt/kafka --shell /usr/sbin/nologin kafka
apt-get install -y openjdk-17-jdk-headless

mkdir -p /var/lib/kafka/data
chown -R kafka:kafka /opt/kafka /var/lib/kafka

cat > /opt/kafka/current/config/kraft-server.properties <<'EOF'
process.roles=broker,controller
node.id=__NODE_ID__
controller.quorum.voters=__CONTROLLER_QUORUM_VOTERS__

listeners=PLAINTEXT://__PRIVATE_IP__:9092,CONTROLLER://__PRIVATE_IP__:9093
advertised.listeners=PLAINTEXT://__PRIVATE_IP__:9092
controller.listener.names=CONTROLLER
inter.broker.listener.name=PLAINTEXT
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT

log.dirs=/var/lib/kafka/data
num.partitions=3
default.replication.factor=3
min.insync.replicas=2
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

log.retention.hours=1
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000
EOF

chown kafka:kafka /opt/kafka/current/config/kraft-server.properties

sudo -u kafka /opt/kafka/current/bin/kafka-storage.sh format \\
    -t "__KAFKA_CLUSTER_ID__" \\
    -c /opt/kafka/current/config/kraft-server.properties \\
    --ignore-formatted

cat > /etc/systemd/system/kafka.service <<'EOF'
[Unit]
Description=Apache Kafka (KRaft mode)
After=network.target

[Service]
Type=simple
User=kafka
Environment=JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ExecStart=/opt/kafka/current/bin/kafka-server-start.sh /opt/kafka/current/config/kraft-server.properties
ExecStop=/opt/kafka/current/bin/kafka-server-stop.sh
Restart=on-failure
LimitNOFILE=100000

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kafka
systemctl start kafka
"""


def build_broker_user_data(hostname: str, private_ip: str) -> str:
    node_id = BROKER_NODE_IDS[private_ip]
    kafka_install = (
        KAFKA_INSTALL_BOOTSTRAP
        .replace("__KAFKA_DOWNLOAD_URL__", KAFKA_DOWNLOAD_URL)
        .replace("__KAFKA_DIST_NAME__", KAFKA_DIST_NAME)
    )
    broker_block = (
        BROKER_BOOTSTRAP
        .replace("__NODE_ID__", str(node_id))
        .replace("__PRIVATE_IP__", private_ip)
        .replace("__CONTROLLER_QUORUM_VOTERS__", CONTROLLER_QUORUM_VOTERS)
        .replace("__KAFKA_CLUSTER_ID__", KAFKA_CLUSTER_ID)
    )
    return (
        _render_common(hostname, private_ip, role="broker-controller")
        + kafka_install
        + broker_block
        + COMPLETION_MARKER
    )


# ============================================================
# BOOTSTRAP DE FLINK (JobManager y TaskManager)
# ============================================================

FLINK_INSTALL_BOOTSTRAP: Final[str] = """
apt-get install -y openjdk-11-jdk-headless

id -u flink &>/dev/null || useradd --system --home-dir /opt/flink --shell /usr/sbin/nologin flink

mkdir -p /opt/flink
cd /opt/flink
curl -fsSL "__FLINK_DOWNLOAD_URL__" -o flink.tgz
tar -xzf flink.tgz
ln -sfn "/opt/flink/__FLINK_DIST_NAME__" /opt/flink/current
rm flink.tgz
chown -R flink:flink /opt/flink

cat > /etc/profile.d/flink.sh <<'EOF'
export PATH="/opt/flink/current/bin:$PATH"
EOF
"""

# config.yaml: formato nuevo de Flink 2.x (YAML anidado), reemplaza al
# antiguo flink-conf.yaml de versiones anteriores.
FLINK_CONFIG_YAML: Final[str] = """jobmanager:
  rpc:
    address: __JOBMANAGER_PRIVATE_IP__
    port: __FLINK_RPC_PORT__
  bind-host: 0.0.0.0
  memory:
    process:
      size: __FLINK_JOBMANAGER_MEMORY__
taskmanager:
  bind-host: 0.0.0.0
  host: __PRIVATE_IP__
  memory:
    process:
      size: __FLINK_TASKMANAGER_MEMORY__
  numberOfTaskSlots: __FLINK_TASKMANAGER_SLOTS__
parallelism:
  default: 2
rest:
  address: __JOBMANAGER_PRIVATE_IP__
  bind-address: 0.0.0.0
  port: __FLINK_UI_PORT__
"""


def _render_flink_config(private_ip: str) -> str:
    return (
        FLINK_CONFIG_YAML
        .replace("__JOBMANAGER_PRIVATE_IP__", JOBMANAGER_PRIVATE_IP)
        .replace("__PRIVATE_IP__", private_ip)
        .replace("__FLINK_RPC_PORT__", str(FLINK_RPC_PORT))
        .replace("__FLINK_UI_PORT__", str(FLINK_UI_PORT))
        .replace("__FLINK_JOBMANAGER_MEMORY__", FLINK_JOBMANAGER_MEMORY)
        .replace("__FLINK_TASKMANAGER_MEMORY__", FLINK_TASKMANAGER_MEMORY)
        .replace("__FLINK_TASKMANAGER_SLOTS__", str(FLINK_TASKMANAGER_SLOTS))
    )


JOBMANAGER_BOOTSTRAP: Final[str] = """
cat > /opt/flink/current/conf/config.yaml <<'EOF'
__FLINK_CONFIG_YAML__
EOF
chown flink:flink /opt/flink/current/conf/config.yaml

cat > /etc/systemd/system/flink-jobmanager.service <<'EOF'
[Unit]
Description=Flink JobManager (standalone)
After=network.target

[Service]
Type=simple
User=flink
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ExecStart=/opt/flink/current/bin/jobmanager.sh start-foreground
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable flink-jobmanager
systemctl start flink-jobmanager
"""

TASKMANAGER_BOOTSTRAP: Final[str] = """
cat > /opt/flink/current/conf/config.yaml <<'EOF'
__FLINK_CONFIG_YAML__
EOF
chown flink:flink /opt/flink/current/conf/config.yaml

cat > /etc/systemd/system/flink-taskmanager.service <<'EOF'
[Unit]
Description=Flink TaskManager (standalone)
After=network.target

[Service]
Type=simple
User=flink
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ExecStart=/opt/flink/current/bin/taskmanager.sh start-foreground
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable flink-taskmanager
systemctl start flink-taskmanager
"""


def build_jobmanager_user_data(hostname: str, private_ip: str) -> str:
    flink_install = (
        FLINK_INSTALL_BOOTSTRAP
        .replace("__FLINK_DOWNLOAD_URL__", FLINK_DOWNLOAD_URL)
        .replace("__FLINK_DIST_NAME__", FLINK_DIST_NAME)
    )
    jm_block = JOBMANAGER_BOOTSTRAP.replace(
        "__FLINK_CONFIG_YAML__", _render_flink_config(private_ip)
    )
    return (
        _render_common(hostname, private_ip, role="flink-jobmanager")
        + flink_install
        + jm_block
        + COMPLETION_MARKER
    )


def build_taskmanager_user_data(hostname: str, private_ip: str) -> str:
    flink_install = (
        FLINK_INSTALL_BOOTSTRAP
        .replace("__FLINK_DOWNLOAD_URL__", FLINK_DOWNLOAD_URL)
        .replace("__FLINK_DIST_NAME__", FLINK_DIST_NAME)
    )
    tm_block = TASKMANAGER_BOOTSTRAP.replace(
        "__FLINK_CONFIG_YAML__", _render_flink_config(private_ip)
    )
    return (
        _render_common(hostname, private_ip, role="flink-taskmanager")
        + flink_install
        + tm_block
        + COMPLETION_MARKER
    )


# ============================================================
# BOOTSTRAP DE POSTGRES/TIMESCALEDB + GRAFANA (co-ubicados)
# ============================================================

DASHBOARD_BOOTSTRAP: Final[str] = """
# ------------------------------------------------------------
# PostgreSQL 16 + extensión TimescaleDB
# ------------------------------------------------------------

install -d /usr/share/postgresql-common/pgdg
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \\
    -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] \\
https://apt.postgresql.org/pub/repos/apt noble-pgdg main" \\
    > /etc/apt/sources.list.d/pgdg.list

curl -fsSL https://packagecloud.io/timescale/timescaledb/gpgkey \\
    -o /usr/share/keyrings/timescaledb.asc
echo "deb [signed-by=/usr/share/keyrings/timescaledb.asc] \\
https://packagecloud.io/timescale/timescaledb/ubuntu/ noble main" \\
    > /etc/apt/sources.list.d/timescaledb.list

apt-get update -y
apt-get install -y postgresql-16 postgresql-client-16 timescaledb-2-postgresql-16

timescaledb-tune --quiet --yes

# Acceso solo desde dentro de la VPC (no desde Internet)
sed -i "s/^#listen_addresses.*/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf
echo "host    all             all             __VPC_CIDR__            md5" \\
    >> /etc/postgresql/16/main/pg_hba.conf

systemctl restart postgresql

sudo -u postgres psql -c "CREATE USER __POSTGRES_USER__ WITH PASSWORD '__POSTGRES_PASSWORD__';"
sudo -u postgres psql -c "CREATE DATABASE __POSTGRES_DB__ OWNER __POSTGRES_USER__;"
sudo -u postgres psql -d __POSTGRES_DB__ -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

# ------------------------------------------------------------
# Grafana OSS
# ------------------------------------------------------------

mkdir -p /etc/apt/keyrings
curl -fsSL https://apt.grafana.com/gpg.key | gpg --dearmor -o /etc/apt/keyrings/grafana.gpg
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \\
    > /etc/apt/sources.list.d/grafana.list

apt-get update -y
apt-get install -y grafana

systemctl daemon-reload
systemctl enable grafana-server
systemctl start grafana-server
"""


def build_dashboard_user_data(hostname: str, private_ip: str) -> str:
    dashboard_block = (
        DASHBOARD_BOOTSTRAP
        .replace("__VPC_CIDR__", VPC_CIDR)
        .replace("__POSTGRES_USER__", POSTGRES_USER)
        .replace("__POSTGRES_PASSWORD__", POSTGRES_PASSWORD)
        .replace("__POSTGRES_DB__", POSTGRES_DB)
    )
    return (
        _render_common(hostname, private_ip, role="dashboard")
        + dashboard_block
        + COMPLETION_MARKER
    )


# ============================================================
# BOOTSTRAP DEL CLIENTE (simulador de agentes + scripts/kafka)
# ============================================================
# Instancia única para correr agentes-simulador (Fase 2) y
# scripts/kafka/create_topics.py -- no separada en productor/consumidor
# como en kafka-flink-streaming-lab, para no sumar más EC2 al Learner Lab.

CLIENT_BOOTSTRAP: Final[str] = """
apt-get install -y python3 python3-pip python3-venv git

sudo -u ubuntu git clone "__PROJECT_REPO_URL__" /home/ubuntu/repo

cd /home/ubuntu/repo/__PROJECT_REPO_SUBDIR__

sudo -u ubuntu python3 -m venv /home/ubuntu/venv
sudo -u ubuntu /home/ubuntu/venv/bin/pip install --upgrade pip
sudo -u ubuntu /home/ubuntu/venv/bin/pip install \\
    -r agentes-simulador/requirements.txt \\
    -r scripts/kafka/requirements.txt

cat > /etc/profile.d/audiencias-venv.sh <<'EOF'
export PATH="/home/ubuntu/venv/bin:$PATH"
EOF

chown -R ubuntu:ubuntu /home/ubuntu/repo /home/ubuntu/venv
"""


def build_client_user_data(hostname: str, private_ip: str) -> str:
    client_block = (
        CLIENT_BOOTSTRAP
        .replace("__PROJECT_REPO_URL__", PROJECT_REPO_URL)
        .replace("__PROJECT_REPO_SUBDIR__", PROJECT_REPO_SUBDIR)
    )
    return (
        _render_common(hostname, private_ip, role="kafka-client")
        + client_block
        + COMPLETION_MARKER
    )


# ============================================================
# FUNCIÓN PARA CREAR INSTANCIAS (idéntica al patrón validado)
# ============================================================

def create_ec2_instance(
    resource_name: str,
    hostname: str,
    private_ip: str,
    role: str,
    user_data: str,
) -> aws.ec2.Instance:
    return aws.ec2.Instance(
        resource_name=resource_name,
        ami=ubuntu_ami.id,
        instance_type=INSTANCE_TYPE,
        subnet_id=public_subnet.id,
        private_ip=private_ip,
        associate_public_ip_address=True,
        vpc_security_group_ids=[lab_security_group.id],
        key_name=KEY_NAME,
        user_data=user_data,
        user_data_replace_on_change=False,
        root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
            volume_type="gp3",
            volume_size=20,
            encrypted=True,
            delete_on_termination=True,
        ),
        metadata_options=aws.ec2.InstanceMetadataOptionsArgs(
            http_endpoint="enabled",
            http_tokens="required",
            http_put_response_hop_limit=1,
        ),
        tags={**COMMON_TAGS, "Name": hostname, "Role": role},
        opts=pulumi.ResourceOptions(
            depends_on=[
                default_internet_route,
                public_route_table_association,
                ssh_ingress_rule,
                flink_ui_ingress_rule,
                grafana_ingress_rule,
                internal_ingress_rule,
                outbound_rule,
            ],
        ),
    )


# ============================================================
# BROKERS KAFKA
# ============================================================

broker_1 = create_ec2_instance(
    "kafka-broker-1-instance", "kafka-broker-1", BROKER_1_PRIVATE_IP,
    "broker-controller", build_broker_user_data("kafka-broker-1", BROKER_1_PRIVATE_IP),
)
broker_2 = create_ec2_instance(
    "kafka-broker-2-instance", "kafka-broker-2", BROKER_2_PRIVATE_IP,
    "broker-controller", build_broker_user_data("kafka-broker-2", BROKER_2_PRIVATE_IP),
)
broker_3 = create_ec2_instance(
    "kafka-broker-3-instance", "kafka-broker-3", BROKER_3_PRIVATE_IP,
    "broker-controller", build_broker_user_data("kafka-broker-3", BROKER_3_PRIVATE_IP),
)


# ============================================================
# FLINK: JOBMANAGER + 3 TASKMANAGERS
# ============================================================

jobmanager = create_ec2_instance(
    "flink-jobmanager-instance", "flink-jobmanager", JOBMANAGER_PRIVATE_IP,
    "flink-jobmanager", build_jobmanager_user_data("flink-jobmanager", JOBMANAGER_PRIVATE_IP),
)

taskmanager_1 = create_ec2_instance(
    "flink-taskmanager-1-instance", "flink-taskmanager-1", TASKMANAGER_1_PRIVATE_IP,
    "flink-taskmanager", build_taskmanager_user_data("flink-taskmanager-1", TASKMANAGER_1_PRIVATE_IP),
)
taskmanager_2 = create_ec2_instance(
    "flink-taskmanager-2-instance", "flink-taskmanager-2", TASKMANAGER_2_PRIVATE_IP,
    "flink-taskmanager", build_taskmanager_user_data("flink-taskmanager-2", TASKMANAGER_2_PRIVATE_IP),
)
taskmanager_3 = create_ec2_instance(
    "flink-taskmanager-3-instance", "flink-taskmanager-3", TASKMANAGER_3_PRIVATE_IP,
    "flink-taskmanager", build_taskmanager_user_data("flink-taskmanager-3", TASKMANAGER_3_PRIVATE_IP),
)


# ============================================================
# DASHBOARD: POSTGRES/TIMESCALEDB + GRAFANA
# ============================================================

dashboard = create_ec2_instance(
    "dashboard-instance", "dashboard", DASHBOARD_PRIVATE_IP,
    "dashboard", build_dashboard_user_data("dashboard", DASHBOARD_PRIVATE_IP),
)


# ============================================================
# CLIENTE (simulador de agentes + scripts/kafka)
# ============================================================

kafka_client = create_ec2_instance(
    "kafka-client-instance", "kafka-client", CLIENT_PRIVATE_IP,
    "kafka-client", build_client_user_data("kafka-client", CLIENT_PRIVATE_IP),
)


# ============================================================
# EXPORTS DE PULUMI
# ============================================================

pulumi.export("awsRegion", AWS_REGION)
pulumi.export("vpcId", vpc.id)
pulumi.export("publicSubnetId", public_subnet.id)
pulumi.export("securityGroupId", lab_security_group.id)

pulumi.export("kafkaVersion", KAFKA_VERSION)
pulumi.export("kafkaClusterId", KAFKA_CLUSTER_ID)
pulumi.export(
    "bootstrapServers",
    f"{BROKER_1_PRIVATE_IP}:{BROKER_PORT},{BROKER_2_PRIVATE_IP}:{BROKER_PORT},{BROKER_3_PRIVATE_IP}:{BROKER_PORT}",
)

pulumi.export("flinkVersion", FLINK_VERSION)
pulumi.export("flinkUiUrl", pulumi.Output.concat("http://", jobmanager.public_ip, f":{FLINK_UI_PORT}"))

pulumi.export("grafanaUrl", pulumi.Output.concat("http://", dashboard.public_ip, f":{GRAFANA_PORT}"))
pulumi.export("postgresPrivateEndpoint", f"{DASHBOARD_PRIVATE_IP}:{POSTGRES_PORT}/{POSTGRES_DB}")

for _name, _instance in [
    ("Broker1", broker_1), ("Broker2", broker_2), ("Broker3", broker_3),
    ("JobManager", jobmanager),
    ("TaskManager1", taskmanager_1), ("TaskManager2", taskmanager_2), ("TaskManager3", taskmanager_3),
    ("Dashboard", dashboard),
    ("Client", kafka_client),
]:
    pulumi.export(f"{_name.lower()}PrivateIp", _instance.private_ip)
    pulumi.export(f"{_name.lower()}PublicIp", _instance.public_ip)
    pulumi.export(
        f"ssh{_name}",
        pulumi.Output.concat("ssh -i ../keys/audiencias-lab-key.pem ubuntu@", _instance.public_ip),
    )
