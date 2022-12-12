############## IMPORTS #######################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

############## DATASET #######################
df = pd.read_csv('ads_full.csv', sep=';')

############## DASH ##########################
st.set_page_config(page_title="Report One Page",layout="wide",page_icon="report.ico")

st.sidebar.success("Selecione uma página acima")

st.markdown("<h1 style='text-align: center;'>REPORT PROCESSO DE TRÁFEGO</h1>", unsafe_allow_html=True)

############ Seletores ######################
col_date, col_prod = st.columns(2)

with col_date:
    start_date, end_date = st.date_input('DATA INÍCIO - DATA FIM :', [datetime.today()-timedelta(7), datetime.today()])
    if start_date <= end_date:
        pass
    else:
        st.error('Error: End date must fall after start date.')

with col_prod:
    product = st.selectbox("PRODUTO",('DIP','ML','AUT','QUANT'))

############ ETAPA 1 ######################

st.markdown("<h1 style='text-align: center;'>ETAPA 1</h1>", unsafe_allow_html=True)

st.write("""
### Conjunto de Anúncio: 02 - [Etapa 1: Teste de criativo] - Semelhantes a compradores 3%
""")

adset_test = ['02 - [Etapa 1: Teste de criativo] - Semelhantes a compradores 3%']
df_ad_test = df[df['adset_name'].isin(adset_test)
              & df['product'].isin([product])
              & (pd.to_datetime(df['date_start'])>=pd.to_datetime(start_date))
              & (pd.to_datetime(df['date_start'])<=pd.to_datetime(end_date))
              & df['impressions'] > 0  
               ]

df_ad_test.reset_index(drop=True, inplace=True)

agg = df_ad_test.groupby(['name']).agg({'product':'last','insta_link':'last','clicks':'sum', 'impressions':'sum', 'spend':'sum'})

agg['ctr'] = agg['clicks'] / agg['impressions'] * 100

agg.sort_values(by='ctr', ascending=False, inplace=True)

st.write("##### - *Público personalizado:* "+str(df_ad_test['Público personalizado:'][0]))
st.write("##### - *Exceto Público personalizado:* "+str(df_ad_test['Exceto Público Personalizado:'][0]))
st.write("##### - *Idade:* "+str(df_ad_test['Idade:'][0]))
st.write("##### - *Posicionamentos:* "+str(df_ad_test['Posicionamentos:'][0]))
st.write("##### - *Gênero:* "+str(df_ad_test['Gênero:'][0]))
st.write("##### - *Pessoas que correspondem a:* "+str(df_ad_test['Pessoas que correspondem a:'][0]))
st.write("##### - *E também deve corresponder a:* "+str(df_ad_test['E também deve corresponder a:'][0]))
st.write("##### - *Excluir:* "+str(df_ad_test['Excluir:'][0]))

best = ['', 0]
for i in range(len(agg)):
    if (agg['ctr'][i] > best[1]) and (agg['impressions'][i] > 10000):
        best[0] = agg.index[i]
        best[1] = agg['ctr'][i]

for i in range(len(agg)):
    name = agg.index[i]
    link = agg['insta_link'][i]
    if agg['impressions'][i] < 10000:
        st.write(f"#### - ➖ [{name}]({link}) --------> Dados insuficientes para análise - Impressões: "+ str(agg['impressions'][i]) + "/ Gasto: R$ " + str(round(agg['spend'][i],2)))
    elif agg.index[i] == best[0]:
        st.write(f"#### - ✅ [{name}]({link}) --------> Promover à Etapa 2 - CTR: " + str(round(agg['ctr'][i],2)))
    else:
        st.write(f"#### - 🚫 [{name}]({link}) --------> Pausar veiculação - CTR: " + str(round(agg['ctr'][i],2)))


############ ETAPA 2 ######################

st.markdown("<h1 style='text-align: center;'>ETAPA 2</h1>", unsafe_allow_html=True)