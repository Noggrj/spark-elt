from kafka import KafkaProducer
import json
import pandas as pd
import time
import os

def criar_produtor(bootstrap_servers='localhost:9092', max_retries=5, retry_interval=5):
    """
    Cria e retorna uma instância do produtor Kafka com tentativas de reconexão.
    """
    for attempt in range(max_retries):
        try:
            print(f"🔄 Tentativa {attempt+1} de conectar ao Kafka em {bootstrap_servers}")
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8')
            )
            print(f"✅ Conexão com Kafka estabelecida com sucesso!")
            return producer
        except Exception as e:
            print(f"⚠️ Erro ao conectar ao Kafka: {str(e)}")
            if attempt < max_retries - 1:
                print(f"⏳ Aguardando {retry_interval} segundos antes de tentar novamente...")
                time.sleep(retry_interval)
            else:
                print("❌ Número máximo de tentativas excedido. Não foi possível conectar ao Kafka.")
                raise

def publicar_clientes_kafka(path="data/raw/clientes.csv", topic="clientes", bootstrap_servers='localhost:9092'):
    """
    Lê o arquivo de clientes e publica cada registro como uma mensagem no Kafka.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {path}")
    
    producer = criar_produtor(bootstrap_servers)
    df = pd.read_csv(path)
    
    print(f"✅ Iniciando publicação de {len(df)} clientes no tópico '{topic}'")
    
    for _, row in df.iterrows():
        # Converte a linha para dicionário e publica
        data = row.to_dict()
        producer.send(topic, key=data['id_cliente'], value=data)
        # Pequena pausa para não sobrecarregar
        time.sleep(0.01)
    
    producer.flush()
    print(f"✅ {len(df)} mensagens de clientes publicadas com sucesso!")
    
    return True

def publicar_transacoes_kafka(path="data/raw/transacoes.csv", topic="transacoes", bootstrap_servers='localhost:9092'):
    """
    Lê o arquivo de transações e publica cada registro como uma mensagem no Kafka.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {path}")
    
    producer = criar_produtor(bootstrap_servers)
    df = pd.read_csv(path)
    
    print(f"✅ Iniciando publicação de {len(df)} transações no tópico '{topic}'")
    
    for _, row in df.iterrows():
        # Converte a linha para dicionário e publica
        data = row.to_dict()
        producer.send(topic, key=data['id_transacao'], value=data)
        # Pequena pausa para não sobrecarregar
        time.sleep(0.01)
    
    producer.flush()
    print(f"✅ {len(df)} mensagens de transações publicadas com sucesso!")
    
    return True

if __name__ == "__main__":
    # Teste dos produtores
    publicar_clientes_kafka()
    publicar_transacoes_kafka()