from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random

#configura o plotly para abrir os arquivos no navegador por padrão
pio.renderers.default = "browser"

#carregar o drinks.csv
df = pd.read_csv("drinks.csv")

#cria o banco de dados em sql e popular com os dados do arquivo csv
conn = sqlite3.connect("consumo_alcool.db")
df.to_sql("drinks", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

#incia o flask
app = Flask(__name__)

html_template = '''
    <h1>Dashboard - Consumo de Alcool</h1>
    <h2> Menu </h2>
        <ul>
            <li> <a href="/grafico1"> Top 10 paises com maior consumo de alcool </a> </li>
            <li> <a href="/grafico2"> Média de consumo por tipo de bebida </a> </li>
            <li> <a href="/grafico4"> Comparativo entre os tipos de bebidas </a> </li>
            <li><a href="/comparar"> Comparar </a></li>
        </ul>
    '''

# rota inicial com o links para os graficos
@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/grafico1')
def grafico1():
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query("""
    SELECT country, total_litres_of_pure_alcohol
    FROM drinks
    ORDER BY total_litres_of_pure_alcohol DESC
    LIMIT 10
    """, conn)
    conn.close()
    fig = px.bar(
        df,
        x="country",
        y="total_litres_of_pure_alcohol",
        title="Top 10 paises com maior consumo de Alcool"
    )
    return fig.to_html()

# media do consumo por tipo global
@app.route('/grafico2')
def grafico2():
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query("SELECT AVG(beer_servings) AS cerveja, AVG(spirit_servings) AS destilados, AVG(wine_servings) AS vinhos FROM drinks", conn)
    conn.close()
    df_melted = df.melt(var_name="Bebidas", value_name="Média de Porções")
    fig = px.bar(df_melted, x="Bebidas", y="Média de Porções", title="Media de consumo global por tipo")
    return fig.to_html()

@app.route('/grafico3')
def grafico3():
    # Define grupos de paises por região (simulando)
    regioes = {
        "Europa": ["France", "Germany", "Italy", "Spain", "Portugal", "UK"],
        "Asia":  ["China","Japan","India","Thailand"],
        "Africa":  ["Angola","Nigeria","Egypt","Algeria"],
        "Americas":  ["USA","Brazil","Canada","Argentina","Mexico"]
    }
    dados = []
    conn = sqlite3.connect("consumo_alcool.db")
    for regiao, paises in regioes.items():
        placeholders = ",".join([f"'{p}'" for p in paises])
        query =  f"""
            SELECT SUM(total_litres_of_pure_alcohol) as total FROM drinks WHERE country IN ({placeholders})
        """
        total = pd.read_sql_query(query, conn)[0] or 0
        dados.append({"Região": regiao, "Consumo Total":total})
    conn.close()
    df_regioes = pd.DataFrame(dados)
    fig = px.pie(df_regioes, names="Região", values="Consumo Total", title="Consumo total por região do mundo")
    return fig.to_html() + "<br/><h1><a href='/'>Voltar ao Inicio</a></h1>"

@app.route("/grafico4")
def grafico4():
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query("SELECT beer_servings, spirit_servings, wine_servings FROM drinks", conn)
    conn.close()
    medias = df.mean().reset_index()
    medias.columns = ["Tipo", "Média"]
    fig = px.pie(medias, names="Tipo", values="Média", title="Proporção média entre tipos de bebidas")
    return fig.to_html() + '<br><h1><a href="/">Voltar ao início</a></h1>'

@app.route("/comparar", methods=['GET','POST'])
def comparar():
    opcoes = ["beer_servings","spirit_servings","wine_servings","total_litres_of_pure_alcohol"]

    if request.method == "POST":
        eixo_x = request.form.get('eixo_x')
        eixo_y = request.form.get('eixo_y')

        if eixo_x == eixo_y:
            return "<h3>Selecione variaveis diferentes!.</h3>"
        
        conn = sqlite3.connect("consumo_alcool.db")

        df = pd.read_sql_query("SELECT country, {}, {} FROM drinks".format(eixo_x,eixo_y), conn)
        conn.close()
        fig = px.scatter(df, x=eixo_x, y=eixo_y, title=f"Comparação entre {eixo_x} e {eixo_y}")
        fig.update_traces(textposition="top center")
        return fig.to_html() + '<br><h1><a href="/">Voltar ao início</a></h1>'

    return render_template_string('''
        <h2>Comparar Campos</h2>
        <form method="POST">
            <label for="eixo_x"> Eixo X: </label>
            <select name="eixo_x">
                {% for col in opcoes %}
                    <option value="{{ col }}"> {{ col }} </option>
                {% endfor %}
            </select><br><br>
            <label for="eixo_y"> Eixo y: </label>
            <select name="eixo_y">
                {% for col in opcoes %}
                    <option value="{{ col }}"> {{ col }} </option>
                {% endfor %}
            </select><br><br>
            <input type="submit" value=" - Comparar - ">
        </form>
    ''', opcoes=opcoes)

# inicia o servidor flask
if __name__ == "__main__":
    app.run(debug=True)
