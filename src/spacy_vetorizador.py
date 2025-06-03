# 06

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Carregar o modelo pré-treinado do spaCy em português
# É necessário instalar previamente: 
# pip install spacy
# python -m spacy download pt_core_news_lg
nlp = spacy.load('pt_core_news_lg')

CLUSTERS_COUNT = 3

def spaCy_Vetorizar():
    df = pd.read_csv("src/conteudos_processados.csv", sep=';', dtype={
        'Url': 'string',
        'original': 'string',
        'processado': 'string',
    })

    df = df.dropna().reset_index(drop=True)
    print(df.head())
    
    # Processar documentos com spaCy para obter embeddings
    print("Processando documentos com spaCy...")
    vetores_documentos = calcular_VetoresSpaCy(df['processado'])
    
    # Calcular a Similaridade de Cosseno entre os Documentos
    matriz_similaridade = cosine_similarity(vetores_documentos)
    
    # Recomendar documentos com base em consulta do usuário
    termo_busca_usuario = "contratos aluguel"
    recomendacoes_df = recomendar_documentos_spaCy(
        termo_busca_usuario,
        df['processado'],
        vetores_documentos
        # num_resultados=5 # Descomente para limitar a 5 resultados
    )

    # Exibir o DataFrame resultante
    if not recomendacoes_df.empty:
        print("Ok")
    else:
        print("Nenhuma recomendação encontrada para o termo de busca.")

    print(recomendacoes_df)
    
    # Kmeans
    df_spacy_docs = aplicar_KMeans(df['processado'], vetores_documentos)
    pca_plotagem(vetores_documentos, df_spacy_docs)

def calcular_VetoresSpaCy(documentos):
    """
    Calcula vetores de documentos usando embeddings pré-treinados do spaCy
    """
    vetores_documentos = []
    
    for doc_texto in documentos:
        # Processar o documento com spaCy
        doc = nlp(doc_texto)
        
        # Usar o vetor do documento completo (média dos vetores das palavras)
        if doc.vector.any():  # Verifica se o vetor não está vazio
            vetores_documentos.append(doc.vector)
        else:
            print(f"Aviso: Documento '{doc_texto[:50]}...' não possui vetor.")
            # Usar vetor de zeros com a dimensão padrão do spaCy
            vetores_documentos.append(np.zeros(nlp.vocab.vectors.shape[1]))
    
    return np.array(vetores_documentos)

def recomendar_documentos_spaCy(consulta, documentos_originais, vetores_documentos, num_resultados=None):
    """
    Recomenda documentos com base em uma consulta usando embeddings do spaCy
    """
    # Processar a consulta com spaCy para obter seu vetor
    doc_consulta = nlp(consulta.lower())
    
    # Verificar se a consulta tem vetor
    if not doc_consulta.vector.any():
        print(f"Aviso: A consulta '{consulta}' não gerou um vetor válido.")
        return pd.DataFrame({'Documento': [], 'Similaridade': []})
    
    # Calcular similaridade entre a consulta e os documentos
    vetor_consulta = doc_consulta.vector.reshape(1, -1)
    similaridades = cosine_similarity(vetor_consulta, vetores_documentos)[0]
    
    # Obter os índices dos documentos ordenados pela similaridade (decrescente)
    indices_ranqueados = np.argsort(similaridades)[::-1]
    
    # Criar o DataFrame de resultados
    docs_ranqueados = [documentos_originais.iloc[i] for i in indices_ranqueados]
    scores_ranqueados = similaridades[indices_ranqueados]
    
    recomendacoes = pd.DataFrame({
        'Documento': docs_ranqueados,
        'Similaridade': scores_ranqueados
    })
    
    # Limitar o número de resultados, se especificado
    if num_resultados is not None:
        recomendacoes = recomendacoes.head(num_resultados)
    
    return recomendacoes

def aplicar_KMeans(documentos, vetores_documentos):
    df_spacy_docs = pd.DataFrame({'Documento Original': documentos})

    # Aplicar KMeans
    num_clusters = CLUSTERS_COUNT 
    kmeans_spacy = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    kmeans_spacy.fit(vetores_documentos)

    # Adicionar as labels dos clusters ao DataFrame
    df_spacy_docs['Cluster'] = kmeans_spacy.labels_

    # Exibir uma amostra dos documentos e seus clusters atribuídos
    print(f"\nAmostra de Documentos e Clusters (KMeans com {num_clusters} clusters):")
    print(df_spacy_docs[['Documento Original', 'Cluster']])
    
    return df_spacy_docs

def pca_plotagem(vetores_documentos, df_spacy_docs):
    pca_spacy = PCA(n_components=3)

    # Aplicando PCA aos vetores spaCy
    caracteristicas_reduzidas_spacy = pca_spacy.fit_transform(vetores_documentos)

    # Preparar DataFrame para Plotagem
    pca_spacy_df = pd.DataFrame(
        caracteristicas_reduzidas_spacy,
        columns=['Componente PCA 1', 'Componente PCA 2', 'Componente PCA 3']
    )
    
    # Adiciona as informações de cluster e documento ao DataFrame do PCA
    pca_spacy_df['Cluster'] = df_spacy_docs['Cluster']
    pca_spacy_df['Documento Original'] = df_spacy_docs['Documento Original']

    # Converter os rótulos dos clusters para string para cores categóricas no Plotly
    pca_spacy_df['Cluster'] = pca_spacy_df['Cluster'].astype(str)

    # Criar Gráfico 3D Interativo com Plotly Express
    fig_spacy = px.scatter_3d(
        pca_spacy_df,
        x='Componente PCA 1',
        y='Componente PCA 2',
        z='Componente PCA 3',
        color='Cluster',
        title='Clusters de Documentos (spaCy + PCA 3D)',
        labels={
            'Componente PCA 1': 'Componente PCA 1',
            'Componente PCA 2': 'Componente PCA 2',
            'Componente PCA 3': 'Componente PCA 3'
        },
        width=900,
        height=700,
        hover_data={
            'Componente PCA 1': ':.2f',
            'Componente PCA 2': ':.2f',
            'Componente PCA 3': ':.2f',
            'Cluster': True,
            'Documento Original': True
        }
    )

    # Exibir o gráfico interativo
    fig_spacy.show()

# Função para demonstrar a similaridade entre palavras usando spaCy
def demonstrar_similaridade_palavras():
    # Exemplo 1: Similaridade entre palavras em uma frase
    doc = nlp("O gato está dormindo no sofá.")
    gato_token = doc[1]  # token 1 é "gato"
    sofa_token = doc[-2]  # token -2 é "sofá"
    
    print("Dimensão do vetor em spaCy:", len(gato_token.vector))
    print("Similaridade spaCy entre 'gato' e 'sofá':", gato_token.similarity(sofa_token))
    
    # Exemplo 2: Similaridade semântica entre palavras relacionadas
    palavra1 = nlp("felino")[0]
    palavra2 = nlp("gato")[0]
    print("Similaridade entre 'felino' e 'gato':", palavra1.similarity(palavra2))
    
    # Exemplo 3: Comparação entre documentos completos
    doc1 = nlp("Contrato de aluguel residencial.")
    doc2 = nlp("Locação de imóvel para moradia.")
    print("Similaridade entre documentos:", doc1.similarity(doc2))

# Executar o processamento com spaCy
if __name__ == "__main__":
    spaCy_Vetorizar()
    # Para testar apenas a similaridade entre palavras, descomente a linha abaixo
    # demonstrar_similaridade_palavras()