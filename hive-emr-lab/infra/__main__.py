import pulumi
import pulumi_aws as aws


# ============================================================
# CONFIGURACIÓN GENERAL DEL LABORATORIO HIVE + EMR
# ============================================================

# Este proyecto usa un bucket S3 persistente creado manualmente:
#
#   s3://bigdata-russell-academy
#
# Ese bucket NO será creado ni destruido por Pulumi.
#
# Pulumi solo administrará infraestructura temporal:
# - Security Group para SSH
# - Cluster EMR con Hadoop + Hive
#
# Flujo del laboratorio:
# 1. Los datasets viven en S3 persistente.
# 2. Creamos un cluster EMR temporal.
# 3. Entramos al master por SSH.
# 4. Copiamos datos de S3 hacia HDFS.
# 5. Ejecutamos HiveQL sobre HDFS.
# 6. Guardamos resultados importantes en S3.
# 7. Destruimos el cluster EMR con pulumi destroy.


# ============================================================
# CONFIGURACIÓN DEL BUCKET PERSISTENTE
# ============================================================

# Bucket creado manualmente desde AWS Console.
# No se elimina con pulumi destroy.
persistent_bucket_name: str = "bigdata-russell-academy"

# Ruta S3 donde EMR guardará logs.
emr_logs_uri = f"s3://{persistent_bucket_name}/logs/emr/"


# ============================================================
# KEY PAIR PARA SSH
# ============================================================

# Esta key pair debe existir en EC2 dentro de la misma región.
# El archivo .pem debe guardarse localmente en:
#
#   hive-emr-lab/keys/
#
# Ejemplo:
#   keys/emr-inverted-index-key.pem
#
# Puedes reutilizar la key del laboratorio anterior si existe
# en la cuenta/región actual de AWS Academy.
# key_name: str = "emr-inverted-index-key"
key_name: str = "emr-hive-lab-key"


# ============================================================
# SECURITY GROUP PARA ACCESO SSH AL MASTER
# ============================================================

# Permitimos SSH al nodo master para:
# - ejecutar comandos HDFS
# - lanzar scripts HiveQL
# - copiar datos S3 -> HDFS
# - revisar aplicaciones instaladas
#
# Para laboratorio se deja abierto a 0.0.0.0/0.
# Más seguro sería restringirlo a tu IP pública /32.
master_security_group = aws.ec2.SecurityGroup(
    resource_name="emr-master-ssh-sg",
    description="Allow SSH access to EMR primary node",

    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="SSH access to EMR master",
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
# CLUSTER EMR CON HADOOP + HIVE
# ============================================================

cluster = aws.emr.Cluster(
    resource_name="hive-emr-cluster",

    # Si un cambio obliga a reemplazar el cluster,
    # primero se elimina el anterior y luego se crea el nuevo.
    # Esto evita tener dos clusters cobrando al mismo tiempo.
    opts=pulumi.ResourceOptions(delete_before_replace=True),

    # Nombre visible en AWS Console.
    name="hive-emr-cluster",

    # Release EMR.
    release_label="emr-7.0.0",

    # Aplicaciones instaladas.
    applications=[
        "Hadoop",
        "Hive",
    ],

    # Rol del servicio EMR.
    service_role="EMR_DefaultRole",

    # Configuración EC2 del cluster.
    ec2_attributes=aws.emr.ClusterEc2AttributesArgs(
        instance_profile="EMR_EC2_DefaultRole",
        key_name=key_name,
        additional_master_security_groups=master_security_group.id,
    ),

    # Nodo master:
    # - coordina el cluster
    # - ejecuta servicios Hadoop/Hive
    # - permite acceso SSH como usuario hadoop
    master_instance_group=aws.emr.ClusterMasterInstanceGroupArgs(
        instance_type="m5.xlarge",
        instance_count=1,
    ),

    # Nodos core/worker:
    # - DataNodes de HDFS
    # - ejecución distribuida de Hive/MapReduce/YARN
    #
    # Total cluster:
    # 1 master + 3 core nodes = 4 EC2
    core_instance_group=aws.emr.ClusterCoreInstanceGroupArgs(
        instance_type="m5.xlarge",
        instance_count=3,
    ),

    # Logs de EMR en el bucket persistente manual.
    log_uri=emr_logs_uri,

    # Configuración Hadoop/HDFS.
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

    visible_to_all_users=True,
    termination_protection=False,

    # Mantiene el cluster encendido sin steps automáticos,
    # para poder conectarnos por SSH y ejecutar Hive manualmente.
    keep_job_flow_alive_when_no_steps=True,

    scale_down_behavior="TERMINATE_AT_TASK_COMPLETION",
)


# ============================================================
# EXPORTS DE PULUMI
# ============================================================

pulumi.export("persistent_bucket_name", persistent_bucket_name)
pulumi.export("taxi_s3_path", f"s3://{persistent_bucket_name}/datasets/taxi/yellow/")
pulumi.export("emr_logs_path", emr_logs_uri)

pulumi.export("cluster_id", cluster.id)
pulumi.export("master_public_dns", cluster.master_public_dns)

pulumi.export("hdfs_taxi_raw_path", "/datasets/taxi/yellow/raw")
pulumi.export("hdfs_taxi_warehouse_path", "/user/hive/warehouse")
pulumi.export("hdfs_wordcount_input_path", "/labs/wordcount/input")
pulumi.export("hdfs_inverted_index_input_path", "/labs/inverted-index/input")