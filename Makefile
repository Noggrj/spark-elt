# Nome fixo da imagem e do container
IMAGE_NAME=pyspark-custom
CONTAINER_NAME=pyspark-container

# Caminhos
CONTAINER_WORKDIR=/home/jovyan/work
HOST_WORKDIR=$(shell cd)

# Build da imagem
build:
	docker build -t $(IMAGE_NAME) .

# Inicia o container com nome fixo
start:
	docker run -it \
		--name $(CONTAINER_NAME) \
		-v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" \
		-w $(CONTAINER_WORKDIR) \
		-p 8888:8888 \
		$(IMAGE_NAME)

# Bash dentro do container (ou novo efêmero se não existir)
login:
	docker exec -it $(CONTAINER_NAME) bash || \
	docker run -it --name $(CONTAINER_NAME) \
		-v "$(HOST_WORKDIR):$(CONTAINER_WORKDIR)" \
		-w $(CONTAINER_WORKDIR) \
		-p 8888:8888 \
		$(IMAGE_NAME) bash

# Parar e remover container
stop:
	docker stop $(CONTAINER_NAME) || exit 0
	docker rm $(CONTAINER_NAME) || exit 0

# Reinicia container
restart:
	make stop
	make start

# Logs do container
watch-logs:
	docker logs -f $(CONTAINER_NAME)

# Lint
lint:
	isort . --check-only
	flake8 .

# Fix lint
lint-fix:
	isort .
	black .
	flake8 .

# Execução local
extract:
	python src/extract/extract_clientes.py
	python src/extract/extract_transacoes.py

transform:
	python src/transform/spark_processing.py

run: extract transform

# Verifica __init__.py
check-init:
	@echo Verificando __init__.py nos pacotes...
	@if not exist src\__init__.py (echo ❌ src\__init__.py faltando! & exit /b 1)
	@if not exist src\extract\__init__.py (echo ❌ src\extract\__init__.py faltando! & exit /b 1)
	@if not exist src\transform\__init__.py (echo ❌ src\transform\__init__.py faltando! & exit /b 1)
	@echo ✅ Todos os __init__.py estão presentes!
