"""
전체 전처리 파이프라인 실행 스크립트
모든 단계를 순차적으로 실행합니다.
"""

import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """스크립트 실행"""
    print("\n" + "=" * 80)
    print(f"{description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        print(f"\n✓ {script_name} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {script_name} 실패: {e}")
        return False
    except Exception as e:
        print(f"\n✗ {script_name} 오류: {e}")
        return False


def main():
    """전체 파이프라인 실행"""
    print("=" * 80)
    print("Open Food Facts 데이터 전처리 파이프라인")
    print("=" * 80)
    
    steps = [
        ("01_data_loading.py", "1단계: 데이터 로딩 및 한국 제품 필터링"),
        ("02_extract_nutrition.py", "2단계: 영양정보 추출 및 전처리"),
        ("03_process_categorical.py", "3단계: 범주형/멀티라벨 변수 정리"),
        ("04_train_test_split.py", "4단계: train/test 분리 및 스케일링/인코딩"),
    ]
    
    for script, description in steps:
        success = run_script(script, description)
        if not success:
            print(f"\n파이프라인이 {description} 단계에서 중단되었습니다.")
            sys.exit(1)
    
    print("\n" + "=" * 80)
    print("전체 파이프라인 완료!")
    print("=" * 80)
    print("\n생성된 파일 (data/ 폴더):")
    print("  - data/df_raw.parquet: 필터링된 원본 데이터")
    print("  - data/df_preprocessed.parquet: 영양정보 추출 및 전처리 완료")
    print("  - data/df_categorical.parquet: 범주형 변수 처리 완료")
    print("  - data/train_data.parquet: 훈련 데이터 (스케일링/인코딩 완료)")
    print("  - data/test_data.parquet: 테스트 데이터 (스케일링/인코딩 완료)")
    print("  - data/preprocessing_artifacts/: 전처리 아티팩트 (스케일러, 인코더 등)")


if __name__ == "__main__":
    main()

