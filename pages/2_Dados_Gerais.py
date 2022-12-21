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
df_filter

st.write("""
 Spend X Tempo
""")

spend_line = alt.Chart(df).mark_bar().encode(
    x='month',
    y=alt.Y(field='spend', aggregate='sum'),

).interactive()

st.altair_chart(spend_line)