"""
1단계: 데이터 로딩 및 기본 전처리
- food.parquet 로딩
- 한국 제품 필터링
- 필요한 컬럼 선택
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_and_filter_korean_products(parquet_path='../food.parquet', output_path='data/df_raw.parquet'):
    """
    food.parquet를 로딩하고 한국 제품만 필터링하여 저장
    
    Parameters:
    -----------
    parquet_path : str
        입력 parquet 파일 경로
    output_path : str
        필터링된 데이터 저장 경로
    
    Returns:
    --------
    pd.DataFrame
        필터링된 데이터프레임
    """
    print("=" * 60)
    print("1단계: 데이터 로딩 및 한국 제품 필터링")
    print("=" * 60)
    
    # 1. 데이터 로딩
    print(f"\n[1-1] {parquet_path} 로딩 중...")
    df = pd.read_parquet(parquet_path, engine='pyarrow')
    print(f"전체 데이터: {len(df):,} 행, {len(df.columns)} 컬럼")
    
    # 2. 한국 제품 필터링
    print("\n[1-2] 한국 제품 필터링 중...")
    # countries_tags는 배열 형태이므로 문자열로 변환하여 검색
    korean_mask = df['countries_tags'].astype(str).str.contains(
        'korea|kr|south-korea|en:kr|en:korea', 
        case=False, 
        na=False
    )
    df_korean = df[korean_mask].copy()
    print(f"한국 제품: {len(df_korean):,} 행 ({len(df_korean)/len(df)*100:.2f}%)")
    
    # 3. 기본 컬럼 선택
    print("\n[1-3] 기본 컬럼 선택 중...")
    basic_columns = [
        'code',                    # 바코드 (ID)
        'product_name',            # 제품명
        'brands',                  # 브랜드
        'brands_tags',             # 브랜드 태그
        'categories',              # 카테고리
        'categories_tags',         # 카테고리 태그
        'countries_tags',          # 국가 태그
        'allergens_tags',          # 알레르겐 태그
        'labels_tags',             # 라벨 태그 (organic, vegan 등)
        'nutriscore_grade',        # Nutri-Score 등급
        'nutriments',              # 영양정보 (딕셔너리 배열)
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in basic_columns if col in df_korean.columns]
    missing_columns = [col for col in basic_columns if col not in df_korean.columns]
    
    if missing_columns:
        print(f"경고: 다음 컬럼이 없습니다: {missing_columns}")
    
    df_raw = df_korean[available_columns].copy()
    print(f"선택된 컬럼: {len(available_columns)}개")
    print(f"최종 데이터: {len(df_raw):,} 행")
    
    # 4. 저장
    print(f"\n[1-4] {output_path}에 저장 중...")
    df_raw.to_parquet(output_path, engine='pyarrow', index=False)
    print("저장 완료!")
    
    # 5. 기본 통계
    print("\n[1-5] 기본 통계:")
    print(f"- 결측치 비율:")
    for col in df_raw.columns:
        if col != 'nutriments':  # nutriments는 별도 처리
            missing_pct = df_raw[col].isna().sum() / len(df_raw) * 100
            if missing_pct > 0:
                print(f"  {col}: {missing_pct:.1f}%")
    
    return df_raw


if __name__ == "__main__":
    # food 폴더에서 실행 시 상위 디렉토리의 food.parquet 사용
    # data 폴더에 저장
    df_raw = load_and_filter_korean_products(parquet_path='../food.parquet', output_path='data/df_raw.parquet')
    print("\n" + "=" * 60)
    print("1단계 완료!")
    print("=" * 60)

