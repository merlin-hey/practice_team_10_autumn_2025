import pandas as pd
import numpy as np
import re
from collections import Counter

class WoodIndustryDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.processed_df = None
        self.product_categories = {}
        
    def _clean_column_name(self, column_name):
        """
        Очистка названий колонок
        """
        cleaned = str(column_name).lower().strip()
        cleaned = re.sub(r'[,\s\.]+', '_', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned)
        return cleaned.strip('_')
    
    def _analyze_product_keywords(self, product_series):
        """
        Автоматический анализ ключевых слов в названиях продуктов
        """
        
        all_products = product_series.astype(str).unique()
        words_counter = Counter()
        
        for product in all_products:
            words = re.findall(r'[а-яa-z]+', product.lower())
            words_counter.update(words)
        
        stop_words = {'мм', 'х', 'из', 'в', 'на', 'с', 'по', 'для', 'и', 'или', 'no', 'г', 'обл', 'м'}
        meaningful_words = {word: count for word, count in words_counter.items() 
                          if count >= 2 and word not in stop_words and len(word) > 2}
     
        sorted_words = sorted(meaningful_words.items(), key=lambda x: x[1], reverse=True)
        
        print("Топ-10 ключевых слов:")
        for word, count in sorted_words[:10]:
            print(f"   {word}: {count} раз")
        
        return dict(sorted_words)
    
    def _create_categories_from_data(self, product_series):
        """
        Создает категории на основе анализа реальных данных
        """
        keywords = self._analyze_product_keywords(product_series)
   
        category_patterns = {
            'плиты': ['плита', 'мдф', 'фанера', 'осп', 'дсп', 'древесноволокнистая'],
            'пиломатериалы': ['брус', 'доска', 'строганная', 'калиброванная', 'обрезная', 'пиломатериал'],
            'целлюлоза_бумага': ['целлюлоза', 'бумага', 'картон', 'крафт', 'гофрированный', 'офсетная'],
            'строительные_конструкции': ['домокомплект', 'стропильная', 'ферма', 'арка', 'колонна', 'балка'],
            'отделочные_материалы': ['вагонка', 'блок-хаус', 'планкен', 'имитация', 'террасная', 'пола'],
            'окна_двери': ['оконный', 'дверной', 'витраж', 'блоки', 'остекления', 'профиля'],
            'упаковка': ['гофротара', 'упаковка', 'ящики', 'тара'],
            'мебельные_изделия': ['мебельный', 'щит', 'царговые', 'лестница'],
            'прочее': ['отходы', 'брикет', 'монтаж', 'доставка', 'работы']
        }
        
        for category, base_words in category_patterns.items():
            extended_words = []
            for word, count in keywords.items():
                if any(base_word in word or word in base_word for base_word in base_words):
                    extended_words.append(word)
            
            category_patterns[category] = list(set(base_words + extended_words))
        
        self.product_categories = category_patterns
        return category_patterns
    
    def _smart_categorize_product(self, product_name):
        """
        Автоматическая категоризация на основе анализа сходства
        """
        product_lower = str(product_name).lower()
        
        if not self.product_categories:
            return 'прочее'
      
        category_scores = {}
        
        for category, keywords in self.product_categories.items():
            score = 0
            for keyword in keywords:
                if keyword in product_lower:
                    score += 2
                elif any(keyword in word or word in keyword for word in product_lower.split()):
                    score += 1
            
            category_scores[category] = score
        
        best_category = max(category_scores.items(), key=lambda x: x[1])
  
        return best_category[0] if best_category[1] > 0 else 'прочее'
    
    def load_data(self):
        """
        Загрузка и первоначальная обработка данных
        """
        self.df = pd.read_excel(self.file_path)\
       
        self.df.columns = [self._clean_column_name(col) for col in self.df.columns]
       
        for col in ['выручка_руб']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(
                    self.df[col].astype(str).str.replace('=E\d+\*D\d+', '', regex=True), 
                    errors='coerce'
                )
        
        return self.df
    
    def clean_data(self):
        """
        Очистка и подготовка данных
        """
        
        if self.df is None:
            self.load_data()
            
        self.processed_df = self.df.copy()
        
        numeric_columns = ['цена_руб', 'количество_шт', 'выручка_руб', 
                          'годовая_выручка_руб', 'годовая_прибыль_руб']
        
        for col in numeric_columns:
            if col in self.processed_df.columns:
                self.processed_df[col] = pd.to_numeric(self.processed_df[col], errors='coerce')
     
        text_columns = ['компания', 'продукция']
        for col in text_columns:
            if col in self.processed_df.columns:
                self.processed_df[col] = self.processed_df[col].astype(str).str.strip()
        
        return self.processed_df
    
    def enrich_data(self):
        """
        Обогащение данных новыми признаками
        """
        
        if self.processed_df is None:
            self.clean_data()
        
        self._create_categories_from_data(self.processed_df['продукция'])

        self.processed_df['категория_продукции'] = self.processed_df['продукция'].apply(
            self._smart_categorize_product
        )
        
        self.processed_df['год_нормализованный'] = self.processed_df['год'] - self.processed_df['год'].min()
        
        if 'выручка_руб' not in self.processed_df.columns or self.processed_df['выручка_руб'].isna().all():
            self.processed_df['выручка_руб'] = self.processed_df['цена_руб'] * self.processed_df['количество_шт']
 
        return self.processed_df
    
    def analyze_categorization_quality(self):
        """
        Анализ качества автоматической категоризации
        """
        if self.processed_df is None:
            self.enrich_data()

        category_stats = self.processed_df['категория_продукции'].value_counts()
        for category, count in category_stats.items():
            percentage = (count / len(self.processed_df)) * 100
    
        print("\nПРИМЕРЫ ПО КАТЕГОРИЯМ:")
        for category in category_stats.index:
            examples = self.processed_df[
                self.processed_df['категория_продукции'] == category
            ]['продукция'].unique()[:3]
            
            print(f"\n{category.upper()}:")
            for example in examples:
                print(f"   • {example}")
    
    def calculate_company_metrics(self):
        """
        Расчет метрик для ранжирования компаний
        """
        if self.processed_df is None:
            self.enrich_data()
        
        company_metrics = self.processed_df.groupby('компания').agg({
            'годовая_прибыль_руб': ['mean', 'std', 'min', 'max'],
            'годовая_выручка_руб': 'mean',
            'цена_руб': 'mean',
            'количество_шт': 'sum',
            'продукция': 'nunique',
            'категория_продукции': 'nunique'
        }).round(2)
        
        company_metrics.columns = ['_'.join(col).strip() for col in company_metrics.columns]
        company_metrics = company_metrics.reset_index()
    
        company_metrics['ранг_по_прибыли'] = company_metrics['годовая_прибыль_руб_mean'].rank(ascending=False)
        company_metrics['рентабельность'] = (company_metrics['годовая_прибыль_руб_mean'] / company_metrics['годовая_выручка_руб_mean'] * 100).round(2)
        company_metrics['стабильность_прибыли'] = (1 / (1 + company_metrics['годовая_прибыль_руб_std'].fillna(0))).round(3)
        
        company_metrics['композитный_рейтинг'] = (
                company_metrics['ранг_по_прибыли'] * 0.4 +
                company_metrics['стабильность_прибыли'].rank(pct=True) * 0.3 +
                company_metrics['продукция_nunique'].rank(pct=True) * 0.2 +
                company_metrics['категория_продукции_nunique'].rank(pct=True) * 0.1).round(3)

        company_metrics['финальный_ранг'] = company_metrics['композитный_рейтинг'].rank(ascending=True)

        return company_metrics.sort_values('финальный_ранг')

    
    def get_data_summary(self):
        """
        Получение сводки по данным
        """
        if self.processed_df is None:
            self.enrich_data()
        
        summary = {
            'total_rows': len(self.processed_df),
            'total_companies': self.processed_df['компания'].nunique(),
            'total_products': self.processed_df['продукция'].nunique(),
            'years': sorted(self.processed_df['год'].unique()),
            'categories_count': self.processed_df['категория_продукции'].nunique(),
            'price_stats': {
                'min': self.processed_df['цена_руб'].min(),
                'max': self.processed_df['цена_руб'].max(),
                'mean': self.processed_df['цена_руб'].mean()
            }
        }
        
        return summary
    
    def run_full_preprocessing(self):
        """
        Запуск полного цикла предобработки
        """
        self.load_data()
        self.clean_data()
        self.enrich_data()
      
        self.analyze_categorization_quality()
        
        summary = self.get_data_summary()
  
        print(f"Обработано: {summary['total_rows']} строк")
        print(f"Компаний: {summary['total_companies']}")
        print(f"Уникальных продуктов: {summary['total_products']}")
        print(f"Годы: {summary['years']}")
        print(f"Категорий: {summary['categories_count']}")
        
        return self.processed_df