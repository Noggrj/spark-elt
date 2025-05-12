from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg, sum, count, desc, year, month

# Imports da camada de extração
from src.extract.extract_clients import extrair_e_validar_clientes, extrair_clientes_spark
from src.extract.extract_transacoes import validar_transacoes_csv, extrair_transacoes_spark

def main():
    # 1. Iniciar sessão Spark
    spark = SparkSession.builder \
        .appName("AnaliseTransacoesLiveCoding") \
        .getOrCreate()

    # 2. Validação com pandas
    extrair_e_validar_clientes()        # valida estrutura e unicidade
    validar_transacoes_csv()            # valida estrutura e datas

    # 3. Leitura dos dados com Spark
    df_clientes = extrair_clientes_spark(spark)
    df_transacoes = extrair_transacoes_spark(spark)

    # 4. Enriquecimento do DataFrame de transações
    df_transacoes = df_transacoes \
        .withColumnRenamed("valor", "valor_reais") \
        .withColumn("ano", year(col("data"))) \
        .withColumn("mes", month(col("data")))

    # 5. Categorização por faixa etária
    df_clientes = df_clientes.withColumn(
        "faixa_etaria",
        when(col("idade") < 30, "jovem")
        .when(col("idade") < 60, "adulto")
        .otherwise("idoso")
    )

    # 6. JOIN entre clientes e transações
    df_join = df_transacoes.join(df_clientes, on="id_cliente", how="inner")

    # 7. Filtragem de alto valor
    df_alto_valor = df_join.filter(col("valor_reais") > 500)

    # 8. Métricas por categoria
    df_agg_categoria = df_join.groupBy("categoria") \
        .agg(
            avg("valor_reais").alias("media_valor"),
            sum("valor_reais").alias("soma_valor"),
            count("*").alias("qtd_transacoes")
        ).orderBy(desc("soma_valor"))

    # 9. Total gasto por cidade
    df_top_cidades = df_join.groupBy("cidade") \
        .agg(sum("valor_reais").alias("total_gasto")) \
        .orderBy(desc("total_gasto"))

    # 10. Top 10 clientes
    df_top_clientes = df_join.groupBy("id_cliente", "nome", "estado") \
        .agg(sum("valor_reais").alias("total_cliente")) \
        .orderBy(desc("total_cliente")) \
        .limit(10)

    # 11. Consulta SQL
    df_join.createOrReplaceTempView("vw_transacoes")
    df_sql = spark.sql("""
        SELECT ano, mes, estado, faixa_etaria,
               COUNT(*) AS total_transacoes,
               ROUND(SUM(valor_reais), 2) AS total_gasto
        FROM vw_transacoes
        GROUP BY ano, mes, estado, faixa_etaria
        ORDER BY ano DESC, mes DESC, total_gasto DESC
    """)

    # 12. Resultados
    print("🔹 Visão por categoria:")
    df_agg_categoria.show()

    print("🔹 Cidades com maior volume financeiro:")
    df_top_cidades.show(5)

    print("🔹 Top 10 clientes:")
    df_top_clientes.show()

    print("🔹 Visão por mês, estado e faixa etária (SQL):")
    df_sql.show(10)

if __name__ == "__main__":
    main()
