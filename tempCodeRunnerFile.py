
    print("="*50)
    print("🚀 스크립트 시작")

    # ✅ 사용자 지정 경로 (여기가 핵심!)
    data_path = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\Fact\tbt_analysis_result.parquet"
    
    print(f"📄 데이터 로드 중: {data_path}")
    
    if not os.path.exists(data_path):
        print(f"❌ [에러] 여전히 파일을 못 찾았습니다. 경로를 다시 확인해주세요: {data_path}")
        exit()

    df = pd.read_parquet(data_path)
    print(f"✅ 로드 성공! 총 {len(df)}개 데이터")

    # 2. 타겟 필터링 (테스트용 상위 5개)
    target_df = df[ 
        (df['language_case'] == 'Gap (내수용)') & 
        (df['category_top'] == 'Snacks') 