import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sqlite3

# Headers para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}
base_url = "https://www.adorocinema.com/filmes/melhores/"
filmes = []

# Limita para as 5 primeiras páginas
for pagina in range(1, 2):
    url = f"{base_url}?page={pagina}"
    print(f"Coletando dados da pagina {pagina}: {url}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Checa se a página foi carregada com sucesso
    if response.status_code != 200:
        print(f"Erro ao carregar a página {pagina}. Status code: {response.status_code}")
        continue

    # Cada filme está em uma div com classe nomeada
    cards = soup.find_all("div", class_="card entity-card entity-card-list cf")
    for card in cards:
        try:
            titulo_tag = card.find("a", class_="meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "https://www.adorocinema.com" + titulo_tag['href'] if titulo_tag else None
            nota_tag = card.find("span", class_="stareval-note")
            nota = nota_tag.text.strip().replace(",", ".") if nota_tag else "N/A"

            # Visitar a página do filme e pegar as informações (diretor e elenco)
            if link:
                filme_response = requests.get(link, headers=headers)
                filme_soup = BeautifulSoup(filme_response.text, "html.parser")
                
                # Diretor - Extração do diretor de forma mais precisa
                diretor_tag = filme_soup.find("div", class_="meta-body-item meta-body-direction meta-body-oneline")
                if diretor_tag:
                    diretor = diretor_tag.text.strip().replace("Direção:", "").replace(",", "").replace("|", "").strip()
                else:
                    diretor = "N/A"

                # Limpar a direção para evitar espaços indesejados
                diretor = diretor.replace("\n", " ").replace("\r", " ").strip()

            else:
                diretor = "N/A"

            # Categoria
            genero_block = filme_soup.find("div", class_="meta-body-info")
            if genero_block:
                genero_links = genero_block.find_all('a')
                generos = [g.text.strip() for g in genero_links]
                categoria = ", ".join(generos[:3]) if generos else "N/A"

            # Ano de lançamento
            ano_tag = genero_block.find("span", class_="date") if genero_block else None
            ano = ano_tag.text.strip() if ano_tag else "N/A"

            # Verificar se todos os dados foram coletados corretamente
            if titulo != "N/A" and link and nota != "N/A":
                filmes.append({
                    "Titulo": titulo,
                    "Direção": diretor,
                    "Nota": nota,
                    "Link": link,
                    "Ano": ano,
                    "Categoria": categoria
                })
            else:
                print(f"Filme incompleto ou erro na coleta de dados: {titulo}")

            # Simula tempo entre as requisições
            tempo = random.uniform(1, 3)
            time.sleep(tempo)
            #print(f'Tempo: {tempo}')
        except Exception as e:
            print(f"Erro ao processar o filme {titulo}. Erro: {e}")

    time.sleep(random.uniform(3, 6))

# Criação do DataFrame
df = pd.DataFrame(filmes)
print(df.head())

# Gerando o CSV corretamente
df.to_csv("filmes_adorocinema.csv", index=False, encoding="utf-8-sig", quotechar='"', quoting=1)

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('filmes_adorocinema.db')
cursor = conn.cursor()

# Criar a tabela no banco de dados, caso não exista
cursor.execute('''
    CREATE TABLE IF NOT EXISTS filmes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        direcao TEXT,
        nota REAL,
        link TEXT,
        ano TEXT,
        categoria TEXT
    )
''')

# Inserir os dados no banco de dados
for filme in filmes:
    try:
        cursor.execute('''
            INSERT INTO filmes (titulo, direcao, nota, link, ano, categoria) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            filme['Titulo'],
            filme['Direção'],
            float(filme['Nota']) if filme['Nota'] != 'N/A' else None,
            filme['Link'],
            filme['Ano'],
            filme['Categoria']
        ))
    except Exception as e:
        print(f"Erro ao inserir filme {filme['Titulo']} no banco de dados. Erro: {e}")

# Commit e fechamento da conexão
conn.commit()
conn.close()

print('Dados salvos com sucesso no banco de dados SQLite!')