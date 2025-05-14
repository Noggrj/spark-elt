import pandas as pd
import os

def validar_transacoes_csv(path="data/raw/transacoes.csv"):
    """
    Valida a existência, colunas obrigatórias e integridade básica do arquivo transacoes.csv
    usando pandas antes de carregar no Spark.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {path}")

    df = pd.read_csv(path)

    print("✅ CSV de transações lido com sucesso!")
    print(df.head())
    print("🔎 Colunas:", list(df.columns))
    print("📏 Total de registros:", len(df))

    # Validações básicas
    assert 'id_transacao' in df.columns, "❌ Coluna 'id_transacao' ausente!"
    assert 'id_cliente' in df.columns, "❌ Coluna 'id_cliente' ausente!"
    assert 'valor' in df.columns, "❌ Coluna 'valor' ausente!"
    assert 'data' in df.columns, "❌ Coluna 'data' ausente!"
    assert pd.to_datetime(df['data'], errors='coerce').notna().all(), "❌ Existem datas inválidas no CSV!"

    return True

def extrair_transacoes_spark(spark, path="data/raw/transacoes.csv"):
    """
    Carrega o arquivo transacoes.csv como DataFrame do Spark.
    """
    df = spark.read.option("header", True).option("inferSchema", True).csv(path)
    print("✅ Transações carregadas no Spark com sucesso:")
    df.printSchema()
    return df
