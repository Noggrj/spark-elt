from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Adicionar o diretório do projeto ao PYTHONPATH
sys.path.append('/home/airflow/project')

# Importar funções do projeto
from pipeline.kafka_pipeline import executar_pipeline_kafka
from generator.data_generator import gerar_e_publicar_dados

# Argumentos padrão para as DAGs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG para executar o pipeline Kafka completo
with DAG(
    'kafka_pipeline_completo',
    default_args=default_args,
    description='Pipeline completo de Kafka (produção e consumo)',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['kafka', 'pipeline', 'completo'],
) as dag_completo:
    
    # Tarefa para executar o pipeline completo
    executar_pipeline = PythonOperator(
        task_id='executar_pipeline_kafka',
        python_callable=executar_pipeline_kafka,
        op_kwargs={
            'mode': 'both',
            'bootstrap_servers': 'kafka:29092'
        },
    )

# DAG para apenas produzir dados no Kafka
with DAG(
    'kafka_producer',
    default_args=default_args,
    description='Produção de dados para o Kafka',
    schedule_interval=timedelta(minutes=30),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['kafka', 'producer'],
) as dag_producer:
    
    # Tarefa para produzir dados no Kafka
    produzir_dados = PythonOperator(
        task_id='produzir_dados_kafka',
        python_callable=executar_pipeline_kafka,
        op_kwargs={
            'mode': 'produce',
            'bootstrap_servers': 'kafka:29092'
        },
    )

# DAG para apenas consumir dados do Kafka
with DAG(
    'kafka_consumer',
    default_args=default_args,
    description='Consumo de dados do Kafka',
    schedule_interval=timedelta(minutes=15),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['kafka', 'consumer'],
) as dag_consumer:
    
    # Tarefa para consumir dados do Kafka
    consumir_dados = PythonOperator(
        task_id='consumir_dados_kafka',
        python_callable=executar_pipeline_kafka,
        op_kwargs={
            'mode': 'consume',
            'bootstrap_servers': 'kafka:29092'
        },
    )

# DAG para geração contínua de dados
with DAG(
    'gerador_dados_continuo',
    default_args=default_args,
    description='Geração contínua de dados para o Kafka',
    schedule_interval=timedelta(hours=2),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['kafka', 'generator'],
) as dag_generator:
    
    # Tarefa para gerar dados continuamente
    gerar_dados = PythonOperator(
        task_id='gerar_dados_continuos',
        python_callable=gerar_e_publicar_dados,
        op_kwargs={
            'bootstrap_servers': 'kafka:29092',
            'intervalo': 1.0,
            'max_iteracoes': 100  # Limitar a 100 iterações por execução
        },
    )