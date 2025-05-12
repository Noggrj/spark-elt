# Nome fixo da imagem e do container
IMAGE_NAME=pyspark-custom
CONTAINER_NAME=pyspark-container

# Caminho interno padrão da imagem jupyter/pyspark-notebook
CONTAINER_WORKDIR=/home/jovyan/work

# Caminho absoluto do host (ajustado em tempo real)
HOST_WORKDIR=$(shell pwd)

# Build da imagem
build:
	docker build -t $(IMAGE_NAME) .

# Inicia o container com nome fixo e volume montado
start:
	docker run -it \
		--name $(CONTAINER_NAME) \
		-v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" \
		-w $(CONTAINER_WORKDIR) \
		-p 8888:8888 \
		$(IMAGE_NAME)

# Acessa o bash no container existente (ou em novo efêmero se não existir)
login:
	docker exec -it $(CONTAINER_NAME) bash || \
	docker run -it --name $(CONTAINER_NAME) \
		-v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" \
		-w $(CONTAINER_WORKDIR) \
		-p 8888:8888 \
		$(IMAGE_NAME) bash

# Para e remove o container pelo nome fixo
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Reiniciar container
restart:
	make stop
	make start

# Logs do container nomeado
watch-logs:
	docker logs -f $(CONTAINER_NAME)

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
