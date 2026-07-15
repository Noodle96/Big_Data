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
# entre ellas mediante cualquier protocolo y puerto.
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
# CLOUD-INIT COMÚN
# ============================================================

BASE_USER_DATA: Final[str] = """#!/bin/bash
set -euxo pipefail

# ------------------------------------------------------------
# Nombre del host
# ------------------------------------------------------------

hostnamectl set-hostname "__HOSTNAME__"


# ------------------------------------------------------------
# Paquetes básicos
# ------------------------------------------------------------

export DEBIAN_FRONTEND=noninteractive

apt-get update -y

apt-get install -y \
    ca-certificates \
    curl \
    jq \
    net-tools \
    unzip \
    vim \
    wget


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
# Información del nodo
# ------------------------------------------------------------

mkdir -p /opt/kafka-lab

cat > /opt/kafka-lab/node-info.txt <<'EOF'
hostname=__HOSTNAME__
private_ip=__PRIVATE_IP__
role=__ROLE__
EOF


# ------------------------------------------------------------
# Confirmación de finalización
# ------------------------------------------------------------

touch /opt/kafka-lab/cloud-init-complete
"""


def build_user_data(
    hostname: str,
    private_ip: str,
    role: str,
) -> str:
    """
    Genera el cloud-init específico de una instancia.

    Args:
        hostname:
            Nombre que tendrá la máquina.

        private_ip:
            Dirección IPv4 privada fija.

        role:
            Papel de la máquina dentro del laboratorio.

    Returns:
        Script Bash que EC2 ejecutará durante el primer arranque.
    """

    return (
        BASE_USER_DATA
        .replace("__HOSTNAME__", hostname)
        .replace("__PRIVATE_IP__", private_ip)
        .replace("__ROLE__", role)
    )


# ============================================================
# FUNCIÓN PARA CREAR INSTANCIAS
# ============================================================

def create_ec2_instance(
    resource_name: str,
    hostname: str,
    private_ip: str,
    role: str,
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

        user_data=build_user_data(
            hostname=hostname,
            private_ip=private_ip,
            role=role,
        ),

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
)

broker_2 = create_ec2_instance(
    resource_name="kafka-broker-2-instance",
    hostname="kafka-broker-2",
    private_ip=BROKER_2_PRIVATE_IP,
    role="broker-controller",
)

broker_3 = create_ec2_instance(
    resource_name="kafka-broker-3-instance",
    hostname="kafka-broker-3",
    private_ip=BROKER_3_PRIVATE_IP,
    role="broker-controller",
)


# ============================================================
# CLIENTE KAFKA
# ============================================================

kafka_client = create_ec2_instance(
    resource_name="kafka-client-instance",
    hostname="kafka-client",
    private_ip=CLIENT_PRIVATE_IP,
    role="producer-consumer-client",
)


# ============================================================
# EXPORTS DE PULUMI
# ============================================================

pulumi.export("awsRegion", AWS_REGION)

pulumi.export("vpcId", vpc.id)
pulumi.export("publicSubnetId", public_subnet.id)
pulumi.export("securityGroupId", kafka_security_group.id)

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
        f"{BROKER_1_PRIVATE_IP}:9092,"
        f"{BROKER_2_PRIVATE_IP}:9092,"
        f"{BROKER_3_PRIVATE_IP}:9092"
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