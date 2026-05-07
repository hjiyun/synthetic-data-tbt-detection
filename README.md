# Synthetic Data for TBT Detection

합성 데이터(Synthetic Data)를 활용해 한국 식품의 **무역기술장벽(TBT, Technical Barriers to Trade)** 위험을 사전 진단하는 엔드투엔드 파이프라인입니다.

Open Food Facts 한국 제품 데이터를 전처리한 뒤, (1) 한/영 라벨링 격차(Gap)를 분석해 TBT 위험 라벨을 만들고, (2) AdsGAN 기반 합성 데이터로 희귀 위험 케이스를 증강한 다음, (3) FDA Nutrition Facts 형식의 영문 라벨을 자동 생성하고, (4) 입력만으로 수출 적합성을 판정하는 진단기를 제공합니다.

## 핵심 아이디어

- **문제**: 한국 식품 데이터 중 영어 라벨이 누락된 "내수용(Gap)" 제품은 수출 시 TBT 위반 위험이 큼. 그러나 Gap 사례가 전체의 **약 1.6%**(2,493건 중 39건)에 불과해 분류기 학습이 어려움.
- **해법**: SynthCity의 **AdsGAN**으로 소수 클래스(위험)만 선택적으로 증강하여 50:50 균형을 맞추고, RandomForest TBT 탐지기를 학습. 추가로 LLM(Upstage Solar)으로 영문 FDA 라벨 콘텐츠/이미지를 자동 생성.

## 파이프라인 구조

```
[Open Food Facts food.parquet]
        │
        ▼
[01-04] 한국 제품 필터링 → 영양/범주/알레르겐 추출 → train/test 분리
        │
        ▼
[Fact/01_tbt_analysis.py]  언어별 라벨링 Gap 분석 (Gap / Compliant / No Data)
        │  → tbt_analysis_result.parquet
        ▼
[merge.py / test.py]  영양 데이터 + TBT 라벨 병합 → final_merged_data.parquet
        │
        ├──► [05-07] LLM 라벨 생성  (Solar API → JSON → Excel → PNG)
        │
        └──► [08] AdsGAN 데이터 증강 + RandomForest TBT 탐지기 학습
                │  → synthetic_adsgan_3000.csv, augmented_train_data.parquet
                ├──► [09] 대화형 자가 진단 도구 (CLI)
                ├──► [10] 증강 효과 검증 실험 (Baseline vs Balanced F1)
                └──► [validation/] 합성 데이터 품질 검증 (KS / Wasserstein / PSI / 판별기 AUROC)
```

## 파일 구조

```
.
├── 01_data_loading.py              # 한국 제품 필터링 (food.parquet → df_raw)
├── 02_extract_nutrition.py         # 영양정보 추출 + 결측/이상치 처리
├── 03_process_categorical.py       # 범주/알레르겐/라벨 boolean 추출
├── 04_train_test_split.py          # train/test 분리 + 스케일링/인코딩
├── run_preprocessing_pipeline.py   # 01-04 일괄 실행
│
├── Fact/
│   ├── 01_tbt_analysis.py          # 한/영 라벨링 Gap 분석 (TBT 라벨 생성)
│   ├── tbt_analysis_result.parquet
│   └── figures/                    # 누적 막대 / Gap 비율 히트맵
│
├── merge.py                        # 영양 데이터 + TBT 결과 병합
├── test.py                         # 병합 무결성 검증
│
├── 05_generate_label_content.py    # LLM(Upstage Solar)로 FDA 라벨 JSON 생성
├── 06_label_report.py              # JSON → Excel/CSV 리포트
├── 07_generate_label_image.py      # PIL로 FDA Nutrition Facts PNG 생성
├── synthetic_labels.json           # 05 출력 (5개 샘플 라벨)
│
├── 08_train_tbt_detector.py        # AdsGAN 증강 + RF 탐지기 학습
├── 09_tbt_diagnostic_tool.py       # 대화형 자가 진단 CLI
├── 10_prove_augmentation_effect.py # Baseline vs Balanced F1 비교 실험
│
├── validation/
│   ├── 01_statistical_validation.py    # KS test / Wasserstein / PSI
│   ├── 02_correlation_validation.py    # 상관계수·산점도 비교
│   ├── 03_discriminator_test.py        # 판별기 AUROC
│   └── run_all_validations.py
│
├── data/                           # 전처리 산출물
├── output_images/                  # 라벨 PNG, 증강 데이터, 결과 그래프
└── requirements.txt
```

## 설치

```bash
pip install -r requirements.txt
```

핵심 의존성:
- `pandas`, `numpy`, `scikit-learn`, `pyarrow` — 데이터 처리
- `synthcity == 0.2.12` — AdsGAN 등 합성 데이터 생성기
- `torch`, `pytorch-lightning` — GPU 가속 (선택)
- `pillow` — FDA 라벨 이미지 렌더링
- `openai` — Upstage Solar API 호출 (`05_generate_label_content.py`)
- `matplotlib`, `seaborn` — 시각화

> `05_generate_label_content.py`는 [Upstage Solar API 키](https://console.upstage.ai/)가 필요합니다. 파일 상단의 `API_KEY` 변수를 본인의 키로 교체하세요.

## 사용법

### 1단계: 전처리 (01-04)

```bash
python run_preprocessing_pipeline.py
```

또는 단계별:

```bash
python 01_data_loading.py        # 한국 제품 필터링
python 02_extract_nutrition.py   # 영양정보 추출
python 03_process_categorical.py # 범주/알레르겐 처리
python 04_train_test_split.py    # train/test 분리
```

### 2단계: TBT Gap 분석 + 데이터 병합

```bash
python Fact/01_tbt_analysis.py   # 한/영 라벨링 Gap 분석
python merge.py                   # 영양 + TBT 결과 병합
```

### 3단계: LLM FDA 라벨 자동 생성 (선택)

```bash
python 05_generate_label_content.py  # JSON 라벨 생성 (Solar API)
python 06_label_report.py            # Excel 리포트
python 07_generate_label_image.py    # PNG 라벨 이미지
```

### 4단계: 합성 데이터 증강 + TBT 탐지

```bash
python 08_train_tbt_detector.py       # AdsGAN으로 3,000개 증강 + RF 학습
python 09_tbt_diagnostic_tool.py      # 대화형 진단 (칼로리·지방·당류·단백질·나트륨 입력)
python 10_prove_augmentation_effect.py # Baseline vs Balanced F1 비교 + 그래프
```

### 5단계: 합성 데이터 품질 검증

```bash
cd validation
python run_all_validations.py
```

## 데이터 라벨 정의 (TBT Risk)

`Fact/01_tbt_analysis.py`의 분류 기준:

| Case | 조건 | TBT 라벨 |
|------|------|---------|
| **Gap (내수용)** | `ingredients_text`에 한국어만 존재 | **위험 (target=1)** |
| **Compliant (수출/글로벌용)** | 한/영 병기 | 안전 (target=0) |
| **English Only** | 영어만 존재 | 안전 (target=0) |
| **No Data** | 둘 다 없음 | 분석 제외 |

분포 예시: `No Data 93.3%` / `English Only 4.5%` / `Gap 1.6%` / `Compliant 0.6%`

## 추출 Feature

### 연속형 (영양정보, 9개)
`energy_100g`, `fat_100g`, `saturated_fat_100g`, `carbohydrates_100g`, `sugars_100g`, `proteins_100g`, `fiber_100g`, `salt_100g`, `sodium_100g`

### 범주형 (2개)
`category_top` (Snacks/Beverages 등 상위 카테고리), `nutriscore_grade` (a~e)

### Boolean — 알레르겐 (7개)
`has_gluten`, `has_nuts`, `has_milk`, `has_eggs`, `has_soy`, `has_fish`, `has_shellfish`

### Boolean — 라벨 (5개)
`is_organic`, `is_vegan`, `is_vegetarian`, `is_fair_trade`, `is_bio`

## 전처리 세부사항

- **결측치**: 연속형은 결측 70% 이상이면 컬럼 제외, 그 외는 카테고리별 평균 → 전체 평균. 범주형은 `"missing"`.
- **이상치**: 영양정보별 현실 범위로 클리핑 (예: `energy_100g` 0–900 kcal, `fat_100g` 0–100 g).
- **스케일링**: 연속형 `StandardScaler`, 범주형 `LabelEncoder`.
- **분할**: 80/20, `random_state=42`.

## 합성 데이터 검증 (`validation/`)

| 검증 | 지표 | 기준 |
|------|------|------|
| 분포 유사성 | KS p-value, Wasserstein, **PSI** | PSI < 0.1 매우 안정 |
| 변수 간 관계 | 상관계수 차이, 산점도 | 차이 < 0.1 양호 |
| 판별기 테스트 | **AUROC** | 0.5에 가까울수록 좋음 (구분 불가) |

## 증강 효과 (`10_prove_augmentation_effect.py`)

소수 클래스(위험) 데이터만 AdsGAN으로 증강해 50:50 균형을 맞춘 뒤, **F1 점수**(위험 탐지 능력)를 Baseline과 비교합니다. 결과는 `balancing_effect.png`로 저장됩니다.

## 주의사항

- `food.parquet`은 약 4GB로 충분한 RAM이 필요합니다.
- 스크립트들의 경로는 `C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food` 절대경로로 하드코딩되어 있습니다. 다른 환경에서 실행할 경우 경로를 수정하세요.
- `05_generate_label_content.py`의 API 키는 커밋 전 반드시 환경변수로 분리하세요.
- AdsGAN 학습은 GPU(CUDA)가 있을 경우 자동으로 활용됩니다 (`08`, `10`).

## 라이선스 / 데이터 출처

- 데이터: [Open Food Facts](https://world.openfoodfacts.org/) (ODbL)
- 합성 데이터 생성: [SynthCity](https://github.com/vanderschaarlab/synthcity)
