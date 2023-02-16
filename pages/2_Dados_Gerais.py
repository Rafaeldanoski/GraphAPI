############## IMPORTS #######################
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
import warnings
warnings.filterwarnings("ignore")

############## DASH ##########################
st.set_page_config(page_title="Dados Gerais",layout="wide",page_icon="report.ico")

st.sidebar.success("Selecione uma página acima")

st.markdown("<h1 style='text-align: center;'>DADOS GERAIS</h1>", unsafe_allow_html=True)

############## DATASET #######################
@st.cache(allow_output_mutation=True)
def load_data(url):
    return pd.read_csv(url)

df = load_data('https://docs.google.com/spreadsheets/d/e/2PACX-1vTBlGmOezNusSw2dRbZAT-ALjJXO0hMkSOlXBdfu76ZzkMIa2HIa62-29iL7yMNEhr-lqV6im8cKIqF/pub?output=csv')

df['yearmonth'] = [(str(df['year'][x]) + format(df['month'][x], '02d')) for x in range(len(df))]

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
              & (pd.to_datetime(df['date_start'], errors='coerce')>=pd.to_datetime(start_date))
              & (pd.to_datetime(df['date_start'], errors='coerce')<=pd.to_datetime(end_date))
              ]

df_graph = df[(df['product'].isin(product))
              ]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Gasto", value=df_filter['spend'].sum().round(2))
col1.metric(label="CTR", value=(df_filter['link_clicks'].sum()/df_filter['impressions'].sum()).round(4)*100)

col2.metric(label="Nº Vendas", value=df_filter['purchase'].sum().round(2))
col2.metric(label="CPC", value=(df_filter['spend'].sum()/df_filter['link_clicks'].sum()).round(2))

col3.metric(label="R$ Vendas", value=df_filter['purchase_value'].sum().round(2))
col3.metric(label="CPM", value=(df_filter['spend'].sum()/df_filter['impressions'].sum()).round(2)*1000)

col4.metric(label="Lucro", value=(df_filter['purchase_value'].sum() - df_filter['spend'].sum()).round(2))
col4.metric(label="Frequência", value=(df_filter['impressions'].sum()/df_filter['reach'].sum()).round(2))

col5.metric(label="ROAS", value=(df_filter['purchase_value'].sum()/df_filter['spend'].sum()).round(2))
col5.metric(label="CPA", value=(df_filter['spend'].sum()/df_filter['purchase'].sum()).round(2))

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Vendas", "CTR", "CPC", "CPM", "CPA"])

with tab1:
    st.write("""
    Vendas
    """)

    sales_line = alt.Chart(df_filter).mark_line(color='red').encode(
        x=alt.X(field='date_start'),
        y=alt.Y(field='purchase', aggregate='sum'),
    ).interactive()

    st.altair_chart(sales_line, use_container_width=True)

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

with tab2:
    df_graph['ctr_link'] = (df_graph['link_clicks'] / df_graph['impressions']) * 100
    st.write("""
    CTR
    """)

    ctr_line = alt.Chart(df_graph).mark_line(color='red').encode(
        x=alt.X(field='yearmonth'),
        y=alt.Y(field='ctr_link', aggregate='mean'),
    ).interactive()

    st.altair_chart(ctr_line, use_container_width=True)

with tab3:
    df_graph['cpc_link'] = (df_graph['spend'] / df_graph['link_clicks'])
    df_graph.replace([np.inf, -np.inf], 0, inplace=True)
    st.write("""
    CPC
    """)

    cpc_line = alt.Chart(df_graph).mark_line(color='red').encode(
        x=alt.X(field='yearmonth'),
        y=alt.Y(field='cpc_link', aggregate='mean'),
    ).interactive()

    st.altair_chart(cpc_line, use_container_width=True)

with tab4:
    st.write("""
    CPM
    """)

    cpc_line = alt.Chart(df_graph).mark_line(color='red').encode(
        x=alt.X(field='yearmonth'),
        y=alt.Y(field='cpm', aggregate='mean'),
    ).interactive()

    st.altair_chart(cpc_line, use_container_width=True)

with tab5:
    df_graph['cpa_acc'] = (df_graph.groupby(['yearmonth'])['spend'].cumsum() / df_graph.groupby(['yearmonth'])['purchase'].cumsum()).round(2)
    df_graph.replace([np.inf, -np.inf], 0, inplace=True)
    agg_graph = df_graph.groupby(['yearmonth']).agg({'cpa_acc':'last', 'yearmonth':'last'})
    st.write("""
    CPA
    """)

    cpa_line = alt.Chart(agg_graph).mark_line(color='red').encode(
        x=alt.X(field='yearmonth'),
        y=alt.Y(field='cpa_acc',sort='-y'),
    ).interactive()

    st.altair_chart(cpa_line, use_container_width=True)