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
	@echo " Limpando pasta logs..."
	@if exist logs rmdir /s /q logs
	@mkdir logs
	@echo " Construindo imagem Docker $(IMAGE_NAME)..."
	docker build --no-cache -t $(IMAGE_NAME) .

# Inicia o container com Docker Compose
start:
	docker-compose up

# Acessa o bash dentro do container
login:
	docker exec -it $(CONTAINER_NAME) bash

# Parar os serviços
stop:
	docker-compose down

# Reiniciar
restart:
	docker-compose down
	docker-compose up

# Ver logs
watch-logs:
	docker-compose logs -f

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
	python extract/clientes.py
	python extract/transacoes.py

transform:
	python transform/spark_processing.py

run: extract transform

check-init:
	@echo Verificando __init__.py nos pacotes...
	@if not exist extract\__init__.py (echo ❌ extract\__init__.py faltando! & exit /b 1)
	@if not exist transform\__init__.py (echo ❌ transform\__init__.py faltando! & exit /b 1)
	@if not exist kafka_module\__init__.py (echo ❌ kafka_module\__init__.py faltando! & exit /b 1)
	@echo ✅ Todos os __init__.py estão presentes!

# Comandos Kafka
kafka-produce:
	python main.py --mode produce

kafka-consume:
	python main.py --mode consume

kafka-pipeline:
	python main.py --mode both

# Webservice Kafka
kafka-webservice:
	python -m kafka_module.webservice

kafka-webservice-docker:
	docker-compose up -d
	docker exec -it $(CONTAINER_NAME) python -m kafka_module.webservice

# Comandos Airflow
airflow-init:
	docker-compose up airflow-webserver airflow-scheduler -d

airflow-stop:
	docker-compose stop airflow-webserver airflow-scheduler postgres

airflow-logs:
	docker-compose logs -f airflow-webserver airflow-scheduler

airflow-ui:
	start http://localhost:8081
