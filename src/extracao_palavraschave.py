# 10

from keybert import KeyBERT

try:
    print("\nCarregando modelo para Extração de Palavras-Chave (KeyBERT)...")
    kw_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2') # Modelo multilíngue!
    # Se quiser um modelo apenas para inglês e menor:
    # kw_model = KeyBERT(model='all-MiniLM-L6-v2')
    print("Modelo KeyBERT carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o modelo KeyBERT: {e}")
    kw_model = None



def extract_keywords_keybert(text, kw_model_instance, top_n=3, keyphrase_ngram_range=(1, 1), stop_words='english', use_mmr=True, diversity=0.7):
    """
    Extrai palavras-chave de um texto usando KeyBERT.

    Args:
        text (str): O texto original.
        kw_model_instance (KeyBERT): A instância carregada do KeyBERT.
        top_n (int): Número de palavras-chave a serem extraídas.
        keyphrase_ngram_range (tuple): Define o tamanho das frases-chave.
        stop_words (str, list, or None): Lista de stopwords ou nome ('english').
                                         None para não usar stopwords.
        use_mmr (bool): Se True, usa Max Marginal Relevance para diversificar as palavras-chave.
        diversity (float): Quão diversas as palavras-chave devem ser (0 a 1), usado com use_mmr.

    Returns:
        list: Lista de tuplas (palavra-chave, pontuação de similaridade).
    """
    if not text or not isinstance(text, str):
        return [("Erro: Texto de entrada inválido.", 0)]
    if not kw_model_instance:
        return [("Erro: Modelo KeyBERT não carregado.", 0)]

    try:
        # A lógica de stop_words agora é controlada diretamente pelo parâmetro 'stop_words' da função.
        # O chamador da função deve decidir a configuração apropriada.
        keywords_with_scores = kw_model_instance.extract_keywords(
            text,
            keyphrase_ngram_range=keyphrase_ngram_range,
            stop_words=stop_words, # Usar diretamente o parâmetro fornecido
            top_n=top_n,
            use_mmr=use_mmr,
            diversity=diversity
        )
        return keywords_with_scores
    except Exception as e:
        # Adicionando mais detalhes ao erro, se possível
        error_message = f"Erro durante a extração de palavras-chave com KeyBERT: {type(e).__name__} - {e}"
        print(error_message) # Imprime o erro no console do Colab para depuração
        return [(error_message, 0)]
    
    
import pandas as pd

import pandas as pd

def extrair_keywords_para_csv(
    caminho_csv: str,
    kw_model,
    caminho_saida: str = "conteudos_com_keywords.csv",
    top_n: int = 3,
    ngram_range: tuple = (1, 1),
    stopwords=None,
    use_mmr: bool = True,
    diversity: float = 0.3
):
    """
    Extrai palavras-chave de cada texto no CSV e salva em nova coluna no arquivo de saída.

    Args:
        caminho_csv (str): Caminho do arquivo CSV de entrada.
        kw_model: Instância carregada do modelo KeyBERT.
        caminho_saida (str): Caminho do CSV de saída com as palavras-chave.
        coluna_texto (str): Nome da coluna com os textos a serem processados.
        top_n (int): Número de palavras-chave a extrair por documento.
        ngram_range (tuple): Tamanho dos n-gramas para extração (ex: (1, 2)).
        stopwords: Stopwords a serem usadas (None, 'english' ou lista personalizada).
        use_mmr (bool): Se True, aplica MMR para diversidade.
        diversity (float): Grau de diversidade no MMR.
    """
    print(f"--- Iniciando extração de palavras-chave com KeyBERT ---")

   # Carregar o DataFrame
    df = pd.read_csv(caminho_csv, sep=';', dtype={
        'Url': 'string',
        'original': 'string',
        'processado': 'string',
    })


    textos = df['original']
    keywords_resultado = []

    if not kw_model:
        raise ValueError("Modelo KeyBERT (kw_model) não carregado.")

    for i, texto in enumerate(textos):
        print(f"\n--- Documento {i+1}/{len(textos)} ---")

        try:
            palavras_chave = extract_keywords_keybert(
                texto,
                kw_model_instance=kw_model,
                top_n=top_n,
                keyphrase_ngram_range=ngram_range,
                stop_words=stopwords,
                use_mmr=use_mmr,
                diversity=diversity
            )

           
            if palavras_chave and isinstance(palavras_chave, list) and "Erro:" not in palavras_chave[0][0]:
                keywords_formatadas = [
                    f"{kw} ({score:.4f})" for kw, score in palavras_chave
                ]
                keywords_resultado.append(str(keywords_formatadas))
                print("Palavras-chave:")
                for k in keywords_formatadas:
                    print("-", k)
            else:
                mensagem = palavras_chave[0][0] if palavras_chave else "Erro na extração"
                keywords_resultado.append(mensagem)
                print("Aviso:", mensagem)

        except Exception as e:
            erro = f"Erro: {str(e)}"
            keywords_resultado.append(erro)
            print(erro)

    # Adiciona as palavras-chave ao DataFrame
    df["keywords_keybert"] = keywords_resultado

    # Salva no CSV
    df.to_csv(caminho_saida, sep=';', index=False)
    print(f"\n--- Concluído! Arquivo salvo em: {caminho_saida} ---")


extrair_keywords_para_csv('src/conteudos_processados.csv',kw_model)