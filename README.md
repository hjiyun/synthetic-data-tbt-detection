# Open Food Facts 데이터 전처리 파이프라인

Open Food Facts의 food.parquet 데이터에서 한국 제품을 필터링하고, 합성 데이터 생성 모델(SynthCity, TabDDPM 등)에 사용할 수 있도록 전처리하는 파이프라인입니다.

## 목적

1. **데이터 추출**: food.parquet에서 성분·영양정보·알레르겐·카테고리 등 tabular feature 추출
2. **전처리**: 결측치 처리, 이상치 처리, 범주형 변수 정리
3. **모델 준비**: train/test 분리, 스케일링, 인코딩

## 파일 구조

```
.
├── 01_data_loading.py              # 1단계: 데이터 로딩 및 한국 제품 필터링
├── 02_extract_nutrition.py         # 2단계: 영양정보 추출 및 전처리
├── 03_process_categorical.py       # 3단계: 범주형/멀티라벨 변수 정리
├── 04_train_test_split.py          # 4단계: train/test 분리 및 스케일링/인코딩
├── run_preprocessing_pipeline.py   # 전체 파이프라인 실행 스크립트
├── requirements.txt                # 필요한 패키지 목록
└── README.md                        # 이 파일
```

## 설치

```bash
pip install -r requirements.txt
```

필요한 패키지:
- pandas >= 2.0.0
- numpy >= 1.24.0
- scikit-learn >= 1.3.0
- pyarrow >= 12.0.0

## 사용법

### 전체 파이프라인 실행

```bash
python run_preprocessing_pipeline.py
```

### 단계별 실행

각 단계를 개별적으로 실행할 수도 있습니다:

```bash
# 1단계: 데이터 로딩 및 한국 제품 필터링
python 01_data_loading.py

# 2단계: 영양정보 추출 및 전처리
python 02_extract_nutrition.py

# 3단계: 범주형/멀티라벨 변수 정리
python 03_process_categorical.py

# 4단계: train/test 분리 및 스케일링/인코딩
python 04_train_test_split.py
```

## 출력 파일

파이프라인 실행 후 `data/` 폴더에 다음 파일들이 생성됩니다:

1. **data/df_raw.parquet**: 필터링된 원본 데이터 (한국 제품만)
2. **data/df_preprocessed.parquet**: 영양정보 추출 및 전처리 완료
3. **data/df_categorical.parquet**: 범주형 변수 처리 완료
4. **data/train_data.parquet**: 훈련 데이터 (스케일링/인코딩 완료)
5. **data/test_data.parquet**: 테스트 데이터 (스케일링/인코딩 완료)
6. **data/preprocessing_artifacts/**: 전처리 아티팩트
   - `scaler.pkl`: 스케일러 객체 (연속형 변수가 있을 경우)
   - `encoders.pkl`: 인코더 딕셔너리
   - `feature_info.pkl`: feature 정보 (컬럼 리스트 등)

## 추출되는 Feature

### 연속형 변수 (영양정보)
- `energy_100g`: 에너지 (kcal/100g)
- `fat_100g`: 지방 (g/100g)
- `saturated_fat_100g`: 포화지방 (g/100g)
- `carbohydrates_100g`: 탄수화물 (g/100g)
- `sugars_100g`: 당류 (g/100g)
- `proteins_100g`: 단백질 (g/100g)
- `fiber_100g`: 식이섬유 (g/100g)
- `salt_100g`: 소금 (g/100g)
- `sodium_100g`: 나트륨 (g/100g)

### 범주형 변수
- `category_top`: 상위 카테고리 (예: snacks, beverages)
- `nutriscore_grade`: Nutri-Score 등급 (a, b, c, d, e)

### Boolean 변수 (알레르겐)
- `has_gluten`: 글루텐 함유 여부
- `has_nuts`: 견과류 함유 여부
- `has_milk`: 우유 함유 여부
- `has_eggs`: 계란 함유 여부
- `has_soy`: 대두 함유 여부
- `has_fish`: 생선 함유 여부
- `has_shellfish`: 갑각류 함유 여부

### Boolean 변수 (라벨)
- `is_organic`: 유기농 여부
- `is_vegan`: 비건 여부
- `is_vegetarian`: 채식 여부
- `is_fair_trade`: 공정무역 여부
- `is_bio`: 바이오 여부

## 전처리 세부사항

### 결측치 처리
- **연속형 변수**: 결측 비율이 70% 이상이면 컬럼 제외, 그 외는 카테고리별 평균 → 전체 평균으로 대치
- **범주형 변수**: "missing" 카테고리로 대치

### 이상치 처리
- 영양정보의 현실적인 범위를 정의하여 클리핑
  - 예: `energy_100g`: 0 ~ 900 kcal/100g
  - 예: `fat_100g`: 0 ~ 100 g/100g

### 스케일링
- 연속형 변수: StandardScaler (z-score 정규화)
- 범주형 변수: LabelEncoder

### Train/Test 분리
- 80% train, 20% test
- Random seed: 42

## 다음 단계

전처리된 데이터를 사용하여:
1. **SynthCity** 또는 **TabDDPM** 같은 생성 모델 학습
2. 합성 데이터 생성
3. 실제 데이터와의 유사도 평가 (통계적 거리, ML 효용성 등)

## 주의사항

- food.parquet 파일이 약 4GB 크기이므로 충분한 메모리가 필요합니다
- 한국 제품은 전체 데이터의 약 0.2% 정도입니다 (약 8,000~10,000개)
- 각 단계는 이전 단계의 출력 파일을 필요로 합니다

