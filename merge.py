import pandas as pd
import numpy as np

def merge_datasets():
    print("=" * 60)
    print("[Final Step] 데이터 병합 및 무결성 검증")
    print("=" * 60)

    # 1. 데이터 로드
    print("[1] 데이터 로딩 중...")
    try:
        df_tbt = pd.read_parquet(r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\Fact\tbt_analysis_result.parquet') # 경로 확인 필요
        df_nutri = pd.read_parquet(r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\data\df_preprocessed.parquet') # 경로 확인 필요
    except FileNotFoundError:
        base_path = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food"
        df_tbt = pd.read_parquet(f"{base_path}\\Fact\\tbt_analysis_result.parquet")
        df_nutri = pd.read_parquet(f"{base_path}\\data\\df_preprocessed.parquet")
    
    print(f" - TBT 데이터(Target): {len(df_tbt):,}행")
    print(f" - 영양 데이터(Source): {len(df_nutri):,}행")

    # 2. Key 컬럼 전처리 (안전장치)
    key_col = 'code'
    df_tbt[key_col] = df_tbt[key_col].astype(str).str.strip()
    df_nutri[key_col] = df_nutri[key_col].astype(str).str.strip()

    print(f"[Info] 매칭 대상: {len(df_tbt):,}개")

    # 3. [수정된 부분] 가져올 영양소 컬럼 명시적 지정
    # 여기에 필요한 모든 영양소 이름을 적습니다.
    target_nutrients = [
        'energy_100g', 'fat_100g', 'saturated_fat_100g', 
        'carbohydrates_100g', 'sugars_100g', 
        'proteins_100g', 'sodium_100g', 'salt_100g'
    ]

    # 실제 영양 데이터 파일에 존재하는 것만 추려냄
    available_nutrients = [c for c in target_nutrients if c in df_nutri.columns]
    print(f"[Check] 영양 데이터 파일에서 찾은 영양소: {available_nutrients}")

    if 'energy_100g' not in available_nutrients:
        print("⚠️ [Warning] 'energy_100g' 컬럼이 영양 데이터 파일(df_preprocessed) 자체에 없습니다!")
        print("   -> 전처리 과정(2단계)에서 결측치가 너무 많아 삭제되었을 수 있습니다.")
    
    # 4. 중복 방지 (TBT 파일에 이미 영양소 컬럼이 있다면 삭제해버림)
    # 그래야 병합할 때 깨끗하게 들어옵니다.
    df_tbt = df_tbt.drop(columns=available_nutrients, errors='ignore')

    # 5. 병합 수행 (Left Join)
    # code와 영양소 컬럼만 딱 찝어서 가져옵니다.
    cols_to_merge = [key_col] + available_nutrients
    
    merged_df = pd.merge(
        df_tbt,
        df_nutri[cols_to_merge],
        on=key_col,
        how='left'
    )

    # 6. 결과 검증
    if 'energy_100g' in merged_df.columns:
        n_zeros = (merged_df['energy_100g'] == 0).sum()
        n_valid = merged_df['energy_100g'].notna().sum()
        print("\n[Result] 최종 데이터 검증")
        print(f" - 영양 정보 매칭됨: {n_valid:,} (이 중 0인 값: {n_zeros:,})")
        
        # 샘플 출력
        print("\n[Sample Data]")
        print(merged_df[['code', 'product_name', 'energy_100g']].head(3))
    else:
        print("\n[Error] 병합은 됐으나 energy_100g 컬럼이 여전히 없습니다.")

    # 7. 저장
    output_path = 'final_merged_data.parquet'
    merged_df.to_parquet(output_path, engine='pyarrow', index=False)
    print(f"\n✅ 저장 완료: {output_path}")

if __name__ == "__main__":
    merge_datasets()