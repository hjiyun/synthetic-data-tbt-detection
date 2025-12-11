# 프로젝트 요약: Open Food Facts 데이터 전처리 파이프라인

## 완료된 작업

### ✅ 1단계: 데이터 로딩 및 한국 제품 필터링
- **파일**: `01_data_loading.py`
- **결과**: 
  - 전체 데이터: 4,184,848 행 → 한국 제품: 8,372 행 (0.20%)
  - `df_raw.parquet` 생성 완료

### ✅ 2단계: 영양정보 추출 및 전처리
- **파일**: `02_extract_nutrition.py`
- **기능**:
  - `nutriments` 배열에서 영양정보 추출 (energy, fat, carbohydrates, proteins 등)
  - 결측치 처리 (카테고리별 평균 → 전체 평균)
  - 이상치 클리핑 (현실적인 영양정보 범위 적용)

### ✅ 3단계: 범주형/멀티라벨 변수 정리
- **파일**: `03_process_categorical.py`
- **기능**:
  - `categories_tags`에서 상위 카테고리 1개 추출
  - `allergens_tags`에서 알레르겐 boolean flag 추출 (7개)
  - `labels_tags`에서 라벨 boolean flag 추출 (5개)

### ✅ 4단계: train/test 분리 및 스케일링/인코딩
- **파일**: `04_train_test_split.py`
- **기능**:
  - train/test 분리 (80/20)
  - 연속형 변수 StandardScaler 스케일링
  - 범주형 변수 LabelEncoder 인코딩
  - 전처리 아티팩트 저장 (scaler, encoders, feature_info)

### ✅ 전체 파이프라인 실행 스크립트
- **파일**: `run_preprocessing_pipeline.py`
- 모든 단계를 순차적으로 실행

## 생성된 파일 구조

```
.
├── 01_data_loading.py              # 1단계 스크립트
├── 02_extract_nutrition.py         # 2단계 스크립트
├── 03_process_categorical.py       # 3단계 스크립트
├── 04_train_test_split.py          # 4단계 스크립트
├── run_preprocessing_pipeline.py   # 전체 실행 스크립트
├── requirements.txt                # 패키지 목록
├── README.md                        # 사용 설명서
└── PROJECT_SUMMARY.md               # 이 파일

[실행 후 생성되는 파일]
└── data/                           # 데이터 폴더
    ├── df_raw.parquet              # 필터링된 원본 데이터
    ├── df_preprocessed.parquet     # 영양정보 추출 완료
    ├── df_categorical.parquet      # 범주형 변수 처리 완료
    ├── train_data.parquet          # 훈련 데이터 (최종)
    ├── test_data.parquet           # 테스트 데이터 (최종)
    └── preprocessing_artifacts/     # 전처리 아티팩트
        ├── scaler.pkl (있을 경우)
        ├── encoders.pkl
        └── feature_info.pkl
```

## 추출되는 Feature 목록

### 연속형 변수 (9개)
1. `energy_100g` - 에너지 (kcal/100g)
2. `fat_100g` - 지방 (g/100g)
3. `saturated_fat_100g` - 포화지방 (g/100g)
4. `carbohydrates_100g` - 탄수화물 (g/100g)
5. `sugars_100g` - 당류 (g/100g)
6. `proteins_100g` - 단백질 (g/100g)
7. `fiber_100g` - 식이섬유 (g/100g)
8. `salt_100g` - 소금 (g/100g)
9. `sodium_100g` - 나트륨 (g/100g)

### 범주형 변수 (2개)
1. `category_top` - 상위 카테고리
2. `nutriscore_grade` - Nutri-Score 등급

### Boolean 변수 - 알레르겐 (7개)
1. `has_gluten` - 글루텐
2. `has_nuts` - 견과류
3. `has_milk` - 우유
4. `has_eggs` - 계란
5. `has_soy` - 대두
6. `has_fish` - 생선
7. `has_shellfish` - 갑각류

### Boolean 변수 - 라벨 (5개)
1. `is_organic` - 유기농
2. `is_vegan` - 비건
3. `is_vegetarian` - 채식
4. `is_fair_trade` - 공정무역
5. `is_bio` - 바이오

**총 Feature 수**: 약 23개 (연속형 9 + 범주형 2 + Boolean 12)

## 사용 방법

### 전체 파이프라인 실행
```bash
python run_preprocessing_pipeline.py
```

### 단계별 실행
```bash
python 01_data_loading.py
python 02_extract_nutrition.py
python 03_process_categorical.py
python 04_train_test_split.py
```

## 다음 단계 (합성 데이터 생성)

전처리된 데이터를 사용하여:

1. **SynthCity** 또는 **TabDDPM** 모델 학습
   ```python
   from synthcity.plugins import Plugins
   
   # train_data.parquet 로딩
   train_df = pd.read_parquet('train_data.parquet')
   
   # 모델 학습
   model = Plugins().get("ctgan")  # 또는 "tabddpm", "tvae" 등
   model.fit(train_df)
   
   # 합성 데이터 생성
   synthetic_df = model.generate(count=10000)
   ```

2. **평가 지표 계산**
   - 통계적 거리 (Wasserstein distance, MMD 등)
   - ML 효용성 (downstream task 성능)
   - 데이터 품질 점수

## 주의사항

1. **메모리**: food.parquet가 약 4GB이므로 충분한 RAM 필요
2. **한국 제품 수**: 약 8,372개 (전체의 0.2%)
3. **결측치**: 일부 컬럼(categories, labels)의 결측 비율이 높음 (70% 이상)
4. **실행 시간**: 전체 파이프라인 실행 시 수 분 소요 가능

## 개선 가능한 부분

1. **더 많은 영양정보 추출**: 비타민, 미네랄 등
2. **카테고리 계층 구조 활용**: 상위 카테고리만이 아닌 전체 계층
3. **텍스트 feature**: product_name, brands 등 NLP 처리
4. **이미지 feature**: 제품 이미지 활용 (선택적)

