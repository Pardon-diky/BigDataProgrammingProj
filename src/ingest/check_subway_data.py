import os
import time
import requests
import pandas as pd
from tqdm import tqdm

API_KEY = "75696c72496a6a75343366556c4168"
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. 수집 기간 설정 (2021년 1월 ~ 2026년 5월)
date_list = pd.date_range(start="2021-01-01", end="2026-05-31", freq="MS").strftime("%Y%m").tolist()

all_data = []

print("서울시 지하철 시간대별 승하차 인원 대용량 수집을 시작")

for target_month in tqdm(date_list, desc="월별 데이터 수집 중"):
    url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/CardSubwayTime/1/1000/{target_month}"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            json_data = response.json()
            
            if "CardSubwayTime" in json_data:
                rows = json_data["CardSubwayTime"]["row"]
                all_data.extend(rows)
            else:
                pass 
        else:
            print(f"\n❌ 서버 응답 실패 ({target_month}) - Status: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 스크립트 에러 발생 ({target_month}): {e}")
        pass
    
    time.sleep(0.1) 

# 3. 데이터 병합 및 CSV 저장
if all_data:
    final_df = pd.DataFrame(all_data)
    
    output_path = os.path.join(OUTPUT_DIR, "raw_subway_time_5years.csv")
    final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print("\n" + "="*50)
    print("시간대별 대용량 지하철 데이터 수집 완료")
    print(f"저장 경로: {output_path}")
    print(f"총 수집된 행(Row) 수: {len(final_df):,} 건")
    print(f"생성된 파일 용량: {file_size_mb:.2f} MB")
    print("="*50)
else:
    print("수집된 데이터가 없습니다.")