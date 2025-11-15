import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class WoodIndustryAnalyzer:
    def __init__(self, processed_df):
        self.df = processed_df
    
    def plot_company_ranking(self, company_metrics, top_n=10):
        """
        Визуализация рейтинга компаний
        """
        top_companies = company_metrics.head(top_n)
    
        fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    
        # График 1: Прибыль компаний
        axes[0].barh(top_companies['компания'], top_companies['годовая_прибыль_руб_mean'] / 1e6)
        axes[0].set_title('Средняя годовая прибыль (млн руб)')
        axes[0].set_xlabel('Прибыль, млн руб')
    
        # График 2: Рентабельность
        axes[1].barh(top_companies['компания'], top_companies['рентабельность'])
        axes[1].set_title('Рентабельность бизнеса (%)')
        axes[1].set_xlabel('Рентабельность, %')
    
        # График 3: Количество продуктов
        axes[2].barh(top_companies['компания'], top_companies['продукция_nunique'])
        axes[2].set_title('Количество уникальных продуктов')
        axes[2].set_xlabel('Количество продуктов')
    
    
        plt.tight_layout()
        plt.show()
    
        return fig
    
    def plot_price_dynamics(self, company_name=None, product_category=None):
        """
        Анализ динамики цен
        """
        filtered_df = self.df.copy()
        
        if company_name:
            filtered_df = filtered_df[filtered_df['компания'] == company_name]
            
        if product_category:
            filtered_df = filtered_df[filtered_df['категория_продукции'] == product_category]
        
        # топ-3 продукта по выручке
        product_revenue = filtered_df.groupby('продукция')['выручка_руб'].sum().nlargest(3)
        top_products = product_revenue.index.tolist()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # График 1: Динамика цен
        for product in top_products:
            product_data = filtered_df[filtered_df['продукция'] == product]
            if not product_data.empty:
                ax1.plot(product_data['год'], product_data['цена_руб'], marker='o', label=product)
        
        ax1.set_title('Динамика цен')
        ax1.set_xlabel('Год')
        ax1.set_ylabel('Цена, руб')
        ax1.legend()
        ax1.grid(True)
        ax1.set_xticks([2022, 2023, 2024])
        
        # График 2: Объемы продаж
        for product in top_products:
            product_data = filtered_df[filtered_df['продукция'] == product]
            if not product_data.empty:
                ax2.plot(product_data['год'], product_data['количество_шт'], marker='s', label=product)
        
        ax2.set_title('Объемы продаж')
        ax2.set_xlabel('Год')
        ax2.set_ylabel('Количество, шт')
        ax2.legend()
        ax2.grid(True)
        ax2.set_xticks([2022, 2023, 2024])
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def plot_product_analysis(self, product_name):
        """
        Простой анализ конкретного продукта
        """    
        product_data = self.df[self.df['продукция'].str.contains(product_name, case=False, na=False)]
    
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 8))
    
        # График 1: Цены по компаниям
        companies = product_data['компания'].unique()
        for company in companies:
            company_data = product_data[product_data['компания'] == company]
            ax1.plot(company_data['год'], company_data['цена_руб'], marker='o', label=company)
    
        ax1.set_title('Цены по компаниям')
        ax1.set_xlabel('Год')
        ax1.set_ylabel('Цена, руб')
        ax1.grid(True)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.set_xticks([2022, 2023, 2024])
    
        # График 2: Доля рынка
        latest_year = 2024
        latest_data = product_data[product_data['год'] == latest_year]
        market_share = latest_data.groupby('компания')['количество_шт'].sum()
    
        total = market_share.sum()
        percentages = [(value / total * 100) for value in market_share.values]
    
        legend_labels = [f"{company}: {percent:.1f}%" 
                    for company, percent in zip(market_share.index, percentages)]
    
        wedges, texts = ax2.pie(market_share.values)
        ax2.set_title(f'Доля рынка ({latest_year} год)')
        ax2.legend(wedges, legend_labels, title="Компании", 
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
        # График 3: Объемы продаж
        sales_by_year = product_data.groupby(['год', 'компания'])['количество_шт'].sum().unstack()
        sales_by_year.plot(kind='bar', ax=ax3)
        ax3.set_title('Объемы продаж по годам')
        ax3.set_xlabel('Год')
        ax3.set_ylabel('Количество, шт')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
        # График 4: Распределение цен
        box_data = [product_data[product_data['компания'] == company]['цена_руб'] 
               for company in product_data['компания'].unique()]
        box_labels = product_data['компания'].unique()
    
        ax4.boxplot(box_data, labels=box_labels)
        ax4.set_title('Распределение цен по компаниям')
        ax4.set_ylabel('Цена, руб')
        ax4.set_xticklabels(box_labels, rotation=45, ha='right')
    
        plt.tight_layout()
        plt.show()
    
        self._print_simple_stats(product_data, product_name)
    
        return fig
    
    def _print_simple_stats(self, product_data, product_name):
        """
        статистика по продукту
        """

        avg_price = product_data['цена_руб'].mean()
        total_volume = product_data['количество_шт'].sum()
        total_revenue = product_data['выручка_руб'].sum()
        
        print(f"Средняя цена: {avg_price:,.0f} руб")
        print(f"Общий объем: {total_volume:,.0f} шт")
        print(f"Общая выручка: {total_revenue:,.0f} руб")
        
        # Топ компании
        company_sales = product_data.groupby('компания')['количество_шт'].sum().sort_values(ascending=False)
        print(f"\nТоп компаний по объему:")
        for company, volume in company_sales.head(3).items():
            print(f"  {company}: {volume:,.0f} шт")
    
    def create_correlation_heatmap(self, company_name):
        """
        тепловая карта корреляций
        """        
        company_data = self.df[self.df['компания'] == company_name]
        
        numeric_cols = ['цена_руб', 'количество_шт', 'выручка_руб', 'год']
        correlation_data = company_data[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        im = ax.imshow(correlation_data, cmap='coolwarm', vmin=-1, vmax=1)
        
        for i in range(len(correlation_data)):
            for j in range(len(correlation_data)):
                ax.text(j, i, f'{correlation_data.iloc[i, j]:.2f}', 
                       ha="center", va="center", color="black")
        
        ax.set_xticks(range(len(correlation_data)))
        ax.set_yticks(range(len(correlation_data)))
        ax.set_xticklabels(correlation_data.columns)
        ax.set_yticklabels(correlation_data.columns)
        ax.set_title(f'Корреляция показателей - {company_name}')
        
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def plot_category_analysis(self):
        """
        анализ по категориям
        """
        
        category_stats = self.df.groupby('категория_продукции').agg({
            'цена_руб': 'mean',
            'количество_шт': 'sum', 
            'выручка_руб': 'sum',
            'продукция': 'nunique' 
        }).sort_values('выручка_руб', ascending=False)
        
        category_stats = category_stats.rename(columns={'продукция': 'количество_продуктов'})
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # График 1: Выручка
        ax1.barh(category_stats.index, category_stats['выручка_руб'] / 1e6)
        ax1.set_title('Выручка по категориям (млн руб)')
        ax1.set_xlabel('Выручка, млн руб')
        
        # График 2: Средняя цена
        ax2.barh(category_stats.index, category_stats['цена_руб'])
        ax2.set_title('Средняя цена по категориям')
        ax2.set_xlabel('Средняя цена, руб')
        
        # График 3: Количество продуктов (исправленная колонка)
        ax3.barh(category_stats.index, category_stats['количество_продуктов'])
        ax3.set_title('Количество продуктов по категориям')
        ax3.set_xlabel('Количество продуктов')
        
        # График 4: Объем продаж
        ax4.barh(category_stats.index, category_stats['количество_шт'])
        ax4.set_title('Объем продаж по категориям')
        ax4.set_xlabel('Количество, шт')
        
        plt.tight_layout()
        plt.show()
        
        # Выводим статистику
        print("\nСтатистика по категориям:")
        
        for category, row in category_stats.iterrows():
            print(f"{category}:")
            print(f"  Выручка: {row['выручка_руб']:,.0f} руб")
            print(f"  Средняя цена: {row['цена_руб']:,.0f} руб")
            print(f"  Количество продуктов: {row['количество_продуктов']}")
            print(f"  Объем продаж: {row['количество_шт']:,.0f} шт")
            print()
        
        return fig, category_stats