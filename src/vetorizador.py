import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from script_limpeza_textos import processar_texto

# Baixar recursos do NLTK
nltk.download('stopwords')
nltk.download('punkt')

# Lista de stop words em português
stop_words_pt = stopwords.words('portuguese')


def Vetorizar_CSV():
    print("Iniciando leitura do CSV...")

    df = pd.read_csv("src/conteudos_processados.csv", sep=';', dtype={
        'Url': 'string',
        'original': 'string',
        'processado': 'string',
    })

    # Remover valores nulos e resetar os índices
    df = df.dropna().reset_index(drop=True)
    print(df.head())

    # Pré-processamento dos textos
    documentos_vec = [preprocessar_documento(doc) for doc in df['original']]
    documentos_vec_processados = [preprocessar_documento(doc) for doc in df['processado']]

    print("Documentos originais pré-processados:")
    print(documentos_vec)
    print("Documentos processados:")
    print(documentos_vec_processados)

    # Vetorização TF-IDF
    original_tfidf, original_vectorizer = tfidf(documentos_vec)
    processados_tfidf, processados_vectorizer = tfidf(documentos_vec_processados)

    # Similaridade cosseno
    calcular_similaridade_cosseno(original_tfidf, documentos_vec)
    calcular_similaridade_cosseno(processados_tfidf, documentos_vec_processados)

    # Termo de busca
    termo_busca = "divórcio"

    # DataFrames para recomendação
    df_documentos_original = pd.DataFrame({
        'Documento': df['original'],
        'Documento Processado': documentos_vec
    })

    df_documentos_processado = pd.DataFrame({
        'Documento': df['processado'],
        'Documento Processado': documentos_vec_processados
    })

    # Recomendação baseada no termo de busca
    print("\nRecomendações com base nos textos originais:")
    recomendacoes_original = recomendar_documentos_ajustada(
        termo_busca, df_documentos_original, original_tfidf, original_vectorizer)
    print(recomendacoes_original)

    print("\nRecomendações com base nos textos processados:")
    recomendacoes_processado = recomendar_documentos_ajustada(
        processar_texto(termo_busca), df_documentos_processado, processados_tfidf, processados_vectorizer)
    print(recomendacoes_processado)


def preprocessar_documento(doc):
    # Tokenização e normalização
    tokens = word_tokenize(doc.lower())
    # Remoção de stopwords e pontuações
    tokens = [palavra for palavra in tokens if palavra not in stop_words_pt and palavra not in string.punctuation]
    return tokens


def tfidf(documentos_tokenizados):
    # Juntar tokens em uma string por documento
    documentos_str = [' '.join(doc) for doc in documentos_tokenizados]

    # Vetorização com TF-IDF
    vectorizador = TfidfVectorizer()
    matriz_tfidf = vectorizador.fit_transform(documentos_str)

    # Visualização opcional
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
    # Pré-processar a consulta
    consulta_processada = ' '.join(preprocessar_documento(consulta))

    # Vetorizar a consulta
    consulta_tfidf = vectorizador.transform([consulta_processada])

    # Calcular similaridade
    similaridade = cosine_similarity(consulta_tfidf, matriz_tfidf)[0]

    # Ordenar índices por maior similaridade
    indices_ranqueados = similaridade.argsort()[::-1]

    # Usar iloc para evitar problemas de índice
    recomendacoes = pd.DataFrame({
        'Documento Processado': df.iloc[indices_ranqueados]['Documento Processado'].values,
        'Similaridade': similaridade[indices_ranqueados]
    })

    return recomendacoes


# Executar a função principal
Vetorizar_CSV()
