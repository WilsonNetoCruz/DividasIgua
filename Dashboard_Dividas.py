
# python -m pip install streamlit      # python -m streamlit run Dashboard_Dividas.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

st.set_page_config(layout='wide')

col01, mid00, col02 = st.columns([3,1,10])
with col01:
    st.image('logo-IGUA.jpeg', width=300)
with col02:
    st.header('Acompanhamento das Dívidas')
    st.subheader('Iguá Saneamento')

st.divider()

# df = pd.read_excel("Livro1.xlsm", sheet_name=None)
df = pd.read_excel("Dívidas Iguá_v2.xlsm", sheet_name=None)

df_resumo = df['Resumo']
df_resumo = df_resumo.iloc[4:, 1:17]
novos_nomes = ['#','Empresa', 'Banco', 'Modalidade', 'Finalidade', 'Nº Contrato', 'Valor Contratado', 'Valor a Desembolsar',
               'Valor Atual', 'Data Inicial', 'Vencimento', 'Custo', 'Prazo Médio (Anos)', 'Taxa Nominal', 'C/C', 'Monitor']
df_resumo.columns = novos_nomes
df_resumo = df_resumo.iloc[1:]

df_total = df_resumo.iloc[31]
df_total = pd.DataFrame(df_total)
df_total = df_total.dropna()

df_resumo = df_resumo.iloc[:-13]

# df_resumo
# df_total

empresas = st.sidebar.selectbox('Empresa', df_resumo['Empresa'].unique())

df_filtered = df_resumo[df_resumo['Empresa']==empresas]
df_filtered

st.divider()

st.caption('Resumo Geral')

col1, col2 = st.columns(2)
col3, col4, col5, col0 = st.columns(4) # col4, col5
col6, col7, col8 = st.columns(3) # col7
col9, col10, col11 = st.columns(3)
col12, col13, col14 = st.columns(3) # col13
col15, col16, col17 = st.columns(3) # col16
col18, col19, col20 = st.columns(3)

## Monitoramento - Tabela
df_resumo['Cor'] = df_resumo['Monitor'].apply(lambda x:
    'yellow' if pd.isna(x) or x == 'Médio - Diferença abaixo 5k' else ('lightgreen' if x == 'OK' else 'red'))
columns_to_display = ['Empresa', 'Monitor', 'Modalidade']

fig_table = go.Figure(data=[go.Table(
    header=dict(values=columns_to_display, fill_color='lightblue', align='center'),
    cells=dict(values=[df_resumo[col] for col in columns_to_display],
               fill_color=[df_resumo['Cor']],
               align='center'))])
fig_table.update_layout(width=375, height=500)
col0.plotly_chart(fig_table, use_container_width=False)

## Modalidades - Valor Contratado
fig_modalidades = px.bar(df_resumo, x='Empresa', y='Valor Contratado',
                          title='Valor por Modalidade',
                          labels={'value': 'Valor', 'variable': 'Tipo', 'Modalidade': 'Modalidade'},
                          color='Modalidade',  # Adicionar cor com base na modalidade
                          color_discrete_map={'Valor Contratado': 'green', 'Valor a Desembolsar': 'blue', 'Valor Atual': 'orange'})
                          #height=600)
fig_table.update_layout(width=400, height=400)
col2.plotly_chart(fig_modalidades, use_container_width=False)

## Monitoramento
fig_monitor = px.pie(df_resumo, names='Monitor', title='Distribuição de Empresas por Monitoramento',
                     labels={'Monitor': 'Status de Monitoramento'}, hole=0.3)

fig_monitor.update_traces(textinfo='percent+label', pull=[0.1 if m == 'OK' else 0 for m in df_resumo['Monitor'].unique()])
fig_monitor.update_layout(width=450, height=550)
col1.plotly_chart(fig_monitor, use_container_width=False)

## Empresas - Comparativos Valores
df_modalidades = df_resumo[['Empresa', 'Modalidade', 'Valor Contratado', 'Valor a Desembolsar', 'Valor Atual', 'Monitor']]
df_modalidades[['Valor Contratado', 'Valor a Desembolsar', 'Valor Atual']] = df_modalidades[['Valor Contratado', 'Valor a Desembolsar', 'Valor Atual']].apply(pd.to_numeric, errors='coerce')

cores = {'Valor Contratado': 'green', 'Valor Atual': 'orange', 'Valor a Desembolsar': 'blue'}
fig = go.Figure()
for tipo_valor, cor in cores.items():
    fig.add_trace(go.Bar(
        x=df_modalidades['Empresa'] + ' - ' + df_modalidades['Modalidade'],
        y=df_modalidades[tipo_valor],
        name=tipo_valor,
        marker_color=cor))
fig.update_layout(
    title='Comparação de Valores por Modalidade e Empresa',
    barmode='group',
    yaxis=dict(title='Valor'),
    legend=dict(title='Tipo'))
    #,height=600)
fig_table.update_layout(width=250, height=400)
col3.plotly_chart(fig, use_container_width=False)

## Sunburst 
fig_sunburst = px.sunburst(
    data_frame=df_resumo,
    path=['Empresa', 'Banco', 'Modalidade', 'Finalidade'], #
    values='Valor Contratado',
    title='Distribuição do Valor Contratado',
    color='Empresa')

fig_sunburst.update_traces(
    textfont_color='white',
    textfont_size=14,
    hovertemplate='<b>%{label}:</b> R$ %{value:.2f}')
col6.plotly_chart(fig_sunburst, use_container_width=True)

## Sunburst
fig_sunburst_custo = px.sunburst(
    data_frame=df_resumo,
    path=['Empresa', 'Modalidade', 'Custo'], #
    values='Valor Contratado',
    title='Distribuição de Financiamento',
    color='Empresa')
fig_sunburst_custo.update_traces(
    textfont_color='white',
    textfont_size=14,
    hovertemplate='<b>%{label}:</b> R$ %{value:.2f}')
col7.plotly_chart(fig_sunburst_custo, use_container_width=True)

## Sunburst sem a empresa mais representativa
df_excluindo_representativa = df_resumo[df_resumo['Empresa'] != 'Igua RJ']

fig_sunburst_menos1 = px.sunburst(
    data_frame=df_excluindo_representativa,
    path=['Empresa', 'Modalidade', 'Custo'],
    values='Valor Contratado',
    title="Distribuição de Financiamento <br><sup>(sem a empresa mais representativa)</sup>",
    #height=800,
    color='Empresa')
fig_sunburst_menos1.update_traces(
    textfont_color='white',
    textfont_size=14,
    hovertemplate='<b>%{label}:</b> R$ %{value:.2f}')
col8.plotly_chart(fig_sunburst_menos1, use_container_width=True)

## Diferenças Totais
data = {
    'Tipo': ['Valor Contratado', 'Valor a Desembolsar', 'Valor Atual'],
    'Valor': [df_total.loc['Valor Contratado'].iloc[0], df_total.loc['Valor a Desembolsar'].iloc[0], df_total.loc['Valor Atual'].iloc[0]]
}
df_grafico = pd.DataFrame(data)

dif_atual_contratado = df_grafico['Valor'][2] - df_grafico['Valor'][0]

fig_totais = px.bar(df_grafico, x='Tipo', y='Valor',
                    title='Valores Totais',
                    labels={'Valor': 'Valor', 'Tipo': 'Tipo'},
                    color='Tipo',
                    color_discrete_map={'Valor Contratado': '#2ecc71', 'Valor a Desembolsar': '#3498db', 'Valor Atual': '#e67e22'})
                    #height=600)
fig_totais.add_shape(type='line',
                     x0=df_grafico['Tipo'][0], x1=df_grafico['Tipo'][2],
                     y0=df_grafico['Valor'][2], y1=df_grafico['Valor'][2],
                     line=dict(color='black', width=2, dash='dash'))
fig_totais.add_trace(go.Scatter(x=[df_grafico['Tipo'][1]], y=[df_grafico['Valor'][0] + (0.5 * dif_atual_contratado)],
                                mode='text', text=[f'Diferença: {-dif_atual_contratado:.2f}'],
                                showlegend=False, textfont={'color': 'red', 'size': 15}))
fig_totais.update_layout(
    xaxis_title=None,
    yaxis_title='Valores',
    font=dict(family="Arial, sans-serif", size=12, color="#444444"),
    margin=dict(t=80, l=20, r=20, b=20),
    showlegend=False)
fig_totais.update_layout(width=500, height=400)
col9.plotly_chart(fig_totais, use_container_width=False)

## Detalhamento Empresa - Comparativo Valores
fig_valor_empresa = go.Figure()
tipos = ['Valor Contratado', 'Valor a Desembolsar', 'Valor Atual']
for i, tipo in enumerate(tipos):
    fig_valor_empresa.add_trace(go.Bar(x=df_filtered['Nº Contrato'],
                        y=df_filtered[tipo],
                        name=tipo,
                        marker_color=['green', 'blue', 'orange'][i]))

fig_valor_empresa.update_layout(title=f'Detalhes da Empresa {empresas}',
                  xaxis_title='Nº Contrato',
                  yaxis_title='Valor',
                  barmode='group',
                  showlegend=True)
                  #height=600)
fig_valor_empresa.update_layout(width=500, height=450)
col11.plotly_chart(fig_valor_empresa, use_container_width=False)

##  Tabela                      
df_resumo_sorted = df_resumo.sort_values(by='Valor Contratado', ascending=False)
df_resumo_sorted['Cor'] = df_resumo_sorted.apply(lambda row:
    'lightblue' if pd.isna(row['Valor Contratado']) or row['Valor Contratado'] > row['Valor Atual'] else
    ('rgb(141,160,203)' if row['Valor Contratado'] <= row['Valor Atual'] else 'red'), axis=1)
fig_tabela = sp.make_subplots(rows=1, cols=1,
                       column_widths=[0.5],
                       subplot_titles=['Monitorar se o Valor Atual supera o Contratado'])
table = go.Figure(go.Table(
    header=dict(values=['Número de Contrato', 'Empresa', 'Valor Contratado', 'Modalidade']),
                #fill_color='rgb(153,153,153)', align='center'),
    cells=dict(values=[df_resumo_sorted['Nº Contrato'],
                       df_resumo_sorted['Empresa'],
                       df_resumo_sorted['Valor Contratado'],
                       df_resumo_sorted['Modalidade']],
                       fill_color=[df_resumo_sorted['Cor']],
                       align='center')))
fig_tabela.add_trace(table.data[0])
fig_tabela.update_layout(title_text='Tabela de Contratos (Ordenado por Valor Contratado)',
                  showlegend=False)
col12.plotly_chart(fig_tabela, use_container_width=False)

df_resumo['n'] = 1
## Sunburst - N° Contratos
df_resumo['Taxa Nominal %'] = df_resumo['Taxa Nominal'].map(lambda x: f"{x * 100:.2f}%" if pd.notna(x) else '')
fig_n_contratos = px.sunburst(
    data_frame=df_resumo,
    path=['Empresa', 'Modalidade', 'Nº Contrato','Taxa Nominal %'], # Conferir
    values='n',
    title='Contratos por Empresa',
    color='Empresa')

fig_n_contratos.update_traces(
    textfont_color='white',
    textfont_size=14,
    hovertemplate='<b>%{label}:</b> %{value:.2f} Contratos')
col14.plotly_chart(fig_n_contratos, use_container_width=True)

## Evolução do Valor Contratado
df_resumo['Vencimento'] = pd.to_datetime(df_resumo['Vencimento'])
df_resumo['Data Inicial'] = pd.to_datetime(df_resumo['Data Inicial'])
fig_evolucao_valor = px.line(df_resumo, x='Data Inicial', y='Valor Contratado', color='Empresa', markers=True,
              title='Evolução do Valor Contratado ao Longo do Tempo',
              labels={'Valor Contratado': 'Valor Contratado', 'Data Inicial': 'Data Inicial'},
              template='plotly_dark')
fig_evolucao_valor.update_layout(legend=dict(traceorder='normal'),
                  legend_tracegroupgap=0,
                  legend_title_text='Empresa')
for trace in fig_evolucao_valor.data:
    trace.update(visible='legendonly')
fig_evolucao_valor.update_xaxes(title_text='Data Inicial')
fig_evolucao_valor.update_yaxes(title_text='Valor Contratado')
col15.plotly_chart(fig_evolucao_valor, use_container_width=False)

## Prazo Médio
fig_prazoMedio = px.scatter(df_resumo, x='Empresa', y='Prazo Médio (Anos)', color='Modalidade',
                 title='Prazo Médio por Empresa, Modalidade e Contrato',
                 labels={'Prazo Médio (Anos)': 'Prazo Médio (Anos)', 'Empresa': 'Empresa'})
fig_prazoMedio.update_layout(xaxis_title='Empresa', yaxis_title='Prazo Médio (Anos)')
col18.plotly_chart(fig_prazoMedio, use_container_width=False)

## Tempo dos contratos até o dia atual
data_atual = datetime.now()
df_resumo['Vencimento'] = pd.to_datetime(df_resumo['Vencimento'])
df_resumo['Diferenca_Datas'] = (df_resumo['Vencimento'] - data_atual).dt.days
df_resumo = df_resumo.sort_values(by='Diferenca_Datas', ascending=False)
df_resumo['Ranking'] = df_resumo['Diferenca_Datas'].rank(ascending=False)
fig_time = go.Figure()
for i, row in df_resumo.iterrows():
    fig_time.add_trace(go.Bar(
        x=[f"{row['Empresa']} - {str(row['Nº Contrato'])}"],
        y=[row['Diferenca_Datas']],
        name=f"{int(row['Ranking'])}° - {row['Empresa']} ({str(row['Nº Contrato'])})",
        text=[f"{row['Diferenca_Datas']} dias"],
        hoverinfo='text'))
fig_time.update_layout(
    title='Diferença entre a Data Atual e o Vencimento',
    yaxis_title='Diferença entre Datas (dias)',
    barmode='group',
    xaxis_tickangle=-45)
col20.plotly_chart(fig_time, use_container_width=False)

## Período de Contrato
fig_periodo = go.Figure()
df_resumo['Vencimento'] = pd.to_datetime(df_resumo['Vencimento'])
df_resumo['Data Inicial'] = pd.to_datetime(df_resumo['Data Inicial'])
for i, row in df_resumo.iterrows():
    fig_periodo.add_trace(go.Scatter(x=[row['Data Inicial'], row['Vencimento']],
                             y=[f"{row['Empresa']} - {str(row['Nº Contrato'])}"] * 2,
                             mode='lines+text',
                             line=dict(color='black', width=2, dash='dash'),
                             showlegend=False,
                             textposition='bottom right'))
    
fig_periodo.add_trace(go.Scatter(x=df_resumo['Data Inicial'],
                         y=df_resumo['Empresa'] + ' - ' + df_resumo['Nº Contrato'].astype(str),
                         mode='markers',
                         marker=dict(color='red', size=8),
                         name='Data Inicial'))
fig_periodo.add_trace(go.Scatter(x=df_resumo['Vencimento'],
                         y=df_resumo['Empresa'] + ' - ' + df_resumo['Nº Contrato'].astype(str),
                         mode='markers',
                         marker=dict(color='blue', size=8),
                         name='Vencimento'))
fig_periodo.update_layout(title='Data Inicial ao Vencimento por Contrato',
                  xaxis_title='Data',
                  yaxis_title='Contrato e Empresa')
col17.plotly_chart(fig_periodo, use_container_width=False)
