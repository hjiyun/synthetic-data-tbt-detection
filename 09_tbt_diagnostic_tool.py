import pandas as pd
import numpy as np
import warnings
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

def run_diagnostic_tool():
    print("=" * 70)
    print("🤖 [TBT AI] 식품 무역장벽 자가 진단 솔루션 (Interactive Demo)")
    print("=" * 70)

    # 1. 데이터 로드 및 모델 재학습 (빠름)
    # 시연을 위해 가벼운 Random Forest를 즉석에서 학습시킵니다.
    base_dir = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food"
    data_path = os.path.join(base_dir, r"data\final_merged_data.parquet")
    tbt_path = os.path.join(base_dir, r"Fact\tbt_analysis_result.parquet")

    print("[System] AI 모델 초기화 중...")
    
    try:
        df = pd.read_parquet(data_path)
        if 'language_case' not in df.columns:
            df_tbt = pd.read_parquet(tbt_path)
            df['code'] = df['code'].astype(str).str.strip()
            df_tbt['code'] = df_tbt['code'].astype(str).str.strip()
            df = pd.merge(df, df_tbt[['code', 'language_case', 'category_top']], on='code', how='left')
    except Exception as e:
        print(f"[Error] 데이터 로드 실패: {e}")
        return

    # 전처리
    df['target'] = df['language_case'].apply(lambda x: 1 if 'Gap' in str(x) else 0)
    feature_cols = ['energy_100g', 'fat_100g', 'sugars_100g', 'proteins_100g', 'sodium_100g']
    
    # 학습 데이터 준비 (카테고리 제외, 영양소 위주로 간소화)
    train_df = df[feature_cols + ['target']].dropna()
    
    # 모델 학습
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(train_df[feature_cols], train_df['target'])
    
    print("[System] 학습 완료. 준비 상태입니다.\n")

    # -----------------------------------------------------------
    # 2. 사용자 입력 인터페이스 (Loop)
    # -----------------------------------------------------------
    while True:
        print("-" * 60)
        print("검사할 제품의 영양 정보를 입력하세요 (종료하려면 'q' 입력)")
        
        try:
            user_input = input(">> 입력 (순서: 칼로리 지방 당류 단백질 나트륨): ")
            if user_input.lower() == 'q':
                print("프로그램을 종료합니다.")
                break
            
            # 입력값 파싱
            vals = list(map(float, user_input.replace(',', '').split()))
            if len(vals) != 5:
                print("⚠️ 오류: 5개의 숫자를 띄어쓰기로 입력해주세요.")
                print("   예시: 450 12 30 5 0.5")
                continue
                
            # 입력 데이터 정리
            input_data = pd.DataFrame([vals], columns=feature_cols)
            
            # -------------------------------------------------------
            # 3. AI 진단 및 결과 출력
            # -------------------------------------------------------
            # 확률 예측
            prob = rf.predict_proba(input_data)[0]
            risk_score = prob[1] * 100 # Gap(내수용)일 확률
            
            print("\n🔍 [AI 진단 결과 리포트]")
            print(f"■ 입력 데이터: {vals}")
            
            if risk_score >= 70:
                print(f"■ TBT 위험도: 🔴 매우 높음 ({risk_score:.1f}%)")
                print("■ 판정: [수출 부적합 / 내수용 스펙]")
                print("■ 조언: 당류와 지방 함량이 수출 기준에 비해 높을 가능성이 큽니다.")
                print("        영문 라벨 작성 시 'High Sugar' 경고 문구가 필요할 수 있습니다.")
            elif risk_score >= 40:
                print(f"■ TBT 위험도: 🟡 주의 ({risk_score:.1f}%)")
                print("■ 판정: [수출 가능성 있음 / 라벨 보완 필요]")
            else:
                print(f"■ TBT 위험도: 🟢 안전 ({risk_score:.1f}%)")
                print("■ 판정: [수출 적합 / 글로벌 스펙]")
                print("■ 조언: 현재 영양 성분은 글로벌 표준 제품들과 유사합니다.")

        except ValueError:
            print("⚠️ 오류: 숫자만 입력해주세요.")
        except Exception as e:
            print(f"⚠️ 오류 발생: {e}")

if __name__ == "__main__":
    run_diagnostic_tool()