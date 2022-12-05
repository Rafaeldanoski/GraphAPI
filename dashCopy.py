############## IMPORTS #######################
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt

############## DATASET #######################
df = pd.read_csv('ads_full.csv', sep=';')

############## DASH ##########################
st.set_page_config(page_title="DashCopy",layout="wide",page_icon="favicon.ico")

st.write("""
# Dash Copy
""")

############ Seletores ######################
temp = st.multiselect("TEMPERATURA",(list(df['TEMPERATURA'].unique())),'FRIO')
product = st.multiselect("PRODUTO",(list(df['product'].unique())),default=['DIP'])
kind = st.multiselect("TIPO",(list(df['kind'].unique())),default=['ESCALA'])
objective = st.multiselect("OBJETIVO",(list(df['objective'].unique())),default=['CONVERSIONS'])

start_date, end_date = st.date_input('start date  - end date :', [datetime.today()-timedelta(30), datetime.today()])
if start_date <= end_date:
    pass
else:
    st.error('Error: End date must fall after start date.')

########### Totais ##########################
df_filter = df[(df['product'].isin(product)) 
            & (df['kind'].isin(kind)) 
            & (pd.to_datetime(df['date_start'])>=pd.to_datetime(start_date))
            & (pd.to_datetime(df['date_start'])<=pd.to_datetime(end_date))
            & df['TEMPERATURA'].isin(temp)
            ]
            

agg_full = df_filter.groupby(['product','kind']).agg({'clicks':'sum', 'impressions':'sum', 'reach':'sum','spend':'sum', 'purchase_value':'sum', 
                                     'purchase':'sum','ctr_acc':'first','video_25':'sum','video_50':'sum','video_75':'sum'})

agg_full['frequency'] = agg_full['impressions'] / agg_full['reach']
agg_full['ctr'] = agg_full['clicks'] / agg_full['impressions'] * 100
agg_full['cpm'] = agg_full['spend'] / agg_full['impressions'] * 1000
agg_full['roas'] = agg_full['purchase_value'] / agg_full['spend']
agg_full['cpc'] = agg_full['spend'] / agg_full['clicks']
agg_full['cpa'] = agg_full['spend'] / agg_full['purchase']
#agg_full['score'] = agg_full['ctr'] * agg_full['clicks']
#agg_full['ctr_delta'] = ((agg_full['ctr'] / agg_full['ctr_acc']) - 1) * 100

agg_full = agg_full.drop(['purchase_value', 'ctr_acc','reach'], axis=1)
agg_full

############ Analítico ####################
classify = st.selectbox(
    'Classificador',
    ('ctr', 'cpm', 'cpc', 'spend','clicks','impressions','purchase'))

asc = st.selectbox('',
    ('Ascendente', 'Descendente'),label_visibility='collapsed')

if asc == 'Ascendente':
    ascending=True
else:
    ascending=False

agg = df_filter.groupby('name').agg({'thumb_link':'last','insta_link':'last','date_start':'nunique','clicks':'sum', 'impressions':'sum', 'reach':'sum','spend':'sum', 'purchase_value':'sum', 
                                     'purchase':'sum','ctr_acc':'first','video_25':'sum','video_50':'sum','video_75':'sum'})

agg.rename(columns={'date_start':'dias', 'insta_link':'Anúncio', 'thumb_link':''}, inplace=True)
agg['frequency'] = agg['impressions'] / agg['reach']
agg['ctr'] = agg['clicks'] / agg['impressions'] * 100
agg['cpm'] = agg['spend'] / agg['impressions'] * 1000
agg['roas'] = agg['purchase_value'] / agg['spend']
agg['cpc'] = agg['spend'] / agg['clicks']
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
     'cpm':'{:.2f}',
     'cpc':'{:.2f}',
     'roas':'{:.2f}',
     'cpa':'{:.2f}',
     'score':'{:.2f}',
     'spend':'{:.2f}',
     'ctr_delta':'{:.2f}',
     'frequency':'{:.2f}',
     'video_25' :'{:.0f}',
     'video_50' :'{:.0f}',
     'video_75' :'{:.0f}'}
df_view.format(f)


st.write(df_view.to_html(escape=False, index=False), unsafe_allow_html=True, use_container_width=True)

########################## Gráficos ######################
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
            ]

st.write("""
 CTR X Tempo
""")

ctr_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
    x='date_start',
    y=alt.Y('ctr_acc'),
        color='month'
).interactive()

st.altair_chart(ctr_line, use_container_width=True)

st.write("""
 Spend X Tempo
""")

spend_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
    x='date_start',
    y='spend_acc',
    color='month'
).interactive()

st.altair_chart(spend_line, use_container_width=True)

st.write("""
 CPM X Tempo
""")

cpm_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
    x='date_start',
    y=alt.Y('cpm_acc'),
    color='month'
).interactive()

st.altair_chart(cpm_line, use_container_width=True)

st.write("""
 Frequency X Tempo
""")

frequency_line = alt.Chart(df_graph).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(
    x='date_start',
    y=alt.Y('frequency_acc'),
    color='month'
).interactive()

st.altair_chart(frequency_line, use_container_width=True)

st.write("""
 CTR X CPM
""")

scatter = alt.Chart(df_graph).mark_point().encode(
    x='cpm_acc',
    y='ctr_acc'
).interactive()

st.altair_chart(scatter, use_container_width=False)

