"""
검증 1: 수치형 변수에 대한 통계적 검증
- KS test (Kolmogorov-Smirnov test)
- Wasserstein distance
- PSI (Population Stability Index)
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ks_2samp
from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def calculate_psi(original, synthetic, bins=10):
    """
    Population Stability Index (PSI) 계산
    PSI < 0.1: 매우 안정적
    PSI 0.1-0.25: 약간의 드리프트
    PSI > 0.25: 큰 드리프트
    """
    # 결측치 제거
    original = original.dropna()
    synthetic = synthetic.dropna()
    
    if len(original) == 0 or len(synthetic) == 0:
        return np.nan
    
    # 범위 계산
    min_val = min(original.min(), synthetic.min())
    max_val = max(original.max(), synthetic.max())
    
    if min_val == max_val:
        return 0.0
    
    # 빈(bin) 경계 설정
    bin_edges = np.linspace(min_val, max_val, bins + 1)
    
    # 히스토그램 계산
    orig_hist, _ = np.histogram(original, bins=bin_edges)
    synth_hist, _ = np.histogram(synthetic, bins=bin_edges)
    
    # 비율로 변환 (0으로 나누기 방지)
    orig_pct = orig_hist / len(original)
    synth_pct = synth_hist / len(synthetic)
    
    # 0인 경우 작은 값 추가 (로그 계산 방지)
    orig_pct = np.where(orig_pct == 0, 0.0001, orig_pct)
    synth_pct = np.where(synth_pct == 0, 0.0001, synth_pct)
    
    # PSI 계산
    psi = np.sum((orig_pct - synth_pct) * np.log(orig_pct / synth_pct))
    
    return psi


def statistical_validation(original_df, synthetic_df, numeric_cols, output_dir=None):
    """수치형 변수에 대한 통계적 검증 수행"""
    if output_dir is None:
        output_dir = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\validation\results'
    """
    수치형 변수에 대한 통계적 검증 수행
    """
    print("=" * 80)
    print("검증 1: 수치형 변수 통계적 검증")
    print("=" * 80)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = []
    
    print("\n[1-1] 통계적 검증 지표 계산 중...")
    
    for col in numeric_cols:
        if col not in original_df.columns or col not in synthetic_df.columns:
            print(f"  경고: {col} 컬럼이 없습니다.")
            continue
        
        orig_data = original_df[col].dropna()
        synth_data = synthetic_df[col].dropna()
        
        if len(orig_data) == 0 or len(synth_data) == 0:
            print(f"  경고: {col} 데이터가 없습니다.")
            continue
        
        # KS test
        ks_stat, ks_pvalue = ks_2samp(orig_data, synth_data)
        
        # Wasserstein distance
        wass_dist = wasserstein_distance(orig_data, synth_data)
        
        # PSI
        psi = calculate_psi(orig_data, synth_data)
        
        # 기본 통계
        orig_mean = orig_data.mean()
        synth_mean = synth_data.mean()
        orig_std = orig_data.std()
        synth_std = synth_data.std()
        
        results.append({
            'Variable': col,
            'KS_Statistic': ks_stat,
            'KS_pvalue': ks_pvalue,
            'Wasserstein_Distance': wass_dist,
            'PSI': psi,
            'Original_Mean': orig_mean,
            'Synthetic_Mean': synth_mean,
            'Original_Std': orig_std,
            'Synthetic_Std': synth_std,
            'Mean_Diff': abs(orig_mean - synth_mean),
            'Std_Diff': abs(orig_std - synth_std)
        })
        
        print(f"  {col}:")
        print(f"    KS statistic: {ks_stat:.4f} (p-value: {ks_pvalue:.4f})")
        print(f"    Wasserstein distance: {wass_dist:.4f}")
        print(f"    PSI: {psi:.4f}")
    
    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(results)
    
    # 결과 저장
    output_path = f'{output_dir}/statistical_validation_results.csv'
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n[1-2] 결과 저장: {output_path}")
    
    # 표 생성 (시각화)
    print("\n[1-3] 결과 표 생성 중...")
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # 표 데이터 준비 (주요 지표만)
    table_data = results_df[['Variable', 'KS_Statistic', 'KS_pvalue', 'Wasserstein_Distance', 'PSI']].copy()
    table_data.columns = ['변수', 'KS 통계량', 'KS p-value', 'Wasserstein 거리', 'PSI']
    
    # 소수점 자리수 조정
    table_data['KS 통계량'] = table_data['KS 통계량'].round(4)
    table_data['KS p-value'] = table_data['KS p-value'].round(4)
    table_data['Wasserstein 거리'] = table_data['Wasserstein 거리'].round(4)
    table_data['PSI'] = table_data['PSI'].round(4)
    
    table = ax.table(cellText=table_data.values,
                     colLabels=table_data.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # 헤더 스타일
    for i in range(len(table_data.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.title('원본 vs 합성 데이터 통계적 검증 결과', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    output_path = f'{output_dir}/statistical_validation_table.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    return results_df


if __name__ == "__main__":
    # 데이터 로딩 (하드코딩된 절대 경로)
    base_dir = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food'
    print("데이터 로딩 중...")
    synthetic_df = pd.read_csv(os.path.join(base_dir, 'output_images', 'synthetic_adsgan_3000.csv'))
    augmented_df = pd.read_parquet(os.path.join(base_dir, 'output_images', 'augmented_train_data.parquet'))
    
    # 원본 데이터 추출 (증강 데이터에서 합성 데이터 제외)
    # 합성 데이터가 3000개이므로, 증강 데이터의 처음 2493개가 원본
    original_size = len(augmented_df) - len(synthetic_df)
    original_df = augmented_df.iloc[:original_size].copy()
    
    print(f"원본 데이터: {len(original_df):,} 행")
    print(f"합성 데이터: {len(synthetic_df):,} 행")
    
    # 수치형 변수
    numeric_cols = ['energy_100g', 'fat_100g', 'sugars_100g', 'proteins_100g', 'sodium_100g']
    
    # 검증 수행
    results = statistical_validation(original_df, synthetic_df, numeric_cols)
    
    print("\n" + "=" * 80)
    print("검증 1 완료!")
    print("=" * 80)

