from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

project_root = "/Users/viniciussilvamoreira/Downloads/Analise-transporte-publico"
venv_python = f"{project_root}/.venv/bin/python"
spark_submit = f"{project_root}/.venv/bin/spark-submit"

with DAG(
    dag_id="sptrans_data_pipeline",
    start_date=pendulum.datetime(2025, 7, 6, tz="America/Sao_Paulo"),
    schedule_interval="@daily",
    catchup=False,
    tags=["sptrans", "data_engineering"],
) as dag:
    
    start_producer = BashOperator(
        task_id="start_kafka_producer",
        bash_command=f"gtimeout 300 {venv_python} {project_root}/kafka_producer/producer.py",
    )

    run_spark_processor = BashOperator(
        task_id="run_spark_streaming_processor",
        bash_command=(
            f"{spark_submit} "
            f"--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 "
            f"{project_root}/spark_jobs/stream_processor.py"
        ),
    )

    start_producer >> run_spark_processor