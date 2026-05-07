"""
검증 2: 변수 간 관계 비교
- 상관계수 비교
- 산점도 비교 (sugars-energy, fat-energy, sugars-fat)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def correlation_validation(original_df, synthetic_df, numeric_cols, output_dir=None):
    """변수 간 관계 비교"""
    if output_dir is None:
        output_dir = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\validation\results'
    """
    변수 간 관계 비교
    """
    print("=" * 80)
    print("검증 2: 변수 간 관계 비교")
    print("=" * 80)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 수치형 변수만 선택
    orig_numeric = original_df[numeric_cols].dropna()
    synth_numeric = synthetic_df[numeric_cols].dropna()
    
    print(f"\n[2-1] 상관계수 계산 중...")
    print(f"  원본 데이터: {len(orig_numeric):,} 행")
    print(f"  합성 데이터: {len(synth_numeric):,} 행")
    
    # 상관계수 계산
    orig_corr = orig_numeric.corr()
    synth_corr = synth_numeric.corr()
    
    # 상관계수 차이
    corr_diff = orig_corr - synth_corr
    
    # 결과 저장
    orig_corr.to_csv(f'{output_dir}/original_correlation.csv', encoding='utf-8-sig')
    synth_corr.to_csv(f'{output_dir}/synthetic_correlation.csv', encoding='utf-8-sig')
    corr_diff.to_csv(f'{output_dir}/correlation_difference.csv', encoding='utf-8-sig')
    
    print("  상관계수 행렬 저장 완료")
    
    # 주요 변수 쌍 (sugars, energy, fat)
    key_pairs = [
        ('sugars_100g', 'energy_100g'),
        ('fat_100g', 'energy_100g'),
        ('sugars_100g', 'fat_100g')
    ]
    
    print("\n[2-2] 주요 변수 쌍 상관계수 비교:")
    comparison_results = []
    
    for var1, var2 in key_pairs:
        if var1 not in numeric_cols or var2 not in numeric_cols:
            continue
        
        orig_corr_val = orig_corr.loc[var1, var2]
        synth_corr_val = synth_corr.loc[var1, var2]
        diff = abs(orig_corr_val - synth_corr_val)
        
        comparison_results.append({
            'Variable_Pair': f'{var1} - {var2}',
            'Original_Correlation': orig_corr_val,
            'Synthetic_Correlation': synth_corr_val,
            'Difference': diff
        })
        
        print(f"  {var1} - {var2}:")
        print(f"    원본: {orig_corr_val:.4f}")
        print(f"    합성: {synth_corr_val:.4f}")
        print(f"    차이: {diff:.4f}")
    
    comparison_df = pd.DataFrame(comparison_results)
    comparison_df.to_csv(f'{output_dir}/correlation_comparison.csv', index=False, encoding='utf-8-sig')
    
    # 산점도 비교
    print("\n[2-3] 산점도 생성 중...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('변수 간 관계 비교: 원본 vs 합성', fontsize=16, fontweight='bold', y=0.995)
    
    for idx, (var1, var2) in enumerate(key_pairs):
        if var1 not in numeric_cols or var2 not in numeric_cols:
            continue
        
        # 원본 데이터 산점도
        ax1 = axes[0, idx]
        scatter1 = ax1.scatter(orig_numeric[var1], orig_numeric[var2], 
                              alpha=0.5, s=10, c='blue', label='원본')
        ax1.set_xlabel(var1.replace('_100g', ''), fontsize=11)
        ax1.set_ylabel(var2.replace('_100g', ''), fontsize=11)
        ax1.set_title(f'원본 데이터\n상관계수: {orig_corr.loc[var1, var2]:.3f}', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 합성 데이터 산점도
        ax2 = axes[1, idx]
        scatter2 = ax2.scatter(synth_numeric[var1], synth_numeric[var2], 
                              alpha=0.5, s=10, c='red', label='합성')
        ax2.set_xlabel(var1.replace('_100g', ''), fontsize=11)
        ax2.set_ylabel(var2.replace('_100g', ''), fontsize=11)
        ax2.set_title(f'합성 데이터\n상관계수: {synth_corr.loc[var1, var2]:.3f}', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    
    plt.tight_layout()
    output_path = f'{output_dir}/scatter_plots_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    # 상관계수 히트맵 비교
    print("\n[2-4] 상관계수 히트맵 생성 중...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # 원본 상관계수
    sns.heatmap(orig_corr, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=axes[0])
    axes[0].set_title('원본 데이터 상관계수', fontsize=12, fontweight='bold')
    
    # 합성 상관계수
    sns.heatmap(synth_corr, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=axes[1])
    axes[1].set_title('합성 데이터 상관계수', fontsize=12, fontweight='bold')
    
    # 차이
    sns.heatmap(corr_diff, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=axes[2])
    axes[2].set_title('상관계수 차이 (원본 - 합성)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    output_path = f'{output_dir}/correlation_heatmaps.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    print("\n" + "=" * 80)
    print("검증 2 완료!")
    print("=" * 80)
    
    return comparison_df


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
    results = correlation_validation(original_df, synthetic_df, numeric_cols)

