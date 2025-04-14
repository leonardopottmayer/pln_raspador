
import pandas as pd
import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px

nltk.download('punkt_tab')


def Word2Vec_Vetorizar() : 
    df = pd.read_csv("src/conteudos_processados.csv", sep=';', dtype={
        'Url': 'string',
        'original': 'string',
        'processado': 'string',
    })

    df = df.dropna().reset_index(drop=True)
    print(df.head())
    
    #Tokenização 
    documentos_tokenizados = [word_tokenize(doc.lower()) for doc in df['processado']]
    
    model_w2v = treinar_modelo_Word2Vec(documentos_tokenizados)
    
    # 3. Calcular o Vetor Médio para cada Documento
    vetores_documentos = calcular_VetorMedio(documentos_tokenizados, model_w2v)
    
    # 4. Calcular a Similaridade de Cosseno entre os Documentos
    matriz_similaridade = cosine_similarity(vetores_documentos)
    
    # 5. Visualizar Resultados com Heatmap -- heatmap não esta suportando alto numero de registros
    ##gerar_heatmap(matriz_similaridade, df['processado'])
    
    
    termo_busca_usuario = "contratos aluguel"
    recomendacoes_df = recomendar_documentos_w2v(
        termo_busca_usuario,
        model_w2v,
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
    
    
    #Kmeans
    df_w2v_docs = aplicar_KMeans(df['processado'],vetores_documentos)
    pca_plotagem(vetores_documentos,df_w2v_docs)
    
    #Utilizando vetores pré-treinados com spaCy
    
    
    
    

def treinar_modelo_Word2Vec(documentos_tokenizados):
    vector_dim = 100 # Dimensão dos vetores
    window_size = 5  # Janela de contexto
    min_word_count = 1 # Contagem mínima para incluir palavra
    num_workers = 4 # Threads para treinamento

    model_w2v = Word2Vec(
        sentences=documentos_tokenizados,
        vector_size=vector_dim,
        window=window_size,
        min_count=min_word_count,
        workers=num_workers,
        sg=0 # Usando CBOW (padrão), 1 para Skip-gram
    )
    return model_w2v


def calcular_VetorMedio(documentos_tokenizados, model_w2v , vector_dim =100):
    vetores_documentos = []
    for doc_tokens in documentos_tokenizados:
    # Pega os vetores das palavras no documento que existem no modelo
        vetores_palavras = [model_w2v.wv[palavra] for palavra in doc_tokens if palavra in model_w2v.wv]

        if len(vetores_palavras) > 0:
            # Calcula a média dos vetores das palavras
            vetor_medio_doc = np.mean(vetores_palavras, axis=0)
            vetores_documentos.append(vetor_medio_doc)
        else:
            # Se nenhuma palavra do documento estiver no vocabulário, adiciona um vetor de zeros
            # (Isso é raro com min_count=1, mas é bom ter por segurança)
            print(f"Aviso: Documento '{' '.join(doc_tokens)}' não possui palavras no vocabulário do modelo.")
            vetores_documentos.append(np.zeros(vector_dim))

        # Garantir que temos um array NumPy
    
    return np.array(vetores_documentos)


def gerar_heatmap(matriz_similaridade, documentos):
    plt.figure(figsize=(10, 8)) # Ajuste (largura, altura) conforme necessário

    # Cria o heatmap usando Seaborn
    sns.heatmap(
        matriz_similaridade,      # A matriz de dados
        annot=True,               # Exibir os valores de similaridade nas células
        cmap='Blues',           # Esquema de cores (outras opções: 'Blues', 'YlGnBu', 'coolwarm', etc.)
        fmt=".2f",                # Formatar os números exibidos para 2 casas decimais
        linewidths=.5,            # Desenhar linhas finas entre as células
        xticklabels=range(len(documentos)), # Rótulos do eixo X (índices dos documentos)
        yticklabels=range(len(documentos))  # Rótulos do eixo Y (índices dos documentos)
    )
    
    # Adiciona títulos e rótulos para clareza
    plt.title('Heatmap de Similaridade de Cosseno entre Documentos', fontsize=14)
    plt.xlabel('Índice do Documento', fontsize=12)
    plt.ylabel('Índice do Documento', fontsize=12)
    
    # Ajusta o layout para evitar sobreposição de elementos
    plt.tight_layout()
    
    # Exibe o gráfico
    plt.show()
    
    
    
    
    
def recomendar_documentos_w2v(consulta, model_w2v, documentos_originais, vetores_documentos, num_resultados=None):
    # 1. Preprocessar (tokenizar, lowercase) a consulta
    tokens_busca = word_tokenize(consulta.lower())
    if not tokens_busca:
        print("Aviso: Consulta vazia após tokenização.")
        return pd.DataFrame({'Documento': [], 'Similaridade': []})

    # 2. Vetorizar a consulta usando o modelo Word2Vec (média dos vetores)
    vetores_palavras_busca = [model_w2v.wv[token] for token in tokens_busca if token in model_w2v.wv]

    # Verifica se alguma palavra da consulta foi encontrada no vocabulário
    if not vetores_palavras_busca:
        print(f"Aviso: Nenhuma palavra da consulta '{consulta}' encontrada no vocabulário do modelo.")
        # Retorna DataFrame vazio se a consulta não tem palavras conhecidas
        return pd.DataFrame({'Documento': [], 'Similaridade': []})

    # Calcula o vetor médio para a busca
    vetor_busca = np.mean(vetores_palavras_busca, axis=0)
    # 3. Calcular a similaridade por cosseno entre a consulta e os documentos
    # O vetor_busca precisa ser 2D (1, N_dims) para a função cosine_similarity
    similaridades = cosine_similarity(vetor_busca.reshape(1, -1), vetores_documentos)[0] # Pega a primeira (e única) linha de scores
    # 4. Obter os índices dos documentos ordenados pela similaridade (decrescente)
    indices_ranqueados = np.argsort(similaridades)[::-1]
    
    # 5. Criar o DataFrame de resultados com base nos índices ranqueados
    # Seleciona os documentos originais e as similaridades na ordem correta
    docs_ranqueados = [documentos_originais[i] for i in indices_ranqueados]
    scores_ranqueados = similaridades[indices_ranqueados]
    recomendacoes = pd.DataFrame({
        'Documento': docs_ranqueados,
        'Similaridade': scores_ranqueados
    })
    # 6. Limitar o número de resultados, se especificado
    if num_resultados is not None:
        recomendacoes = recomendacoes.head(num_resultados)
    return recomendacoes


def aplicar_KMeans(documentos, vetores_documentos):
    df_w2v_docs = pd.DataFrame({'Documento Original': documentos})

    # 2. Aplicar KMeans
    # Definindo o número de clusters (pode ser ajustado/otimizado)
    num_clusters = 3 # Você pode experimentar outros valores

    # Aplicando o KMeans aos vetores Word2Vec
    # Adicionar n_init=10 para evitar warnings e melhorar a robustez
    kmeans_w2v = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)

    # O fit é feito diretamente nos vetores Word2Vec (que já são densos)
    kmeans_w2v.fit(vetores_documentos)

    # Adicionando as labels (rótulos) dos clusters ao DataFrame
    df_w2v_docs['Cluster'] = kmeans_w2v.labels_

    # Exibindo uma amostra dos documentos e seus clusters atribuídos
    print(f"\nAmostra de Documentos e Clusters (KMeans com {num_clusters} clusters):")
    print(df_w2v_docs[['Documento Original', 'Cluster']])
    return df_w2v_docs

def pca_plotagem(vetores_documentos, df_w2v_docs):
    pca_w2v = PCA(n_components=3)

    # Aplicando PCA aos vetores Word2Vec (não precisa de .toarray())
    caracteristicas_reduzidas_w2v = pca_w2v.fit_transform(vetores_documentos)

    # 4. Preparar DataFrame para Plotagem
    # Criando um DataFrame que inclui as 3 componentes PCA, Cluster e Documento
    pca_w2v_df = pd.DataFrame(
        caracteristicas_reduzidas_w2v,
        columns=['Componente PCA 1', 'Componente PCA 2', 'Componente PCA 3']
    )
    # Adiciona as informações de cluster e documento ao DataFrame do PCA
    pca_w2v_df['Cluster'] = df_w2v_docs['Cluster']
    pca_w2v_df['Documento Original'] = df_w2v_docs['Documento Original']

    # Convertendo os rótulos dos clusters para string para cores categóricas no Plotly
    pca_w2v_df['Cluster'] = pca_w2v_df['Cluster'].astype(str)

    # 5. Criar Gráfico 3D Interativo com Plotly Express
    fig_w2v = px.scatter_3d(
        pca_w2v_df,
        x='Componente PCA 1',
        y='Componente PCA 2',
        z='Componente PCA 3',        # Mapeando a terceira componente para o eixo Z
        color='Cluster',             # Colorindo os pontos pelo cluster atribuído
        title='Clusters de Documentos (Word2Vec + PCA 3D)', # Título atualizado
        labels={                     # Rótulos dos eixos
            'Componente PCA 1': 'Componente PCA 1',
            'Componente PCA 2': 'Componente PCA 2',
            'Componente PCA 3': 'Componente PCA 3'
        },
        width=900,                   # Largura/Altura do gráfico (ajustável)
        height=700,
        hover_data={                 # Dados a exibir ao passar o mouse sobre um ponto
            'Componente PCA 1': ':.2f', # Formata PCA para 2 casas decimais no hover
            'Componente PCA 2': ':.2f',
            'Componente PCA 3': ':.2f',
            'Cluster': True, # Mostra o número do cluster
            'Documento Original': True # Mostra o texto do documento original
        }
        # Alternativa para hover_data: hover_data=['Documento Original', 'Cluster']
        )

        # Opcional: Ajustar a aparência dos marcadores
        # fig_w2v.update_traces(marker=dict(size=5, opacity=0.8))

        # Exibir o gráfico interativo
    fig_w2v.show()
    
    
    
    
Word2Vec_Vetorizar()