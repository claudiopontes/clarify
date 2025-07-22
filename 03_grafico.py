# 03_grafico 
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Dicionarios com as Informações da Caixa Dropdown

dados_conceitos = {'java':{'Variaveis':8, 'Condicionais':10, 'loops':4, 'poo':3, 'funções':4},
                   'python':{'Variaveis':9, 'Condicionais':7, 'loops':8, 'poo':2, 'funções':6},
                   'sql':{'Variaveis':10, 'Condicionais':9, 'loops':5, 'poo':3, 'funções':9},
                   'golang':{'Variaveis':7, 'Condicionais':5, 'loops':7, 'poo':7, 'funções':7},
                   'javascript':{'Variaveis':6, 'Condicionais':2, 'loops':9, 'poo':4, 'funções':8}
                   }

cores_map = dict(
    java = 'red',
    python = 'green',
    sql = 'yellow',
    golang = 'blue',
    javascript = 'pink'
)

app = dash.Dash(__name__)

# contrução do app e dos dados
app.layout = html.Div([
    html.H4('Cursos de TI', style={'textAlign':'center'}),
    html.Div(
        dcc.Dropdown(
            id='dropdown_linguagens',
            options=[{'label':'Java', 'value':'java'},
                     {'label':'Python', 'value':'python'},
                     {'label':'SQL', 'value':'sql'},
                     {'label':'GoLang', 'value':'golang'},
                     {'label':'JavaScript', 'value':'javascript'},
                     ],
            value = ['java'],
            multi=True,
            style={'width':'50%', 'margin':'0 auto'}
        )
    ),
    dcc.Graph(id='grafico_linguagem')
], style={'width':'80%', 'margin':'0 auto'}
)

# Uma função que vai ser chamada atraves do evento
@app.callback(
    Output('grafico_linguagem', 'figure'), 
    [Input('dropdown_linguagens','value')]
)

# função para criação do grafico
def scarter_linguagens(linguagens_selecionadas):
    scarter_trace = []
    for linguagem in linguagens_selecionadas:
        dados_linguagem = dados_conceitos[linguagem]
        for conceito, conhecimento in dados_linguagem.items():
            scarter_trace.append(
                go.Scatter(
                    x=[conceito],
                    y=[conhecimento],
                    mode='markers',
                    name=linguagem.title(),
                    marker={'size':15, 'color':cores_map[linguagem]},
                    showlegend=False
                )
            )
    scarter_layout = go.Layout(
        title='Meus conhecimentos em Liguagens',
        xaxis= dict(title = 'Conceitos', showgrid=False),
        yaxis= dict(title = 'Níveis de Conhecimento', showgrid=False)
    )
    return {'data':scarter_trace, 'layout':scarter_layout}

# chanada para rodar o app 
if __name__ == '__main__':
    app.run(debug=True)
