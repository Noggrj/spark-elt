FROM jupyter/pyspark-notebook

# Diretório onde está a pasta src/
WORKDIR /home/jovyan/work

# Instala dependências adicionais
RUN pip install --no-cache-dir pyspark faker numpy pandas polars \
    flake8 isort black

# Garante que o Python encontre a pasta src/ como pacote
ENV PYTHONPATH=/home/jovyan/work

# Copia todos os arquivos para dentro do container
COPY . .

# Executa o script como módulo (forma correta para pacotes Python)
CMD ["/opt/conda/bin/python", "-m", "spark-processing.py"]
