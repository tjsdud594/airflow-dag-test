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
""" ###############################
https://github.com/apache/airflow/blob/providers-trino/5.1.0/tests/system/providers/trino/example_trino.py
""" 
from datetime import timedelta, datetime

# [START import_module]
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.providers.trino.operators.trino import TrinoOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

# [END import_module]

args = {'owner': 'syryu',
        'start_date': days_ago(n=1)}

# [START instantiate_dag]

with DAG(
    dag_id="example_trino",
    default_args=args,
    schedule=None,  # Override to match your needs
    catchup=False,
    tags=["example"]
) as dag:
    
    trino_create_schema = TrinoOperator(
            task_id="trino_create_schema",
            trino_conn_id="trino_hive",
            sql=f"CREATE SCHEMA IF NOT EXISTS airflow_trino3",
            handler=list
        )

    trino_create_table = TrinoOperator(
            task_id="trino_create_table",
            trino_conn_id="trino_hive",
            sql=f"""CREATE TABLE IF NOT EXISTS airflow_trino3.test3(
            cityid bigint,
            cityname varchar
            )""",
            handler=list
        )

    trino_insert = TrinoOperator(
            task_id="trino_insert",
            trino_conn_id="trino_hive",
            sql=f"""INSERT INTO airflow_trino3.test3 VALUES (3, 'San Francisco')""",
            handler=list
        )

    trino_templated_query = TrinoOperator(
            task_id="trino_templated_query",
            trino_conn_id="trino_hive",
            sql="SELECT * FROM {{ params.SCHEMA }}.{{ params.TABLE }}",
            handler=list,
            params={"SCHEMA": "airflow_trino3", "TABLE": "test3"}
        )


trino_create_schema >> trino_create_table >> trino_insert >> trino_templated_query