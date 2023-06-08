#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example DAG which uses SparkKubernetesOperator and SparkKubernetesSensor.
In this example, we create two tasks which execute sequentially.
The first task is to submit sparkApplication on Kubernetes cluster(the example uses spark-pi application).
and the second task is to check the final state of the sparkApplication that submitted in the first state.

Spark-on-k8s operator is required to be already installed on Kubernetes
https://github.com/GoogleCloudPlatform/spark-on-k8s-operator
"""

from datetime import timedelta, datetime
from typing import Dict
import boto3

# [START import_module]
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.providers.trino.operators.trino import TrinoOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

# [END import_module]


def get_file_from_s3(s3_client, Bucket, Key) -> Dict:
    """ 
    S3 파일을 읽어서 utf-8 디코딩한 데이터를 반환합니다.
    단, 파일이 UTF-8로 작성되어 있어야 정상적으로 파일을 읽을 수 있음.
    Args:
        s3_client: boto3 s3 클라이언트
        Bucket: 버킷명
        Key: 오브젝트 키
    Returns:
        data_dict
    Raises:
        None
    Example:
        import boto3
        s3_client = boto3.client("s3")    
        bucket = "hr-rcmd-stg"
        key_sql = "redshift/sql/casting_query/inst1_tskxban01.sql"
        sql_file = get_file_from_s3(s3_client, bucket, key_sql)
        print(sql_file)
        print(type(sql_file)) # str
    """
    try:
        data = s3_client.get_object(Bucket=Bucket, Key=Key)
        file = data['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error Occurred get_file_from_s3: {e}")
        raise e
    return file

s3_client = boto3.client("s3")
Bucket = "imgr-buc-inner"
Key = "trino_sql/tier2_join.sql"

# [START default_args]
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'max_active_runs': 1,
    'retries': 0
}

# configmaps = [
#     k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="kubernetes-admin")),
#     k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="test-configmap-2")),
# ]

# [END default_args]

# [START instantiate_dag]

dag = DAG(
    'dw_example',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    tags=['For session']
)

t0 = SparkKubernetesOperator(
    task_id='Tier_0_spark',
    namespace="guru-tenant",
    application_file="t0_spark.yaml",
    kubernetes_conn_id="guru",
    do_xcom_push=True,
    dag=dag,
    api_group="sparkoperator.hpe.com",
    api_version="v1beta2"
)

t0_sensor = SparkKubernetesSensor(
    task_id='Tier_0_monitor',
    namespace="guru-tenant",
    application_name="{{ task_instance.xcom_pull(task_ids='Tier_0')['metadata']['name'] }}",
    kubernetes_conn_id="guru",
    dag=dag,
    api_group="sparkoperator.hpe.com"
)

t1 = SparkKubernetesOperator(
    task_id='Tier_1_spark',
    namespace="guru-tenant",
    application_file="t1_spark.yaml",
    kubernetes_conn_id="guru",
    do_xcom_push=True,
    dag=dag,
    api_group="sparkoperator.hpe.com",
    api_version="v1beta2"
)

t1_sensor = SparkKubernetesSensor(
    task_id='Tier_1_monitor',
    namespace="guru-tenant",
    application_name="{{ task_instance.xcom_pull(task_ids='Tier_0')['metadata']['name'] }}",
    kubernetes_conn_id="guru",
    dag=dag,
    api_group="sparkoperator.hpe.com"
)

t2 = TrinoOperator(
        task_id="Tier_2_trino",
        trino_conn_id="trino_hive",
        sql=get_file_from_s3(s3_client, Bucket, Key),
        handler=list
    )

t0 >> t0_sensor >> t1 >> t1_sensor >> t2