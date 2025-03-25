import os
import nltk
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Baixar recursos necessários do NLTK
nltk.download('punkt_tab')
nltk.download('stopwords')

def remover_urls(texto):
    """Remove URLs do texto."""
    return re.sub(r'http\S+', '', texto)

def processar_texto(texto):
    """Realiza a limpeza e processamento do texto jurídico."""
    # Remover URLs
    texto = remover_urls(texto)
    
    # Converter para minúsculas
    texto = texto.lower()
    
    # Tokenização
    tokens = word_tokenize(texto, language='portuguese')
    
    # Remover pontuação e caracteres especiais
    tokens = [word for word in tokens if word.isalnum()]
    
    # Lista de stopwords personalizada para manter termos jurídicos relevantes
    stop_words = set(stopwords.words('portuguese'))
    
    # Remover stopwords
    tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)

def processar_arquivos(pasta_origem, pasta_destino):
    """Processa todos os arquivos .txt na pasta de origem e salva na pasta de destino."""
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    for arquivo in os.listdir(pasta_origem):
        if arquivo.endswith(".txt"):
            caminho_origem = os.path.join(pasta_origem, arquivo)
            caminho_destino = os.path.join(pasta_destino, arquivo)
            
            with open(caminho_origem, "r", encoding="utf-8") as f:
                texto = f.read()
            
            texto_limpo = processar_texto(texto)
            
            with open(caminho_destino, "w", encoding="utf-8") as f:
                f.write(texto_limpo)
            
            print(f"Processado: {arquivo}")

# Caminhos de entrada e saída
pasta_entrada = ""  
pasta_saida = ""  

# Executar processamento
processar_arquivos(pasta_entrada, pasta_saida)
