############## IMPORTS #######################
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
import warnings
warnings.filterwarnings("ignore")

############## DASH ##########################
st.set_page_config(page_title="DashCopy",layout="wide",page_icon="favicon.ico")

st.sidebar.success("Selecione uma página acima")

st.write("""
# Dash Copy
""")

############## DATASET #######################
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

df = load_data('https://docs.google.com/spreadsheets/d/e/2PACX-1vTBlGmOezNusSw2dRbZAT-ALjJXO0hMkSOlXBdfu76ZzkMIa2HIa62-29iL7yMNEhr-lqV6im8cKIqF/pub?output=csv')

d = (datetime.today() - pd.to_datetime(df['date_start'].max(),errors='coerce')).days
if d >= 2:
    from graph_api import *
    fb_api = open("tokens/fb_token").read()
    ad_acc = "3120164588217844"
    graph = GraphAPI(ad_acc, fb_api)
    graph.updateAdsData()


############ Seletores ######################
col1, col2, col3, col4 = st.columns(4)

with col1:
   temp = st.multiselect("TEMPERATURA",(list(df['TEMPERATURA'].unique())),'FRIO')

with col2:
   product = st.multiselect("PRODUTO",(list(df['product'].unique())),default=['DIP'])

with col3:
   kind = st.multiselect("TIPO",(list(df['kind'].unique())),default=['ESCALA'])

with col4:
   objective = st.multiselect("OBJETIVO",(list(df['objective'].unique())),default=['CONVERSIONS'])
   

df_pre_filter = df[(df['product'].isin(product)) 
                & (df['kind'].isin(kind)) 
                & df['TEMPERATURA'].isin(temp)
                ]


adset = st.checkbox('ADSET')
if adset:
    adset = st.multiselect("ADSET",(list(df_pre_filter['adset_name'].unique())))
else:
    adset = list(df_pre_filter['adset_name'].unique())

ad = st.checkbox('AD')
if ad:
    ad = st.multiselect("AD",(list(df_pre_filter['name'].unique())))
else:
    ad = list(df_pre_filter['name'].unique())

col_date, col_empty, col_empty2, col_empty3 = st.columns(4)
with col_date:
    start_date, end_date = st.date_input('DATA INÍCIO - DATA FIM :', [datetime.today()-timedelta(days=int(datetime.today().date().strftime("%d"))-1), datetime.today()])
    if start_date <= end_date:
        pass
    else:
        st.error('Error: End date must fall after start date.')

col_full_period, col_last7, col_last_month, col_empty3, col_empty4, col_empty5, col_empty6, col_empty7, col_empty8 = st.columns(9)
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




########### Totais ##########################
df_filter = df[(df['product'].isin(product)) 
            & (df['kind'].isin(kind)) 
            & (pd.to_datetime(df['date_start'], errors='coerce')>=pd.to_datetime(start_date))
            & (pd.to_datetime(df['date_start'], errors='coerce')<=pd.to_datetime(end_date))
            & df['TEMPERATURA'].isin(temp)
            & df['adset_name'].isin(adset)
            & df['name'].isin(ad)
            ]
            

agg_full = df_filter.groupby(['product','kind','adset_name']).agg({'date_start':'nunique','clicks':'sum','link_clicks':'sum' ,'impressions':'sum', 'reach':'sum','spend':'sum', 
                                                                   'purchase_value':'sum','purchase':'sum','ctr_acc':'first','video_25':'sum','video_50':'sum','video_75':'sum'})

agg_full.rename(columns={'date_start':'dias'}, inplace=True)
agg_full['frequency'] = agg_full['impressions'] / agg_full['reach']
agg_full['ctr_total'] = agg_full['clicks'] / agg_full['impressions'] * 100
agg_full['ctr'] = agg_full['link_clicks'] / agg_full['impressions'] * 100
agg_full['cpm'] = agg_full['spend'] / agg_full['impressions'] * 1000
agg_full['roas'] = agg_full['purchase_value'] / agg_full['spend']
agg_full['cpc_total'] = agg_full['spend'] / agg_full['clicks']
agg_full['cpc'] = agg_full['spend'] / agg_full['link_clicks']
agg_full['cpa'] = agg_full['spend'] / agg_full['purchase']
#agg_full['score'] = agg_full['ctr'] * agg_full['clicks']
#agg_full['ctr_delta'] = ((agg_full['ctr'] / agg_full['ctr_acc']) - 1) * 100

agg_full.replace([np.inf, -np.inf], 0, inplace=True)

agg_full = agg_full.drop(['purchase_value', 'ctr_acc','reach'], axis=1)
st.dataframe(agg_full, use_container_width=True)

############ Analítico ####################
col_classify, col_asc, col_empty2, col_empty3 = st.columns(4)
with col_classify:
    classify = st.selectbox(
        'CLASSIFICADOR',
        ('ctr', 'ctr_total', 'cpm', 'cpc_total', 'cpc', 'spend','clicks','link_clicks','impressions','purchase'))

with col_asc:
    asc = st.selectbox(
        '',
        ('Ascendente', 'Descendente'))

if asc == 'Ascendente':
    ascending=True
else:
    ascending=False



agg = df_filter.groupby('name').agg({'thumb_link':'last','insta_link':'last','date_start':'nunique','clicks':'sum','link_clicks':'sum','impressions':'sum', 
                                     'reach':'sum','spend':'sum', 'purchase_value':'sum', 'purchase':'sum','ctr_acc':'first','video_25':'sum','video_50':'sum','video_75':'sum'})

agg.rename(columns={'date_start':'dias', 'insta_link':'Anúncio', 'thumb_link':''}, inplace=True)
agg['frequency'] = agg['impressions'] / agg['reach']
agg['ctr_total'] = agg['clicks'] / agg['impressions'] * 100
agg['ctr'] = agg['link_clicks'] / agg['impressions'] * 100
agg['cpm'] = agg['spend'] / agg['impressions'] * 1000
agg['roas'] = agg['purchase_value'] / agg['spend']
agg['cpc_total'] = agg['spend'] / agg['clicks']
agg['cpc'] = agg['spend'] / agg['link_clicks']
agg['cpa'] = agg['spend'] / agg['purchase']
#agg['score'] = agg['ctr'] * agg['clicks']
#agg['ctr_delta'] = ((agg['ctr'] / agg['ctr_acc']) - 1) * 100

agg.replace([np.inf, -np.inf], 0, inplace=True)

for i in range(len(agg)):
    link = agg['Anúncio'][i]
    agg['Anúncio'][i] = f'<a target="_blank" href="{link}">'+agg.index[i]+'</a>'
    
    agg[''][i] = "<img src='" + agg[''][i] + f"""' 
    style='display:block;margin-left:auto;margin-right:auto;width:{80}px;border:0;'><div style='text-align:center'>"""


agg.sort_values(by=classify, ascending=ascending, inplace=True)
agg = agg.drop(['purchase_value', 'ctr_acc','reach'], axis=1).round(2)

def color_negative(v, color):
    return f"color: {color};" if v < 1 else None

def color_negative2(v, color):
    return f"color: {color};" if v > 1 else None

def color_negative3(v, color):
    return f"color: {color};" if v > 15 else None

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
     'cpc_total':'{:.2f}',
     'roas':'{:.2f}',
     'cpa':'{:.2f}',
     'score':'{:.2f}',
     'spend':'{:.2f}',
     'ctr_delta':'{:.2f}',
     'frequency':'{:.2f}',
     'video_25' :'{:.0f}',
     'video_50' :'{:.0f}',
     'video_75' :'{:.0f}',
     'purchase' :'{:.0f}',
     'link_clicks' :'{:.0f}'}
df_view.format(f)

st.write(df_view.to_html(escape=False, index=False), unsafe_allow_html=True)

########################## Gráficos ######################
col_violin, col_scatter = st.columns(2)

with col_violin:
    st.write("""
    CTR
    """)

    violin_plot = alt.Chart(agg).transform_density(
        'ctr',
        as_=['ctr', 'density'],
        extent=[-0.5, 2.5]
    ).mark_area(orient='horizontal').encode(
        y='ctr',
        x=alt.X(
            'density:Q',
            stack='center',
            impute=None,
            title=None,
            axis=alt.Axis(labels=False, values=[0],grid=False, ticks=True),
        ),
        column=alt.Column(
            header=alt.Header(
                titleOrient='bottom',
                labelOrient='bottom',
                labelPadding=0,
            ),
        )
    ).properties(
        width=0
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    ).interactive()


    st.altair_chart(violin_plot, use_container_width=False)
    
with col_scatter:
    st.write("""
    CTR X CPM
    """)

    scatter_full = alt.Chart(agg).mark_point().encode(
        x='cpm',
        y='ctr'
    ).interactive()

    st.altair_chart(scatter_full, use_container_width=False)


###################### KPI por anúncio #######################
st.write("""
 # KPI's por anúncio
""")

option = st.selectbox(
    "Anúncio",
    (agg.index))

df_graph = df[(df['name']==option)
            & (df['product'].isin(product))
            & (df['kind'].isin(kind))
            & df['TEMPERATURA'].isin(temp)
            & df['adset_name'].isin(adset)
            ]

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

st.write("""
 ROAS X Tempo
""")

roas_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
    x='date_start',
    y=alt.Y('purchase_roas_acc'),
    color='adset_name:N',
    strokeDash='month'
).interactive()

st.altair_chart(roas_line, use_container_width=True)


st.write("""
 CTR X CPM
""")

scatter = alt.Chart(df_graph).mark_point().encode(
    x='cpm_acc',
    y='ctr_link_acc'
).interactive()

st.altair_chart(scatter, use_container_width=False)