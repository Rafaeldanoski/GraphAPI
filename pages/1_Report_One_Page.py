############## IMPORTS #######################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

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
    product = st.selectbox("PRODUTO",('DIP','ML','AUT','QUA'))

############ ETAPA 1 ######################

st.markdown("<h1 style='text-align: center;'>ETAPA 1</h1>", unsafe_allow_html=True)

df_filter = df[(df['product'].isin([product]))
              & (pd.to_datetime(df['date_start'])>=pd.to_datetime(start_date))
              & (pd.to_datetime(df['date_start'])<=pd.to_datetime(end_date))
              & (df['impressions'] > 0)
               ]            
df_filter.reset_index(drop=True, inplace=True)

st.write("""
### Conjunto de Anúncio: 02 - [Etapa 1: Teste de criativo] - Semelhantes a compradores 3%
""")

adset_test = ['02 - [Etapa 1: Teste de criativo] - Semelhantes a compradores 3%','02 -  [Etapa 1: Teste de criativo] - Interesses em trader']
df_ad_test = df_filter[df_filter['adset_name'].isin(adset_test)
               ]

df_ad_test.reset_index(drop=True, inplace=True)

agg = df_ad_test.groupby(['name']).agg({'product':'last','insta_link':'last','clicks':'sum', 'impressions':'sum', 'spend':'sum'})

agg['ctr'] = agg['clicks'] / agg['impressions'] * 100

agg.sort_values(by='ctr', ascending=False, inplace=True)

with st.expander('INFORMAÇÕES DO PÚBLICO'):
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

import re
df_filter['etapa'] = ""
for i in range(len(df_filter['adset_name'])):
    a_string = df_filter['adset_name'][i]
    result = re.findall(r"\[([][A-Za-z0-9_: ]+)\]", a_string)
    try:
        df_filter['etapa'][i] = result[0]
    except:
        df_filter['etapa'][i] = result

df_pub_test = df_filter[(df_filter['etapa'] == 'Etapa 2: Teste de publico')
               ]            
df_pub_test.reset_index(drop=True, inplace=True)

agg_pub_test = df_pub_test.groupby(['name','adset_name']).agg({'name':'last','adset_name':'last','insta_link':'last','clicks':'sum', 'impressions':'sum', 'spend':'sum'})

agg_pub_test['ctr'] = agg_pub_test['clicks'] / agg_pub_test['impressions'] * 100

agg_pub_test.sort_values(by='ctr', ascending=False, inplace=True)

for a in range(len(agg_pub_test['name'].unique())):
    agg_pub_test_write = agg_pub_test[agg_pub_test['name']==(agg_pub_test['name'].unique()[a])
                                     ]

    st.write(f"""
    ### Anúncio: {agg_pub_test['name'].unique()[a]}
    """)

    best_adset = ['', 0]
    for i in range(len(agg_pub_test_write)):
        if (agg_pub_test_write['ctr'][i] > best_adset[1]) and (agg_pub_test_write['impressions'][i] > 10000):
            best_adset[0] = agg_pub_test_write.index[i]
            best_adset[1] = agg_pub_test_write['ctr'][i]

    for i in range(len(agg_pub_test_write)):
        name = agg_pub_test_write['adset_name'][i]
        if agg_pub_test_write['impressions'][i] < 10000:
            st.write(f"#### - ➖ {name} --------> Dados insuficientes para análise - Impressões: "+ str(agg_pub_test_write['impressions'][i]) + "/ Gasto: R$ " + str(round(agg_pub_test_write['spend'][i],2)))
        elif (agg_pub_test_write.index[i] == best_adset[0]) and (agg_pub_test_write.ctr[i] >= 1.5):
            st.write(f"#### - ✅ {name} --------> Promover à Etapa 3 - CTR: " + str(round(agg_pub_test_write['ctr'][i],2)))
        else:
            st.write(f"#### - 🚫 {name} --------> Pausar veiculação - CTR: " + str(round(agg_pub_test_write['ctr'][i],2)))

    st.write("")



############ ETAPA 3 ######################

st.markdown("<h1 style='text-align: center;'>ETAPA 3</h1>", unsafe_allow_html=True)

step_prod = ['Etapa 3: Escala']

df_ad_prod = df[(df['product'].isin([product]))
              & (df['impressions'] > 0)
              & (pd.to_datetime(df['date_start'])>='2022-12-01')
               ]
df_ad_prod.reset_index(drop=True, inplace=True)

df_ad_prod['etapa'] = ""
for i in range(len(df_ad_prod['adset_name'])):
    a_string = df_ad_prod['adset_name'][i]
    result = re.findall(r"\[([][A-Za-z0-9_: ]+)\]", a_string)
    try:
        df_ad_prod['etapa'][i] = result[0]
    except:
        df_ad_prod['etapa'][i] = result

df_ad_prod = df_ad_prod[df_ad_prod['etapa'].isin(step_prod)]

df_ad_prod.reset_index(drop=True, inplace=True)

for g in range(len(df_ad_prod['name'].unique())):

    st.write(f"""
    ### Anúncio: {df_ad_prod['name'].unique()[g]}
    """)

    with st.expander('INFORMAÇÕES DO PÚBLICO'):
        st.write("##### - *Público personalizado:* "+str(df_ad_prod['Público personalizado:'][0]))
        st.write("##### - *Exceto Público personalizado:* "+str(df_ad_prod['Exceto Público Personalizado:'][0]))
        st.write("##### - *Idade:* "+str(df_ad_prod['Idade:'][0]))
        st.write("##### - *Posicionamentos:* "+str(df_ad_prod['Posicionamentos:'][0]))
        st.write("##### - *Gênero:* "+str(df_ad_prod['Gênero:'][0]))
        st.write("##### - *Pessoas que correspondem a:* "+str(df_ad_prod['Pessoas que correspondem a:'][0]))
        st.write("##### - *E também deve corresponder a:* "+str(df_ad_prod['E também deve corresponder a:'][0]))
        st.write("##### - *Excluir:* "+str(df_ad_prod['Excluir:'][0]))

    df_line = df_ad_prod[df_ad_prod['name']==df_ad_prod['name'].unique()[g]]

    ctr_line = alt.Chart(df_line).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
    x='date_start',
    y='ctr_acc',
    strokeDash='month'
    )

    st.altair_chart(ctr_line.interactive(), use_container_width=True)