import time
import os

# Imports da camada Kafka
from kafka_module.producers import publicar_clientes_kafka, publicar_transacoes_kafka
from transform.spark_processing import main as processar_spark

def verificar_arquivos():
    """
    Verifica se os arquivos de dados existem.
    """
    arquivos = [
        "data/raw/clientes.csv",
        "data/raw/transacoes.csv"
    ]
    
    for arquivo in arquivos:
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return False
    
    return True

def executar_pipeline_kafka(mode='both', bootstrap_servers='kafka:29092'):
    """
    Executa o pipeline ELT com Kafka.
    
    Parâmetros:
    - mode: Modo de execução ('produce', 'consume', 'both')
    - bootstrap_servers: Endereço dos servidores Kafka
    """
    # Verificar arquivos de dados
    if not verificar_arquivos():
        print("❌ Verifique se os arquivos de dados existem em data/raw/")
        return
    
    # Aguardar o Kafka inicializar completamente
    print("⏳ Aguardando 15 segundos para o Kafka inicializar completamente...")
    time.sleep(15)
    
    # Modo produtor: publicar dados no Kafka
    if mode in ['produce', 'both']:
        print("🔹 Iniciando produtores Kafka...")
        print(f"🔹 Conectando ao Kafka em: {bootstrap_servers}")
        publicar_clientes_kafka(bootstrap_servers=bootstrap_servers)
        publicar_transacoes_kafka(bootstrap_servers=bootstrap_servers)
    
    # Pequena pausa para garantir que as mensagens foram publicadas
    if mode == 'both':
        print("⏳ Aguardando 5 segundos para iniciar consumidores...")
        time.sleep(5)
    
    # Modo consumidor: processar dados com Spark Streaming
    if mode in ['consume', 'both']:
        print("🔹 Iniciando processamento Spark com Kafka...")
        processar_spark(modo="kafka", bootstrap_servers=bootstrap_servers)

# Ponto de entrada para execução direta (compatibilidade)
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Pipeline ELT com Kafka e Spark')
    parser.add_argument('--mode', choices=['produce', 'consume', 'both'], default='both',
                      help='Modo de execução: produce (apenas produzir), consume (apenas consumir), both (ambos)')
    parser.add_argument('--bootstrap-servers', default=os.environ.get('BOOTSTRAP_SERVERS', 'kafka:29092'),
                      help='Endereço dos servidores Kafka (padrão: kafka:29092)')
    
    args = parser.parse_args()
    executar_pipeline_kafka(args.mode, args.bootstrap_servers)