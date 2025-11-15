from data_processing import WoodIndustryDataProcessor
from analyzer import WoodIndustryAnalyzer

print("Тестируем модуль аналитики")
print("=" * 40)

processor = WoodIndustryDataProcessor('продукция_выручка2.xlsx')
df = processor.run_full_preprocessing()

if df is not None:
    analyzer = WoodIndustryAnalyzer(df)
    metrics = processor.calculate_company_metrics()
    
    if metrics is not None:
        print("1. Рейтинг компаний(график)")
        analyzer.plot_company_ranking(metrics)
        
        print("2. Динамика цен МДФ (график)")
        analyzer.plot_price_dynamics(company_name='МДФ')
        
        print("3. Анализ продукта 'брус'")
        analyzer.plot_product_analysis('брус')
        
        print("4. Корреляции для МДФ (график)")
        analyzer.create_correlation_heatmap('МДФ')
        
        print("5. Анализ категорий")
        analyzer.plot_category_analysis()
    else:
        print("Ошибка: не удалось получить метрики компаний")
else:
    print("Ошибка: не удалось загрузить данные")