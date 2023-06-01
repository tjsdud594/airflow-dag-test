from datetime import datetime, timedelta
# The DAG object; we'll need this to instantiate a DAG
# from airflow import DAG
from airflow.models import DAG

# Operators; we need this to operate!
# from airflow.operators.python import PythonOperator
from airflow.operators.python_operator import PythonOperator

with DAG(
    "spark_test",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5)
    },
    description="A simple spark tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    def spark_job():
        from pyspark.sql import SparkSession
        import pandas as pd 

        print("1111111111111")
        
        spark = SparkSession.builder.master("local").appName("sparktest").getOrCreate()
        print("2222222222222222")

        df_test = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [10.0, 3.5, 7.315],
            'c': ['apple', 'banana', 'tomato']
        })
        print("3333333333333")

        df_spark = spark.createDataFrame(df_test)
        print("444444444")

        df_spark.show()
        df_test.head()
        print("555555555")

    t1 = PythonOperator(task_id='task_1', python_callable=spark_job, dag=dag)

    t1