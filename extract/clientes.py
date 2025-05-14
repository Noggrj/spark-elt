# src/extract/extract_clientes.py

import pandas as pd
import os

def extrair_e_validar_clientes(path: str = "data/raw/clientes.csv") -> pd.DataFrame:
    """
    Lê e valida o arquivo clientes.csv com pandas.
    Valida a existência do arquivo, as colunas obrigatórias e unicidade de IDs.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {path}")

    df = pd.read_csv(path)

    print("✅ CSV de clientes lido com sucesso!")
    print(df.head())
    print("🔎 Colunas:", list(df.columns))
    print("📏 Total de registros:", len(df))

    # Validações simples
    assert 'id_cliente' in df.columns, "Coluna 'id_cliente' ausente!"
    assert df['id_cliente'].is_unique, "IDs de cliente não são únicos!"

    return df

def extrair_clientes_spark(spark, path: str = "data/raw/clientes.csv"):
    """
    Lê o arquivo clientes.csv como DataFrame do Spark.
    """
    df = spark.read.option("header", True).option("inferSchema", True).csv(path)
    print("✅ Dados de clientes carregados no Spark com sucesso:")
    df.printSchema()
    return df
