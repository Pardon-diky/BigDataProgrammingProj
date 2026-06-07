import os
import glob
import pandas as pd
from tqdm import tqdm

# 60222396 이준혁 빅데이터 기말프로젝트 - 대용량 미세먼지 데이터 전처리
# 1. 전국 데이터에서 '서울'만 추출
# 2. HDFS 적재랑 Spark 처리 쉽도록 월별로 파일 쪼개기 (YYYYMM 기준)

RAW_DIR = "data/dust_raw"
PROCESSED_DIR = "data/dust_processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

raw_files = glob.glob(os.path.join(RAW_DIR, "*.*"))
valid_files = [f for f in raw_files if f.endswith(('.csv', '.xls', '.xlsx'))]

if not valid_files:
    print("에러: 처리할 데이터 파일이 없습니다. 경로를 확인하세요.")
    exit()

print(f"총 {len(valid_files)}개 파일 전처리 시작.")

total_rows = 0
seoul_rows = 0

for file in tqdm(valid_files, desc="데이터 처리중"):
    try:
        # 공공데이터 csv는 인코딩이 제각각이라 예외처리 필요
        if file.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='cp949')
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding='utf-8')
        else:
            df = pd.read_excel(file)
            
        total_rows += len(df)
        
        region_col = next((col for col in df.columns if '지역' in col or '구분' in col), None)
                
        if region_col:
            # 서울 데이터만 뽑기
            df_seoul = df[df[region_col].astype(str).str.contains('서울', na=False)]
        else:
            df_seoul = df
            
        # 측정일시(예: 2025010101) 기준으로 앞 6자리(YYYYMM) 잘라서 월별로 묶기
        date_col = '측정일시' if '측정일시' in df.columns else None
        
        if date_col and len(df_seoul) > 0:
            df_seoul[date_col] = df_seoul[date_col].astype(str)
            df_seoul['Month_Partition'] = df_seoul[date_col].str.slice(0, 6)
            
            # 월별로 파일 분할 저장
            for month, group in df_seoul.groupby('Month_Partition'):
                output_filename = f"seoul_dust_{month}.csv"
                output_path = os.path.join(PROCESSED_DIR, output_filename)
                
                # 파일 있으면 이어붙이고, 없으면 새로 쓰기
                if os.path.exists(output_path):
                    group.drop(columns=['Month_Partition']).to_csv(output_path, mode='a', index=False, header=False, encoding='utf-8-sig')
                else:
                    group.drop(columns=['Month_Partition']).to_csv(output_path, mode='w', index=False, encoding='utf-8-sig')
                
                seoul_rows += len(group)

    except Exception as e:
        print(f"[{file}] 처리 중 에러: {e}")

# 결과 출력
print("\n--- 전처리 완료 ---")
print(f"스캔한 전체 데이터: {total_rows}건")
print(f"추출된 서울 데이터: {seoul_rows}건")
print(f"저장 폴더: {PROCESSED_DIR}/")