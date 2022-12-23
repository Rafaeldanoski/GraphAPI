############## IMPORTS #######################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

############## DATASET #######################
df = pd.read_csv('ads_full.csv', sep=';')
df['yearmonth'] = (df['year'].map(str) + df['month'].map(str)).map(int)

############## DASH ##########################
st.set_page_config(page_title="Dados Gerais",layout="wide",page_icon="report.ico")

st.sidebar.success("Selecione uma página acima")

st.markdown("<h1 style='text-align: center;'>DADOS GERAIS</h1>", unsafe_allow_html=True)

############ Seletores ######################
col_date, col_prod = st.columns(2)

with col_date:
    start_date, end_date = st.date_input('DATA INÍCIO - DATA FIM :', [datetime.today()-timedelta(days=int(datetime.today().date().strftime("%d"))-1), datetime.today()])
    if start_date <= end_date:
        pass
    else:
        st.error('Error: End date must fall after start date.')

col_full_period, col_last7, col_last_month, col_empty3, col_empty4, col_full_products, col_empty6, col_empty7, col_empty8, col_empty9 = st.columns(10)
def reset_full_period():
    st.session_state['last7'] = False
    st.session_state['last_month'] = False

def reset_seven():
    st.session_state['full_period'] = False
    st.session_state['last_month'] = False

def reset_month():
    st.session_state['last7'] = False
    st.session_state['full_period'] = False

with col_full_period:
    full_period = st.checkbox('Todo o período', key='full_period', on_change=reset_full_period)
    if full_period:
        start_date, end_date = df['date_start'].min(), df['date_start'].max()

with col_last7:
    last7 = st.checkbox('Últimos 7 dias', key='last7', on_change=reset_seven)
    if last7:
        start_date, end_date = datetime.today()-timedelta(7), datetime.today()

with col_last_month:
    last_month = st.checkbox('Últimos 30 dias', key='last_month', on_change=reset_month)
    if last_month:
        start_date, end_date = datetime.today()-timedelta(30), datetime.today()

def set_full_products():
    st.session_state['multiselect_product'] = list(df['product'].unique())

with col_prod:
    product = st.multiselect("PRODUTO",(list(df['product'].unique())), default=['DIP'], key='multiselect_product')

with col_full_products:
    full_prods = st.button('Todos os produtos', key='full_prod', on_click=set_full_products)



df_filter = df[(df['product'].isin(product))
              & (pd.to_datetime(df['date_start'])>=pd.to_datetime(start_date))
              & (pd.to_datetime(df['date_start'])<=pd.to_datetime(end_date))
              ]

df_graph = df[(df['product'].isin(product))
              ]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Gasto", value=df_filter['spend'].sum().round(2))
col2.metric(label="Nº Vendas", value=df_filter['purchase'].sum().round(2))
col3.metric(label="R$ Vendas", value=df_filter['purchase_value'].sum().round(2))
col4.metric(label="Lucro", value=(df_filter['purchase_value'].sum() - df_filter['spend'].sum()).round(2))
col5.metric(label="ROAS", value=(df_filter['purchase_value'].sum()/df_filter['spend'].sum()).round(2))

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