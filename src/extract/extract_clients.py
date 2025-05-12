# src/extract/extract_clientes.py

import pandas as pd
import os

def extrair_e_validar_clientes(path="data/raw/clientes.csv"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {path}")

    df = pd.read_csv(path)

    print("✅ CSV de clientes lido com sucesso!")
    print(df.head())
    print("🔎 Colunas:", list(df.columns))
    print("📏 Total de registros:", len(df))

    # Validação simples
    assert 'id_cliente' in df.columns, "Coluna 'id_cliente' ausente!"
    assert df['id_cliente'].is_unique, "IDs de cliente não são únicos!"

    return df
