
# 🚀 Projeto ELT com PySpark, Kafka e Streaming

Este projeto é uma pipeline completa de **Extração, Carregamento e Transformação (ELT)** construída com Python, PySpark e Apache Kafka, organizada em contêineres Docker. A arquitetura implementa um fluxo de dados em tempo real, dividida em camadas (`extract`, `transform` e `kafka`), seguindo boas práticas de modularização e escalabilidade para processar grandes volumes de dados em streaming.

---

## 📁 Estrutura do Projeto

```
.
├── Dockerfile
├── Makefile
├── start_spark.py               # Ponto de entrada para execução via Docker
├── requirements.txt
├── data/
│   └── raw/                     # Contém os CSVs de entrada (clientes e transações)
├── src/
│   ├── __init__.py
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── extract_clientes.py
│   │   └── extract_transacoes.py
│   └── transform/
│       ├── __init__.py
│       └── spark_processing.py
```

---

## 🧱 Tecnologias Utilizadas

- [Python 3.11+](https://www.python.org/) - Linguagem de programação principal
- [Apache Spark 3+ (via PySpark)](https://spark.apache.org/) - Framework de processamento distribuído
- [Apache Kafka](https://kafka.apache.org/) - Plataforma de streaming distribuído
- [Kafka UI](https://github.com/provectuslabs/kafka-ui) - Interface visual para gerenciamento do Kafka
- [Pandas](https://pandas.pydata.org/) - Biblioteca para análise de dados
- [Faker](https://faker.readthedocs.io/) - Geração de dados sintéticos para testes
- [Docker](https://www.docker.com/) - Containerização da aplicação
- [Jupyter Base Notebook (imagem Docker)](https://hub.docker.com/r/jupyter/pyspark-notebook) - Ambiente interativo

---

## 📦 Instalação e Execução (via Docker)

### 1. Build da imagem

```bash
make build
```

### 2. Inicie os serviços e Execute o Pipeline

```bash
make start
```
### 3. Verifique os logs

## 📂 Fontes de Dados

Os dados de entrada estão localizados em `data/raw/`:

- `clientes.csv`
- `transacoes.csv`

Esses arquivos são validados antes da transformação com Spark:

- Checagem de colunas obrigatórias  
- Unicidade de chaves  
- Validação de formato de datas  

---

## 🔄 Pipeline

### 🔹 Etapa Extract (pandas)
- Valida dados brutos com `pandas`
- Verifica integridade e estrutura dos arquivos

### 🔸 Etapa Transform (PySpark)
- Cria colunas derivadas (`ano`, `mês`, `faixa_etaria`)
- Agrega dados por categoria, cidade e cliente
- Executa consultas SQL no Spark

---


## 🧰 Comandos úteis (Makefile)

```bash
make build           # Build da imagem Docker
make start           # Executa o pipeline via Docker
make lint            # Verifica estilo de código com flake8, isort
make lint-fix        # Aplica formatação com black, isort
make check-init      # Verifica arquivos __init__.py nas pastas
```

## 🌐 Webservice Kafka

O projeto agora inclui um webservice para interagir com o Kafka através de uma API REST.

### Endpoints disponíveis:

- `GET /`: Página inicial com informações sobre os endpoints
- `GET /status`: Verifica o status da conexão com o Kafka
- `GET /mensagens/{topico}`: Obtém as últimas mensagens de um tópico
- `POST /publicar/{topico}`: Publica uma mensagem em um tópico

### Executando o webservice:

```bash
# Localmente
make kafka-webservice

# Via Docker
make kafka-webservice-docker

## 🧑‍💻 Autor

---

## 📜 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.
