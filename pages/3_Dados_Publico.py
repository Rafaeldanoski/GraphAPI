############## IMPORTS #######################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import altair as alt
import warnings
warnings.filterwarnings("ignore")

############## DATASET #######################
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQyxwQ2Ij7uvS1bMUAD-WWWhyWRofQDcI3_cAhBoGyY1f2t9b23C57Z6TZGIllOlZGq2895gL21n5oA/pub?output=csv'
df = pd.read_csv(url)

############## DASH ##########################
st.set_page_config(page_title="Dados Público",layout="wide",page_icon="publico.ico")

st.sidebar.success("Selecione uma página acima")

st.markdown("<h1 style='text-align: center;'>DADOS DE PÚBLICO</h1>", unsafe_allow_html=True)

############## GRÁFICOS ##########################
age_hist = alt.Chart(df).mark_bar().encode(
    alt.X("Qual a sua idade?:Q", bin=True),
    y='count()'
).interactive()

st.altair_chart(age_hist, use_container_width=True)

agg = df.groupby('Escolha a área que melhor se encaixa com a sua profissão:').agg({'Escolha a área que melhor se encaixa com a sua profissão:':'count'})
agg.index.names = ['index']
agg['cat'] = agg.index

base = alt.Chart(agg).encode(
    theta=alt.Theta("Escolha a área que melhor se encaixa com a sua profissão::Q", stack=True),
    radius=alt.Radius("Escolha a área que melhor se encaixa com a sua profissão:", scale=alt.Scale(type="sqrt", zero=True, rangeMin=100)),
    color=alt.Color("Escolha a área que melhor se encaixa com a sua profissão::N"),
)

pie = base.mark_arc(innerRadius=20, stroke="#fff")
text = base.mark_text(radiusOffset=30).encode(text="cat:N")

st.altair_chart(pie + text, use_container_width=True)


age_heatmap = alt.Chart(df).mark_rect().encode(
    x='Qual sua renda mensal aproximada?',
    y='Escolha a área que melhor se encaixa com a sua profissão:',
    color=alt.Color('count()', scale=alt.Scale(scheme="blues"))
)

text = age_heatmap.mark_text(baseline='middle').encode(
    text='count()',
    color=alt.condition(
        alt.datum.num_cars > 100,
        alt.value('black'),
        alt.value('white')
    )
)

st.altair_chart(age_heatmap + text, use_container_width=True)