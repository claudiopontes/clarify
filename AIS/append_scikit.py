# importa o algoritimo de clustering do kmeans da biblioteca scikit-learn 
from sklearn.cluster import KMeans

# importa escalador StandardScaler da biblioteca scikit-learn paa padronizar os dados
from sklearn.preprocessing import StandardScaler

#definir os dados de exemplo
#será uma lista de listas
x = [[1, 2], [1, 4], [1, 0],[10,2], [10,4], [10,0]]

# vamos instanciar o standard scaler para padronizar os dados   
scaler = StandardScaler()

#aplicar o escalador aos dados para que tenham média 0 e desvio padrão 1
x_scaled = scaler.fit_transform(x)

#cria a instancia do algoritmo KMeans com 2 clusters
kmeans = KMeans(n_clusters=2, random_state=42)

# aplicar o algoritmo KMeans aos dados escalados
kmeans.fit(x_scaled)

#exibir os rotulos dos clusters atribuidos a cada ponto de dados
print("Rótulos dos clusters:", kmeans.labels_)