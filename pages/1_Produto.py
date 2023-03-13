############## IMPORTS #######################
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
import warnings
warnings.filterwarnings("ignore")

############## DASH ##########################
st.set_page_config(page_title="Produto",layout="wide",page_icon="favicon.ico")

st.sidebar.success("Selecione uma página acima")

st.markdown("<h1 style='text-align: center;'>DADOS PRODUTOS</h1>", unsafe_allow_html=True)

############## DATASET #######################
@st.experimental_memo
def load_data(url):
    return pd.read_csv(url)

df = load_data('https://docs.google.com/spreadsheets/d/e/2PACX-1vTBlGmOezNusSw2dRbZAT-ALjJXO0hMkSOlXBdfu76ZzkMIa2HIa62-29iL7yMNEhr-lqV6im8cKIqF/pub?output=csv')

############ Seletores ######################
col_date, col_kind, col_prod, col_adset, col_ad = st.columns(5)

with col_kind:
   kind = st.multiselect("TIPO",(list(df['kind'].unique())), key='kind')
if st.session_state['kind']==[]:
    kind = df['kind'].unique()
if st.session_state['kind']==['REMARKETING']:
    kind = ['QUA', 'REMARKETING']

with col_prod:
   product = st.multiselect("PRODUTO",(list(df['product'].unique())), key='product')
if st.session_state['product']==[]:
    product = df['product'].unique()
   
with col_date:
    start_date, end_date = st.date_input('DATA INÍCIO - DATA FIM :', [datetime.today()-timedelta(days=int(datetime.today().date().strftime("%d"))-1), datetime.today()])
    if start_date <= end_date:
        pass
    else:
        st.error('Error: End date must fall after start date.')

col_full_period, col_last7, col_last_month, col_empty4, col_empty5, col_empty6, col_empty7, col_empty8, col_empty9, col_empty10, col_empty11 = st.columns(11)
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

df_pre_filter = df[(df['product'].isin(product)) 
                & (pd.to_datetime(df['date_start'], errors='coerce')>=pd.to_datetime(start_date))
                & (pd.to_datetime(df['date_start'], errors='coerce')<=pd.to_datetime(end_date))
                & (df['kind'].isin(kind))
                ]


with col_adset:
    adset = st.multiselect("ADSET",(list(df_pre_filter['adset_name'].unique())), key='adset')
if st.session_state['adset']==[]:
    adset = df_pre_filter['adset_name'].unique()
    

with col_ad:
    ad = st.multiselect("AD",(list(df_pre_filter['name'].unique())), key='ad')
if st.session_state['ad']==[]:
    ad = df_pre_filter['name'].unique()


########### Totais ##########################
df_filter = df_pre_filter[(df_pre_filter['adset_name'].isin(adset))
            & (df_pre_filter['name'].isin(ad))
            ]
            

agg_full = df_filter.groupby(['product','kind','adset_name']).agg({'date_start':'nunique', 'spend':'sum', 'purchase':'sum', 'impressions':'sum', 'engagement':'sum',
                                                                   'link_clicks':'sum' , 'reach':'sum', 'purchase_value':'sum'})

agg_full.rename(columns={'date_start':'dias'}, inplace=True)
agg_full['custo/eng'] = agg_full['spend'] / agg_full['engagement']
agg_full['frequencia'] = agg_full['impressions'] / agg_full['reach']
agg_full['cpm'] = agg_full['spend'] / agg_full['impressions'] * 1000
agg_full['ctr'] = agg_full['link_clicks'] / agg_full['impressions'] * 100
agg_full['cpc'] = agg_full['spend'] / agg_full['link_clicks']

agg_full.replace([np.inf, -np.inf], 0, inplace=True)

agg_full = agg_full.drop(['purchase_value','reach'], axis=1)
agg_full = agg_full[['dias','spend','purchase','engagement','custo/eng','impressions','link_clicks','cpm','ctr','cpc','frequencia']]
st.dataframe(agg_full)

############ Analítico ####################
col_classify, col_asc, col_empty2, col_empty3 = st.columns(4)
with col_classify:
    classify = st.selectbox(
        'CLASSIFICADOR',
        ('ctr',  'cpm', 'cpc', 'spend', 'link_clicks','impressions','purchase', 'frequencia', 'engagement', 'custo/eng'))

with col_asc:
    asc = st.selectbox(
        '',
        ('Descendente', 'Ascendente'))

if asc == 'Ascendente':
    ascending=True
else:
    ascending=False



agg = df_filter.groupby('name').agg({'thumb_link':'last','insta_link':'last','date_start':'nunique','spend':'sum', 'purchase':'sum', 'engagement':'sum','impressions':'sum', 
                                     'link_clicks':'sum', 'reach':'sum', 'purchase_value':'sum'})

agg.rename(columns={'date_start':'dias', 'insta_link':'Anúncio', 'thumb_link':''}, inplace=True)
agg['custo/eng'] = agg['spend'] / agg['engagement']
agg['frequencia'] = agg['impressions'] / agg['reach']
agg['cpm'] = agg['spend'] / agg['impressions'] * 1000
agg['ctr'] = agg['link_clicks'] / agg['impressions'] * 100
agg['cpc'] = agg['spend'] / agg['link_clicks']

agg.replace([np.inf, -np.inf], 0, inplace=True)

for i in range(len(agg)):
    link = agg['Anúncio'][i]
    agg['Anúncio'][i] = f'<a target="_blank" href="{link}">'+agg.index[i]+'</a>'
    
    agg[''][i] = "<img src='" + agg[''][i] + f"""' 
    style='display:block;margin-left:auto;margin-right:auto;width:{80}px;border:0;'><div style='text-align:center'>"""


agg.sort_values(by=classify, ascending=ascending, inplace=True)
agg = agg.drop(['purchase_value','reach'], axis=1).round(2)
agg = agg[['','Anúncio','dias','spend','purchase','engagement','custo/eng','impressions', 'link_clicks','cpm','ctr','cpc','frequencia']]

def color_negative(v, color):
    return f"color: {color};" if v < 1 else None

def color_negative2(v, color):
    return f"color: {color};" if v > 1 else None

def color_negative3(v, color):
    return f"color: {color};" if v > 10 else None

df_view = agg.style.applymap(color_negative, color='red', 
                              subset=['ctr']).hide_index()

df_view.applymap(color_negative2, color='red', 
                              subset=['cpc']).hide_index()

df_view.applymap(color_negative3, color='red', 
                              subset=['cpm']).hide_index()

f = {'ctr':'{:.2f}',
     'ctr_total':'{:.2f}',
     'cpm':'{:.2f}',
     'cpc':'{:.2f}',
     'custo/eng':'{:.2f}',
     'cpc_total':'{:.2f}',
     'roas':'{:.2f}',
     'cpa':'{:.2f}',
     'score':'{:.2f}',
     'spend':'{:.2f}',
     'ctr_delta':'{:.2f}',
     'frequencia':'{:.2f}',
     'video_25' :'{:.0f}',
     'video_50' :'{:.0f}',
     'video_75' :'{:.0f}',
     'purchase' :'{:.0f}',
     'link_clicks' :'{:.0f}'}
df_view.format(f)

st.write(df_view.to_html(escape=False, index=False), unsafe_allow_html=True)

###################### KPI por anúncio #######################

st.write("""
 # KPI's por anúncio
""")

option = st.selectbox(
    "Anúncio",
    (agg.index))

df_graph = df[(df['name']==option)
            & (df['product'].isin(product))
            & df['adset_name'].isin(adset)
            ]

tab_ctr, tab_cpc, tab_spend, tab_cpm, tab_frequency, tab_impressions, tab_clicks = st.tabs(["CTR", "CPC", "GASTO", "CPM", "FREQUÊNCIA", "IMPRESSÕES", "CLICKS"])

with tab_ctr:
    st.write("""
    CTR X Tempo
    """)

    ctr_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y='ctr_link_acc',
        color='adset_name:N',
        strokeDash='month'
    )

    st.altair_chart(ctr_line.interactive(), use_container_width=True)

with tab_cpc:
    st.write("""
    CPC X Tempo
    """)

    cpc_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y='cpc_link_acc',
        color='adset_name:N',
        strokeDash='month'
    )

    st.altair_chart(cpc_line.interactive(), use_container_width=True)

with tab_spend:
    st.write("""
    Spend X Tempo
    """)

    spend_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y='spend_acc',
        color='adset_name:N',
        strokeDash='month'
    ).interactive()

    st.altair_chart(spend_line, use_container_width=True)

with tab_cpm:
    st.write("""
    CPM X Tempo
    """)

    cpm_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y=alt.Y('cpm_acc'),
        color='adset_name:N',
        strokeDash='month'
    ).interactive()

    st.altair_chart(cpm_line, use_container_width=True)

with tab_frequency:
    st.write("""
    Frequency X Tempo
    """)

    frequency_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y=alt.Y('frequency_acc'),
        color='adset_name:N',
        strokeDash='month'
    ).interactive()

    st.altair_chart(frequency_line, use_container_width=True)

with tab_impressions:
    st.write("""
    Impressions X Tempo
    """)

    impressions_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y=alt.Y('impressions_acc'),
        color='adset_name:N',
        strokeDash='month'
    ).interactive()

    st.altair_chart(impressions_line, use_container_width=True)

with tab_clicks:
    st.write("""
    Clicks no link X Tempo
    """)

    clicks_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
        x='date_start',
        y=alt.Y('link_clicks_acc'),
        color='adset_name:N',
        strokeDash='month'
    ).interactive()

    st.altair_chart(clicks_line, use_container_width=True)
