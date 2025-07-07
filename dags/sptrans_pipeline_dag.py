from __future__ import annotations
import pendulum
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

project_root = "/Users/viniciussilvamoreira/Downloads/Analise-transporte-publico"

venv_python = f"{project_root}/.venv/bin/python"
spark_submit = f"{project_root}/.venv/bin/spark-submit"

with DAG(
    dag_id="sptrans_data_pipeline",
    start_date=pendulum.datetime(2025, 7, 7, tz="America/Sao_Paulo"),
    schedule_interval=None,
    catchup=False,
    tags=["sptrans", "data_engineering_project"],
    doc_md="""
    ### Pipeline de Dados da SPTrans (Versão Final Robusta)
    
    Orquestra a coleta, processamento e armazenamento de dados da SPTrans.
    Este pipeline usa um produtor offline para garantir a execução a qualquer momento.
    
    1.  **start_kafka_producer**: Executa o produtor offline que lê dados de um arquivo de amostra.
    2.  **wait_for_topic_creation**: Espera 15 segundos para o tópico ser criado no Kafka.
    3.  **run_spark_streaming_processor**: Inicia o job Spark para consumir os dados e salvá-los em formato Parquet.
    """,
) as dag:
    
    start_producer = BashOperator(
        task_id="start_kafka_producer",
        bash_command=(
            f"gtimeout 300 {venv_python} {project_root}/kafka_producer/producer_offline.py || "
            f"if [ $? -eq 124 ]; then exit 0; else exit $?; fi"
        ),
    )

    wait_for_topic_creation = BashOperator(
        task_id="wait_for_topic_creation",
        bash_command="echo 'Aguardando 15 segundos...' && sleep 15",
    )

    run_spark_processor = BashOperator(
        task_id="run_spark_streaming_processor",
        bash_command=(
            f"{spark_submit} "
            f"--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 "
            f"{project_root}/spark_jobs/stream_processor.py"
        ),
    )

    start_producer >> wait_for_topic_creation >> run_spark_processor