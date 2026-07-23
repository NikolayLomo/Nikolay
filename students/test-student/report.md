# Отчёт по Практическому занятию №1

**Студент:** Иванов Иван  
**Группа:** ИИ-201  

## Формируемые компетенции
- ПК-7.1 (ML-2.1)
- ПК-9.2 (PL-1.2)

## Цель
Освоить среду Google Colab и библиотеки Pandas, NumPy, Plotly.

## Ход выполнения
1. Загрузил датасет Iris.
2. Проверил данные на пропуски с помощью Pandas.
3. Построил scatter-plot через Plotly для визуализации.

```python
import pandas as pd
import plotly.express as px
df = pd.read_csv('iris.csv')
fig = px.scatter(df, x='sepal_length', y='sepal_width', color='species')
