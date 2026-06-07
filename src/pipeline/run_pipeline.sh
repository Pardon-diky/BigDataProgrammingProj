#!/bin/bash

LOCAL_DIR="/home/maria_dev/bigdata_final_project"
HDFS_DIR="/user/maria_dev/bigdata_final_project"

echo "파이프라인 가동"


hdfs dfs -mkdir -p ${HDFS_DIR}/raw_data
hdfs dfs -mkdir -p ${HDFS_DIR}/dust_processed
hdfs dfs -mkdir -p ${HDFS_DIR}/dust_raw
hdfs dfs -mkdir -p ${HDFS_DIR}/weather

echo "데이터 적재 중"


hdfs dfs -put -n ${LOCAL_DIR}/data/dust_raw/*.csv ${HDFS_DIR}/dust_raw/ 2>/dev/null
hdfs dfs -put -n ${LOCAL_DIR}/data/dust_processed/*.csv ${HDFS_DIR}/dust_processed/ 2>/dev/null
hdfs dfs -put -n ${LOCAL_DIR}/data/month_subway_*.csv ${HDFS_DIR}/raw_data/ 2>/dev/null
hdfs dfs -put -n ${LOCAL_DIR}/data/month_seoul_raining.csv ${HDFS_DIR}/weather/ 2>/dev/null

echo "데이터 적재 완료"

# 3. 분석 실행
spark-submit --master local[*] ${LOCAL_DIR}/src/analyze/spark_analyze_seoul.py