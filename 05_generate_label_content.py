import pandas as pd
import json
import re
import os
import ast
from openai import OpenAI
from tqdm import tqdm

# =========================================================
# 1. 설정 및 API 초기화
# =========================================================

API_KEY = "api key" 
BASE_URL = "https://api.upstage.ai/v1"

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

def clean_json_string(text):
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx : end_idx + 1]
    return text.strip()

def clean_product_name(val):
    try:
        val = str(val)
        if val.startswith('[') and 'text' in val:
            match = re.search(r"'text':\s*'([^']*)'", val)
            if match: return match.group(1)
            match_double = re.search(r'"text":\s*"([^"]*)"', val)
            if match_double: return match_double.group(1)
        return val
    except Exception:
        return "Unknown Snack"

def create_fda_label_prompt(row):
    raw_name = row.get('product_name', 'Unknown Snack')
    product_name = clean_product_name(raw_name)
    
    nutrition_info = {
        "Energy": f"{row.get('energy_100g', 0):.0f} kcal",
        "Fat": f"{row.get('fat_100g', 0)}g",
        "Saturated Fat": f"{row.get('saturated_fat_100g', 0)}g",
        "Carbs": f"{row.get('carbohydrates_100g', 0)}g",
        "Sugars": f"{row.get('sugars_100g', 0)}g",
        "Protein": f"{row.get('proteins_100g', 0)}g",
        "Sodium": f"{row.get('sodium_100g', 0) * 1000:.0f}mg" if pd.notnull(row.get('sodium_100g')) else "0mg"
    }

    raw_allergens = str(row.get('allergens_tags', ''))
    if raw_allergens in ['None', 'nan', 'missing']: raw_allergens = ""
    clean_allergens = raw_allergens.replace('en:', '').replace('-', ' ').replace(',', ', ')

    prompt = f"""
    Role: You are a Food Regulatory Expert specialized in US FDA compliance.
    Task: Convert the given Korean snack data into a JSON format for a US Nutrition Facts label.
    
    [Input Data]
    - Original Name: {product_name}
    - Category: Snack
    - Nutrition (per 100g): {json.dumps(nutrition_info)}
    - Raw Allergen Tags: {clean_allergens if clean_allergens else "Unknown (Infer from name)"}
    
    [Target JSON Structure]
    {{
      "product_name_en": "...",
      "serving_size": "30g",
      "calories_per_serving": "...",
      "nutrition_facts": {{ "total_fat": "...", "sodium": "...", "total_carbohydrate": "...", "protein": "..." }},
      "allergen_statement": "Contains: ...",
      "marketing_claims": ["..."] 
    }}
    """
    return prompt

# =========================================================
# 2. 메인 실행 로직
# =========================================================

if __name__ == "__main__":
    print("="*50)
    print("[SCRIPT START] Generating Label Content (Filter: Energy > 0)")
    print("="*50)

    tbt_path = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\Fact\tbt_analysis_result.parquet"
    nutri_path = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\data\df_preprocessed.parquet" 

    if not os.path.exists(tbt_path) or not os.path.exists(nutri_path):
        print("[ERROR] Files not found."); exit()

    print("[INFO] Loading Data...")
    df_tbt = pd.read_parquet(tbt_path)
    df_nutri = pd.read_parquet(nutri_path)

    # 1. Key 타입 통일
    df_tbt['code'] = df_tbt['code'].astype(str).str.strip()
    df_nutri['code'] = df_nutri['code'].astype(str).str.strip()

    # 2. TBT 파일의 옛날 영양소 컬럼 삭제 (충돌 방지)
    nutri_cols = [
        'energy_100g', 'fat_100g', 'saturated_fat_100g', 
        'carbohydrates_100g', 'sugars_100g', 'proteins_100g', 
        'sodium_100g', 'allergens_tags'
    ]
    df_tbt = df_tbt.drop(columns=[c for c in nutri_cols if c in df_tbt.columns], errors='ignore')

    # 3. 병합
    cols_to_use = ['code'] + [c for c in nutri_cols if c in df_nutri.columns]
    df = pd.merge(df_tbt, df_nutri[cols_to_use], on='code', how='left')

    # 4. [수정됨] 타겟 필터링 (Gap + Snack + Energy > 0)
    print("[INFO] Filtering valid products...")
    
    target_df = df[ 
        (df['language_case'] == 'Gap (내수용)') & 
        (df['category_top'] == 'Snacks') &
        (df['energy_100g'] > 0)  # [중요] 에너지가 0보다 큰 것만 선택!
    ].head(5)
    
    print(f"[INFO] Target Products Found: {len(target_df)}")
    
    # 5. 확인
    if len(target_df) > 0:
        print("\n[CHECK] Energy Values (Should be > 0):")
        print(target_df[['code', 'product_name', 'energy_100g']])
    
    # 6. AI 생성 시작
    generated_data = []

    if len(target_df) == 0:
        print("[WARNING] No valid products found (Check your filter conditions).")
    else:
        print(f"\n[INFO] Calling AI Model for {len(target_df)} products...")
        for index, row in tqdm(target_df.iterrows(), total=len(target_df)):
            prompt = create_fda_label_prompt(row)
            try:
                response = client.chat.completions.create(
                    model="solar-pro",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs strictly JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False,
                    temperature=0.2,
                    max_tokens=1024
                )
                content = clean_json_string(response.choices[0].message.content)
                label_data = json.loads(content)
                label_data['original_code'] = row.get('code', 'unknown')
                generated_data.append(label_data)
                
            except Exception as e:
                print(f"[ERROR] Index {index}: {e}")

    # 7. 저장
    if generated_data:
        save_dir = os.path.dirname(os.path.abspath(__file__))
        output_json_path = os.path.join(save_dir, 'synthetic_labels.json')
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(generated_data, f, indent=2, ensure_ascii=False)
            
        print("="*50)
        print("[SUCCESS] JSON Generation Complete.")
        
        # 결과 미리보기
        result_df = pd.DataFrame(generated_data)
        if 'calories_per_serving' in result_df.columns:
            print("\n[Result Preview - Calories]")
            print(result_df[['product_name_en', 'calories_per_serving']].head(3))
    else:
        print("[FAIL] No data generated.")