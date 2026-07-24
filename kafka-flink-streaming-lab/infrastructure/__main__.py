from typing import Final

import pulumi
import pulumi_aws as aws


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_NAME: Final[str] = "kafka-ec2-lab"
AWS_REGION: Final[str] = aws.config.region or "us-east-1"

# Este nombre debe coincidir con el Key Pair registrado en AWS.
# El archivo privado local es: ../keys/kafka-lab-key.pem
KEY_NAME: Final[str] = "kafka-lab-key"

# t3.small dispone de 2 GiB de memoria.
# Posteriormente limitaremos la memoria de Kafka para el laboratorio.
INSTANCE_TYPE: Final[str] = "t3.small"

VPC_CIDR: Final[str] = "10.20.0.0/16"
PUBLIC_SUBNET_CIDR: Final[str] = "10.20.1.0/24"

BROKER_1_PRIVATE_IP: Final[str] = "10.20.1.11"
BROKER_2_PRIVATE_IP: Final[str] = "10.20.1.12"
BROKER_3_PRIVATE_IP: Final[str] = "10.20.1.13"
CLIENT_PRIVATE_IP: Final[str] = "10.20.1.20"

COMMON_TAGS: Final[dict[str, str]] = {
    "Project": PROJECT_NAME,
    "Environment": "academy-lab",
    "ManagedBy": "Pulumi",
}


# ============================================================
# CONFIGURACIÓN DE KAFKA (KRaft, sin Zookeeper)
# ============================================================

KAFKA_VERSION: Final[str] = "3.9.0"
KAFKA_SCALA_VERSION: Final[str] = "2.13"
KAFKA_DIST_NAME: Final[str] = f"kafka_{KAFKA_SCALA_VERSION}-{KAFKA_VERSION}"

# Se usa archive.apache.org en vez del mirror dinámico para que la URL
# no cambie con el tiempo (reproducibilidad).
KAFKA_DOWNLOAD_URL: Final[str] = (
    f"https://archive.apache.org/dist/kafka/{KAFKA_VERSION}/{KAFKA_DIST_NAME}.tgz"
)

BROKER_PORT: Final[int] = 9092
CONTROLLER_PORT: Final[int] = 9093

# Generado UNA sola vez con:
#   python3 -c "import uuid,base64; print(base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip('='))"
# Debe ser el MISMO en los 3 brokers: identifica al clúster KRaft.
# Si el clúster se destruye y se recrea desde cero, se puede reutilizar
# el mismo valor sin problema.
KAFKA_CLUSTER_ID: Final[str] = "X2k7a_8UT5i145WnsLy8qQ"

# node.id de KRaft para cada broker (debe ser único por nodo).
BROKER_NODE_IDS: Final[dict[str, int]] = {
    BROKER_1_PRIVATE_IP: 1,
    BROKER_2_PRIVATE_IP: 2,
    BROKER_3_PRIVATE_IP: 3,
}


def _controller_quorum_voters() -> str:
    """
    Arma el valor de controller.quorum.voters a partir de las IPs
    privadas fijas de los 3 brokers, ej:
    "1@10.20.1.11:9093,2@10.20.1.12:9093,3@10.20.1.13:9093"
    """
    return ",".join(
        f"{node_id}@{ip}:{CONTROLLER_PORT}"
        for ip, node_id in BROKER_NODE_IDS.items()
    )


CONTROLLER_QUORUM_VOTERS: Final[str] = _controller_quorum_voters()


# ============================================================
# AMI UBUNTU 24.04 LTS
# ============================================================

ubuntu_ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=[
                "ubuntu/images/hvm-ssd-gp3/"
                "ubuntu-noble-24.04-amd64-server-*"
            ],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="architecture",
            values=["x86_64"],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="root-device-type",
            values=["ebs"],
        ),
    ],
)


# ============================================================
# VPC
# ============================================================

vpc = aws.ec2.Vpc(
    resource_name="kafka-lab-vpc",
    cidr_block=VPC_CIDR,
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={
        **COMMON_TAGS,
        "Name": "kafka-lab-vpc",
    },
)


# ============================================================
# INTERNET GATEWAY
# ============================================================

internet_gateway = aws.ec2.InternetGateway(
    resource_name="kafka-lab-internet-gateway",
    vpc_id=vpc.id,
    tags={
        **COMMON_TAGS,
        "Name": "kafka-lab-internet-gateway",
    },
)


# ============================================================
# SUBRED PÚBLICA
# ============================================================

availability_zones = aws.get_availability_zones(
    state="available",
)

public_subnet = aws.ec2.Subnet(
    resource_name="kafka-lab-public-subnet",
    vpc_id=vpc.id,
    cidr_block=PUBLIC_SUBNET_CIDR,
    availability_zone=availability_zones.names[0],
    map_public_ip_on_launch=True,
    tags={
        **COMMON_TAGS,
        "Name": "kafka-lab-public-subnet",
    },
)


# ============================================================
# TABLA DE RUTAS
# ============================================================

public_route_table = aws.ec2.RouteTable(
    resource_name="kafka-lab-public-route-table",
    vpc_id=vpc.id,
    tags={
        **COMMON_TAGS,
        "Name": "kafka-lab-public-route-table",
    },
)

default_internet_route = aws.ec2.Route(
    resource_name="kafka-lab-default-internet-route",
    route_table_id=public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id,
)

public_route_table_association = aws.ec2.RouteTableAssociation(
    resource_name="kafka-lab-public-route-table-association",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id,
)


# ============================================================
# SECURITY GROUP
# ============================================================

kafka_security_group = aws.ec2.SecurityGroup(
    resource_name="kafka-lab-security-group",
    name="kafka-lab-security-group",
    description="Security Group for distributed Kafka laboratory",
    vpc_id=vpc.id,
    revoke_rules_on_delete=True,
    tags={
        **COMMON_TAGS,
        "Name": "kafka-lab-security-group",
    },
)


# SSH abierto temporalmente desde Internet.
ssh_ingress_rule = aws.ec2.SecurityGroupRule(
    resource_name="kafka-lab-ssh-ingress",
    type="ingress",
    protocol="tcp",
    from_port=22,
    to_port=22,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=kafka_security_group.id,
    description="Temporary SSH access from Internet",
)


# Las instancias que usan este Security Group pueden comunicarse
# entre ellas mediante cualquier protocolo y puerto (incluye 9092/9093
# de Kafka: brokers entre sí, y el cliente hacia los brokers).
internal_ingress_rule = aws.ec2.SecurityGroupRule(
    resource_name="kafka-lab-internal-ingress",
    type="ingress",
    protocol="-1",
    from_port=0,
    to_port=0,
    source_security_group_id=kafka_security_group.id,
    security_group_id=kafka_security_group.id,
    description="Internal communication between Kafka laboratory nodes",
)


# Salida a Internet para descargar paquetes, Java y Kafka.
outbound_rule = aws.ec2.SecurityGroupRule(
    resource_name="kafka-lab-outbound",
    type="egress",
    protocol="-1",
    from_port=0,
    to_port=0,
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=kafka_security_group.id,
    description="Allow all outbound traffic",
)


# ============================================================
# CLOUD-INIT COMÚN (paquetes base + hostname + /etc/hosts)
# ============================================================

COMMON_BOOTSTRAP: Final[str] = """#!/bin/bash
set -euxo pipefail

# ------------------------------------------------------------
# Nombre del host
# ------------------------------------------------------------

hostnamectl set-hostname "__HOSTNAME__"


# ------------------------------------------------------------
# Paquetes básicos + Java (requerido por Kafka)
# ------------------------------------------------------------

export DEBIAN_FRONTEND=noninteractive

apt-get update -y

apt-get install -y \\
    ca-certificates \\
    curl \\
    jq \\
    net-tools \\
    unzip \\
    vim \\
    wget \\
    openjdk-17-jdk-headless


# ------------------------------------------------------------
# Resolución local de nombres
# ------------------------------------------------------------

cat >> /etc/hosts <<'EOF'

# Kafka distributed laboratory
10.20.1.11 kafka-broker-1
10.20.1.12 kafka-broker-2
10.20.1.13 kafka-broker-3
10.20.1.20 kafka-client
EOF


# ------------------------------------------------------------
# Descarga e instalación del binario de Kafka (común a brokers y
# cliente: el cliente lo necesita para las herramientas CLI, como
# kafka-topics.sh y kafka-consumer-groups.sh).
# ------------------------------------------------------------

mkdir -p /opt/kafka
cd /opt/kafka
curl -fsSL "__KAFKA_DOWNLOAD_URL__" -o kafka.tgz
tar -xzf kafka.tgz
ln -sfn "/opt/kafka/__KAFKA_DIST_NAME__" /opt/kafka/current
rm kafka.tgz

cat > /etc/profile.d/kafka.sh <<'EOF'
export PATH="/opt/kafka/current/bin:$PATH"
EOF


# ------------------------------------------------------------
# Información del nodo
# ------------------------------------------------------------

mkdir -p /opt/kafka-lab

cat > /opt/kafka-lab/node-info.txt <<EOF
hostname=__HOSTNAME__
private_ip=__PRIVATE_IP__
role=__ROLE__
kafka_version=__KAFKA_VERSION__
EOF
"""


# ------------------------------------------------------------
# Bloque adicional SOLO para brokers: configura y arranca el
# proceso de Kafka en modo KRaft (broker + controller combinados).
# ------------------------------------------------------------

BROKER_BOOTSTRAP: Final[str] = """
# ------------------------------------------------------------
# Usuario de sistema para correr Kafka
# ------------------------------------------------------------

id -u kafka &>/dev/null || useradd --system --home-dir /opt/kafka --shell /usr/sbin/nologin kafka

mkdir -p /var/lib/kafka/data
chown -R kafka:kafka /opt/kafka /var/lib/kafka


# ------------------------------------------------------------
# server.properties (KRaft, sin Zookeeper)
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Formateo del storage KRaft (requiere el mismo CLUSTER_ID en
# los 3 brokers). --ignore-formatted evita error si ya se formateó.
# ------------------------------------------------------------

sudo -u kafka /opt/kafka/current/bin/kafka-storage.sh format \\
    -t "__KAFKA_CLUSTER_ID__" \\
    -c /opt/kafka/current/config/kraft-server.properties \\
    --ignore-formatted


# ------------------------------------------------------------
# Servicio systemd
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Bloque adicional SOLO para el cliente: Python + librerías para
# producer.py / consumer.py (no corre el servicio de Kafka).
# ------------------------------------------------------------

CLIENT_BOOTSTRAP: Final[str] = """
export DEBIAN_FRONTEND=noninteractive

apt-get install -y python3 python3-pip python3-venv

pip3 install --break-system-packages kafka-python pyyaml
"""


COMPLETION_MARKER: Final[str] = """
touch /opt/kafka-lab/cloud-init-complete
"""


def _render_common(hostname: str, private_ip: str, role: str) -> str:
    return (
        COMMON_BOOTSTRAP
        .replace("__HOSTNAME__", hostname)
        .replace("__PRIVATE_IP__", private_ip)
        .replace("__ROLE__", role)
        .replace("__KAFKA_DOWNLOAD_URL__", KAFKA_DOWNLOAD_URL)
        .replace("__KAFKA_DIST_NAME__", KAFKA_DIST_NAME)
        .replace("__KAFKA_VERSION__", KAFKA_VERSION)
    )


def build_broker_user_data(hostname: str, private_ip: str) -> str:
    """
    Cloud-init completo para un broker: paquetes base + Kafka
    instalado, configurado en modo KRaft, formateado y corriendo
    como servicio systemd.
    """
    node_id = BROKER_NODE_IDS[private_ip]

    broker_block = (
        BROKER_BOOTSTRAP
        .replace("__NODE_ID__", str(node_id))
        .replace("__PRIVATE_IP__", private_ip)
        .replace("__CONTROLLER_QUORUM_VOTERS__", CONTROLLER_QUORUM_VOTERS)
        .replace("__KAFKA_CLUSTER_ID__", KAFKA_CLUSTER_ID)
    )

    return (
        _render_common(hostname, private_ip, role="broker-controller")
        + broker_block
        + COMPLETION_MARKER
    )


def build_client_user_data(hostname: str, private_ip: str) -> str:
    """
    Cloud-init completo para el cliente: paquetes base + binario de
    Kafka (solo para las herramientas CLI) + Python y librerías para
    correr producer.py / consumer.py.
    """
    return (
        _render_common(hostname, private_ip, role="producer-consumer-client")
        + CLIENT_BOOTSTRAP
        + COMPLETION_MARKER
    )


# ============================================================
# FUNCIÓN PARA CREAR INSTANCIAS
# ============================================================

def create_ec2_instance(
    resource_name: str,
    hostname: str,
    private_ip: str,
    role: str,
    user_data: str,
) -> aws.ec2.Instance:
    """
    Crea una instancia EC2 del laboratorio.

    Todas las máquinas comparten:

    - La misma VPC.
    - La misma subred.
    - El mismo Security Group.
    - El mismo Key Pair.
    - Un disco raíz EBS gp3 de 20 GiB.
    """

    instance = aws.ec2.Instance(
        resource_name=resource_name,

        ami=ubuntu_ami.id,
        instance_type=INSTANCE_TYPE,

        subnet_id=public_subnet.id,
        private_ip=private_ip,
        associate_public_ip_address=True,

        vpc_security_group_ids=[
            kafka_security_group.id,
        ],

        key_name=KEY_NAME,

        user_data=user_data,

        # Un cambio posterior en user_data no destruirá la instancia.
        # Pulumi podría detenerla e iniciarla para aplicar ciertos cambios.
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

        tags={
            **COMMON_TAGS,
            "Name": hostname,
            "Role": role,
        },

        opts=pulumi.ResourceOptions(
            depends_on=[
                default_internet_route,
                public_route_table_association,
                ssh_ingress_rule,
                internal_ingress_rule,
                outbound_rule,
            ],
        ),
    )

    return instance


# ============================================================
# BROKERS KAFKA
# ============================================================

broker_1 = create_ec2_instance(
    resource_name="kafka-broker-1-instance",
    hostname="kafka-broker-1",
    private_ip=BROKER_1_PRIVATE_IP,
    role="broker-controller",
    user_data=build_broker_user_data("kafka-broker-1", BROKER_1_PRIVATE_IP),
)

broker_2 = create_ec2_instance(
    resource_name="kafka-broker-2-instance",
    hostname="kafka-broker-2",
    private_ip=BROKER_2_PRIVATE_IP,
    role="broker-controller",
    user_data=build_broker_user_data("kafka-broker-2", BROKER_2_PRIVATE_IP),
)

broker_3 = create_ec2_instance(
    resource_name="kafka-broker-3-instance",
    hostname="kafka-broker-3",
    private_ip=BROKER_3_PRIVATE_IP,
    role="broker-controller",
    user_data=build_broker_user_data("kafka-broker-3", BROKER_3_PRIVATE_IP),
)


# ============================================================
# CLIENTE KAFKA
# ============================================================

kafka_client = create_ec2_instance(
    resource_name="kafka-client-instance",
    hostname="kafka-client",
    private_ip=CLIENT_PRIVATE_IP,
    role="producer-consumer-client",
    user_data=build_client_user_data("kafka-client", CLIENT_PRIVATE_IP),
)


# ============================================================
# EXPORTS DE PULUMI
# ============================================================

pulumi.export("awsRegion", AWS_REGION)

pulumi.export("vpcId", vpc.id)
pulumi.export("publicSubnetId", public_subnet.id)
pulumi.export("securityGroupId", kafka_security_group.id)

pulumi.export("kafkaVersion", KAFKA_VERSION)
pulumi.export("kafkaClusterId", KAFKA_CLUSTER_ID)
pulumi.export("controllerQuorumVoters", CONTROLLER_QUORUM_VOTERS)

pulumi.export("broker1PrivateIp", broker_1.private_ip)
pulumi.export("broker2PrivateIp", broker_2.private_ip)
pulumi.export("broker3PrivateIp", broker_3.private_ip)
pulumi.export("clientPrivateIp", kafka_client.private_ip)

pulumi.export("broker1PublicIp", broker_1.public_ip)
pulumi.export("broker2PublicIp", broker_2.public_ip)
pulumi.export("broker3PublicIp", broker_3.public_ip)
pulumi.export("clientPublicIp", kafka_client.public_ip)

pulumi.export(
    "bootstrapServers",
    (
        f"{BROKER_1_PRIVATE_IP}:{BROKER_PORT},"
        f"{BROKER_2_PRIVATE_IP}:{BROKER_PORT},"
        f"{BROKER_3_PRIVATE_IP}:{BROKER_PORT}"
    ),
)

pulumi.export(
    "sshBroker1",
    pulumi.Output.concat(
        "ssh -i ../keys/kafka-lab-key.pem ubuntu@",
        broker_1.public_ip,
    ),
)

pulumi.export(
    "sshBroker2",
    pulumi.Output.concat(
        "ssh -i ../keys/kafka-lab-key.pem ubuntu@",
        broker_2.public_ip,
    ),
)

pulumi.export(
    "sshBroker3",
    pulumi.Output.concat(
        "ssh -i ../keys/kafka-lab-key.pem ubuntu@",
        broker_3.public_ip,
    ),
)

pulumi.export(
    "sshClient",
    pulumi.Output.concat(
        "ssh -i ../keys/kafka-lab-key.pem ubuntu@",
        kafka_client.public_ip,
    ),
)
