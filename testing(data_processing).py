from data_processing import WoodIndustryDataProcessor

processor = WoodIndustryDataProcessor('продукция_выручка2.xlsx')

df = processor.run_full_preprocessing()

metrics = processor.calculate_company_metrics()

print("\nРанжирование компаний:")
top_companies = metrics
for _, company in top_companies.iterrows():
    print(f"   {company['компания']}: {company['годовая_прибыль_руб_mean']:,.0f} руб (рентабельность: {company['рентабельность']}%)")

print(f"\nВсего обработано {len(df)} записей")
print(f"Создано {len(processor.product_categories)} категорий")