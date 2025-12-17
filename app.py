import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_processing import WoodIndustryDataProcessor
from analyzer import WoodIndustryAnalyzer

# ===================== НАСТРОЙКИ =====================
st.set_page_config(page_title="Деревообработка РФ", page_icon="evergreen_tree", layout="wide")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);}
    h1, h2, h3 {color: #1e4d2b; font-family: 'Segoe UI', sans-serif;}
    .big {font-size: 1.8em; font-weight: bold; color: #27ae60;}
</style>
""", unsafe_allow_html=True)

st.title("Деревообработка России 2022–2024")

# ===================== ЗАГРУЗКА ДАННЫХ =====================
@st.cache_data(show_spinner="Загружаем и обрабатываем данные...")
def load_data(path):
    processor = WoodIndustryDataProcessor(path)
    df = processor.run_full_preprocessing()
    metrics = processor.calculate_company_metrics()
    return df, processor, metrics

uploaded_file = st.file_uploader("Загрузите Excel-файл", type=["xlsx"])
file_path = "temp.xlsx" if uploaded_file else "продукция_выручка2.xlsx"

if uploaded_file:
    with open("temp.xlsx", "wb") as f:
        f.write(uploaded_file.getbuffer())

try:
    df, processor, company_metrics = load_data(file_path)
    analyzer = WoodIndustryAnalyzer(df)
    st.success("Данные успешно загружены и обработаны!")
except Exception as e:
    st.error("Ошибка загрузки данных")
    st.info("Положите файл **продукция_выручка2.xlsx** в папку с app.py или загрузите его выше")
    st.stop()

# ===================== ТОП-10 КОМПАНИЙ =====================
st.markdown("## ТОП-10 компаний по средней годовой прибыли")
top10 = company_metrics.nlargest(10, 'годовая_прибыль_руб_mean')[['компания', 'годовая_прибыль_руб_mean', 'рентабельность']].copy()
top10['годовая_прибыль_руб_mean'] = top10['годовая_прибыль_руб_mean'].apply(lambda x: f"{x:,.0f} ₽")
top10['рентабельность'] = top10['рентабельность'].apply(lambda x: f"{x:.1f}%")
top10 = top10.rename(columns={"компания": "Компания", "годовая_прибыль_руб_mean": "Прибыль в год", "рентабельность": "Рентабельность"})
st.dataframe(top10, use_container_width=True)

fig_ranking = analyzer.plot_company_ranking(company_metrics, top_n=10)
st.pyplot(fig_ranking)

# ===================== АНАЛИЗ ПО КЛЮЧЕВОМУ СЛОВУ И ПРОДУКТУ =====================
st.markdown("## Анализ по ключевому слову и конкретному продукту")

keyword = st.text_input("Введите ключевое слово для поиска продуктов (например, 'брус', 'доска', 'плита')", value="брус", key="keyword_input")

if st.button("Найти и проанализировать группу продуктов", type="primary", use_container_width=True):
    mask = df['продукция'].str.contains(keyword, case=False, na=False)
    group_df = df[mask].copy()

    if group_df.empty:
        st.warning(f"По слову '{keyword}' ничего не найдено")
    else:
        # Сохраняем данные группы в session_state
        st.session_state.group_df = group_df
        st.session_state.keyword = keyword
        st.success(f"Найдено {group_df['продукция'].nunique()} продуктов по слову '{keyword}'")

# Если группа уже найдена — показываем анализ
if 'group_df' in st.session_state:
    group_df = st.session_state.group_df
    keyword = st.session_state.keyword

    with st.expander(f"Группа продуктов по слову '{keyword}' ({group_df['продукция'].nunique()} шт)", expanded=True):
        # Графики группы
        try:
            fig_group = analyzer.plot_product_analysis(keyword)
            st.pyplot(fig_group)
        except Exception as e:
            st.warning("Графики группы недоступны")

        # Статистика группы
        group_stats = (group_df.groupby(['компания', 'год'])
                       .agg({'цена_руб': 'mean', 'количество_шт': 'sum', 'выручка_руб': 'sum'})
                       .round(0).astype(int)
                       .sort_values('выручка_руб', ascending=False))

        total_group = group_stats['выручка_руб'].sum()
        st.markdown(f"**Общая выручка по группе: <span class='big'>{total_group:,.0f} ₽</span>**", unsafe_allow_html=True)

        st.dataframe(
            group_stats.style.format({
                'цена_руб': '{:,.0f} ₽',
                'количество_шт': '{:,.0f} шт',
                'выручка_руб': '{:,.0f} ₽'
            }),
            use_container_width=True
        )

        csv_group = group_stats.to_csv(encoding='utf-8-sig')
        st.download_button("Скачать статистику группы", csv_group, f"группа_{keyword}.csv", "text/csv")

    # Выбор и анализ конкретного продукта
    products_found = sorted(group_df['продукция'].unique())
    selected_product = st.selectbox("Выберите конкретный продукт из группы", products_found, key="product_select")

    if st.button("Анализировать выбранный продукт", type="secondary", use_container_width=True):
        product_df = group_df[group_df['продукция'] == selected_product]

        # Графики продукта
        try:
            fig_product = analyzer.plot_product_analysis(selected_product)
            st.pyplot(fig_product)
        except Exception as e:
            st.warning("Графики продукта недоступны")

        # Статистика продукта
        prod_stats = (product_df.groupby(['компания', 'год'])
                      .agg({'цена_руб': 'mean', 'количество_шт': 'sum', 'выручка_руб': 'sum'})
                      .round(0).astype(int)
                      .sort_values('выручка_руб', ascending=False))

        total_prod = prod_stats['выручка_руб'].sum()
        st.markdown(f"**Выручка по «{selected_product}»: <span class='big'>{total_prod:,.0f} ₽</span>**", unsafe_allow_html=True)

        st.dataframe(
            prod_stats.style.format({
                'цена_руб': '{:,.0f} ₽',
                'количество_шт': '{:,.0f} шт',
                'выручка_руб': '{:,.0f} ₽'
            }),
            use_container_width=True
        )

        csv_prod = prod_stats.to_csv(encoding='utf-8-sig')
        st.download_button("Скачать статистику продукта", csv_prod, f"{selected_product}.csv", "text/csv")
