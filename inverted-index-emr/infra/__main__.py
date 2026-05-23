import random

import pulumi
import pulumi_aws as aws


# ============================================================
# GENERACIÓN DE NOMBRE ÚNICO PARA EL BUCKET S3
# ============================================================

# En AWS S3, los nombres de buckets deben ser globalmente únicos.
# Por eso generamos un sufijo aleatorio para reducir la posibilidad
# de que el nombre ya exista en otra cuenta AWS.
random_suffix: int = random.randint(10000, 99999)

# Nombre real del bucket S3.
bucket_name: str = f"inverted-index-emr-{random_suffix}"


# ============================================================
# CREACIÓN DEL BUCKET S3
# ============================================================

# Este bucket almacenará:
# - input/: archivos de entrada .txt
# - jars/: archivo .jar del job MapReduce
# - output/: resultados generados por Hadoop
# - logs/: logs del cluster EMR
bucket = aws.s3.Bucket(
    resource_name="inverted-index-bucket",
    bucket=bucket_name,
)


# ============================================================
# CREACIÓN DEL CLUSTER EMR
# ============================================================

# Amazon EMR levantará un cluster Hadoop administrado.
# En este laboratorio usaremos Hadoop MapReduce para ejecutar
# el índice invertido.
cluster = aws.emr.Cluster(
    resource_name="inverted-index-emr-cluster",

    # Nombre visible del cluster en AWS.
    name="inverted-index-emr-cluster",

    # Versión de Amazon EMR.
    release_label="emr-7.0.0",

    # Aplicaciones instaladas en el cluster.
    applications=["Hadoop"],

    # Rol IAM usado por el servicio EMR.
    service_role="EMR_DefaultRole",

    # Perfil IAM usado por las instancias EC2 del cluster.
    ec2_attributes=aws.emr.ClusterEc2AttributesArgs(
        instance_profile="EMR_EC2_DefaultRole",
    ),

    # Nodo master: coordina el cluster.
    master_instance_group=aws.emr.ClusterMasterInstanceGroupArgs(
        instance_type="m5.xlarge",
        instance_count=1,
    ),

    # Nodo core/worker: ejecuta tareas MapReduce.
    core_instance_group=aws.emr.ClusterCoreInstanceGroupArgs(
        instance_type="m5.xlarge",
        instance_count=1,
    ),

    # Ruta S3 donde EMR guardará logs.
    log_uri=pulumi.Output.concat(
        "s3://",
        bucket.bucket,
        "/logs/",
    ),

    # Configuración Hadoop: MapReduce usando YARN.
    configurations_json="""
    [
      {
        "Classification": "mapred-site",
        "Properties": {
          "mapreduce.framework.name": "yarn"
        }
      }
    ]
    """,

    # Hace visible el cluster para usuarios autorizados.
    visible_to_all_users=True,

    # Permite eliminar el cluster sin protección extra.
    termination_protection=False,

    # Comportamiento al reducir/apagar nodos.
    scale_down_behavior="TERMINATE_AT_TASK_COMPLETION",
)


# ============================================================
# EXPORTS DE PULUMI
# ============================================================

# Estos valores aparecerán al ejecutar pulumi up.
# Luego los usaremos para subir input, subir el .jar,
# ejecutar el job y revisar resultados.

pulumi.export("bucket_name", bucket.bucket)

pulumi.export(
    "input_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/input/"),
)

pulumi.export(
    "jar_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/jars/"),
)

pulumi.export(
    "output_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/output/"),
)

pulumi.export(
    "logs_path",
    pulumi.Output.concat("s3://", bucket.bucket, "/logs/"),
)

pulumi.export("cluster_id", cluster.id)