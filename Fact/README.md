# TBT 분석: 언어별 데이터 존재 여부 확인

Open Food Facts 데이터를 활용한 TBT(무역기술장벽) 리스크 분석입니다.

## 목적

한국 식품 제품의 언어별 라벨링 현황을 분석하여:
- **내수용 제품** (한국어만 있음): TBT 리스크 높음
- **수출/글로벌용 제품** (한/영 병기): 데이터 충족
- **데이터 부족**: 분석 제외

## 분석 단계

### Step 1: 모집단 정의
- 전체 데이터에서 `countries_tags`에 `en:south-korea`가 포함된 제품만 필터링
- 결과: 한국 시장 제품 데이터셋

### Step 2: 언어별 데이터 존재 여부 확인
- `ingredients_text`에서 한국어/영어 성분 정보 확인
- Case 분류:
  - **Case A (Gap)**: 한국어만 있음 → TBT 리스크 높음
  - **Case B (Compliant)**: 한/영 병기 → 데이터 충족
  - **Case C (No Data)**: 둘 다 없음 → 분석 제외

### Step 3: 카테고리별 세분화
- 상위 카테고리별로 그룹화
- 주요 카테고리: Snacks, Beverages, Instant Noodles, Sauces 등

### Step 4: 시각화
- 누적 막대 그래프 (제품 수)
- 비율 막대 그래프 (퍼센트)
- Gap 비율 히트맵

## 사용 방법

```bash
cd Fact
python 01_tbt_analysis.py
```

## 출력 파일

1. **`tbt_analysis_result.parquet`**: 분석 결과 데이터
2. **`figures/stacked_bar_chart.png`**: 누적 막대 그래프 (제품 수)
3. **`figures/stacked_bar_chart_percentage.png`**: 누적 막대 그래프 (비율)
4. **`figures/gap_heatmap.png`**: Gap 비율 히트맵

## 분석 결과 예시

```
언어별 데이터 통계:
  No Data (데이터 부족): 2,325 (93.3%)
  English Only: 113 (4.5%)
  Gap (내수용): 39 (1.6%)
  Compliant (수출/글로벌용): 16 (0.6%)
```

## 시각화 설명

### 누적 막대 그래프
- **X축**: 식품 카테고리
- **Y축**: 제품 수 (또는 비율 %)
- **색상**:
  - 🔴 빨간색: Gap (내수용) - TBT 리스크 높음
  - 🔵 파란색: Compliant (수출/글로벌용) - 데이터 충족
  - ⚪ 회색: No Data (데이터 부족)

### 히트맵
- 카테고리별 Gap 비율을 색상으로 표현
- 빨간색이 진할수록 TBT 리스크가 높은 카테고리

## 다음 단계

이 분석 결과를 바탕으로:
1. **Gap이 높은 카테고리** 식별
2. **합성 데이터 생성**으로 영어 라벨링 보완
3. **TBT 리스크 완화** 전략 수립


