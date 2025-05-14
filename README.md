# 🚀 Projeto ELT com PySpark, Kafka e Streaming

## 📋 Sobre o Projeto
Este projeto implementa uma pipeline de dados em tempo real utilizando tecnologias modernas de Big Data. A arquitetura é baseada em um fluxo ELT (Extração, Carregamento e Transformação) que processa dados de clientes e transações através de um sistema distribuído.

O pipeline é composto por:

- Extração e validação de dados com Pandas
- Geração de dados sintéticos com Faker para testes e desenvolvimento
- Streaming em tempo real com Apache Kafka
- Processamento distribuído com Apache Spark
- Visualização através de interface gráfica para Kafka
Tudo isso é orquestrado em contêineres Docker, garantindo portabilidade e escalabilidade.

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

- [Python 3.11+](https://www.python.org/)
- [Apache Spark 3+ (via PySpark)](https://spark.apache.org/)
- [Apache Kafka](https://kafka.apache.org/) - Plataforma de streaming distribuído
- [Zookeeper](https://zookeeper.apache.org/) - Coordenação de serviços distribuídos
- [Flask](https://flask.palletsprojects.com/) - Framework web para API REST
- [Pandas](https://pandas.pydata.org/)
- [Faker](https://faker.readthedocs.io/)
- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
- [Jupyter Base Notebook (imagem Docker)](https://hub.docker.com/r/jupyter/pyspark-notebook)


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


## 🧑‍💻 Autor
Desenvolvido por Matheus Nogueira

## 📜 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.
