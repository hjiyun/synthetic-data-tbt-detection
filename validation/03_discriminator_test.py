"""
검증 3: 합성 판별기 테스트
원본과 합성을 섞어놓고, "이 샘플이 합성인지 맞히는 분류기"를 학습
판별기 성능(AUROC)이 0.5에 가까울수록 합성이 원본과 구분이 어렵다는 뜻
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def discriminator_test(original_df, synthetic_df, numeric_cols, output_dir=None):
    """합성 판별기 테스트"""
    if output_dir is None:
        output_dir = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\validation\results'
    """
    합성 판별기 테스트
    """
    print("=" * 80)
    print("검증 3: 합성 판별기 테스트")
    print("=" * 80)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 원본 데이터에 라벨 추가 (0: 원본)
    original_df_labeled = original_df.copy()
    original_df_labeled['is_synthetic'] = 0
    
    # 합성 데이터에 라벨 추가 (1: 합성)
    synthetic_df_labeled = synthetic_df.copy()
    synthetic_df_labeled['is_synthetic'] = 1
    
    # 데이터 합치기
    combined_df = pd.concat([original_df_labeled, synthetic_df_labeled], ignore_index=True)
    
    # 샘플 수 맞추기 (더 작은 쪽에 맞춤)
    min_size = min(len(original_df_labeled), len(synthetic_df_labeled))
    original_sample = original_df_labeled.sample(n=min_size, random_state=42)
    synthetic_sample = synthetic_df_labeled.sample(n=min_size, random_state=42)
    combined_df = pd.concat([original_sample, synthetic_sample], ignore_index=True)
    
    print(f"\n[3-1] 데이터 준비 완료:")
    print(f"  원본 샘플: {len(original_sample):,} 행")
    print(f"  합성 샘플: {len(synthetic_sample):,} 행")
    print(f"  전체: {len(combined_df):,} 행")
    
    # Feature 선택 (수치형 변수만)
    feature_cols = [col for col in numeric_cols if col in combined_df.columns]
    
    # 결측치 제거
    combined_df = combined_df[feature_cols + ['is_synthetic']].dropna()
    
    X = combined_df[feature_cols]
    y = combined_df['is_synthetic']
    
    # Train/Test 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"\n[3-2] 판별기 모델 학습 중...")
    print(f"  Train: {len(X_train):,} 행")
    print(f"  Test: {len(X_test):,} 행")
    
    # 여러 모델 테스트
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    results = []
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('합성 판별기 성능 비교 (ROC Curve)', fontsize=16, fontweight='bold', y=1.02)
    
    for idx, (model_name, model) in enumerate(models.items()):
        print(f"\n  {model_name} 학습 중...")
        
        # 학습
        model.fit(X_train, y_train)
        
        # 예측
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred = model.predict(X_test)
        
        # AUROC 계산
        auroc = roc_auc_score(y_test, y_pred_proba)
        
        # ROC Curve
        fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
        
        # 결과 저장
        results.append({
            'Model': model_name,
            'AUROC': auroc,
            'AUROC_Distance_from_0.5': abs(auroc - 0.5)
        })
        
        print(f"    AUROC: {auroc:.4f}")
        print(f"    0.5로부터의 거리: {abs(auroc - 0.5):.4f}")
        
        # ROC Curve 그리기
        ax = axes[idx]
        ax.plot(fpr, tpr, linewidth=2, label=f'{model_name} (AUC = {auroc:.3f})')
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random (AUC = 0.5)')
        ax.set_xlabel('False Positive Rate', fontsize=11)
        ax.set_ylabel('True Positive Rate', fontsize=11)
        ax.set_title(model_name, fontsize=12, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = f'{output_dir}/discriminator_roc_curves.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n[3-3] ROC Curve 저장: {output_path}")
    plt.close()
    
    # 결과 표 생성
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('AUROC_Distance_from_0.5')
    
    print("\n[3-4] 판별기 성능 요약:")
    print(results_df.to_string(index=False))
    
    # 결과 저장
    results_df.to_csv(f'{output_dir}/discriminator_results.csv', index=False, encoding='utf-8-sig')
    
    # 최고 성능 모델의 상세 결과
    best_model_name = results_df.iloc[0]['Model']
    best_model = models[best_model_name]
    best_model.fit(X_train, y_train)
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]
    y_pred = best_model.predict(X_test)
    
    # Classification Report
    print(f"\n[3-5] 최고 성능 모델 ({best_model_name}) 상세 결과:")
    print(classification_report(y_test, y_pred, target_names=['원본', '합성']))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['원본', '합성'], yticklabels=['원본', '합성'])
    ax.set_xlabel('예측', fontsize=12)
    ax.set_ylabel('실제', fontsize=12)
    ax.set_title(f'{best_model_name} - Confusion Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_path = f'{output_dir}/discriminator_confusion_matrix.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    # Feature Importance (Random Forest인 경우)
    if best_model_name == 'Random Forest':
        feature_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': best_model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=feature_importance, x='Importance', y='Feature', ax=ax, palette='viridis')
        ax.set_xlabel('중요도', fontsize=12)
        ax.set_ylabel('변수', fontsize=12)
        ax.set_title('판별기 Feature Importance', fontsize=14, fontweight='bold')
        plt.tight_layout()
        output_path = f'{output_dir}/discriminator_feature_importance.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  저장 완료: {output_path}")
        plt.close()
    
    # 해석
    avg_auroc = results_df['AUROC'].mean()
    avg_distance = results_df['AUROC_Distance_from_0.5'].mean()
    
    print("\n[3-6] 해석:")
    print(f"  평균 AUROC: {avg_auroc:.4f}")
    print(f"  평균 0.5로부터의 거리: {avg_distance:.4f}")
    
    if avg_auroc < 0.55:
        print("  ✓ 합성 데이터가 원본과 매우 유사합니다 (구분이 어려움)")
    elif avg_auroc < 0.65:
        print("  △ 합성 데이터가 원본과 어느 정도 유사합니다")
    else:
        print("  ✗ 합성 데이터가 원본과 구분 가능합니다 (개선 필요)")
    
    print("\n" + "=" * 80)
    print("검증 3 완료!")
    print("=" * 80)
    
    return results_df


if __name__ == "__main__":
    # 데이터 로딩 (하드코딩된 절대 경로)
    base_dir = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food'
    print("데이터 로딩 중...")
    synthetic_df = pd.read_csv(os.path.join(base_dir, 'output_images', 'synthetic_adsgan_3000.csv'))
    augmented_df = pd.read_parquet(os.path.join(base_dir, 'output_images', 'augmented_train_data.parquet'))
    
    # 원본 데이터 추출
    original_size = len(augmented_df) - len(synthetic_df)
    original_df = augmented_df.iloc[:original_size].copy()
    
    print(f"원본 데이터: {len(original_df):,} 행")
    print(f"합성 데이터: {len(synthetic_df):,} 행")
    
    # 수치형 변수
    numeric_cols = ['energy_100g', 'fat_100g', 'sugars_100g', 'proteins_100g', 'sodium_100g']
    
    # 검증 수행
    results = discriminator_test(original_df, synthetic_df, numeric_cols)

