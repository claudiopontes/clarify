import pandas as pd

# carregar os dados da planilha


caminho = 'C:/Users/integral/Desktop/Phyton_2_Claudio/base_inicial.xlsx'
df1 = pd.read_excel(caminho,sheet_name='Relatório de Vendas')
df2 = pd.read_excel(caminho,sheet_name='Relatório de Vendas1')

# exibir as primeiras linhas para conferir como estão os dados
print('------- Primeiro relatório ----------------')
print(df1.head())
print('------- Segundo relatório ----------------')
print(df2.head())

# verificar se há duplicatas nas duas tabelas

print('Duplicatas no relatório 1')
print(df1.duplicated().sum())
print('Duplicatas no relatório 2')
print(df2.duplicated().sum())

#Agora vamos consolidar as duas tabelas
print('Dados consolidados ')
df_consolidado = pd.concat([df1, df2], ignore_index=True )
print(df_consolidado.head())

# Exebir o número de clientes por cidade
clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('Clientes por Cidade')
print(clientes_por_cidade)

# número de vendas por plano
vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()
print('Número de Vedas por plano')
print(vendas_por_plano)

# exibir as 3 primeiras cidades com mais clientes
top_3_cidades = clientes_por_cidade.head(3)
print('Top 3 cidades')
print(top_3_cidades)

# Exibir o total de clientes
total_clientes = df_consolidado['Cliente'].nunique()
print(f'\n Número total de clientes: {total_clientes}')

#Adcionar uma coluna de Status (Exemplo fictitio de analise)
# Vamos classifciar os  planos com o preimun se for entrerprise, caso contrario será padrão 

df_consolidado['Status'] = df_consolidado['Plano Vendido'].apply(lambda x: 'Premium' if x == 'Enterprise' else 'Padrão')

# Exibir a distribuição dos status
status_dist = df_consolidado['Status'].value_counts()
print('\n Distribuição dos status: ')
print(status_dist)

# Salvar a tabela em um arquivo 
# Primeiro em Excel 
df_consolidado.to_excel('dados_consolidados_planilha.xlsx', index=False)

# Depois em CSV
df_consolidado.to_csv('dados_consolidados_texto.csv', index=False)

#Exibir Mensagem Final
print('\n Arquivos Gerados com Sucesso')