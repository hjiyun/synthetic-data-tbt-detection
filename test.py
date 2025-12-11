import pandas as pd

def final_check():
    print("=" * 60)
    print("[최종 점검] 병합 및 데이터 확인")
    print("=" * 60)

    # 1. 파일 경로 (사용자 환경)
    tbt_path = r"c:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\Fact\tbt_analysis_result.parquet"
    nutri_path = r"c:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\data\df_preprocessed.parquet"

    # 2. 로드
    df_tbt = pd.read_parquet(tbt_path)
    df_nutri = pd.read_parquet(nutri_path)

    # 3. 키 컬럼 통일
    df_tbt['code'] = df_tbt['code'].astype(str).str.strip()
    df_nutri['code'] = df_nutri['code'].astype(str).str.strip()

    # 4. 병합 (Left Join)
    # 영양 정보 파일에서 가져올 컬럼들
    nutri_cols = ['code', 'energy_100g', 'fat_100g', 'sugars_100g', 'proteins_100g', 'sodium_100g']
    
    merged_df = pd.merge(
        df_tbt,
        df_nutri[nutri_cols],
        on='code',
        how='left'
    )

    # 5. 결과 확인
    print(f"\n1. 전체 데이터 수: {len(merged_df):,}개")
    
    # 0이 아닌 값이 몇 개인지 확인
    valid_energy = merged_df[merged_df['energy_100g'] > 0]['energy_100g'].count()
    print(f"2. 에너지가 0보다 큰 제품 수: {valid_energy:,}개")
    
    print("\n3. 상위 5개 제품 샘플:")
    print(merged_df[['product_name', 'energy_100g', 'sugars_100g']].head(5))
    
    # 저장
    merged_df.to_parquet('final_merged_data.parquet')
    print("\n✅ [완료] final_merged_data.parquet 저장됨")

if __name__ == "__main__":
    final_check()