#!/bin/bash

# Hive External Table Mapping Script

echo "하이브 테이블 매핑"

hdfs dfs -chmod -R 777 /user/maria_dev/bigdata_final_project/

hive -e "
DROP TABLE IF EXISTS subway_raw;
DROP TABLE IF EXISTS dust_processed;

CREATE EXTERNAL TABLE IF NOT EXISTS subway_raw (
    ride_date STRING,
    line_num STRING,
    station_name STRING,
    passenger_in INT,
    passenger_out INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/bigdata_final_project/raw_data/';

CREATE EXTERNAL TABLE IF NOT EXISTS dust_processed (
    measure_date STRING,
    station_name STRING,
    pm10 DOUBLE,
    pm25 DOUBLE,
    month STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/bigdata_final_project/dust_processed/';

SHOW TABLES;
"

echo "하이브 매핑 완료"