import streamlit as st
import requests 
import pandas as pd
import plotly.express as px

st.set_page_config(layout= 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOAR DE VENDAS :shopping_trolley:')

## Requests > Json > DataFrame

## Método get da biblioteca Requests

url = 'https://labdados.com/produtos' # Endereço da API
regioes = ['Brasil','Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao= st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}
responses = requests.get(url)
dados = pd.DataFrame.from_dict(responses.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtros_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtros_vendedores:
    dados = dados[dados['Vendedor'].isin(filtros_vendedores)]

## Tabelas
### Tabelas de receitas
receitas_estados = dados.groupby('Local da compra')[['Preço']].sum()
receitas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receitas_estados, left_on = 'Local da compra', right_index =True).sort_values(by='Preço',ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas de quantidae de vendas

quantidade_vendas = dados.groupby('Local da compra').size().reset_index(name='Quantidade de Vendas')
quantidade_vendas = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(quantidade_vendas, on='Local da compra').sort_values(by='Quantidade de Vendas', ascending=False)


quantidade_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M')).size().reset_index(name='Quantidade de Vendas')
quantidade_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
quantidade_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

quantidade_categoria = dados.groupby('Categoria do Produto').size().reset_index(name='Quantidade de Vendas').sort_values('Quantidade de Vendas', ascending=False)

## Gráficos

### Tabelas  vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

fig_map_receita = px.scatter_geo(receitas_estados,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Preço',
                                 template='seaborn',
                                 hover_name ='Local da compra',
                                 hover_data = {'lat':False,'lon':False},
                                 title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0,  receita_mensal.max()),
                             color = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')


fig_receita_estados = px.bar(receitas_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True,
                             title= 'Top estados (receita)')


fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categoria,
                                text_auto = True,
                                title ='Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

fig_map_contagem = px.scatter_geo(quantidade_vendas,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Quantidade de Vendas',
                                 template='seaborn',
                                 hover_name ='Local da compra',
                                 hover_data = {'lat':False,'lon':False},
                                 title = 'Quantidade de vendas por estado')

fig_quantidade_mensal = px.line(quantidade_mensal,
                             x = 'Mês',
                             y = 'Quantidade de Vendas',
                             markers = True,
                             range_y = (0, quantidade_mensal.max()),
                             color = 'Ano',
                             title = 'Quantidade de vendas por mês')

fig_quantidade_mensal.update_layout(yaxis_title = 'Quantidade')


fig_quantidade_estados = px.bar(quantidade_vendas.head(),
                             x = 'Local da compra',
                             y = 'Quantidade de Vendas',
                             text_auto= True,
                             title= 'Top estados (Quantidade de Vendas)')


fig_quantidade_estados.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_quantidade_categorias = px.bar(quantidade_categoria,
                                   x = 'Categoria do Produto',
                                   y = 'Quantidade de Vendas',
                                   text_auto = True,
                                   title ='Quantidade de Vendas')

fig_quantidade_categorias.update_layout(yaxis_title = 'Quantidade')






## Visualização no Streamlit
aba1, aba2, aba3 =  st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])
                         

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)
with aba2:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Quantidade de Vendas',formata_numero(dados['Preço'].count()))
        st.plotly_chart(fig_map_contagem, use_container_width=True)
        st.plotly_chart(fig_quantidade_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_quantidade_mensal, use_container_width = True)
        st.plotly_chart(fig_quantidade_categorias, use_container_width = True)
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores), 
                                        x ='sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top{qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width = True) 
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores), 
                                        x ='count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top{qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores,use_container_width = True)         
        
        #st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))


#st.dataframe(dados)


## Uma tabela com o total de receita por estado