############## IMPORTS #######################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

############## DATASET #######################
df = pd.read_csv('ads_full.csv', sep=';')

############## DASH ##########################
st.set_page_config(page_title="Dados Gerais",layout="wide",page_icon="report.ico")

st.sidebar.success("Selecione uma página acima")

st.markdown("<h1 style='text-align: center;'>DADOS GERAIS</h1>", unsafe_allow_html=True)

############ Seletores ######################
col_date, col_prod = st.columns(2)

with col_date:
    start_date, end_date = st.date_input('DATA INÍCIO - DATA FIM :', [datetime.today()-timedelta(30), datetime.today()])
    if start_date <= end_date:
        pass
    else:
        st.error('Error: End date must fall after start date.')

with col_prod:
    product = st.multiselect("PRODUTO",(list(df['product'].unique())),default=['DIP'])

df_filter = df[(df['product'].isin(product))
              & (pd.to_datetime(df['date_start'])>=pd.to_datetime(start_date))
              & (pd.to_datetime(df['date_start'])<=pd.to_datetime(end_date))
              ]

df['yearmonth'] = (df['year'].map(str) + df['month'].map(str)).map(int)

df_graph = df[(df['product'].isin(product))
              ]

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Gasto", value=df_filter['spend'].sum().round(2))
col2.metric(label="Nº Vendas", value=df_filter['purchase'].sum().round(2))
col3.metric(label="R$ Vendas", value=df_filter['purchase_value'].sum().round(2))
col4.metric(label="ROAS", value=(df_filter['purchase_value'].sum()/df_filter['spend'].sum()).round(2))

st.write("""
 Spend X Tempo
""")

spend_bar = alt.Chart(df_graph).mark_bar().encode(
    x=alt.X(field='yearmonth'),
    y=alt.Y(field='spend', aggregate='sum'),

).interactive()

purchase_line = alt.Chart(df_graph).mark_line(color='red').encode(
    x=alt.X(field='yearmonth'),
    y=alt.Y(field='purchase_value', aggregate='sum'),
).interactive()

st.altair_chart(spend_bar + purchase_line, use_container_width=True)