# 04

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
from script_limpeza_textos import processar_texto

# Baixar recursos do NLTK
nltk.download('stopwords')
nltk.download('punkt')

# Lista de stop words em português
stop_words_pt = stopwords.words('portuguese')

CLUSTERS_COUNT = 4


def Vetorizar_CSV():
    print("Iniciando leitura do CSV...")

    df = pd.read_csv("src/conteudos_processados.csv", sep=';', dtype={
        'Url': 'string',
        'original': 'string',
        'processado': 'string',
    })

    df = df.dropna().reset_index(drop=True)
    print(df.head())

    documentos_vec = [preprocessar_documento(doc) for doc in df['original']]
    documentos_vec_processados = [preprocessar_documento(doc) for doc in df['processado']]

    original_tfidf, original_vectorizer = tfidf(documentos_vec)
    processados_tfidf, processados_vectorizer = tfidf(documentos_vec_processados)

    calcular_similaridade_cosseno(original_tfidf, documentos_vec)
    calcular_similaridade_cosseno(processados_tfidf, documentos_vec_processados)

    termo_busca = "contrato"

    df_documentos_original = pd.DataFrame({
        'Documento': df['original'],
        'Documento Processado': documentos_vec
    })
    
    df_documentos_processado = pd.DataFrame({
        'Documento': df['processado'],
        'Documento Processado': documentos_vec_processados
    })
    
    tfidf_original_list = original_tfidf.toarray().tolist()
    tfidf_processado_list = processados_tfidf.toarray().tolist()
    
    df['tfidf_original'] = [str(vetor) for vetor in tfidf_original_list]
    df['tfidf_processado'] = [str(vetor) for vetor in tfidf_processado_list]    
    df.to_csv('conteudos_vetorizados.csv', sep=';', index=False)
    
    print("\nRecomendações com base nos textos originais:")
    recomendacoes_original = recomendar_documentos_ajustada(
        termo_busca, df_documentos_original, original_tfidf, original_vectorizer)
    print(recomendacoes_original)

    print("\nRecomendações com base nos textos processados:")
    recomendacoes_processado = recomendar_documentos_ajustada(
        processar_texto(termo_busca), df_documentos_processado, processados_tfidf, processados_vectorizer)
    print(recomendacoes_processado)

    # ============ CLUSTERIZAÇÃO E VISUALIZAÇÃO ============
    print("\nAplicando KMeans e PCA...")

    df_clusters, modelo_kmeans = aplicar_kmeans(original_tfidf, df_documentos_original, num_clusters=CLUSTERS_COUNT)
    componentes_pca, modelo_pca = reduzir_dimensionalidade(original_tfidf)

    plotar_clusters(componentes_pca, df_clusters, titulo='Clusters com base nos documentos originais')


def preprocessar_documento(doc):
    tokens = word_tokenize(doc.lower())
    tokens = [palavra for palavra in tokens if palavra not in stop_words_pt and palavra not in string.punctuation]
    return tokens


def tfidf(documentos_tokenizados):
    documentos_str = [' '.join(doc) for doc in documentos_tokenizados]
    vectorizador = TfidfVectorizer()
    matriz_tfidf = vectorizador.fit_transform(documentos_str)

    df_tfidf = pd.DataFrame(matriz_tfidf.toarray(), columns=vectorizador.get_feature_names_out())
    print("\nMatriz TF-IDF:")
    print(df_tfidf)

    return matriz_tfidf, vectorizador


def calcular_similaridade_cosseno(matriz_tfidf, documentos):
    similaridade = cosine_similarity(matriz_tfidf)
    df_similaridade = pd.DataFrame(
        similaridade,
        index=[f"Doc{i}" for i in range(len(documentos))],
        columns=[f"Doc{i}" for i in range(len(documentos))]
    )
    print("\nMatriz de Similaridade por Cosseno:")
    print(df_similaridade)
    return df_similaridade


def recomendar_documentos_ajustada(consulta, df, matriz_tfidf, vectorizador):
    consulta_processada = ' '.join(preprocessar_documento(consulta))
    consulta_tfidf = vectorizador.transform([consulta_processada])
    similaridade = cosine_similarity(consulta_tfidf, matriz_tfidf)[0]
    indices_ranqueados = similaridade.argsort()[::-1]

    recomendacoes = pd.DataFrame({
        'Documento Processado': df.iloc[indices_ranqueados]['Documento Processado'].values,
        'Similaridade': similaridade[indices_ranqueados]
    })

    return recomendacoes


# ======= FUNÇÕES DE CLUSTERIZAÇÃO E PLOTAGEM =======

def aplicar_kmeans(matriz_tfidf, df_documentos, num_clusters=CLUSTERS_COUNT):
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(matriz_tfidf)

    df_documentos = df_documentos.copy()
    df_documentos['Cluster'] = kmeans.labels_
    
    return df_documentos, kmeans


def reduzir_dimensionalidade(matriz_tfidf, n_componentes=2):
    pca = PCA(n_components=n_componentes)
    componentes = pca.fit_transform(matriz_tfidf.toarray())
    return componentes, pca


def plotar_clusters(componentes_pca, df_documentos, titulo='Clusters de Documentos'):
    df_pca = pd.DataFrame(componentes_pca, columns=['Componente PCA 1', 'Componente PCA 2'])
    df_pca['Cluster'] = df_documentos['Cluster'].astype(str)
    df_pca['Documento Original'] = df_documentos['Documento']

    fig = px.scatter(
        df_pca,
        x='Componente PCA 1',
        y='Componente PCA 2',
        color='Cluster',
        title=titulo,
        labels={'Componente PCA 1': 'Componente PCA 1', 'Componente PCA 2': 'Componente PCA 2'},
        width=800,
        height=600,
        hover_data=['Documento Original']
    )
    fig.show()


# Executar
Vetorizar_CSV()