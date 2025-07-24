
import config
import pandas as pd
import sqlite3
import os 
from flask import Flask, request, jsonify, render_template_string
import dash 
from dash import Dash, html, dcc
import plotly.graph_objects as go
import numpy as np  
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

DB_PATH = config.DB_PATH

# Função para inicializar o banco de dados SQL
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS inadimplencia(
                        mes TEXT PRIMARY KEY,
                        inadimplencia REAL
                        )
        ''')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS selic(
                        mes TEXT PRIMARY KEY,
                        selic_diaria REAL
                        )
        ''')
        conn.commit()

#Rotas
@app.route('/')
def index():
    return render_template_string(''' 
        <h1 style="color:green"> Upload de dados Economicos </h1>
        <br>
        <form action='/upload' method ='POST' enctype='multipart/form-data'>
            <label for='campo_inadimplencia'>Arquivo de Inadimplencia</label>
            <input name='campo_inadimplencia' type='file' required="true"><br><br>
            <label for='campo_selic'>Arquivo Taxa Selic</label>
            <input name='campo_selic' type="file" required="true">
        <br><br>
        <input style='background-color:green; color:white' type='submit' value="Fazer upload">
        </form> 
        <br><br><hr>
        <a href="/consultar"> Consultar Dados</a><br>
        <a href="/graficos"> Visualizar Gráficos</a><br>
        <a href="/editar_inadimplencia"> Editar dados de Inadimplencia</a><br>
        <a href="/editar_selic"> Editar Taxas da Selic</a><br>
        <a href="/correlacao"> Analisar a Correlação</a><br>
        <a href="/insights_3d"> Gráficos 3D</a>
    ''')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    # verificar se os arquivos de fato foram enviados
    if not inad_file or not selic_file:
        return jsonify({'Erro':'Ambos os arquivos devem ser enviados'})

    inad_df = pd.read_csv(inad_file, sep=';', names=['data','inadimplencia'], header=0)
    selic_df = pd.read_csv(selic_file, sep=';', names=['data','selic_diaria'], header=0)

    # formata o campo de data como datahora padrão 
    inad_df['data'] = pd.to_datetime(inad_df['data'], format="%d/%m/%Y")
    selic_df['data'] = pd.to_datetime(selic_df['data'], format="%d/%m/%Y")

    # gera uma nova coluna chamada de mes e preenche de acordo com a coluna data
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    # limpa as duplicidades e agrupa conjuntos
    inad_mensal =  inad_df[['mes', 'inadimplencia']].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    # armazenar no banco de dados as informações após limpeza
    with sqlite3.connect(DB_PATH) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists='replace', index=False)
        selic_mensal.to_sql('selic', conn, if_exists='replace', index=False)
    return jsonify({'Mensagem':'Dados inseridos com sucesso!'})

@app.route('/consultar', methods=['POST', 'GET'])
def consultar():
    # Resultado se a pagina for carregada recebendo POST
    if request.method == 'POST':
        tabela = request.form.get('campo_tabela')
        if tabela not in ['inadimplencia', 'selic']:
            return jsonify({'Erro':'Tabela é invalida'})
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f'SELECT * FROM {tabela}', conn)
        return df.to_html(index=False)

    # Resultado sem receber um POST, ou seja, primeiro carregamento da pagina de consulta
    return render_template_string(''' 
        <h1 style="color:green"> Consultar Tabelas </h1>
        <form action='/consultar' method='POST'>
            <label for='campo_tabela'> Escolha a tabela: </label>
            <select name='campo_tabela'>
                <option value='inadimplencia'>Inadimplência</option>
                <option value='selic'>Taxa Selic</option>
            </select>   
            <input type="submit" value="Consultar">                                                   
        </form>
        <br>
        <h1><a href='/'>Voltar</a></h1>
    ''')

@app.route('/graficos')
def graficos():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)

    # Verifica se os DataFrames estão vazios
    if inad_df.empty or selic_df.empty:
        return jsonify({'Erro': 'Nenhum dado encontrado para plotar os gráficos.'})

    # Cria os gráficos
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=inad_df['mes'],
        y=inad_df['inadimplencia'],
        mode='lines+markers',
        name='Inadimplencia'
    ))
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=selic_df['mes'],
        y=selic_df['selic_diaria'],
        mode='lines+markers',
        name='Selic'
    ))

    # principais templates ggplotly, plotly_dark, plotly_white, seaborn, simple_white, presentation, ygridoff, gridon, none
    fig1.update_layout(
        title='Evolução da Inadimplência',
        xaxis_title='Mês',
        yaxis_title='(%)',
        template='plotly_dark'
    )
    fig2.update_layout(
        title='Média Mensal Selic',
        xaxis_title='Mês',
        yaxis_title='Taxa (%)',
        template='plotly_dark'
    )

    # monta HTML para o gráfico
    graph_html_1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    graph_html_2 = fig2.to_html(full_html=False, include_plotlyjs='cdn')   
    return render_template_string('''
        <html>
            <head>
                <meta charset='UTF-8'>
                <title>Gráficos Econômicos</title>
                <style>
                    .container {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .graph {
                        width: 48%;
                        flex-wrap: wrap;
                    }                
                </style>
                <h1 style="color:green"> Gráficos Econômicos </h1>
                <div class="container">
                    <div class="graph"> 
                        {{ grafico1 | safe }}  
                    </div>
                    &nbsp;
                    <div class="graph">
                        {{ grafico2 | safe }}                  
                    </div>
                </div>
            </head>
            <body>
                <h1><a href='/'>Voltar</a></h1>            
            </body>
        </html>
    ''', grafico1 = graph_html_1, grafico2 = graph_html_2)

# Rota para editar a tabela de inadimplencia
@app.route('/editar_inadimplencia', methods=['POST', 'GET'])
def editar_inadimplencia():
    # Bloco que será carregado apenas quando receber o posto
    if request.method == 'POST':
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({'Erro':'Valor Inválido'})
        
        # atualizar os dados do banco
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE inadimplencia SET inadimplencia = ? WHERE mes = ?", (novo_valor, mes))
            conn.commit()
        return jsonify({'Mensagem':f'Dados do mes {mes} atualizado com sucesso !'})
    # Bloco que será carregado a primeira vez que a pagina abrir (sem receber o pos)
    return render_template_string(''' 
        <h1> Editar Inadimplencia</h1>
        <form method = "POST" action = '/editar_inadimplencia'>
            <label>Mês (AAAA-MM):</label>
            <input type="text" name="campo_mes" required><br>
                                  
            <label> Novo valor de Inadimplencia (%):</label>
            <input type="text" name="campo_valor" required><br>
                                  
            <input type="submit" value="Atualizar dados">
        </form>     
        <br><br>
        <h1><a href='/'>Voltar</a></h1>                   

    '''
    )

# Rota para editar a tabela de selic
@app.route('/editar_selic', methods=['POST', 'GET'])
def editar_selic():
    # Bloco que será carregado apenas quando receber o posto
    if request.method == 'POST':
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({'Erro':'Valor Inválido'})
        
        # atualizar os dados do banco
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE selic SET selic_diaria = ? WHERE mes = ?", (novo_valor, mes))
            conn.commit()
        return jsonify({'Mensagem':f'Dados do mes {mes} atualizado com sucesso '})
    # Bloco que será carregado a primeira vez que a pagina abrir (sem receber o pos)
    return render_template_string(''' 
        <h1> Editar Taxa Selic</h1>
        <form method = "POST" action = '/editar_selic'>
            <label>Mês (AAAA-MM):</label>
            <input type="text" name="campo_mes" required><br>
                                  
            <label> Novo valor da taxa (%):</label>
            <input type="text" name="campo_valor" required><br>
                                  
            <input type="submit" value="Atualizar dados">
        </form>     
        <br><br>
        <h1><a href='/'>Voltar</a></h1>                   

    '''
    )

@app.route('/correlacao', methods=['POST', 'GET'])
def correlacao():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)

    # Verifica se os DataFrames estão vazios
    if inad_df.empty or selic_df.empty:
        return jsonify({'Erro': 'Nenhum dado encontrado para análise de correlação.'})

    # Merge dos DataFrames
    merged = pd.merge(inad_df, selic_df, on='mes')

    # Calcular a correlação
    correl = merged['inadimplencia'].corr(merged['selic_diaria'])

    # regressão linear
    x = merged['selic_diaria']
    y = merged['inadimplencia']
    m, b = np.polyfit(y, x, 1)

    # Plotar a regressão linear
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        name='Inadimplência x Selic',
        marker=dict(
                color='rgba(0, 123, 255, 0.8)', size=12,  line=dict(color='white', width=2), symbol='circle'
            ),
        hovertemplate='SELIC: %{x:.2f}% <br>Inadimplência: %{y:.2f}% <extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=m*x + b,
        mode='lines',
        name='Linha de Tendência',
        line=dict(color='rgba(220, 53, 69, 1)', width=4, dash='dot')
        )
    )
    fig.update_layout(
        title={'text': f'<b>Correlação entre SELIC e Inadimplência<b><br><span stype="font-size:16px">Coeficiente de Correlação: {correl:.2f} </span>',
               'x':0.5, 
               'y':0.95,
               'xanchor': 'center',
               'yanchor': 'top'   
               },
        xaxis_title=dict(text = 'SELIC Média Mensal (%)',
                   font = dict(size=18, family = 'Arial', color='gray')
        ),
        yaxis_title=dict(text = 'Inadimplência (%)',
                   font = dict(size=18, family = 'Arial', color='gray')
        ),
        xaxis=dict(
            tickfont=dict(size=14, family='Arial', color='black'),
            gridcolor='lightgray'
        ),
        yaxis=dict(
            tickfont=dict(size=14, family='Arial', color='black'),
            gridcolor='lightgray'
        ),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font =dict(size=14, family='Arial', color='black'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            xanchor='center',
            y=1.05,
            x=0.5,
            bordercolor='white',
            borderwidth=0
        ),
        margin=dict(l=60, r=60, t=120, b=60)
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return render_template_string('''
        <html>
            <head>
                <title> Correlação entre Inadimplência e Selic </title>
                <style>
                    body { font-family: Arial, sans-serif; 
                    background-color: #ffffff; 
                    color: #333; 
                    }
                    .container { width: 90%; 
                    margin: auto; 
                    text-align: center; 
                    }
                    h1 { margin-top: 40px; 
                    }
                    a { text-decoration: none; 
                    color: #007bff; 
                    }
                    a:hover { text-decoration: underline; 
                    }
                </style>
            </head>
            <body>
            <div class="container">
                <h1>Correlação entre SELIC e Inadimplência</h1>
                <div>{{graph|safe}}</div>
                <br
                <div>
                <h1><a href="/">Voltar</a></h1>
                </div>
            </div>
            </body>
        </html>
    ''', graph=graph_html)

@app.route('/insights_3d')
def insights_3d():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)

    # Verifica se os DataFrames estão vazios
    if inad_df.empty or selic_df.empty:
        return jsonify({'Erro': 'Nenhum dado encontrado para análise 3D.'})

    # Merge dos DataFrames
    merged = pd.merge(inad_df, selic_df, on='mes').sort_values('mes')
    merged['mes_idx'] = range(len(merged))

    # tendencia de inadimplencia (dirença mes a mes)
    merged['tend_inad'] = merged['inadimplencia'].diff().fillna(0)
    trend_color = ['subiu' if x > 0 else 'caiu' if x < 0 else 'estável' for x in merged['tend_inad']]

    # Derivadas Discretas
    merged['var_inad'] = merged['inadimplencia'].diff().fillna(0)
    merged['var_selic'] = merged['selic_diaria'].diff().fillna(0)

    #clustering
    features = merged[['selic_diaria','inadimplencia']].copy()
    scaler = StandardScaler()
    scaler_features = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    merged['cluster'] = kmeans.fit_predict(scaler_features)

    # Plano de Regressão 3D
    X = merged[['mes_idx', 'selic_diaria']].values 
    Y = merged['inadimplencia'].values
    A = np.c_[X, np.ones(X.shape[0])]
    coeffs, _, _, _ = np.linalg.lstsq(A, Y, rcond = None)

    # Malha do Plano 3D
    xi = np.linspace(merged['mes_idx'].min(), merged['mes_idx'].max(), 30)
    yi = np.linspace(merged['selic_diaria'].min(), merged['selic_diaria'].max())
    xi, yi = np.meshgrid(xi, yi)
    zi = coeffs[0] * xi + coeffs[1] * yi + coeffs[2]

    # montar grafico de dispersao 
    scatter = go.Scatter3d(
        x=merged['mes_idx'],
        y=merged['selic_diaria'],
        z=merged['inadimplencia'],
        mode='markers',
        marker=dict(
            size=8,
            color=merged['cluster'],  # cores por cluster
            colorscale='Viridis',
            opacity=0.9
        ),
        text=[
            f"Mês: {m}<br>Inadimplência: {z:.2f}%<br>SELIC: {y:.2f}%<br>Var Inad: {vi:.2f}<br>Var SELIC: {vs:.2f}<br>Tendência: {t}"
            for m, z, y, vi, vs, t in zip(
                merged['mes'], merged['inadimplencia'], merged['selic_diaria'],
                merged['var_inad'], merged['var_selic'], trend_color
            )
        ],
        hovertemplate = '%{text}<extra></extra>'
    )

    # Superfície do plano de regressão
    surface = go.Surface(
        x = xi, 
        y = yi, 
        z = zi,
        showscale = False,
        colorscale = 'Reds',
        opacity = 0.5,
        name = 'Plano de Regressão'
    )

    fig = go.Figure(data=[scatter,surface])
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='Tempo (Meses)',
                tickvals=merged['mes_idx'],
                ticktext=merged['mes']
            ),
            yaxis=dict(title='SELIC (%)'),
            zaxis=dict(title='Inadimplência (%)')
        ),
        title="Insights Econômicos em 3D com Tendência, Derivadas e Clustering",
        margin=dict(l=0, r=0, b=0, t=50),
        height=800
    )
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    return render_template_string(''' 
        <html>
            <head>
                <title> Insights Economicos 3D ☻ </title>
                <style>
                    body { font-family: Arial, sans-serif; 
                    background-color: #f8f9fa; 
                    color: #222; 
                    text-align: center;
                    }
                    .container { width: 95%; 
                    margin: auto; 
                    }
                    h1 { margin-top: 40px; 
                    }
                    a { text-decoration: none; 
                    color: #007bff; 
                    }
                    a:hover { text-decoration: underline; 
                    }
                </style>
            </head> 
            <body>
                <div class="container">
                    <h1> Gráfico 3D com Insights Economicos</h1>
                    <p>Analise visual com clusters, tendencias e plano de regressão</p>
                </div>                                
                <div>{{grafico|safe}}</div>
                <br
                <div>
                    <h1><a href="/">Voltar</a></h1>
                    <p>Feito com carinho por Cláudio ontes ♥</p>
                </div>
            </div>
            </body>
        </html>
    ''', grafico=graph_html)


if __name__ == '__main__':
    init_db()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT, 
        debug=config.FLASK_DEBUG,  
        threaded=config.FLASK_THREADED,
        use_reloader=config.FLASK_USE_RELOADER
    )
