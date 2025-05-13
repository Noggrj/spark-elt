import argparse
import time
import os

# Imports da camada Kafka
from src.kafka.producers import publicar_clientes_kafka, publicar_transacoes_kafka
from src.transform.spark_processing import main as processar_spark

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

def main():
    """
    Função principal que inicia o pipeline ELT com Kafka.
    """
    parser = argparse.ArgumentParser(description='Pipeline ELT com Kafka e Spark')
    parser.add_argument('--mode', choices=['produce', 'consume', 'both'], default='both',
                      help='Modo de execução: produce (apenas produzir), consume (apenas consumir), both (ambos)')
    parser.add_argument('--bootstrap-servers', default=os.environ.get('BOOTSTRAP_SERVERS', 'kafka:29092'),
                      help='Endereço dos servidores Kafka (padrão: kafka:29092)')
    
    args = parser.parse_args()
    
    # Verificar arquivos de dados
    if not verificar_arquivos():
        print("❌ Verifique se os arquivos de dados existem em data/raw/")
        return
    
    # Aguardar o Kafka inicializar completamente
    print("⏳ Aguardando 15 segundos para o Kafka inicializar completamente...")
    time.sleep(15)
    
    # Modo produtor: publicar dados no Kafka
    if args.mode in ['produce', 'both']:
        print("🔹 Iniciando produtores Kafka...")
        print(f"🔹 Conectando ao Kafka em: {args.bootstrap_servers}")
        publicar_clientes_kafka(bootstrap_servers=args.bootstrap_servers)
        publicar_transacoes_kafka(bootstrap_servers=args.bootstrap_servers)
    
    # Pequena pausa para garantir que as mensagens foram publicadas
    if args.mode == 'both':
        print("⏳ Aguardando 5 segundos para iniciar consumidores...")
        time.sleep(5)
    
    # Modo consumidor: processar dados com Spark Streaming
    if args.mode in ['consume', 'both']:
        print("🔹 Iniciando processamento Spark com Kafka...")
        processar_spark(modo="kafka", bootstrap_servers=args.bootstrap_servers)

if __name__ == "__main__":
    main()