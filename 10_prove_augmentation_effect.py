import pandas as pd
import numpy as np
import warnings
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder

# SynthCity
try:
    from synthcity.plugins import Plugins
    from synthcity.plugins.core.dataloader import GenericDataLoader
except ImportError:
    print("[ERROR] synthcity가 필요합니다.")
    exit()

warnings.filterwarnings('ignore')

def compare_performance_balanced():
    print("=" * 70)
    print("🧪 [실험] 합성 데이터를 활용한 '희귀 케이스(TBT 위험)' 증강 효과 검증")
    print("=" * 70)

    # 1. 데이터 준비
    base_dir = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food"
    data_path = os.path.join(base_dir, r"data\final_merged_data.parquet")
    tbt_path = os.path.join(base_dir, r"Fact\tbt_analysis_result.parquet")

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

    # 전처리 & 타겟 정의
    df['target'] = df['language_case'].apply(lambda x: 1 if 'Gap' in str(x) else 0)
    feature_cols = ['energy_100g', 'fat_100g', 'sugars_100g', 'proteins_100g', 'sodium_100g', 'category_top']
    
    # 데이터 정제
    data = df[feature_cols + ['target']].dropna()
    le = LabelEncoder()
    data['category_top'] = le.fit_transform(data['category_top'].astype(str))

    # 데이터 분포 확인
    n_safe = (data['target'] == 0).sum()
    n_risk = (data['target'] == 1).sum()
    print(f"[데이터 분포] 안전(0): {n_safe}개 vs 위험(1): {n_risk}개")
    print(f" -> 위험 비율이 {n_risk / len(data) * 100:.2f}%로 매우 희박합니다.")

    if n_risk < 10:
        print("⚠️ 위험 데이터가 너무 적어 증강이 어려울 수 있습니다.")

    # 2. 데이터 분할
    X = data[feature_cols]
    y = data['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # ---------------------------------------------------------
    # [실험 A] Baseline: 불균형 상태 그대로 학습
    # ---------------------------------------------------------
    print("\n🔵 [실험 A] 원본 데이터만 사용하여 학습...")
    rf_base = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf_base.fit(X_train, y_train)
    
    pred_base = rf_base.predict(X_test)
    acc_base = accuracy_score(y_test, pred_base)
    f1_base = f1_score(y_test, pred_base, zero_division=0)
    
    print(f"   -> 정확도: {acc_base*100:.2f}%")
    print(f"   -> F1 점수: {f1_base:.4f} (위험 제품 탐지 능력)")
    
    # ---------------------------------------------------------
    # [실험 B] Targeted Augmentation: 위험 데이터만 골라서 증강
    # ---------------------------------------------------------
    print("\n🔴 [실험 B] '위험(Class 1)' 데이터만 선택적 증강 시작 (AdsGAN)...")
    
    # 학습 데이터 중에서 '위험(1)'인 것만 추출
    train_df = X_train.copy()
    train_df['target'] = y_train
    
    minority_data = train_df[train_df['target'] == 1]
    majority_count = len(train_df[train_df['target'] == 0])
    minority_count = len(minority_data)
    
    # 목표: 위험 데이터를 안전 데이터 개수만큼 늘리기 (50:50 밸런싱)
    n_to_generate = majority_count - minority_count
    
    print(f"   -> 학습용 위험 데이터: {minority_count}개")
    print(f"   -> 목표 생성 개수: {n_to_generate}개 (밸런싱)")
    
    if n_to_generate > 0:
        # 소수 클래스만 학습
        loader = GenericDataLoader(minority_data, target_column='target')
        
        try:
            # GPU 사용
            syn_model = Plugins().get("adsgan", n_iter=500) # 반복 횟수 늘림
            syn_model.fit(loader)
            
            print("   -> 합성 데이터 생성 중...")
            synthetic_data = syn_model.generate(count=n_to_generate).dataframe()
            
            # 원본(전체) + 합성(위험군) 합치기
            augmented_df = pd.concat([train_df, synthetic_data])
            
            # 셔플
            augmented_df = augmented_df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            print(f"   -> 증강 완료! 데이터 비율이 50:50으로 조정되었습니다.")
            print(f"      (총 {len(augmented_df)}개: 0={majority_count}, 1={len(augmented_df[augmented_df['target']==1])})")

            # 모델 학습
            X_aug = augmented_df[feature_cols]
            y_aug = augmented_df['target']
            
            rf_aug = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_aug.fit(X_aug, y_aug)
            
            pred_aug = rf_aug.predict(X_test)
            acc_aug = accuracy_score(y_test, pred_aug)
            f1_aug = f1_score(y_test, pred_aug, zero_division=0)
            
            print(f"   -> 정확도: {acc_aug*100:.2f}%")
            print(f"   -> F1 점수: {f1_aug:.4f}")
            
        except Exception as e:
            print(f"   -> [Error] 생성 실패: {e}")
            acc_aug, f1_aug = acc_base, f1_base
    else:
        print("   -> 이미 데이터가 충분하거나 불균형하지 않습니다.")
        acc_aug, f1_aug = acc_base, f1_base

    # ---------------------------------------------------------
    # 3. 최종 결과 비교
    # ---------------------------------------------------------
    print("=" * 70)
    print("📊 [최종 성과 분석]")
    print(f"1. 원본 데이터 F1 점수 : {f1_base:.4f}")
    print(f"2. 합성 데이터 F1 점수 : {f1_aug:.4f}")
    
    if f1_aug > f1_base:
        print(f"\n🚀 결론: 합성 데이터를 통해 TBT 탐지 능력(F1)이 획기적으로 향상되었습니다!")
        print("   (희귀했던 '위험' 케이스를 AI가 학습할 수 있게 되었습니다.)")
    else:
        print("\n🤔 변화가 없거나 미미합니다. 위험 데이터 샘플이 너무 적어 패턴 학습이 어려울 수 있습니다.")

    # 그래프 저장
    plt.figure(figsize=(10, 5))
    metrics = ['Accuracy', 'F1-Score']
    x = np.arange(len(metrics))
    width = 0.35
    
    plt.bar(x - width/2, [acc_base, f1_base], width, label='Original', color='gray', alpha=0.7)
    plt.bar(x + width/2, [acc_aug, f1_aug], width, label='Augmented (Balanced)', color='red', alpha=0.8)
    
    plt.xticks(x, metrics)
    plt.ylabel('Score')
    plt.title('Impact of Synthetic Data Balancing on TBT Detection')
    plt.legend()
    plt.ylim(0, 1.1)
    
    for i, v in enumerate([acc_base, f1_base]):
        plt.text(i - width/2, v + 0.01, f"{v:.2f}", ha='center')
    for i, v in enumerate([acc_aug, f1_aug]):
        plt.text(i + width/2, v + 0.01, f"{v:.2f}", ha='center', fontweight='bold')

    plt.savefig('balancing_effect.png')
    print("   -> 결과 그래프 저장됨: balancing_effect.png")

if __name__ == "__main__":
    compare_performance_balanced()