import streamlit as st
import requests
import pandas as pd
import time 

# Bloco para conseguir fazer o download da tabela
@st.cache_data
def convert_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()



st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y').dt.date
dados['Frete'] = dados['Frete'].round(2)
dados['Frete'] = dados['Frete'].astype(float)
preço_maximo = dados['Preço'].max()
frete_maximo = dados['Frete'].max()
avalicao_maxima = dados['Avaliação da compra'].max()
qtd_parcelas = dados['Quantidade de parcelas'].max()


with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0.0, preço_maximo, (0.0, preço_maximo))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Seleciona a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Frete'):
    frete = st.slider('Selecione o valor do frete', 0.0, frete_maximo, (0.0, frete_maximo))
with st.sidebar.expander('Vendedor'):
    Vendedor = st.multiselect('Selecione o vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    Local_da_Compra = st.multiselect('Selecione Local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    Avaliacao = st.slider('Selecione o valor da Avaliação', 1, avalicao_maxima, (1, avalicao_maxima))
with st.sidebar.expander('Tipo de pagamento'):
    Tipo_pagamento = st.multiselect('Selecione o Tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    Quantidade_de_parcelas = st.slider('Selecione as quantidades de parcelas', 1, qtd_parcelas, (1, qtd_parcelas))



# Filtragem das colunas
# As variaveis que tem espaço tem que ir dessa forma `Tipo de pagamento`
query = '''
Produto in @produtos and \
Vendedor in @Vendedor and \
`Local da compra` in @Local_da_Compra and \
`Tipo de pagamento` in @Tipo_pagamento and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
@frete[0] <= Frete <= @frete[1] and \
@Avaliacao[0] <= `Avaliação da compra` <= @Avaliacao[1] and \
@Quantidade_de_parcelas[0] <= `Quantidade de parcelas` <= @Quantidade_de_parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility= 'collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data=convert_csv(dados_filtrados), file_name = nome_arquivo,mime = 'text/csv', on_click = mensagem_sucesso)
