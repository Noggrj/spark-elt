# Nome fixo da imagem e do container
IMAGE_NAME=pyspark-custom
CONTAINER_NAME=pyspark-container

# Caminho interno padrão da imagem jupyter/pyspark-notebook
CONTAINER_WORKDIR=/home/jovyan/work

# Caminho absoluto do host (ajustado para Windows)
HOST_WORKDIR=$(CURDIR)

# Build da imagem
build:
	docker build -t $(IMAGE_NAME) .

# Inicia os containers com docker-compose
start:
	docker-compose up -d

# Para e remove os containers com docker-compose
stop:
	docker-compose down

# Acessa o bash no container existente (ou em novo efêmero se não existir)
login:
	docker exec -it $(CONTAINER_NAME) bash || docker run -it --name $(CONTAINER_NAME) -v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" -w $(CONTAINER_WORKDIR) -p 8888:8888 $(IMAGE_NAME) bash

# Reiniciar container
restart:
	make stop
	make start

# Logs do container nomeado
watch-logs:
	docker-compose logs -f

# Checagem de código
lint:
	isort . --check-only
	flake8 .

# Correções automáticas
lint-fix:
	isort .
	black .
	flake8 .

# Execução local sem Docker
extract:
	python src/extract/extract_clientes.py
	python src/extract/extract_transacoes.py

transform:
	python src/transform/spark_processing.py

run: extract transform

# Verificação dos __init__.py
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
