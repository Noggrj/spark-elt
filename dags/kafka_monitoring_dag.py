from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import json
import requests
from kafka import KafkaConsumer, KafkaProducer
import sys

# Adicionar o diretório do projeto ao PYTHONPATH
sys.path.append('/home/airflow/project')

# Argumentos padrão para as DAGs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Função para verificar a saúde do Kafka
def verificar_saude_kafka():
    try:
        # Tentar criar um consumidor Kafka
        consumer = KafkaConsumer(
            bootstrap_servers='kafka:29092',
            group_id='health_check',
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000
        )
        
        # Listar tópicos disponíveis
        topics = consumer.topics()
        
        # Fechar o consumidor
        consumer.close()
        
        return {
            'status': 'healthy',
            'topics': list(topics),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Função para contar mensagens nos tópicos
def contar_mensagens_topicos():
    try:
        # Criar consumidor
        consumer = KafkaConsumer(
            bootstrap_servers='kafka:29092',
            group_id='message_counter',
            auto_offset_reset='earliest',
            consumer_timeout_ms=10000
        )
        
        # Obter tópicos
        topics = consumer.topics()
        
        # Contar mensagens por tópico
        resultados = {}
        for topic in topics:
            # Atribuir partições do tópico
            partitions = consumer.partitions_for_topic(topic)
            if not partitions:
                resultados[topic] = 0
                continue
                
            # Obter final offsets
            tp_list = [consumer.TopicPartition(topic, p) for p in partitions]
            consumer.assign(tp_list)
            consumer.seek_to_beginning()
            beginning_offsets = {tp: consumer.position(tp) for tp in tp_list}
            
            consumer.seek_to_end()
            end_offsets = {tp: consumer.position(tp) for tp in tp_list}
            
            # Calcular total de mensagens
            total_msgs = sum(end_offsets[tp] - beginning_offsets[tp] for tp in tp_list)
            resultados[topic] = total_msgs
        
        # Fechar consumidor
        consumer.close()
        
        return {
            'status': 'success',
            'contagem_mensagens': resultados,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# DAG para monitoramento do Kafka
with DAG(
    'kafka_monitoring',
    default_args=default_args,
    description='Monitoramento do Kafka',
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['kafka', 'monitoring'],
) as dag_monitoring:
    
    # Tarefa para verificar a saúde do Kafka
    verificar_saude = PythonOperator(
        task_id='verificar_saude_kafka',
        python_callable=verificar_saude_kafka,
    )
    
    # Tarefa para contar mensagens nos tópicos
    contar_mensagens = PythonOperator(
        task_id='contar_mensagens_topicos',
        python_callable=contar_mensagens_topicos,
    )
    
    # Definir a ordem de execução
    verificar_saude >> contar_mensagens