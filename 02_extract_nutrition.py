import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. 영양 정보 추출 함수 (Numpy Array 구조 완벽 대응)
# ==========================================
def extract_nutrition_from_nutriments(df, nutriments_col='nutriments'):
    print("\n[2-1] nutriments에서 영양정보 추출 중 (Numpy 대응)...")
    
    # 추출할 영양소와 매칭될 'name' 키값들 (우선순위 순서대로)
    # energy-kcal을 energy보다 먼저 둬서 칼로리 정확도 높임
    nutrition_map = {
        'energy_100g': ['energy-kcal', 'energy'], 
        'fat_100g': ['fat'],
        'saturated_fat_100g': ['saturated-fat'],
        'carbohydrates_100g': ['carbohydrates'],
        'sugars_100g': ['sugars'],
        'proteins_100g': ['proteins'],
        'sodium_100g': ['sodium'],
        'salt_100g': ['salt']
    }
    
    df = df.copy()
    
    # 결과를 담을 딕셔너리 초기화
    extracted_data = {col: [] for col in nutrition_map.keys()}
    
    # 데이터프레임 순회
    for idx, row in df.iterrows():
        nutr_array = row[nutriments_col]
        
        # 1. nutriments 데이터를 리스트 형태로 표준화
        items = []
        if isinstance(nutr_array, np.ndarray):
            items = nutr_array # Numpy 배열은 그대로 반복 가능
        elif isinstance(nutr_array, list):
            items = nutr_array
        
        # 2. 해당 행(row)의 영양소 정보를 임시 저장할 딕셔너리
        # 예: {'energy': 100, 'fat': 10 ...}
        row_nutrients = {}
        
        # nutriments 배열 안의 딕셔너리들을 하나씩 검사
        for item in items:
            if not isinstance(item, dict): continue
            
            name = item.get('name')
            val_100g = item.get('100g')
            
            # 100g 값이 있는 경우만 가져옴
            if name and val_100g is not None:
                row_nutrients[name] = float(val_100g)

        # 3. 우리가 원하는 컬럼별로 값 매핑
        for target_col, search_names in nutrition_map.items():
            final_value = 0.0
            
            # 우선순위대로 찾음 (예: energy-kcal 먼저 찾고 없으면 energy 찾기)
            for name in search_names:
                if name in row_nutrients:
                    val = row_nutrients[name]
                    
                    # 에너지 단위 보정 (energy 항목인데 값이 너무 크면 kJ로 간주)
                    if target_col == 'energy_100g' and name == 'energy':
                        # 451 같은 값은 kJ일 확률이 높음. energy-kcal이 없어서 이걸 쓸 때는 변환 고려
                        # 하지만 여기선 단순화를 위해 그대로 두거나 4.184로 나눔
                        # 안전하게: energy-kcal이 이미 있으면 위에서 잡혔을 것임.
                        # 여기 왔다는 건 energy-kcal이 없다는 뜻. 
                        # 보통 energy는 kJ임. kcal로 변환.
                        val = val / 4.184
                    
                    final_value = val
                    break # 찾았으면 루프 종료
            
            extracted_data[target_col].append(final_value)

    # 추출된 데이터를 데이터프레임에 추가
    for col, values in extracted_data.items():
        df[col] = values
        
    print(f"  > 영양성분 {len(nutrition_map)}개 추출 완료")
    
    # 디버깅: 첫 3개 행의 에너지 값 확인
    print(f"  > [Debug] First 3 Energy Values: {extracted_data['energy_100g'][:3]}")
    
    return df

# ==========================================
# 2. 결측치 처리 함수
# ==========================================
def handle_missing_values(df):
    print("\n[2-2] 결측치 처리 중 (삭제 안 함)...")
    df = df.copy()
    
    # 1. 영양정보 -> 0으로 채움
    nutrition_cols = [col for col in df.columns if '_100g' in col]
    for col in nutrition_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(0.0)
    print(f"  > 영양성분 결측치 0으로 대치 완료")

    # 2. 범주형 변수 -> 'missing' 문자열로 채움
    categorical_cols = ['nutriscore_grade', 'categories_tags', 'allergens_tags', 'labels_tags']
    for col in categorical_cols:
        if col in df.columns:
            if df[col].isna().sum() > 0:
                df[col] = df[col].fillna('missing')
    print(f"  > 범주형 변수 결측치 'missing' 대치 완료")
    
    return df

# ==========================================
# 3. 리스트/배열 -> 문자열 변환 함수 (Numpy Array 오류 해결)
# ==========================================
def convert_lists_to_string(df):
    print("\n[2-3] 데이터 타입 정리 (List/Array -> String)...")
    df = df.copy()
    
    target_cols = ['categories_tags', 'allergens_tags', 'labels_tags', 
                   'brands_tags', 'countries_tags', 'ingredients_text']
    
    for col in target_cols:
        if col in df.columns:
            def process_value(val):
                # Numpy 배열이나 리스트인 경우
                if isinstance(val, (list, np.ndarray)):
                    if len(val) == 0: 
                        return "missing"
                    # 문자열로 변환하여 콤마로 연결
                    return ",".join(str(x) for x in val)
                # 결측치인 경우
                elif pd.isna(val):
                    return "missing"
                # 그 외 (이미 문자열 등)
                else:
                    return str(val)
            
            df[col] = df[col].apply(process_value)
            print(f"  > {col}: 변환 완료")
            
    return df

# ==========================================
# 메인 실행
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("[최종 수정] 영양정보 추출 및 저장 (Numpy 구조 대응)")
    print("=" * 60)
    
    try:
        df_raw = pd.read_parquet('data/df_raw.parquet')
    except:
        path = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\data\df_raw.parquet"
        df_raw = pd.read_parquet(path)

    print(f"입력 데이터: {len(df_raw):,} 행")
    
    # 2. 추출
    df_nutrition = extract_nutrition_from_nutriments(df_raw)
    
    # 3. 결측치 처리
    df_cleaned = handle_missing_values(df_nutrition)

    # 4. 키 컬럼 문자열 변환
    if 'code' in df_cleaned.columns:
        df_cleaned['code'] = df_cleaned['code'].astype(str).str.strip()
    
    # 5. 리스트/배열 타입 변환
    df_final = convert_lists_to_string(df_cleaned)
    

    # 6. 저장
    output_path = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\data\df_preprocessed.parquet'
    
    try:
        print(f"\n[저장] {output_path} 저장 시작...")
        df_final.to_parquet(output_path, engine='pyarrow', index=False)
        print("✅ 저장 성공!")
        print("이제 test.py(병합)를 실행하면 숫자가 정상적으로 나올 것입니다.")
        
    except Exception as e:
        print(f"\n[Error] 저장 중 오류 발생: {e}")
    