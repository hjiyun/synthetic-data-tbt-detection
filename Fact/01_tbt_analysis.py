"""
TBT 분석: 언어별 데이터 존재 여부 확인 및 시각화
- Step 1: 한국 관련 제품 추출 (en:south-korea)
- Step 2: 언어별 데이터 존재 여부 확인 (ingredients_text_ko vs ingredients_text_en)
- Step 3: 카테고리별 세분화
- Step 4: 시각화 (누적 막대 그래프, 히트맵)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False

def load_korean_products(parquet_path='../../food.parquet'):
    """
    Step 1: 한국 관련 제품 추출
    countries_tags에 'en:south-korea'가 포함된 행만 필터링
    """
    print("=" * 80)
    print("Step 1: 모집단 정의 (한국 관련 제품 추출)")
    print("=" * 80)
    
    print(f"\n[1-1] {parquet_path} 로딩 중...")
    df = pd.read_parquet(parquet_path, engine='pyarrow')
    print(f"전체 데이터: {len(df):,} 행, {len(df.columns)} 컬럼")
    
    print("\n[1-2] 한국 제품 필터링 중...")
    # en:south-korea가 포함된 행만 필터링
    korean_mask = df['countries_tags'].astype(str).str.contains(
        'en:south-korea|en:kr|en:korea|south-korea', 
        case=False, 
        na=False
    )
    df_korean = df[korean_mask].copy()
    print(f"한국 제품: {len(df_korean):,} 행 ({len(df_korean)/len(df)*100:.2f}%)")
    
    return df_korean


def check_language_data(df):
    """
    Step 2: 언어별 데이터 존재 여부 확인
    ingredients_text에서 한국어/영어 성분 정보 확인
    """
    print("\n" + "=" * 80)
    print("Step 2: 언어별 데이터 존재 여부 확인")
    print("=" * 80)
    
    df = df.copy()
    
    # ingredients_text 컬럼 확인
    if 'ingredients_text' not in df.columns:
        print("경고: ingredients_text 컬럼이 없습니다.")
        return df
    
    print("\n[2-1] ingredients_text 구조 분석 중...")
    
    # ingredients_text가 딕셔너리 형태인지 확인
    sample_text = df['ingredients_text'].dropna().iloc[0] if df['ingredients_text'].notna().any() else None
    print(f"  Sample type: {type(sample_text)}")
    
    # 언어별 컬럼이 있는지 확인
    lang_cols = {
        'ko': [c for c in df.columns if 'ingredients' in c.lower() and ('ko' in c.lower() or 'korean' in c.lower())],
        'en': [c for c in df.columns if 'ingredients' in c.lower() and ('en' in c.lower() or 'english' in c.lower())]
    }
    
    print(f"\n[2-2] 언어별 컬럼 확인:")
    print(f"  한국어 컬럼: {lang_cols['ko']}")
    print(f"  영어 컬럼: {lang_cols['en']}")
    
    # ingredients_text에서 언어별 정보 추출 시도
    # OFF 데이터는 ingredients_text가 딕셔너리 리스트 형태: [{'lang': 'ko', 'text': '...'}, {'lang': 'en', 'text': '...'}]
    def extract_language_info(row):
        """ingredients_text에서 언어별 정보 추출"""
        result = {
            'has_ko': False,
            'has_en': False
        }
        
        try:
            # Series에서 직접 접근
            if 'ingredients_text' not in row.index:
                return result
            
            ingredients = row['ingredients_text']
            
            # None 체크 (배열이 아닌 경우에만 pd.isna 사용)
            if ingredients is None:
                return result
            
            # 배열인 경우 먼저 체크
            if isinstance(ingredients, (list, np.ndarray)):
                if len(ingredients) == 0:
                    return result
                
                # 딕셔너리 리스트 형태인 경우 (OFF 표준 형식)
                for item in ingredients:
                    if isinstance(item, dict):
                        lang = item.get('lang', '').lower()
                        text = item.get('text', '')
                        if lang in ['ko', 'korean', 'kr'] or any('\uAC00' <= char <= '\uD7A3' for char in str(text)):
                            result['has_ko'] = True
                        if lang in ['en', 'english']:
                            result['has_en'] = True
            # 딕셔너리 형태인 경우
            elif isinstance(ingredients, dict):
                lang = ingredients.get('lang', '').lower()
                if lang in ['ko', 'korean', 'kr']:
                    result['has_ko'] = True
                if lang in ['en', 'english']:
                    result['has_en'] = True
            # 문자열 형태인 경우
            elif isinstance(ingredients, str):
                # 한국어 문자 포함 여부 (유니코드 범위)
                has_korean_char = any('\uAC00' <= char <= '\uD7A3' for char in ingredients)
                # 영어 포함 여부
                has_english = any(char.isalpha() and ord(char) < 128 for char in ingredients)
                
                result['has_ko'] = has_korean_char and len(ingredients.strip()) > 0
                result['has_en'] = has_english and len(ingredients.strip()) > 0
        except Exception as e:
            # 오류 발생 시 기본값 반환
            pass
        
        return result
    
    print("\n[2-3] 언어별 데이터 존재 여부 분석 중...")
    language_info = df.apply(extract_language_info, axis=1)
    df['has_ingredients_ko'] = [info['has_ko'] for info in language_info]
    df['has_ingredients_en'] = [info['has_en'] for info in language_info]
    
    # Case 분류
    def classify_language_case(row):
        has_ko = row['has_ingredients_ko']
        has_en = row['has_ingredients_en']
        
        if has_ko and not has_en:
            return 'Gap (내수용)'  # Case A: TBT 리스크 높음
        elif has_ko and has_en:
            return 'Compliant (수출/글로벌용)'  # Case B: 데이터 충족
        elif not has_ko and not has_en:
            return 'No Data (데이터 부족)'  # Case C: 분석 제외
        elif not has_ko and has_en:
            return 'English Only'  # 영어만 있는 경우
        else:
            return 'Unknown'
    
    df['language_case'] = df.apply(classify_language_case, axis=1)
    
    # 통계 출력
    print("\n[2-4] 언어별 데이터 통계:")
    case_counts = df['language_case'].value_counts()
    for case, count in case_counts.items():
        pct = count / len(df) * 100
        print(f"  {case}: {count:,} ({pct:.1f}%)")
    
    return df


def categorize_products(df):
    """
    Step 3: 카테고리별 세분화
    상위 카테고리를 선정하여 그룹화
    """
    print("\n" + "=" * 80)
    print("Step 3: 카테고리별 세분화")
    print("=" * 80)
    
    df = df.copy()
    
    print("\n[3-1] 카테고리 추출 중...")
    
    def extract_top_category(categories_tags):
        """categories_tags에서 상위 카테고리 추출"""
        # None 체크
        if categories_tags is None:
            return 'Unknown'
        
        # 배열인 경우 먼저 체크
        if isinstance(categories_tags, (list, np.ndarray)):
            if len(categories_tags) == 0:
                return 'Unknown'
            first_tag = str(categories_tags[0])
        elif isinstance(categories_tags, str):
            if categories_tags == 'missing' or categories_tags == 'nan':
                return 'Unknown'
            if ',' in categories_tags:
                first_tag = categories_tags.split(',')[0].strip()
            else:
                first_tag = categories_tags
        else:
            return 'Unknown'
        
        try:
            
            # en: 접두사 제거 및 카테고리명 추출
            category = first_tag.replace('en:', '').replace('en-', '').strip()
            
            # 주요 카테고리 매핑
            category_mapping = {
                'snacks': 'Snacks',
                'instant-noodles': 'Instant Noodles',
                'ramen': 'Instant Noodles',
                'beverages': 'Beverages',
                'sauces': 'Sauces',
                'condiments': 'Sauces',
                'dairies': 'Dairies',
                'meats-and-their-products': 'Meat Products',
                'plant-based-foods-and-beverages': 'Plant-based Foods',
                'breakfasts': 'Breakfast Foods',
                'desserts': 'Desserts',
            }
            
            # 매핑된 카테고리 반환 또는 원본 반환
            for key, value in category_mapping.items():
                if key in category.lower():
                    return value
            
            return category.title() if category else 'Unknown'
        except Exception:
            return 'Unknown'
    
    df['category_top'] = df['categories_tags'].apply(extract_top_category)
    
    # 상위 카테고리 통계
    print("\n[3-2] 카테고리별 제품 수:")
    category_counts = df['category_top'].value_counts().head(15)
    for cat, count in category_counts.items():
        print(f"  {cat}: {count:,}")
    
    return df


def visualize_gap_analysis(df, output_dir='figures'):
    """
    Step 4: 시각화
    - 누적 막대 그래프 (Stacked Bar Chart)
    - 결측치 히트맵 (Missingno Matrix)
    """
    print("\n" + "=" * 80)
    print("Step 4: 시각화")
    print("=" * 80)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 전처리: 카테고리별로 그룹화
    category_analysis = df.groupby(['category_top', 'language_case']).size().unstack(fill_value=0)
    
    # 상위 10개 카테고리만 선택
    top_categories = df['category_top'].value_counts().head(10).index
    category_analysis = category_analysis.loc[top_categories]
    
    # 누적 막대 그래프
    print("\n[4-1] 누적 막대 그래프 생성 중...")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 색상 정의
    colors = {
        'Gap (내수용)': '#FF4444',  # 빨간색
        'Compliant (수출/글로벌용)': '#4444FF',  # 파란색
        'No Data (데이터 부족)': '#CCCCCC',  # 회색
        'English Only': '#FFAA44',  # 주황색
        'Unknown': '#888888'  # 어두운 회색
    }
    
    # 누적 막대 그래프 그리기
    bottom = np.zeros(len(category_analysis))
    for case in category_analysis.columns:
        if case in colors:
            ax.bar(category_analysis.index, category_analysis[case], 
                   bottom=bottom, label=case, color=colors[case], alpha=0.8)
            bottom += category_analysis[case]
    
    ax.set_xlabel('식품 카테고리', fontsize=12, fontweight='bold')
    ax.set_ylabel('제품 수', fontsize=12, fontweight='bold')
    ax.set_title('카테고리별 언어 라벨링 현황 (TBT 리스크 분석)', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    output_path = f'{output_dir}/stacked_bar_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    # 비율 막대 그래프 (퍼센트)
    print("\n[4-2] 비율 막대 그래프 생성 중...")
    category_pct = category_analysis.div(category_analysis.sum(axis=1), axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bottom = np.zeros(len(category_pct))
    for case in category_pct.columns:
        if case in colors:
            ax.bar(category_pct.index, category_pct[case], 
                   bottom=bottom, label=case, color=colors[case], alpha=0.8)
            bottom += category_pct[case]
    
    ax.set_xlabel('식품 카테고리', fontsize=12, fontweight='bold')
    ax.set_ylabel('비율 (%)', fontsize=12, fontweight='bold')
    ax.set_title('카테고리별 언어 라벨링 비율 (TBT 리스크 분석)', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    output_path = f'{output_dir}/stacked_bar_chart_percentage.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    # 히트맵 (카테고리별 Gap 비율)
    print("\n[4-3] 히트맵 생성 중...")
    gap_ratio = (category_analysis.get('Gap (내수용)', 0) / category_analysis.sum(axis=1) * 100).sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    gap_ratio_df = pd.DataFrame({'Gap 비율 (%)': gap_ratio})
    sns.heatmap(gap_ratio_df, annot=True, fmt='.1f', cmap='Reds', 
                cbar_kws={'label': 'Gap 비율 (%)'}, ax=ax, vmin=0, vmax=100)
    ax.set_title('카테고리별 언어 라벨링 Gap 비율 히트맵', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('')
    plt.tight_layout()
    
    output_path = f'{output_dir}/gap_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    print("\n[4-4] 시각화 완료!")


if __name__ == "__main__":
    # 전체 파이프라인 실행
    print("=" * 80)
    print("TBT 분석: 언어별 데이터 존재 여부 확인 및 시각화")
    print("=" * 80)
    
    # Step 1: 한국 제품 추출
    df_korean = load_korean_products()
    
    # Step 2: 언어별 데이터 확인
    df_analyzed = check_language_data(df_korean)
    
    # Step 3: 카테고리별 세분화
    df_categorized = categorize_products(df_analyzed)
    
    # Step 4: 시각화
    visualize_gap_analysis(df_categorized)
    
    # 결과 저장
    output_path = 'tbt_analysis_result.parquet'
    print(f"\n[최종] 결과 저장 중: {output_path}")
    df_categorized.to_parquet(output_path, engine='pyarrow', index=False)
    print("저장 완료!")
    
    print("\n" + "=" * 80)
    print("전체 분석 완료!")
    print("=" * 80)

