
# 🚀 Projeto ELT com PySpark

Este projeto é uma pipeline de **Extração, Validação e Transformação (ELT)** construída com Python e PySpark, organizada em um contêiner Docker. A arquitetura está dividida em camadas (`extract` e `transform`) e segue boas práticas de modularização e escalabilidade para processar grandes volumes de dados.

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
- [Pandas](https://pandas.pydata.org/)
- [Faker](https://faker.readthedocs.io/)
- [Docker](https://www.docker.com/)
- [Jupyter Base Notebook (imagem Docker)](https://hub.docker.com/r/jupyter/pyspark-notebook)

---

## 📦 Instalação e Execução (via Docker)

### 1. Build da imagem

```bash
make build
```

Ou manualmente:

```bash
docker build -t pyspark-custom .
```

### 2. Execução do pipeline

```bash
make start
```

Ou diretamente:

```bash
docker run -it \
  -v "$(pwd):/home/jovyan/work" \
  -w /home/jovyan/work \
  -p 8888:8888 \
  pyspark-custom
```

---

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

## 🧪 Testar validação manual

```bash
python -m src.extract.extract_clientes
python -m src.extract.extract_transacoes
```

---

## 🧰 Comandos úteis (Makefile)

```bash
make build           # Build da imagem Docker
make start           # Executa o pipeline via Docker
make lint            # Verifica estilo de código com flake8, isort
make lint-fix        # Aplica formatação com black, isort
make check-init      # Verifica arquivos __init__.py nas pastas
```

---

## 📄 Requisitos

Você pode gerar os requisitos do container com:

```bash
docker run -it pyspark-custom pip freeze > requirements.txt
```

---

## 🧑‍💻 Autor

---

## 📜 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.
