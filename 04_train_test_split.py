"""
4단계: train/test 분리 및 스케일링/인코딩
- train/test 분리 (80/20)
- 연속형 변수 스케일링
- 범주형 변수 인코딩
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def prepare_feature_columns(df):
    """
    최종 feature 컬럼 선택 및 정리
    
    Parameters:
    -----------
    df : pd.DataFrame
        입력 데이터프레임
    
    Returns:
    --------
    tuple
        (연속형 컬럼 리스트, 범주형 컬럼 리스트, 전체 feature 컬럼 리스트)
    """
    # 연속형 변수 (영양정보)
    continuous_cols = [col for col in df.columns if '_100g' in col]
    
    # 범주형 변수
    categorical_cols = ['category_top', 'nutriscore_grade']
    
    # Boolean flag 변수 (범주형으로 처리하되, 이미 0/1이므로 그대로 사용 가능)
    boolean_cols = [col for col in df.columns if col.startswith('has_') or col.startswith('is_')]
    
    # ID 컬럼 (제외)
    id_cols = ['code']
    
    # 전체 feature 컬럼
    all_feature_cols = continuous_cols + categorical_cols + boolean_cols
    
    return continuous_cols, categorical_cols, boolean_cols, all_feature_cols, id_cols


def split_train_test(df, test_size=0.2, random_state=42):
    """
    train/test 분리
    
    Parameters:
    -----------
    df : pd.DataFrame
        입력 데이터프레임
    test_size : float
        테스트 세트 비율
    random_state : int
        랜덤 시드
    
    Returns:
    --------
    tuple
        (train_df, test_df)
    """
    print("\n[4-1] train/test 분리 중...")
    
    train_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        random_state=random_state,
        shuffle=True
    )
    
    print(f"  Train: {len(train_df):,} 행 ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Test: {len(test_df):,} 행 ({len(test_df)/len(df)*100:.1f}%)")
    
    return train_df, test_df


def scale_continuous_features(train_df, test_df, continuous_cols, scaler_type='standard'):
    """
    연속형 변수 스케일링
    
    Parameters:
    -----------
    train_df : pd.DataFrame
        훈련 데이터프레임
    test_df : pd.DataFrame
        테스트 데이터프레임
    continuous_cols : list
        연속형 컬럼 리스트
    scaler_type : str
        스케일러 타입 ('standard' 또는 'minmax')
    
    Returns:
    --------
    tuple
        (스케일된 train_df, 스케일된 test_df, 스케일러 객체 또는 None)
    """
    print(f"\n[4-2] 연속형 변수 스케일링 ({scaler_type})...")
    
    train_df = train_df.copy()
    test_df = test_df.copy()
    
    # 연속형 변수가 없으면 스케일링 건너뛰기
    if len(continuous_cols) == 0:
        print("  연속형 변수가 없어 스케일링을 건너뜁니다.")
        return train_df, test_df, None
    
    # 스케일러 선택
    if scaler_type == 'standard':
        scaler = StandardScaler()
    elif scaler_type == 'minmax':
        scaler = MinMaxScaler()
    else:
        raise ValueError(f"Unknown scaler_type: {scaler_type}")
    
    # 훈련 데이터로 fit
    train_scaled = scaler.fit_transform(train_df[continuous_cols])
    train_df[continuous_cols] = train_scaled
    
    # 테스트 데이터 transform
    test_scaled = scaler.transform(test_df[continuous_cols])
    test_df[continuous_cols] = test_scaled
    
    print(f"  스케일링된 컬럼: {len(continuous_cols)}개")
    if len(continuous_cols) > 0:
        print(f"  Train 통계 (첫 번째 컬럼 예시):")
        print(f"    평균: {train_df[continuous_cols[0]].mean():.4f}, 표준편차: {train_df[continuous_cols[0]].std():.4f}")
    
    return train_df, test_df, scaler


def encode_categorical_features(train_df, test_df, categorical_cols):
    """
    범주형 변수 인코딩 (Label Encoding)
    
    Parameters:
    -----------
    train_df : pd.DataFrame
        훈련 데이터프레임
    test_df : pd.DataFrame
        테스트 데이터프레임
    categorical_cols : list
        범주형 컬럼 리스트
    
    Returns:
    --------
    tuple
        (인코딩된 train_df, 인코딩된 test_df, 인코더 딕셔너리)
    """
    print(f"\n[4-3] 범주형 변수 인코딩...")
    
    train_df = train_df.copy()
    test_df = test_df.copy()
    
    encoders = {}
    
    for col in categorical_cols:
        if col not in train_df.columns:
            print(f"  경고: {col} 컬럼이 없습니다.")
            continue
        
        # LabelEncoder 생성 및 fit
        le = LabelEncoder()
        
        # train과 test의 모든 고유값을 포함하여 fit
        all_values = pd.concat([train_df[col], test_df[col]]).unique()
        le.fit(all_values)
        
        # 변환
        train_df[col] = le.transform(train_df[col])
        test_df[col] = le.transform(test_df[col])
        
        encoders[col] = le
        
        print(f"  {col}: {len(le.classes_)}개 클래스")
        print(f"    클래스: {list(le.classes_)}")
    
    return train_df, test_df, encoders


def save_preprocessing_artifacts(scaler, encoders, feature_info, output_dir='data/preprocessing_artifacts'):
    """
    전처리 아티팩트 저장 (스케일러, 인코더 등)
    
    Parameters:
    -----------
    scaler : sklearn scaler or None
        스케일러 객체 (연속형 변수가 없으면 None)
    encoders : dict
        인코더 딕셔너리
    feature_info : dict
        feature 정보 (컬럼 리스트 등)
    output_dir : str
        출력 디렉토리
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # 스케일러 저장 (있는 경우만)
    if scaler is not None:
        with open(f'{output_dir}/scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        print(f"  scaler.pkl 저장 완료")
    else:
        print(f"  스케일러 없음 (연속형 변수 없음)")
    
    # 인코더 저장
    with open(f'{output_dir}/encoders.pkl', 'wb') as f:
        pickle.dump(encoders, f)
    print(f"  encoders.pkl 저장 완료")
    
    # feature 정보 저장
    with open(f'{output_dir}/feature_info.pkl', 'wb') as f:
        pickle.dump(feature_info, f)
    print(f"  feature_info.pkl 저장 완료")
    
    print(f"\n[4-4] 전처리 아티팩트 저장 완료: {output_dir}/")


if __name__ == "__main__":
    print("=" * 60)
    print("4단계: train/test 분리 및 스케일링/인코딩")
    print("=" * 60)
    
    # 이전 단계 결과 로딩
    df_categorical = pd.read_parquet('data/df_categorical.parquet')
    print(f"\n입력 데이터: {len(df_categorical):,} 행")
    
    # Feature 컬럼 준비
    continuous_cols, categorical_cols, boolean_cols, all_feature_cols, id_cols = prepare_feature_columns(df_categorical)
    
    print(f"\nFeature 컬럼 정보:")
    print(f"  연속형: {len(continuous_cols)}개 - {continuous_cols}")
    print(f"  범주형: {len(categorical_cols)}개 - {categorical_cols}")
    print(f"  Boolean: {len(boolean_cols)}개 - {boolean_cols}")
    print(f"  전체: {len(all_feature_cols)}개")
    
    # ID와 feature 분리
    df_features = df_categorical[all_feature_cols + id_cols].copy()
    
    # train/test 분리
    train_df, test_df = split_train_test(df_features, test_size=0.2, random_state=42)
    
    # 연속형 변수 스케일링
    train_scaled, test_scaled, scaler = scale_continuous_features(
        train_df, test_df, continuous_cols, scaler_type='standard'
    )
    
    # 범주형 변수 인코딩
    train_encoded, test_encoded, encoders = encode_categorical_features(
        train_scaled, test_scaled, categorical_cols
    )
    
    # 저장
    print(f"\n[4-5] 최종 데이터 저장 중...")
    train_encoded.to_parquet('data/train_data.parquet', engine='pyarrow', index=False)
    test_encoded.to_parquet('data/test_data.parquet', engine='pyarrow', index=False)
    print("  data/train_data.parquet 저장 완료")
    print("  data/test_data.parquet 저장 완료")
    
    # 전처리 아티팩트 저장
    feature_info = {
        'continuous_cols': continuous_cols,
        'categorical_cols': categorical_cols,
        'boolean_cols': boolean_cols,
        'all_feature_cols': all_feature_cols,
        'id_cols': id_cols,
    }
    save_preprocessing_artifacts(scaler, encoders, feature_info)
    
    print("\n" + "=" * 60)
    print("4단계 완료!")
    print("=" * 60)
    print(f"\n최종 데이터 요약:")
    print(f"  Train: {len(train_encoded):,} 행, {len(all_feature_cols)} features")
    print(f"  Test: {len(test_encoded):,} 행, {len(all_feature_cols)} features")

