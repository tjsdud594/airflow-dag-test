# airflow-dag-test
## 💡목표
1. Kubernetes 환경에서 Spark Job을 호출하는 방법 습득
2. Airflow에서 Trino Job을 호출하는 방법 습득

![image](https://github.com/tjsdud594/airflow-dag-test/assets/84279479/e9157407-d8c8-4eb2-b9b5-1a679ecff444)

# 1. Kubernetes 환경에서 Spark Job을 호출 방법
## 사전 작업 
- Airflow의 Connections에서 kubernetes Cluster Connection 생성 필요
  - 해당 connection name은 SparkKubernetesOperator의 kubernetes_conn_id parameter로 쓰인다.
## Dag
- 사용 Operator : SparkKubernetesOperator 
- dag file은 git에 위치한다.
## SparkApplication
- format : yaml
- spark-submit에 들어갈 설정값들을 넣어준다.
  - memory/cpu 설정, spark job 파일 위치, spark config, image, ...
- SparkApplication은 git에 위치한다.
## Spark
- 실제로 실행할 Spark code
- S3에 위치하도록 설정

# 2. Kubernetes 환경에서 Trino Job을 호출 방법
## 사전 작업 
- Airflow의 Connections에서 Trino Connection 생성 필요
  - 해당 connection name은 TrinoOperator의 trino_conn_id parameter로 쓰인다.
 
## 호출 방식
- TrinoOperator : task_id, trino_conn_id, sql, dag parameter 필요
  - sql : trino에서 실행할 query를 직접 string으로 넣으면 된다.
    - 기본적으로 소스파일을 s3에서 관리하고 있기때문에 s3의 파일을 읽어오는 방식으로 넣어주었다.
