import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Baixar stop words do NLTK
nltk.download('stopwords')

# Baixar tokenizador
nltk.download('punkt')
nltk.download('punkt_tab')

# Lista de stop words em português
stop_words_pt = stopwords.words('portuguese')

def Vetorizar_CSV():
    print(" fdsfasfa")
    df = pd.read_csv("src\conteudos_processados.csv",sep = ';', dtype={
    'Url': 'string',
    'original': 'string',
    'processado': 'string',
    })
    print(df.head())
    df= df.dropna()
    
    ## vec 1
    documentos_vec = [preprocessar_documento(doc) for doc in df['original']]
    print(documentos_vec)
    documentos_vec_processados = [preprocessar_documento(doc) for doc in df['processado']]
    print(documentos_vec_processados)
    
    ## tf-idf
    original_tfidf= tfidf(documentos_vec)
    processados_tfidf = tfidf(documentos_vec_processados)
    
    calcular_similaridade_cosseno(original_tfidf, documentos_vec)
    calcular_similaridade_cosseno(processados_tfidf, documentos_vec_processados)
    
    # Entrada pelo usuário
    termo_busca = "aluguel"

    # Obter as recomendações ajustadas com valores de similaridade
    df_documentos_busca_original = pd.DataFrame({
    'Documento Original': df['original'],
    'Documento Original Vetorizado': documentos_vec
    })
    
    df_documentos_busca_procesados = pd.DataFrame({
    'Documento Processado': df['original'],
    'Documento Processado Vetorizado': documentos_vec_processados
    })

    recomendacoes_df_ajustada_original = recomendar_documentos_ajustada(termo_busca, df_documentos_busca_original , original_tfidf, TfidfVectorizer())
    recomendacoes_df_ajustada_processado = recomendar_documentos_ajustada(termo_busca, df_documentos_busca_procesados , documentos_vec_processados, TfidfVectorizer())

    print(recomendacoes_df_ajustada_original)
    print(recomendacoes_df_ajustada_processado)
    
    


def preprocessar_documento(doc):
    # Tokenização e normalização (minúsculas)
    tokens = word_tokenize(doc.lower())
    # Remoção de stopwords e pontuação
    tokens = [palavra for palavra in tokens if palavra not in stop_words_pt and palavra not in string.punctuation]
    return tokens



def tfidf(d):

 # Juntando os documentos processados novamente como strings
 documentos_processados_str = [' '.join(doc) for doc in d]

# Vetorização com TF-IDF
 vectorizador = TfidfVectorizer()
 matriz_tfidf = vectorizador.fit_transform(documentos_processados_str)

# Convertendo a matriz TF-IDF para um DataFrame para visualização
 df_tfidf = pd.DataFrame(matriz_tfidf.toarray(), columns=vectorizador.get_feature_names_out())


 print(df_tfidf)
 return df_tfidf

def calcular_similaridade_cosseno(matriz_tfidf, documentos):
    similaridade_cosseno = cosine_similarity(matriz_tfidf)

    # Convertendo para um DataFrame para melhor visualização
    df_similaridade_cosseno = pd.DataFrame(
        similaridade_cosseno,
        index=[f"Doc{i}" for i in range(len(documentos))],
        columns=[f"Doc{i}" for i in range(len(documentos))]
    )

    # Exibindo a matriz de similaridade por cosseno
    print(df_similaridade_cosseno)
    
    return df_similaridade_cosseno

def recomendar_documentos_ajustada(consulta, df, matriz_tfidf, vectorizador):
    # Preprocessar a consulta da mesma maneira que os documentos
    consulta_processada = ' '.join(preprocessar_documento(consulta))

    # Vetorizar a consulta usando o mesmo modelo TF-IDF
    consulta_tfidf = vectorizador.transform([consulta_processada])

    # Calcular a similaridade por cosseno entre a consulta e os documentos
    similaridade = cosine_similarity(consulta_tfidf, matriz_tfidf)[0]

    # Obter os índices dos documentos ordenados pela similaridade
    indices_ranqueados = similaridade.argsort()[::-1]

    # Exibir os documentos mais similares com base no termo de busca e suas similaridades
    recomendacoes = pd.DataFrame({
        'Documento Processado': df.loc[indices_ranqueados, 'Documento Processado'],
        'Similaridade': similaridade[indices_ranqueados]
    })

    return recomendacoes


    
    
Vetorizar_CSV()