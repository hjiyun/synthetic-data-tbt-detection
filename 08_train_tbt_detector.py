import pandas as pd
import numpy as np
import torch
import warnings
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# SynthCity 라이브러리 (설치 필요)
try:
    from synthcity.plugins import Plugins
    from synthcity.plugins.core.dataloader import GenericDataLoader
except ImportError:
    print("[ERROR] 'synthcity'가 설치되지 않았습니다. 'pip install synthcity'를 실행하세요.")
    exit()

warnings.filterwarnings('ignore')

def train_tbt_detector():
    print("=" * 60)
    print("[Step 8] TBT 위반 탐지 AI 개발 (GPU 가속 활성화)")
    print("=" * 60)

    # GPU 사용 가능 여부 확인
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] 학습 디바이스: {device.upper()}")
    if device == "cuda":
        print(f"       GPU 모델명: {torch.cuda.get_device_name(0)}")

    # 1. 데이터 로드
    # 경로 설정 (사용자 환경)
    base_dir = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food"
    merged_path = os.path.join(base_dir, "final_merged_data.parquet") # 또는 현재 폴더
    tbt_path = os.path.join(base_dir, r"Fact\tbt_analysis_result.parquet")

    # 파일이 없으면 현재 폴더에서 찾기
    if not os.path.exists(merged_path):
        merged_path = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\data\final_merged_data.parquet"

    try:
        df = pd.read_parquet(merged_path)
        
        # language_case(내수용/수출용 라벨) 정보가 없으면 TBT 파일에서 가져와서 병합
        if 'language_case' not in df.columns:
            print("[INFO] 'language_case' 라벨 정보를 병합합니다...")
            df_tbt = pd.read_parquet(tbt_path)
            
            # 키 컬럼 타입 통일
            df['code'] = df['code'].astype(str).str.strip()
            df_tbt['code'] = df_tbt['code'].astype(str).str.strip()
            
            # 병합
            df = pd.merge(df, df_tbt[['code', 'language_case', 'category_top']], on='code', how='left')
            
    except Exception as e:
        print(f"[ERROR] 데이터 로드 실패: {e}")
        print("이전 단계(병합)가 정상적으로 완료되었는지 확인해주세요.")
        return

    print(f"[INFO] 원본 데이터 크기: {len(df):,}행")

    # 2. 데이터 전처리
    # TBT 위험(Risk) 정의: 'Gap (내수용)' 이면 1 (위험), 아니면 0 (안전)
    # 데이터를 숫자로 변환해야 생성 모델이 학습할 수 있음
    
    # 타겟 생성
    df['target'] = df['language_case'].apply(lambda x: 1 if 'Gap' in str(x) else 0)
    
    print(f" - TBT 위험 제품(내수용): {df['target'].sum()}개")
    print(f" - TBT 안전 제품(수출용): {len(df) - df['target'].sum()}개")

    # 학습에 사용할 컬럼 (영양소 5종 + 카테고리)
    feature_cols = [
        'energy_100g', 'fat_100g', 'sugars_100g', 'proteins_100g', 'sodium_100g', 
        'category_top'
    ]
    
    # 결측치 제거
    train_df = df[feature_cols + ['target']].dropna()

    # 카테고리(문자열) -> 숫자 변환
    le = LabelEncoder()
    train_df['category_top'] = le.fit_transform(train_df['category_top'].astype(str))
    
    print("\n[1] 데이터 증강 (Synthetic Data Generation) 시작...")
    print("    사용 모델: AdsGAN (AdsGAN is a SOTA GAN model suitable for tabular data)")
    
    # ---------------------------------------------------------
    # (A) SynthCity로 가짜 데이터 생성
    # ---------------------------------------------------------
    # 데이터 로더 준비
    loader = GenericDataLoader(train_df, target_column='target')
    
    # 모델 선택: AdsGAN (속도와 성능 균형이 좋음)
    # GPU가 있으면 자동으로 활용합니다.
    try:
        syn_model = Plugins().get("adsgan", n_iter=300) # 반복 횟수(Epoch) 설정
        
        print(" -> 모델 학습 중... (잠시만 기다려주세요)")
        syn_model.fit(loader)
        print(" -> 학습 완료!")
        
        # 가짜 데이터 3,000개 생성
        print(" -> 가짜 데이터 3,000개 생성 중...")
        synthetic_data = syn_model.generate(count=3000).dataframe()
        
        # 원본 + 가짜 데이터 합치기
        augmented_df = pd.concat([train_df, synthetic_data])
        print(f"[INFO] 증강 완료! 총 데이터 크기: {len(train_df):,} -> {len(augmented_df):,}행")
        
    except Exception as e:
        print(f"[WARNING] 생성 모델 학습 실패 ({e}).")
        print(" -> 원본 데이터로만 탐지 모델을 학습합니다.")
        augmented_df = train_df

    # ---------------------------------------------------------
    # (B) TBT 위반 탐지 AI 학습
    # ---------------------------------------------------------
    print("\n[2] TBT 위반 탐지기(Classifier) 학습 시작...")
    
    X = augmented_df[feature_cols]
    y = augmented_df['target']
    
    # 학습용/테스트용 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 모델 학습 (Random Forest)
    detector = RandomForestClassifier(n_estimators=100, random_state=42)
    detector.fit(X_train, y_train)
    
    # ---------------------------------------------------------
    # (C) 성능 평가 및 중요도 분석
    # ---------------------------------------------------------
    y_pred = detector.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*60)
    print(f"🎯 [최종 결과] TBT 위반 탐지 AI 성능")
    print(f"   정확도(Accuracy): {acc*100:.2f}%")
    print("="*60)
    
    # 중요도 분석
    print("\n[분석] TBT 위험 판별 핵심 요인 (Top 3):")
    importances = detector.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    for i in range(3):
        col_name = feature_cols[indices[i]]
        print(f" {i+1}. {col_name}: {importances[indices[i]]:.4f}")
        
    print("\n[결론] 위 영양소들이 내수용/수출용을 가르는 가장 중요한 기준입니다.")
    if acc > 0.8:
        print(" -> 모델 성능이 우수합니다. 실제 TBT 사전 진단 도구로 활용 가능합니다.")

if __name__ == "__main__":
    train_tbt_detector()