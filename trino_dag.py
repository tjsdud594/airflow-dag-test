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
from airflow import models

# [END import_module]

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

# [END default_args]

# [START instantiate_dag]

dag = models.DAG(
    dag_id='trino_test',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    tags=['example']
)

def trino_job_print(sql, **kwargs):
    print('=' * 60)
    print('fruit_name:', sql, '\n finished')
    print('=' * 60)
    print(kwargs)
    print('=' * 60)
    return 'print complete!!!'

trino_create_schema = TrinoOperator(
        task_id="trino_create_schema",
        sql=f"CREATE SCHEMA IF NOT EXISTS airflow_trino;",
        handler=list,
    )

t1 = PythonOperator(task_id='task_1',
                    provide_context=True,
                    python_callable=trino_job_print,
                    op_kwargs={'sql': 'CREATE SCHEMA IF NOT EXISTS airflow_trino;'},
                    dag=dag)

trino_create_table = TrinoOperator(
        task_id="trino_create_table",
        sql=f"""CREATE TABLE IF NOT EXISTS airflow_trino.test1(
        cityid bigint,
        cityname varchar
        )""",
        handler=list,
    )


t2 = PythonOperator(task_id='task_1',
                    provide_context=True,
                    python_callable=trino_job_print,
                    op_kwargs={'sql': 'CREATE TABLE IF NOT EXISTS airflow_trino.test1'},
                    dag=dag)


trino_insert = TrinoOperator(
        task_id="trino_insert",
        sql=f"""INSERT INTO airflow_trino.test1 VALUES (1, 'San Francisco');""",
        handler=list,
    )

t3 = PythonOperator(task_id='task_1',
                    provide_context=True,
                    python_callable=trino_job_print,
                    op_kwargs={'sql': 'INSERT INTO airflow_trino.test1 VALUES (1, "San Francisco")'},
                    dag=dag)

trino_templated_query = TrinoOperator(
        task_id="trino_templated_query",
        sql="SELECT * FROM {{ params.SCHEMA }}.{{ params.TABLE }}",
        handler=list,
        params={"SCHEMA": "airflow_trino", "TABLE": "test1"},
    )

t4 = PythonOperator(task_id='task_1',
                    provide_context=True,
                    python_callable=trino_job_print,
                    op_kwargs={'sql': 'SELECT * FROM airflow_trino.test1'},
                    dag=dag)

trino_create_schema >> t1 >> trino_create_table >> t2 >> trino_insert >> t3 >> trino_templated_query