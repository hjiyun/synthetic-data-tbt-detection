"""
3단계: 범주형/멀티라벨 변수 정리
- categories에서 상위 카테고리 추출
- allergens_tags, labels_tags에서 boolean flag 생성
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def extract_top_category(categories_tags):
    """
    categories_tags에서 가장 상위 카테고리 1개만 추출
    
    Parameters:
    -----------
    categories_tags : array or str
        카테고리 태그 배열
    
    Returns:
    --------
    str
        상위 카테고리명
    """
    if pd.isna(categories_tags):
        return 'missing'
    
    try:
        # numpy array나 list로 변환
        if isinstance(categories_tags, np.ndarray):
            if categories_tags.size == 0:
                return 'missing'
            tag_list = categories_tags.tolist()
        elif isinstance(categories_tags, list):
            if len(categories_tags) == 0:
                return 'missing'
            tag_list = categories_tags
        elif isinstance(categories_tags, str):
            # 문자열인 경우
            if categories_tags == 'missing' or categories_tags == 'nan' or categories_tags == '':
                return 'missing'
            # 쉼표로 구분된 문자열인 경우 (2단계에서 변환된 형태)
            if ',' in categories_tags:
                tag_list = [tag.strip() for tag in categories_tags.split(',') if tag.strip()]
                if len(tag_list) > 0:
                    first_tag = str(tag_list[0])
                    category = first_tag.replace('en:', '').replace('en-', '')
                    category = category.strip()
                    return category if category else 'missing'
                else:
                    return 'missing'
            # 리스트 형태의 문자열인 경우 파싱 시도
            try:
                import ast
                parsed = ast.literal_eval(categories_tags)
                if isinstance(parsed, list) and len(parsed) > 0:
                    tag_list = parsed
                else:
                    return 'missing'
            except:
                # 단일 문자열인 경우
                category = categories_tags.replace('en:', '').replace('en-', '')
                category = category.strip()
                return category if category else 'missing'
        else:
            return 'missing'
        
        # 첫 번째 태그에서 카테고리명 추출
        if len(tag_list) > 0:
            first_tag = str(tag_list[0])
            # 'en:' 접두사 제거
            category = first_tag.replace('en:', '').replace('en-', '')
            # 특수문자 제거 및 정리
            category = category.strip()
            return category if category else 'missing'
        else:
            return 'missing'
    except Exception:
        return 'missing'


def extract_allergen_flags(allergens_tags):
    """
    allergens_tags에서 주요 알레르겐 boolean flag 추출
    
    Parameters:
    -----------
    allergens_tags : array or str
        알레르겐 태그 배열
    
    Returns:
    --------
    dict
        알레르겐별 boolean flag
    """
    flags = {
        'has_gluten': False,
        'has_nuts': False,
        'has_milk': False,
        'has_eggs': False,
        'has_soy': False,
        'has_fish': False,
        'has_shellfish': False,
    }
    
    if pd.isna(allergens_tags):
        return flags
    
    try:
        # numpy array나 list로 변환
        if isinstance(allergens_tags, np.ndarray):
            if allergens_tags.size == 0:
                return flags
            tag_list = allergens_tags.tolist()
        elif isinstance(allergens_tags, list):
            if len(allergens_tags) == 0:
                return flags
            tag_list = allergens_tags
        elif isinstance(allergens_tags, str):
            # 문자열인 경우 (2단계에서 변환된 형태 또는 원본 문자열)
            if allergens_tags == 'missing' or allergens_tags == 'nan' or allergens_tags == '':
                return flags
            # 쉼표로 구분된 문자열인 경우
            if ',' in allergens_tags:
                tag_list = [tag.strip() for tag in allergens_tags.split(',') if tag.strip()]
            else:
                tag_list = [allergens_tags]
        else:
            # 문자열로 변환하여 처리
            tags_str = str(allergens_tags).lower()
            if 'gluten' in tags_str or 'wheat' in tags_str:
                flags['has_gluten'] = True
            if 'nuts' in tags_str or 'nut' in tags_str or 'almond' in tags_str or 'hazelnut' in tags_str or 'peanuts' in tags_str:
                flags['has_nuts'] = True
            if 'milk' in tags_str or 'lactose' in tags_str:
                flags['has_milk'] = True
            if 'eggs' in tags_str or 'egg' in tags_str:
                flags['has_eggs'] = True
            if 'soy' in tags_str or 'soya' in tags_str or 'soybeans' in tags_str:
                flags['has_soy'] = True
            if 'fish' in tags_str:
                flags['has_fish'] = True
            if 'shellfish' in tags_str or 'crustacean' in tags_str:
                flags['has_shellfish'] = True
            return flags
        
        # 태그 리스트를 문자열로 변환
        tags_str = ' '.join([str(tag).lower() for tag in tag_list])
        
        # 각 알레르겐 확인
        if 'gluten' in tags_str or 'wheat' in tags_str:
            flags['has_gluten'] = True
        if 'nuts' in tags_str or 'nut' in tags_str or 'almond' in tags_str or 'hazelnut' in tags_str or 'peanuts' in tags_str:
            flags['has_nuts'] = True
        if 'milk' in tags_str or 'lactose' in tags_str:
            flags['has_milk'] = True
        if 'eggs' in tags_str or 'egg' in tags_str:
            flags['has_eggs'] = True
        if 'soy' in tags_str or 'soya' in tags_str or 'soybeans' in tags_str:
            flags['has_soy'] = True
        if 'fish' in tags_str:
            flags['has_fish'] = True
        if 'shellfish' in tags_str or 'crustacean' in tags_str:
            flags['has_shellfish'] = True
    except Exception:
        pass
    
    return flags


def extract_label_flags(labels_tags):
    """
    labels_tags에서 주요 라벨 boolean flag 추출
    
    Parameters:
    -----------
    labels_tags : array or str
        라벨 태그 배열
    
    Returns:
    --------
    dict
        라벨별 boolean flag
    """
    flags = {
        'is_organic': False,
        'is_vegan': False,
        'is_vegetarian': False,
        'is_fair_trade': False,
        'is_bio': False,
    }
    
    if pd.isna(labels_tags):
        return flags
    
    try:
        # numpy array나 list로 변환
        if isinstance(labels_tags, np.ndarray):
            if labels_tags.size == 0:
                return flags
            tag_list = labels_tags.tolist()
        elif isinstance(labels_tags, list):
            if len(labels_tags) == 0:
                return flags
            tag_list = labels_tags
        elif isinstance(labels_tags, str):
            # 문자열인 경우 (2단계에서 변환된 형태 또는 원본 문자열)
            if labels_tags == 'missing' or labels_tags == 'nan' or labels_tags == '':
                return flags
            # 쉼표로 구분된 문자열인 경우
            if ',' in labels_tags:
                tag_list = [tag.strip() for tag in labels_tags.split(',') if tag.strip()]
            else:
                tag_list = [labels_tags]
        else:
            # 문자열로 변환하여 처리
            tags_str = str(labels_tags).lower()
            if 'organic' in tags_str or 'usda-organic' in tags_str:
                flags['is_organic'] = True
            if 'vegan' in tags_str:
                flags['is_vegan'] = True
            if 'vegetarian' in tags_str:
                flags['is_vegetarian'] = True
            if 'fair-trade' in tags_str or 'fair_trade' in tags_str:
                flags['is_fair_trade'] = True
            if 'bio' in tags_str:
                flags['is_bio'] = True
            return flags
        
        # 태그 리스트를 문자열로 변환
        tags_str = ' '.join([str(tag).lower() for tag in tag_list])
        
        # 각 라벨 확인
        if 'organic' in tags_str or 'usda-organic' in tags_str:
            flags['is_organic'] = True
        if 'vegan' in tags_str:
            flags['is_vegan'] = True
        if 'vegetarian' in tags_str:
            flags['is_vegetarian'] = True
        if 'fair-trade' in tags_str or 'fair_trade' in tags_str:
            flags['is_fair_trade'] = True
        if 'bio' in tags_str:
            flags['is_bio'] = True
    except Exception:
        pass
    
    return flags


def process_categorical_features(df):
    """
    범주형/멀티라벨 변수 정리
    
    Parameters:
    -----------
    df : pd.DataFrame
        입력 데이터프레임
    
    Returns:
    --------
    pd.DataFrame
        범주형 변수가 정리된 데이터프레임
    """
    print("\n[3-1] 범주형 변수 정리 중...")
    
    df = df.copy()
    
    # 1. 상위 카테고리 추출
    print("  - categories에서 상위 카테고리 추출...")
    if 'categories_tags' in df.columns:
        df['category_top'] = df['categories_tags'].apply(extract_top_category)
        print(f"    카테고리 종류: {df['category_top'].nunique()}개")
        print(f"    카테고리 분포:")
        for cat, count in df['category_top'].value_counts().head(10).items():
            print(f"      {cat}: {count:,} ({count/len(df)*100:.1f}%)")
    else:
        df['category_top'] = 'missing'
        print("    경고: categories_tags 컬럼이 없습니다.")
    
    # 2. 알레르겐 flag 추출
    print("\n  - allergens_tags에서 알레르겐 flag 추출...")
    if 'allergens_tags' in df.columns:
        allergen_flags = df['allergens_tags'].apply(extract_allergen_flags)
        for flag_name in ['has_gluten', 'has_nuts', 'has_milk', 'has_eggs', 'has_soy', 'has_fish', 'has_shellfish']:
            df[flag_name] = allergen_flags.apply(lambda x: x[flag_name])
            count = df[flag_name].sum()
            print(f"    {flag_name}: {count:,} ({count/len(df)*100:.1f}%)")
    else:
        print("    경고: allergens_tags 컬럼이 없습니다.")
        for flag_name in ['has_gluten', 'has_nuts', 'has_milk', 'has_eggs', 'has_soy', 'has_fish', 'has_shellfish']:
            df[flag_name] = False
    
    # 3. 라벨 flag 추출
    print("\n  - labels_tags에서 라벨 flag 추출...")
    if 'labels_tags' in df.columns:
        label_flags = df['labels_tags'].apply(extract_label_flags)
        for flag_name in ['is_organic', 'is_vegan', 'is_vegetarian', 'is_fair_trade', 'is_bio']:
            df[flag_name] = label_flags.apply(lambda x: x[flag_name])
            count = df[flag_name].sum()
            print(f"    {flag_name}: {count:,} ({count/len(df)*100:.1f}%)")
    else:
        print("    경고: labels_tags 컬럼이 없습니다.")
        for flag_name in ['is_organic', 'is_vegan', 'is_vegetarian', 'is_fair_trade', 'is_bio']:
            df[flag_name] = False
    
    # 4. nutriscore_grade 정리
    print("\n  - nutriscore_grade 정리...")
    if 'nutriscore_grade' in df.columns:
        # 결측치를 'missing'으로 처리 (이미 처리되었을 수 있음)
        df['nutriscore_grade'] = df['nutriscore_grade'].fillna('missing')
        print(f"    Nutri-Score 등급 분포:")
        for grade, count in df['nutriscore_grade'].value_counts().items():
            print(f"      {grade}: {count:,} ({count/len(df)*100:.1f}%)")
    else:
        df['nutriscore_grade'] = 'missing'
        print("    경고: nutriscore_grade 컬럼이 없습니다.")
    
    return df


if __name__ == "__main__":
    # 이전 단계 결과 로딩
    print("=" * 60)
    print("3단계: 범주형/멀티라벨 변수 정리")
    print("=" * 60)
    
    df_preprocessed = pd.read_parquet('data/df_preprocessed.parquet')
    print(f"\n입력 데이터: {len(df_preprocessed):,} 행")
    
    # 범주형 변수 처리
    df_categorical = process_categorical_features(df_preprocessed)
    
    # 저장
    output_path = 'data/df_categorical.parquet'
    print(f"\n[3-2] {output_path}에 저장 중...")
    df_categorical.to_parquet(output_path, engine='pyarrow', index=False)
    print("저장 완료!")
    
    print("\n" + "=" * 60)
    print("3단계 완료!")
    print("=" * 60)

