import pandas as pd
import json
import os

def analyze_and_export():
    print("=" * 60)
    print("[Step 6] 결과 분석 및 엑셀 리포트 생성")
    print("=" * 60)

    # 1. 생성된 JSON 파일 로드
    json_path = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\synthetic_labels.json'
    if not os.path.exists(json_path):
        print(f"[ERROR] {json_path} 파일이 없습니다. 05번 스크립트를 먼저 실행하세요.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[INFO] 로드된 라벨 데이터: {len(data)}개")

    # 2. JSON 데이터를 보기 좋은 표(DataFrame)로 변환
    # pd.json_normalize: 중첩된 JSON(nutrition_facts 등)을 펼쳐서 컬럼으로 만듦
    df_result = pd.json_normalize(data)
    
    print("\n[INFO] 데이터 구조 변환 완료")
    print(" - 생성된 컬럼들:", df_result.columns.tolist())

    # 3. 주요 정보 요약 및 비교 (콘솔 출력용)
    print("\n" + "="*60)
    print(" 📊 [분석] 한국 제품 -> 미국 FDA 라벨 변환 결과 (Top 3)")
    print("="*60)
    
    # 보고 싶은 주요 컬럼만 선택
    display_cols = ['original_code', 'product_name_en', 'serving_size', 
                    'calories_per_serving', 'allergen_statement']
    
    # 실제 존재하는 컬럼만 필터링
    valid_cols = [c for c in display_cols if c in df_result.columns]
    
    for idx, row in df_result[valid_cols].head(3).iterrows():
        print(f"\n[Product {idx+1}] Code: {row.get('original_code')}")
        print(f" - New Name (EN) : {row.get('product_name_en')}")
        print(f" - Serving Size  : {row.get('serving_size')}")
        print(f" - Calories      : {row.get('calories_per_serving')}")
        print(f" - Allergens     : {row.get('allergen_statement')}")

    # 4. 엑셀로 저장 (최종 산출물)
    output_excel = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\output_imagesfinal_fda_labels_report.xlsx'
    
    # 리스트 형태(marketing_claims)를 문자열로 변환해야 엑셀 저장 시 에러 안 남
    for col in df_result.columns:
        df_result[col] = df_result[col].apply(lambda x: str(x) if isinstance(x, list) else x)

    try:
        df_result.to_excel(output_excel, index=False)
        print("\n" + "="*60)
        print(f"✅ [최종 완료] 리포트 저장됨: {output_excel}")
        print("   이 파일을 열어서 내용을 확인하시면 됩니다.")
        print("="*60)
    except Exception as e:
        print(f"\n[ERROR] 엑셀 저장 실패: {e}")
        # 엑셀이 없으면 CSV로라도 저장
        df_result.to_csv(r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\output_images\final_fda_labels_report.csv', index=False)
        print(" -> CSV로 대체 저장되었습니다.")

if __name__ == "__main__":
    analyze_and_export()