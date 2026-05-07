"""
전체 검증 파이프라인 실행
모든 검증을 순차적으로 실행합니다.
"""

import sys
import subprocess
from pathlib import Path
import os

def run_script(script_name, description):
    """스크립트 실행"""
    print("\n" + "=" * 80)
    print(f"{description}")
    print("=" * 80)
    
    # 하드코딩된 절대 경로
    validation_dir = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\validation'
    script_path = os.path.join(validation_dir, script_name)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,
            cwd=validation_dir
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
    """전체 검증 파이프라인 실행"""
    print("=" * 80)
    print("합성 데이터 검증 파이프라인")
    print("=" * 80)
    
    steps = [
        ("01_statistical_validation.py", "검증 1: 수치형 변수 통계적 검증"),
        ("02_correlation_validation.py", "검증 2: 변수 간 관계 비교"),
        ("03_discriminator_test.py", "검증 3: 합성 판별기 테스트"),
    ]
    
    for script, description in steps:
        success = run_script(script, description)
        if not success:
            print(f"\n파이프라인이 {description} 단계에서 중단되었습니다.")
            sys.exit(1)
    
    print("\n" + "=" * 80)
    print("전체 검증 파이프라인 완료!")
    print("=" * 80)
    print("\n생성된 파일 (validation/results/):")
    print("  - statistical_validation_results.csv: 통계적 검증 결과")
    print("  - statistical_validation_table.png: 통계적 검증 표")
    print("  - original_correlation.csv: 원본 데이터 상관계수")
    print("  - synthetic_correlation.csv: 합성 데이터 상관계수")
    print("  - correlation_comparison.csv: 상관계수 비교")
    print("  - scatter_plots_comparison.png: 산점도 비교")
    print("  - correlation_heatmaps.png: 상관계수 히트맵")
    print("  - discriminator_results.csv: 판별기 성능 결과")
    print("  - discriminator_roc_curves.png: ROC Curve")
    print("  - discriminator_confusion_matrix.png: Confusion Matrix")


if __name__ == "__main__":
    main()

