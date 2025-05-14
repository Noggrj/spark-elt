# Nome fixo da imagem e do container
IMAGE_NAME=pyspark-custom
CONTAINER_NAME=pyspark-container

# Caminhos
CONTAINER_WORKDIR=/home/jovyan/work
HOST_WORKDIR=$(shell cd)

# Caminho absoluto seguro do host (resolvido em tempo de execução)
HOST_WORKDIR=$(shell cd && pwd)

# Comando para build da imagem
build:
	docker build -t $(IMAGE_NAME) .

# Inicia o container com montagem de volume correta
start:
	docker run -it -v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" -p 8888:8888 $(IMAGE_NAME)

# Acessa o bash dentro do container
login:
	docker run -it -v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" -p 8888:8888 $(IMAGE_NAME) bash

# Parar (inútil em containers interativos efêmeros)
stop:
	@echo "Use Ctrl+C para parar o container."

# Reiniciar
restart:
	make stop
	make start

# Logs não aplicáveis
watch-logs:
	@echo "Logs indisponíveis com container efêmero."

# Lint
lint:
	isort . --check-only
	flake8 .

# Fix lint
lint-fix:
	isort .
	black .
	flake8 .

extract:
	python src/extract/extract_clientes.py
	python src/extract/extract_transacoes.py

transform:
	python src/transform/spark_processing.py

run: extract transform

check-init:
	@echo Verificando __init__.py nos pacotes...
	@if not exist src\__init__.py (echo ❌ src\__init__.py faltando! & exit /b 1)
	@if not exist src\extract\__init__.py (echo ❌ src\extract\__init__.py faltando! & exit /b 1)
	@if not exist src\transform\__init__.py (echo ❌ src\transform\__init__.py faltando! & exit /b 1)
	@echo ✅ Todos os __init__.py estão presentes!

# Comandos Kafka
kafka-produce:
	python kafka_pipeline.py --mode produce

kafka-consume:
	python kafka_pipeline.py --mode consume

kafka-pipeline:
	python kafka_pipeline.py --mode both

# Webservice Kafka
kafka-webservice:
	python -m src.kafka.webservice

kafka-webservice-docker:
	docker-compose up -d
	docker exec -it $(CONTAINER_NAME) python -m src.kafka.webservice
