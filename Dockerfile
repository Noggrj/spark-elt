FROM jupyter/pyspark-notebook

WORKDIR /home/jovyan/work

RUN pip install --no-cache-dir pyspark faker numpy pandas polars \
    flake8 isort black

COPY . .

CMD ["/opt/conda/bin/python", "-m", "spark-processing.py"]

