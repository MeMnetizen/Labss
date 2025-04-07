import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    df = pd.read_csv('all_regions_combined.csv')
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
    df['week'] = pd.to_numeric(df['week'], errors='coerce').fillna(0).astype(int)
    df = df[(df['year'] != 0) & (df['week'] != 0)]
    return df

df = load_data()

if 'selected_index' not in st.session_state:
    st.session_state.selected_index = 0
if 'week_range' not in st.session_state:
    st.session_state.week_range = (1, 52)
if 'year_range' not in st.session_state:
    st.session_state.year_range = (df['year'].min(), df['year'].max())

with st.sidebar:
    st.title("Фільтри")
    selected_param = st.selectbox("Оберіть параметр", ['vci', 'tci', 'vhi'])
    oblasts = df['oblast'].unique()
    selected_oblast = st.selectbox("Оберіть область", oblasts)
    week_range = st.slider("Інтервал тижнів", 1, 52, (1, 52))
    year_range = st.slider("Інтервал років", df['year'].min(), df['year'].max(), (df['year'].min(), df['year'].max()))
    ascending = st.checkbox("Сортувати за зростанням")
    descending = st.checkbox("Сортувати за спаданням")

filtered_data = df[
    (df['week'].between(week_range[0], week_range[1])) &
    (df['year'].between(year_range[0], year_range[1])) &
    (df['oblast'] == selected_oblast)
]

if ascending and descending:
    st.warning("Оберіть лише один тип сортування!")
elif ascending:
    filtered_data = filtered_data.sort_values(by=selected_param, ascending=True)
elif descending:
    filtered_data = filtered_data.sort_values(by=selected_param, ascending=False)

tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння"])

with tab1:
    columns_to_show = ['year', 'week', 'oblast', selected_param]
    st.dataframe(filtered_data[columns_to_show])

with tab2:
    if not filtered_data.empty:
        pivot_table = filtered_data.pivot_table(
            index='year',
            columns='week',
            values=selected_param,
            aggfunc='mean'
        ).fillna(0)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(pivot_table, annot=False, cmap='viridis', ax=ax)
        ax.set_title(f'Теплова карта параметру {selected_param.upper()} для {selected_oblast} область')
        ax.set_xlabel("Тиждень")
        ax.set_ylabel("Рік")
        st.pyplot(fig)
    else:
        st.warning("Немає даних для відображення")

with tab3:
    compare_data = df[
        (df['week'].between(week_range[0], week_range[1])) &
        (df['year'].between(year_range[0], year_range[1]))
    ]
    
    if not compare_data.empty:
        avg_values = compare_data.groupby('oblast')[selected_param].mean().sort_values()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(avg_values.index, avg_values.values)
        ax.set_title(f'Середнє значення {selected_param.upper()} по областям')
        ax.set_xlabel("Область")
        ax.set_ylabel(f"Середній {selected_param.upper()}")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    else:
        st.warning("Немає даних для порівняння")