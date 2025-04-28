# NOVA VERSÃO AJUSTADA
# Roda Word2Vec e SpaCy para "original" e "processado" e salva resultados

import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
import spacy
import os
import matplotlib.pyplot as plt
import seaborn as sns

nltk.download('punkt')

# Constantes
CLUSTERS_COUNT = 3
RESULTADOS_DIR = "resultados"
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# Carregar spaCy
nlp = spacy.load('pt_core_news_lg')

# Funções comuns
def salvar_matriz_similaridade(matriz_similaridade, nome_saida):
    df_sim = pd.DataFrame(matriz_similaridade)
    df_sim.to_csv(os.path.join(RESULTADOS_DIR, nome_saida), sep=';', index=False)

def salvar_recomendacoes(recomendacoes_df, nome_saida):
    recomendacoes_df.to_csv(os.path.join(RESULTADOS_DIR, nome_saida), sep=';', index=False)

def salvar_plot_3d(caracteristicas_reduzidas, clusters, documentos, nome_saida, titulo):
    df_plot = pd.DataFrame(caracteristicas_reduzidas, columns=['PCA1', 'PCA2', 'PCA3'])
    df_plot['Cluster'] = clusters.astype(str)
    df_plot['Documento'] = documentos

    fig = px.scatter_3d(
        df_plot, x='PCA1', y='PCA2', z='PCA3',
        color='Cluster', hover_data=['Documento'],
        title=titulo
    )
    fig.write_html(os.path.join(RESULTADOS_DIR, nome_saida + '.html'))

def aplicar_kmeans(vetores, num_clusters=CLUSTERS_COUNT):
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(vetores)
    return clusters

# 1. Word2Vec Experimentos
def rodar_word2vec(df, tipo_texto):
    documentos = df[tipo_texto].dropna().tolist()
    documentos_tokenizados = [word_tokenize(doc.lower()) for doc in documentos]

    model_w2v = Word2Vec(
        sentences=documentos_tokenizados,
        vector_size=100, window=5, min_count=1, workers=4
    )

    vetores_documentos = []
    for doc_tokens in documentos_tokenizados:
        vetores = [model_w2v.wv[w] for w in doc_tokens if w in model_w2v.wv]
        if vetores:
            vetores_documentos.append(np.mean(vetores, axis=0))
        else:
            vetores_documentos.append(np.zeros(100))
    vetores_documentos = np.array(vetores_documentos)

    matriz_sim = cosine_similarity(vetores_documentos)
    salvar_matriz_similaridade(matriz_sim, f"word2vec_{tipo_texto}_similaridade.csv")

    # Simula busca
    termo = "contratos aluguel"
    tokens_busca = word_tokenize(termo.lower())
    vetores_busca = [model_w2v.wv[t] for t in tokens_busca if t in model_w2v.wv]
    if vetores_busca:
        vetor_consulta = np.mean(vetores_busca, axis=0).reshape(1, -1)
        similaridades = cosine_similarity(vetor_consulta, vetores_documentos)[0]
        indices = np.argsort(similaridades)[::-1]
        recomendacoes = pd.DataFrame({
            'Documento': [documentos[i] for i in indices],
            'Similaridade': similaridades[indices]
        })
        salvar_recomendacoes(recomendacoes, f"word2vec_{tipo_texto}_recomendacoes.csv")

    # KMeans + PCA
    clusters = aplicar_kmeans(vetores_documentos)
    pca = PCA(n_components=3)
    componentes = pca.fit_transform(vetores_documentos)
    salvar_plot_3d(componentes, clusters, documentos, f"word2vec_{tipo_texto}_pca", f"Word2Vec {tipo_texto}")

# 2. spaCy Experimentos
def rodar_spacy(df, tipo_texto):
    documentos = df[tipo_texto].dropna().tolist()
    vetores_documentos = []
    for doc in documentos:
        vetor = nlp(doc).vector
        vetores_documentos.append(vetor)
    vetores_documentos = np.array(vetores_documentos)

    matriz_sim = cosine_similarity(vetores_documentos)
    salvar_matriz_similaridade(matriz_sim, f"spacy_{tipo_texto}_similaridade.csv")

    termo = "contratos aluguel"
    vetor_consulta = nlp(termo.lower()).vector.reshape(1, -1)
    similaridades = cosine_similarity(vetor_consulta, vetores_documentos)[0]
    indices = np.argsort(similaridades)[::-1]
    recomendacoes = pd.DataFrame({
        'Documento': [documentos[i] for i in indices],
        'Similaridade': similaridades[indices]
    })
    salvar_recomendacoes(recomendacoes, f"spacy_{tipo_texto}_recomendacoes.csv")

    clusters = aplicar_kmeans(vetores_documentos)
    pca = PCA(n_components=3)
    componentes = pca.fit_transform(vetores_documentos)
    salvar_plot_3d(componentes, clusters, documentos, f"spacy_{tipo_texto}_pca", f"spaCy {tipo_texto}")

if __name__ == "__main__":
    df = pd.read_csv("src/conteudos_processados.csv", sep=';', dtype={
        'Url': 'string', 'original': 'string', 'processado': 'string'
    })

    print("Rodando Word2Vec para texto processado e original...")
    rodar_word2vec(df, "processado")
    rodar_word2vec(df, "original")

    print("Rodando spaCy para texto processado e original...")
    rodar_spacy(df, "processado")
    rodar_spacy(df, "original")

    print("\nResultados salvos na pasta 'resultados'!")
