from flask import Flask, request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import time
import os
from .producers import criar_produtor

app = Flask(__name__)

# Configuração padrão
BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')

# Cache de mensagens para os consumidores
mensagens_cache = {
    'clientes': [],
    'transacoes': []
}

# Função para consumir mensagens em background
def consumir_mensagens(topic, group_id='webservice-group'):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        print(f"✅ Consumidor iniciado para o tópico: {topic}")
        
        for message in consumer:
            # Adiciona a mensagem ao cache
            mensagens_cache[topic].append(message.value)
            # Mantém apenas as últimas 100 mensagens
            if len(mensagens_cache[topic]) > 100:
                mensagens_cache[topic] = mensagens_cache[topic][-100:]
            
    except Exception as e:
        print(f"❌ Erro ao consumir mensagens do tópico {topic}: {str(e)}")

# Inicia os consumidores em threads separadas
# Substituindo o @app.before_first_request que foi removido em versões recentes do Flask
@app.route('/iniciar-consumidores', methods=['GET'])
def iniciar_consumidores_endpoint():
    iniciar_consumidores()
    return jsonify({'status': 'consumidores iniciados'})

def iniciar_consumidores():
    for topic in ['clientes', 'transacoes']:
        thread = threading.Thread(target=consumir_mensagens, args=(topic,))
        thread.daemon = True
        thread.start()
        print(f"🔄 Thread de consumo iniciada para o tópico: {topic}")

# Inicialização com with_appcontext
@app.before_request
def before_request():
    if not hasattr(app, '_consumidores_iniciados'):
        iniciar_consumidores()
        app._consumidores_iniciados = True

# Rota principal
@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'endpoints': {
            'GET /status': 'Verifica status da conexão com Kafka',
            'GET /mensagens/{topico}': 'Obtém mensagens do tópico',
            'POST /publicar/{topico}': 'Publica mensagem no tópico'
        }
    })

# Verificar status da conexão com Kafka
@app.route('/status')
def status():
    try:
        producer = criar_produtor(bootstrap_servers=BOOTSTRAP_SERVERS, max_retries=1)
        producer.close()
        return jsonify({'status': 'conectado', 'bootstrap_servers': BOOTSTRAP_SERVERS})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500

# Obter mensagens de um tópico
@app.route('/mensagens/<topico>')
def obter_mensagens(topico):
    if topico not in mensagens_cache:
        return jsonify({'erro': f'Tópico {topico} não encontrado'}), 404
    
    # Opção para limitar o número de mensagens retornadas
    limite = request.args.get('limite', default=50, type=int)
    return jsonify({
        'topico': topico,
        'mensagens': mensagens_cache[topico][-limite:]
    })

# Publicar mensagem em um tópico
@app.route('/publicar/<topico>', methods=['POST'])
def publicar_mensagem(topico):
    if not request.is_json:
        return jsonify({'erro': 'Conteúdo deve ser JSON'}), 400
    
    dados = request.get_json()
    
    try:
        producer = criar_produtor(bootstrap_servers=BOOTSTRAP_SERVERS)
        
        # Extrai a chave se fornecida, ou usa None
        chave = dados.pop('key', None)
        
        # Envia a mensagem
        future = producer.send(topico, key=chave, value=dados)
        # Aguarda confirmação
        record_metadata = future.get(timeout=10)
        
        producer.flush()
        producer.close()
        
        return jsonify({
            'status': 'sucesso',
            'topico': topico,
            'particao': record_metadata.partition,
            'offset': record_metadata.offset
        })
        
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)