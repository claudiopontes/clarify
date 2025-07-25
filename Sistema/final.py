import pandas as pd
import numpy as np
import plotly.express as px
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output

#primeira etapa, carregar e limpar os dados
#função para carregar dadso com tratamento de exceção   

def load_data(file_path):
    try:
        data = pd.read_csv(file_path, encoding='ISO-8859-1')
        return data
    except:
        print(f"Erro ao carregar o arquivo. Verifique o caminho e o formato do arquivo: {file_path}")
        return None

# carregar os CSVs
avengers_df = load_data("avengers.csv")
drinks_df = load_data("drinks.csv")

#Etapa 2 limpeza dos dados 
#essa função vai limpar dos dados, tratando dados nulos e convertendo os seus respectivos tipo

def clean_data(df,numeric_columns):
    try:
        #remover linhas Nulas
        df = df.dropna()

        # garantir que as colunas de data estejam no formato correto
        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        print("Dados limpos com sucesso.")
        return df
    except Exception as e:
        print(f"Erro ao limpar os dados. {e}. Verifique as colunas e os tipos de dados.")
        return None

# Limpar avengers_df
avengers_df = clean_data(avengers_df, ['Appearances'])
# Limpar drinks_df
drinks_df = clean_data(drinks_df, ['beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol'])

#verificar se os dados foram carregados e limpos corretamente
print('\nAvengers DataFrame após limpeza:')
print(avengers_df.head())
print('\nDrinks DataFrame após limpeza:')
print(drinks_df.head())