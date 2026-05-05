from typing import List
import pulumi
import pulumi_aws as aws

# =========================
# CONFIG
# =========================

INSTANCE_TYPE: str = "t3.small"

ami_info = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical
    filters=[
        {
            "name": "name",
            "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
        },
        {"name": "virtualization-type", "values": ["hvm"]},
    ],
)

AMI: str = ami_info.id

KEY_NAME: str = "hadoop-cluster-key"

# =========================
# SECURITY GROUP
# =========================

security_group: aws.ec2.SecurityGroup = aws.ec2.SecurityGroup(
    "hadoop-cluster-sg",
    description="Security group for Hadoop cluster",
    ingress=[
        # SSH
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        # HDFS UI
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=9870,
            to_port=9870,
            cidr_blocks=["0.0.0.0/0"],
        ),
        # YARN UI
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=8088,
            to_port=8088,
            cidr_blocks=["0.0.0.0/0"],
        ),
        # Comunicación interna entre nodos
        aws.ec2.SecurityGroupIngressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            self=True,
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

# =========================
# INSTANCES
# =========================


def create_instance(name: str) -> aws.ec2.Instance:
    return aws.ec2.Instance(
        name,
        instance_type=INSTANCE_TYPE,
        ami=AMI,
        key_name=KEY_NAME,
        vpc_security_group_ids=[security_group.id],
        root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
            volume_size=8,  # GiB
            volume_type="gp3",
            delete_on_termination=True,
        ),
        tags={"Name": name},
    )


# Master
master: aws.ec2.Instance = create_instance("hadoop-master")

# Workers
workers: List[aws.ec2.Instance] = [ 
    create_instance("hadoop-worker-1"),
    create_instance("hadoop-worker-2"),
    create_instance("hadoop-worker-3"),
]

# =========================
# OUTPUTS
# =========================

pulumi.export("master_public_ip", master.public_ip)
pulumi.export("master_private_ip", master.private_ip)
pulumi.export("worker_private_ips", [w.private_ip for w in workers])
