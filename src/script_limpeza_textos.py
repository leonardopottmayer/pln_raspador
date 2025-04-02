import os
import csv
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer, WordNetLemmatizer

# Baixar recursos necessários do NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('rslp')
nltk.download('wordnet')

# Inicializar stemmer e lematizador
stemmer = RSLPStemmer()
lemmatizer = WordNetLemmatizer()

def remover_urls(texto):
    """Remove URLs do texto."""
    return re.sub(r'http\S+', '', texto)

def processar_texto(texto):
    """Realiza a limpeza e processamento do texto jurídico."""
    texto = remover_urls(texto)
    texto = texto.lower()
    tokens = word_tokenize(texto, language='portuguese')
    tokens = [word for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('portuguese'))
    tokens = [word for word in tokens if word not in stop_words]
    tokens_stem = [stemmer.stem(word) for word in tokens]
    tokens_lem = [lemmatizer.lemmatize(word) for word in tokens_stem]
    return ' '.join(tokens_lem)

def extrair_metadados(texto):
    """Extrai metadados estruturados do texto jurídico considerando diferentes padrões."""
    url_match = re.search(r'URL:\s*(\S+)', texto)
    titulo_match = re.search(r'Título:\s*(.*?)\n', texto)
    if not titulo_match:
        titulo_match = re.search(r'\n\s*([\w\s]+?)\s*(?:Data de publicação|Resumo Legal Site|Pensador Jurídico)', texto)
    data_match = re.search(r'(Data de publicação|Data):\s*(\d{2}/\d{2}/\d{4}|Data não encontrada)', texto)
    autor_match = re.search(r'Autor:\s*(.*?)(?=\n|---|Resumo Legal Site|$)', texto)
    
    url = url_match.group(1).strip() if url_match else 'Não encontrado'
    titulo = titulo_match.group(1).strip() if titulo_match else 'Não encontrado'
    data = data_match.group(2).strip() if data_match else 'Não encontrado'
    autor = autor_match.group(1).strip() if autor_match else 'Não encontrado'
    
    # Separar o conteúdo do texto corretamente
    conteudo_inicio = texto.find('--- CONTEÚDO ---')
    if conteudo_inicio != -1:
        conteudo = texto[conteudo_inicio + len('--- CONTEÚDO ---'):].strip()
    else:
        conteudo = re.split(r'\n\n|Resumo Legal Site|Pensador Jurídico', texto, maxsplit=1)[-1].strip()
    
    return url, titulo, autor, data, conteudo

def processar_arquivos(pasta_origem, arquivo_saida):
    """Processa os arquivos .txt e salva em formato CSV."""
    with open(arquivo_saida, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerow(['URL', 'Título', 'Autor', 'Data', 'Texto Original', 'Texto Processado'])
        
        for arquivo in os.listdir(pasta_origem):
            if arquivo.endswith(".txt"):
                caminho_origem = os.path.join(pasta_origem, arquivo)
                with open(caminho_origem, "r", encoding="utf-8") as f:
                    texto = f.read()
                
                url, titulo, autor, data, conteudo = extrair_metadados(texto)
                texto_processado = processar_texto(conteudo)
                
                writer.writerow([url, titulo, autor, data, conteudo.replace('\n', ' '), texto_processado.replace('\n', ' ')])
                print(f"Processado: {arquivo}")

# Caminhos de entrada e saída
pasta_entrada = "C:/Users/rickb/OneDrive/Documentos/Educacional/furb/PLN/pln_raspador/conteudos"
arquivo_saida = "C:/Users/rickb/OneDrive/Documentos/Educacional/furb/PLN/pln_raspador/conteudos_processados.csv"

# Executar processamento
processar_arquivos(pasta_entrada, arquivo_saida)
