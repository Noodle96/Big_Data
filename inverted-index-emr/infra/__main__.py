import random

import pulumi
import pulumi_aws as aws


# ============================================================
# CONFIGURACIÓN GENERAL DEL LABORATORIO
# ============================================================

# Región asumida desde Pulumi config:
#   pulumi config get aws:region
#
# Este archivo crea:
# - 1 bucket S3 para staging y logs
# - 1 cluster EMR con Hadoop
# - 1 nodo master
# - 3 nodos core/worker
#
# Nuevo enfoque:
# - S3 se usa solo para subir archivos y almacenar logs.
# - El procesamiento real se hará usando HDFS dentro del cluster EMR.
# - Entraremos por SSH al master.
# - Desde el master subiremos archivos al HDFS con hdfs dfs -put.
# - Luego ejecutaremos hadoop jar usando rutas HDFS: /input y /output.


# ============================================================
# GENERACIÓN DE NOMBRE ÚNICO PARA EL BUCKET S3
# ============================================================

# En S3, el nombre de un bucket debe ser único globalmente.
# Por eso agregamos un sufijo aleatorio.
random_suffix: int = random.randint(10000, 99999)

# Nombre real del bucket.
bucket_name: str = f"inverted-index-emr-{random_suffix}"


# ============================================================
# BUCKET S3
# ============================================================

# Este bucket se usará para:
# - staging/input/: guardar temporalmente los .txt antes de copiarlos al master
# - staging/jars/: guardar el .jar compilado del job
# - logs/: guardar logs generados por EMR
#
# IMPORTANTE:
# En este nuevo enfoque, el job NO leerá directamente desde S3.
# Primero copiaremos los archivos desde S3 hacia el nodo master
# y luego los subiremos manualmente al HDFS.
bucket = aws.s3.Bucket(
    resource_name="inverted-index-bucket",
    bucket=bucket_name,

    # Permite que Pulumi elimine el bucket aunque tenga logs/archivos.
    # Esto evita el error BucketNotEmpty durante pulumi destroy.
    force_destroy=True,
)


# ============================================================
# KEY PAIR PARA SSH
# ============================================================

# Para entrar al nodo master por SSH, EMR necesita un EC2 Key Pair.
#
# Este código NO crea la llave privada .pem.
# Primero debes crearla tú con AWS CLI, por ejemplo:
#
#   aws ec2 create-key-pair \
#     --key-name emr-inverted-index-key \
#     --query 'KeyMaterial' \
#     --output text > emr-inverted-index-key.pem
#
#   chmod 400 emr-inverted-index-key.pem
#
# El nombre de la key pair creada debe coincidir con este valor.
key_name: str = "emr-inverted-index-key"


# ============================================================
# SECURITY GROUP PARA PERMITIR SSH AL MASTER
# ============================================================

# Este security group permitirá conexión SSH al nodo master.
#
# Para laboratorio lo dejamos abierto a 0.0.0.0/0.
# Eso significa "desde cualquier IP".
#
# Más seguro sería reemplazarlo por tu IP pública:
#   x.x.x.x/32
#
# Ejemplo:
#   cidr_blocks=["190.XXX.XXX.XXX/32"]
master_security_group = aws.ec2.SecurityGroup(
    resource_name="emr-master-ssh-sg",
    description="Allow SSH access to EMR primary node",

    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="SSH access",
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],

    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            description="Allow all outbound traffic",
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)


# ============================================================
# CLUSTER EMR CON HADOOP + HDFS
# ============================================================

cluster = aws.emr.Cluster(
    resource_name="inverted-index-emr-cluster",

    opts=pulumi.ResourceOptions(delete_before_replace=True),

    # Nombre visible en AWS Console.
    name="inverted-index-emr-cluster",

    # Versión de Amazon EMR.
    release_label="emr-7.0.0",

    # Instalamos Hadoop porque ejecutaremos MapReduce clásico.
    # applications=["Hadoop"],
    applications=["Hadoop", "Hive"],
    

    # Rol del servicio EMR.
    service_role="EMR_DefaultRole",

    # Configuración EC2 del cluster.
    ec2_attributes=aws.emr.ClusterEc2AttributesArgs(
        # Perfil usado por las EC2 del cluster.
        instance_profile="EMR_EC2_DefaultRole",

        # Key pair usada para conectarnos por SSH.
        key_name=key_name,

        # Security group adicional para permitir SSH al master.
        additional_master_security_groups=master_security_group.id,
    ),

    # ========================================================
    # MASTER NODE
    # ========================================================

    # Nodo master/primary:
    # - coordina el cluster
    # - ejecuta servicios como ResourceManager
    # - permite acceso SSH como usuario hadoop
    # - desde aquí ejecutaremos comandos hdfs y hadoop jar
    master_instance_group=aws.emr.ClusterMasterInstanceGroupArgs(
        instance_type="m5.xlarge", # m5.large
        instance_count=1,
    ),

    # ========================================================
    # CORE / WORKER NODES
    # ========================================================

    # Nodos core/worker:
    # - ejecutan tareas MapReduce
    # - almacenan bloques HDFS
    # - funcionan como DataNodes
    #
    # Con instance_count=3 tendremos:
    #   1 master + 3 workers = 4 nodos EC2 en total
    core_instance_group=aws.emr.ClusterCoreInstanceGroupArgs(
        instance_type="m5.xlarge", # m5.large
        instance_count=3,
    ),

    # Logs de EMR en S3.
    log_uri=pulumi.Output.concat(
        "s3://",
        bucket.bucket,
        "/logs/",
    ),

    # Configuración Hadoop.
    configurations_json="""
    [
      {
        "Classification": "mapred-site",
        "Properties": {
          "mapreduce.framework.name": "yarn"
        }
      },
      {
        "Classification": "hdfs-site",
        "Properties": {
          "dfs.replication": "3"
        }
      }
    ]
    """,

    # Visible para usuarios autorizados de la cuenta.
    visible_to_all_users=True,

    # Permite destruir el cluster desde Pulumi sin protección extra.
    termination_protection=False,

    # Mantiene el cluster vivo para que podamos entrar por SSH
    # y ejecutar comandos manuales.
    keep_job_flow_alive_when_no_steps=True,

    # Comportamiento de apagado de nodos.
    scale_down_behavior="TERMINATE_AT_TASK_COMPLETION",
)


# ============================================================
# EXPORTS DE PULUMI
# ============================================================

pulumi.export("bucket_name", bucket.bucket)

# Rutas S3 de staging. Ahora NO serán rutas finales del job.
pulumi.export(
    "s3_staging_input_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/staging/input/"),
)

pulumi.export(
    "s3_staging_jar_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/staging/jars/"),
)

pulumi.export(
    "logs_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/logs/"),
)

pulumi.export("cluster_id", cluster.id)

# DNS público del master para conectarte por SSH.
pulumi.export("master_public_dns", cluster.master_public_dns)

# Rutas HDFS que usaremos dentro del cluster.
pulumi.export("hdfs_input_path", "/input")
pulumi.export("hdfs_output_path", "/output")
pulumi.export("hdfs_jar_path", "/home/hadoop/inverted-index.jar")