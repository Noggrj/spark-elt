from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg, sum, count, desc, year, month, from_json, broadcast
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from extract.clientes import extrair_e_validar_clientes, extrair_clientes_spark
from extract.transacoes import validar_transacoes_csv, extrair_transacoes_spark


def criar_schema_clientes():
    """
    Define o schema para os dados de clientes vindos do Kafka.
    """
    return StructType([
        StructField("id_cliente", StringType(), True),
        StructField("nome", StringType(), True),
        StructField("idade", IntegerType(), True),
        StructField("email", StringType(), True),
        StructField("estado", StringType(), True)
    ])

def criar_schema_transacoes():
    """
    Define o schema para os dados de transações vindos do Kafka.
    """
    return StructType([
        StructField("id_transacao", StringType(), True),
        StructField("id_cliente", StringType(), True),
        StructField("valor", DoubleType(), True),
        StructField("data", StringType(), True),
        StructField("categoria", StringType(), True),
        StructField("cidade", StringType(), True)
    ])

def processar_dados_batch(spark):
    """
    Processa os dados em modo batch (lendo dos arquivos CSV).
    """
    # Validação com pandas
    extrair_e_validar_clientes()        # valida estrutura e unicidade
    validar_transacoes_csv()            # valida estrutura e datas

    # Leitura dos dados com Spark
    df_clientes = extrair_clientes_spark(spark)
    df_transacoes = extrair_transacoes_spark(spark)

    # Processamento dos dados
    return processar_dataframes(spark, df_clientes, df_transacoes)

def processar_dados_kafka(spark, bootstrap_servers='localhost:9092'):
    """
    Processa os dados em modo streaming (lendo do Kafka).
    """
    # Leitura dos dados do Kafka (apenas transações em streaming)
    df_transacoes_kafka = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", "transacoes")
        .option("startingOffsets", "earliest")
        .load()
    )

    # Parsing dos dados JSON do Kafka para transações
    schema_transacoes = criar_schema_transacoes()
    df_transacoes = (
        df_transacoes_kafka
        .selectExpr("CAST(value AS STRING)")
        .select(from_json("value", schema_transacoes).alias("data"))
        .select("data.*")
    )

    # Leitura dos dados de clientes diretamente do CSV (modo estático)
    df_clientes = extrair_clientes_spark(spark)
    
    # Processamento dos dados
    return processar_dataframes_streaming(spark, df_clientes, df_transacoes)

def processar_dataframes(spark, df_clientes, df_transacoes):
    """
    Processa os DataFrames de clientes e transações (modo batch).
    """
    # Enriquecimento do DataFrame de transações
    df_transacoes = (df_transacoes
        .withColumnRenamed("valor", "valor_reais")
        .withColumn("ano", year(col("data")))
        .withColumn("mes", month(col("data"))))

    # Categorização por faixa etária
    df_clientes = df_clientes.withColumn(
        "faixa_etaria",
        when(col("idade") < 30, "jovem")
        .when(col("idade") < 60, "adulto")
        .otherwise("idoso")
    )

    # JOIN entre clientes e transações
    df_join = df_transacoes.join(df_clientes, on="id_cliente", how="inner")

    # Filtragem de alto valor
    df_alto_valor = df_join.filter(col("valor_reais") > 500)

    # Métricas por categoria
    df_agg_categoria = (df_join.groupBy("categoria")
        .agg(
            avg("valor_reais").alias("media_valor"),
            sum("valor_reais").alias("soma_valor"),
            count("*").alias("qtd_transacoes")
        ).orderBy(desc("soma_valor")))

    # Total gasto por cidade
    df_top_cidades = (df_join.groupBy("cidade")
        .agg(sum("valor_reais").alias("total_gasto"))
        .orderBy(desc("total_gasto")))

    # Top 10 clientes
    df_top_clientes = (df_join.groupBy("id_cliente", "nome", "estado")
        .agg(sum("valor_reais").alias("total_cliente"))
        .orderBy(desc("total_cliente"))
        .limit(10))

    # Consulta SQL
    df_join.createOrReplaceTempView("vw_transacoes")
    df_sql = spark.sql("""
        SELECT ano, mes, estado, faixa_etaria,
               COUNT(*) AS total_transacoes,
               ROUND(SUM(valor_reais), 2) AS total_gasto
        FROM vw_transacoes
        GROUP BY ano, mes, estado, faixa_etaria
        ORDER BY ano DESC, mes DESC, total_gasto DESC
    """)

    # Resultados
    print("🔹 Visão por categoria:")
    df_agg_categoria.show()

    print("🔹 Cidades com maior volume financeiro:")
    df_top_cidades.show(5)

    print("🔹 Top 10 clientes:")
    df_top_clientes.show()

    print("🔹 Visão por mês, estado e faixa etária (SQL):")
    df_sql.show(10)

    return {
        "categoria": df_agg_categoria,
        "cidades": df_top_cidades,
        "clientes": df_top_clientes,
        "sql": df_sql
    }

def processar_dataframes_streaming(spark, df_clientes, df_transacoes):
    """
    Processa os DataFrames em modo streaming.
    """
    # Categorização por faixa etária
    df_clientes = df_clientes.withColumn(
        "faixa_etaria",
        when(col("idade") < 30, "jovem")
        .when(col("idade") < 60, "adulto")
        .otherwise("idoso")
    )

    # Enriquecimento do DataFrame de transações
    df_transacoes = df_transacoes.withColumnRenamed("valor", "valor_reais")
    
    print("🔹 Iniciando queries de streaming...")

    # Métricas por categoria (streaming)
    query_categoria = (df_transacoes.groupBy("categoria")
        .agg(
            avg("valor_reais").alias("media_valor"),
            sum("valor_reais").alias("soma_valor"),
            count("*").alias("qtd_transacoes")
        )
        .writeStream
        .outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 10)
        .trigger(processingTime="5 seconds")
        .start())
    
    print("✅ Query de categorias iniciada")
    
    # Total gasto por cidade (streaming)
    query_cidades = (df_transacoes.groupBy("cidade")
        .agg(sum("valor_reais").alias("total_gasto"))
        .orderBy(desc("total_gasto"))
        .writeStream
        .outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 10)
        .trigger(processingTime="5 seconds")
        .start())
    
    print("✅ Query de cidades iniciada")
    
    # JOIN entre streaming e estático (sem precisar converter)
    df_join_static = (df_transacoes.join(
        broadcast(df_clientes), 
        on="id_cliente"
    ))
    
    # Top 10 clientes (streaming com join estático)
    query_top_clientes = (df_join_static.groupBy("id_cliente", "nome", "estado")
        .agg(sum("valor_reais").alias("total_cliente"))
        .orderBy(desc("total_cliente"))
        .limit(10)
        .writeStream
        .outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 10)
        .trigger(processingTime="5 seconds")
        .start())
    
    print("✅ Query de top clientes iniciada")
    
    # Retornar as queries para que possam ser gerenciadas pelo chamador
    return {
        "queries": [query_categoria, query_cidades, query_top_clientes]
    }

def main(modo="batch", bootstrap_servers='localhost:9092'):
    """
    Função principal que inicia o processamento.
    
    Parâmetros:
    - modo: "batch" para processar arquivos CSV, "kafka" para processar dados do Kafka
    - bootstrap_servers: endereço dos servidores Kafka (padrão: localhost:9092)
    """
    # Iniciar sessão Spark
    spark = SparkSession.builder \
        .appName("AnaliseTransacoesLiveCoding") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
        .getOrCreate()
    
    # Configurar nível de log
    spark.sparkContext.setLogLevel("WARN")

    # Processar dados de acordo com o modo
    if modo == "batch":
        print("🔹 Iniciando processamento em modo BATCH (arquivos CSV)")
        resultado = processar_dados_batch(spark)
    elif modo == "kafka":
        print(f"🔹 Iniciando processamento em modo STREAMING (Kafka: {bootstrap_servers})")
        resultado = processar_dados_kafka(spark, bootstrap_servers)
        
        # No modo Kafka, aguardar as queries terminarem
        if "queries" in resultado:
            try:
                for query in resultado["queries"]:
                    query.awaitTermination()
            except KeyboardInterrupt:
                print("⚠️ Processamento interrompido pelo usuário")
                for query in resultado["queries"]:
                    query.stop()
    else:
        raise ValueError(f"Modo inválido: {modo}. Use 'batch' ou 'kafka'.")

    print("✅ Processamento concluído!")

if __name__ == "__main__":
    main()
