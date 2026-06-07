# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg as _avg, substring, dayofweek, when, corr, to_date

spark = SparkSession.builder.appName("Seoul_Total_Analysis").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 1. 지하철 데이터
subway = spark.read.option("header", "true").csv("/user/maria_dev/bigdata_final_project/raw_data/") \
    .select(col("사용일자").alias("date"), 
            (col("승차총승객수").cast("double") + col("하차총승객수").cast("double")).alias("passengers")) \
    .groupBy("date").agg(_sum("passengers").alias("total_passengers"))

# 2. 미세먼지 데이터
dust = spark.read.option("header", "true").csv("/user/maria_dev/bigdata_final_project/dust_processed/") \
    .withColumn("date", substring(col("측정일시"), 1, 8)) \
    .groupBy("date").agg(_avg(col("PM10").cast("double")).alias("avg_pm10"))

# 3. 강수량 데이터
rain = spark.read.option("header", "true").csv("/user/maria_dev/bigdata_final_project/weather/") \
    .groupBy("date").agg(_avg(col("rainfall").cast("double")).alias("avg_rain"))

# 4. 세 가지 데이터 조인
df = subway.join(dust, "date").join(rain, "date") \
    .withColumn("is_weekend", when(dayofweek(to_date(col("date"), "yyyyMMdd")).isin([1, 7]), "Weekend").otherwise("Weekday"))

# 5. 분석 결과 출력
count = df.count()

if count > 0:
    print("--- [질문 1: 강수량은 지하철 이용객 수에 영향을 미치는가?] ---")
    df.select(
        corr("total_passengers", "avg_rain").alias("Rain_Correlation")
    ).show()

    print("\n--- [질문 2: 미세먼지(PM10)는 지하철 이용객 수에 영향을 미치는가?] ---")
    df.select(
        corr("total_passengers", "avg_pm10").alias("PM10_Correlation")
    ).show()

    print("\n--- [질문 3: 평일과 주말에 따라 기상 변수의 영향력이 달라지는가?] ---")
    df.groupBy("is_weekend").agg(
        corr("total_passengers", "avg_rain").alias("Rain_Correlation"),
        corr("total_passengers", "avg_pm10").alias("PM10_Correlation")
    ).show()
else:
    print("데이터가 조인되지 않았습니다.")

spark.stop()