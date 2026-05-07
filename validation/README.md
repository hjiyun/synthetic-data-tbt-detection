# 합성 데이터 검증

원본 데이터와 합성 데이터를 비교하여 합성 데이터의 품질을 검증합니다.

## 검증 항목

### 1. 수치형 변수 통계적 검증
- **KS Test (Kolmogorov-Smirnov test)**: 분포 차이 검정
- **Wasserstein Distance**: 분포 간 거리 측정
- **PSI (Population Stability Index)**: 드리프트 측정
  - PSI < 0.1: 매우 안정적
  - PSI 0.1-0.25: 약간의 드리프트
  - PSI > 0.25: 큰 드리프트

**대상 변수**: energy_100g, fat_100g, sugars_100g, proteins_100g, sodium_100g

### 2. 변수 간 관계 비교
- **상관계수 비교**: 원본과 합성 데이터의 상관계수 차이
- **산점도 비교**: 주요 변수 쌍의 관계 시각화
  - sugars - energy
  - fat - energy
  - sugars - fat

### 3. 합성 판별기 테스트
- 원본과 합성을 섞어놓고, "이 샘플이 합성인지 맞히는 분류기"를 학습
- **AUROC (Area Under ROC Curve)**: 판별기 성능
  - AUROC ≈ 0.5: 합성이 원본과 구분이 어려움 (좋음)
  - AUROC > 0.7: 합성이 원본과 구분 가능 (개선 필요)

## 사용 방법

### 전체 검증 실행
```bash
cd validation
python run_all_validations.py
```

### 개별 검증 실행
```bash
cd validation
python 01_statistical_validation.py
python 02_correlation_validation.py
python 03_discriminator_test.py
```

## 출력 파일

모든 결과는 `validation/results/` 폴더에 저장됩니다:

### 검증 1 결과
- `statistical_validation_results.csv`: 통계적 검증 결과 (CSV)
- `statistical_validation_table.png`: 통계적 검증 결과 표 (이미지)

### 검증 2 결과
- `original_correlation.csv`: 원본 데이터 상관계수 행렬
- `synthetic_correlation.csv`: 합성 데이터 상관계수 행렬
- `correlation_difference.csv`: 상관계수 차이
- `correlation_comparison.csv`: 주요 변수 쌍 상관계수 비교
- `scatter_plots_comparison.png`: 산점도 비교 (6개 그래프)
- `correlation_heatmaps.png`: 상관계수 히트맵 비교

### 검증 3 결과
- `discriminator_results.csv`: 판별기 성능 결과
- `discriminator_roc_curves.png`: ROC Curve (3개 모델)
- `discriminator_confusion_matrix.png`: Confusion Matrix
- `discriminator_feature_importance.png`: Feature Importance (Random Forest)

## 해석 가이드

### 통계적 검증
- **KS p-value > 0.05**: 분포가 유사함 (좋음)
- **Wasserstein Distance 작을수록**: 분포가 유사함 (좋음)
- **PSI < 0.1**: 매우 안정적 (좋음)

### 상관계수 비교
- **차이 < 0.1**: 상관관계가 잘 유지됨 (좋음)
- **차이 0.1-0.2**: 어느 정도 유지됨
- **차이 > 0.2**: 상관관계가 크게 달라짐 (개선 필요)

### 판별기 테스트
- **AUROC < 0.55**: 합성이 원본과 매우 유사 (매우 좋음)
- **AUROC 0.55-0.65**: 합성이 원본과 어느 정도 유사 (좋음)
- **AUROC > 0.65**: 합성이 원본과 구분 가능 (개선 필요)

## 참고

- 원본 데이터: `output_images/augmented_train_data.parquet`의 처음 부분
- 합성 데이터: `output_images/synthetic_adsgan_3000.csv`

