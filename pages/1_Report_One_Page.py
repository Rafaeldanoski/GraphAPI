############## IMPORTS #######################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

############## DATASET #######################
df = pd.read_csv('ads_full.csv', sep=';')

############## DASH ##########################
st.set_page_config(page_title="Report One Page",layout="wide",page_icon="report.ico")

st.sidebar.success("Selecione uma página acima")

st.write("""
# Report Processo de Tráfego
""")

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

st.write("""
# ETAPA 1
""")

st.write("""
### Conjunto de Anúncio: 02 - [Etapa 1: Teste de criativo] - Semelhantes a compradores 3%
""")

adset_test = ['02 - [Etapa 1: Teste de criativo] - Semelhantes a compradores 3%']
df_ad_test = df[df['adset_name'].isin(adset_test)
              & df['product'].isin(product)
              & (pd.to_datetime(df['date_start'])>=pd.to_datetime(start_date))
              & (pd.to_datetime(df['date_start'])<=pd.to_datetime(end_date))  
               ]

agg = df_ad_test.groupby(['name']).agg({'insta_link':'last','clicks':'sum', 'impressions':'sum', 'spend':'sum'})

agg['ctr'] = agg['clicks'] / agg['impressions'] * 100

for i in range(len(agg)):
    link = agg['insta_link'][i]
    agg['insta_link'][i] = f'<a href="{link}">'+agg.index[i]+'</a>'

agg.sort_values(by='ctr', ascending=False, inplace=True)
agg

for i in range(len(agg)):
    if agg['impressions'][i] < 10000:
        st.write(agg['insta_link'][i]+" --------> Dados insuficientes para análise - Impressões: "+ str(agg['impressions'][i]) + "/ Gasto: R$ " + str(round(agg['spend'][i],2)))
    elif agg['ctr'][i] >= 1.5:
        st.write(agg.index[i]+" --------> Promover à Etapa 2 - CTR: "+ str(round(agg['ctr'][i],2)))
    else:
        st.write(agg.index[i]+" --------> Pausar veiculação - CTR: "+ str(round(agg['ctr'][i],2)))