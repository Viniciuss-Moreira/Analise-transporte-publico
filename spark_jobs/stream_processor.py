from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType, LongType, TimestampType

# --- CONFIGURAÇÕES DE SAÍDA ---
OUTPUT_PATH = "data/posicoes_onibus_parquet"
CHECKPOINT_PATH = "data/_checkpoints/posicoes_onibus_parquet"
# -----------------------------

# 1. Spark Session simples, sem configurações extras
spark = SparkSession.builder \
    .appName("SPTransToParquet") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print("Spark Session criada.")

# 2. Schema (o mesmo de antes)
schema = StructType([
    StructField("timestamp_captura", StringType(), True),
    StructField("id_linha", LongType(), True),
    StructField("letreiro_ida", StringType(), True),
    StructField("letreiro_volta", StringType(), True),
    StructField("destino_principal", StringType(), True),
    StructField("prefixo_veiculo", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("timestamp_veiculo", StringType(), True),
    StructField("acessivel", BooleanType(), True)
])

# 3. Leitura do Stream do Kafka
kafka_stream_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "posicoes_onibus") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Processamento e Transformação
processed_df = kafka_stream_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp_veiculo", to_timestamp(col("timestamp_veiculo"))) \
    .withColumn("timestamp_captura", col("timestamp_veiculo"))

print("Estrutura do stream processada. Enviando para arquivos Parquet...")

# 5. MUDANÇA FINAL: Saída dos Dados (Sink) para Parquet
query = processed_df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", OUTPUT_PATH) \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .start()

query.awaitTermination()