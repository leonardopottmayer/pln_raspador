# 09

import nltk
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from summarizer import Summarizer # Para bert-extractive-summarizer
import pandas as pd
nltk.download('punkt_tab')


# Carregar modelos e tokenizadores

# --- Modelo T5 para Sumarização Abstrativa ---
# Modelos menores como 't5-small' ou 't5-base' são mais rápidos para exemplos didáticos
# e consomem menos memória no Colab.
# Para resultados de maior qualidade (e maior tempo de processamento), considere 't5-large'.
t5_model_name = "t5-small"
try:
    print(f"Carregando modelo T5: {t5_model_name}...")
    t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_name)
    t5_tokenizer = T5Tokenizer.from_pretrained(t5_model_name, legacy=False)
    print("Modelo T5 carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o modelo T5: {e}")
    t5_model, t5_tokenizer = None, None

# --- Modelo BERT para Sumarização Extrativa (via bert-extractive-summarizer) ---
# A biblioteca `Summarizer` cuida do carregamento do BERT e da lógica de sumarização.
# Por padrão, ela usa 'bert-large-uncased'.
try:
    print("\nCarregando modelo para Sumarização Extrativa (BERT)...")
    # Você pode especificar um modelo BERT diferente se desejar, ex: Summarizer(model='bert-base-uncased')
    # Ou até mesmo outros modelos de embedding como XLNetModel, XLNetTokenizer, etc.
    bert_summarizer = Summarizer()
    print("Modelo de sumarização extrativa (BERT) carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o sumarizador extrativo com BERT: {e}")
    bert_summarizer = None

# Verificar se os modelos foram carregados
if not t5_model or not bert_summarizer:
    print("\nERRO: Um ou mais modelos não puderam ser carregados. Verifique as mensagens de erro acima.")
    print("O notebook pode não funcionar corretamente.")
else:
    print("\nTodos os modelos parecem estar prontos!")
    
    
    
def summarize_text_abstractive_t5(text, model, tokenizer, min_length=30, max_length=150, num_beams=4):
    """
    Gera um resumo abstrativo de um texto usando um modelo T5.

    Args:
        text (str): O texto original a ser sumarizado.
        model (T5ForConditionalGeneration): O modelo T5 carregado.
        tokenizer (T5Tokenizer): O tokenizador T5 carregado.
        min_length (int): Comprimento mínimo do resumo gerado.
        max_length (int): Comprimento máximo do resumo gerado.
        num_beams (int): Número de feixes para a busca durante a geração (afeta qualidade e tempo).

    Returns:
        str: O resumo abstrativo gerado.
    """
    if not text or not isinstance(text, str):
        return "Erro: Texto de entrada inválido."
    if not model or not tokenizer:
        return "Erro: Modelo T5 ou tokenizador não carregado."

    # Adicionar o prefixo da tarefa para o T5
    task_prefix = "summarize: "
    input_text = task_prefix + text.strip()

    # Tokenizar
    # Usamos padding="longest" e truncation=True para lidar com lotes de tamanhos variados,
    # mas aqui estamos processando um texto por vez. max_length do T5 é tipicamente 512 ou 1024.
    inputs = tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True, padding="longest")

    # Mover inputs para o dispositivo correto (GPU se disponível)
    device = model.device
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)

    # Gerar o resumo
    summary_ids = model.generate(
        input_ids,
        attention_mask=attention_mask,
        num_beams=num_beams,
        min_length=min_length,
        max_length=max_length,
        early_stopping=True # Parar a geração mais cedo se uma boa sequência for encontrada
    )

    # Decodificar o resumo
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


def summarize_text_extractive_bert(text, summarizer_model, num_sentences=None, ratio=0.2):
    """
    Gera um resumo extrativo de um texto usando o bert-extractive-summarizer.

    Args:
        text (str): O texto original a ser sumarizado.
        summarizer_model (Summarizer): O objeto Summarizer carregado.
        num_sentences (int, optional): Número exato de sentenças no resumo.
                                       Se fornecido, 'ratio' é ignorado.
        ratio (float, optional): Proporção do texto original a ser usada no resumo
                                 (ex: 0.2 para 20% do número original de sentenças).
                                 Usado se 'num_sentences' não for fornecido.

    Returns:
        str: O resumo extrativo gerado.
    """
    if not text or not isinstance(text, str):
        return "Erro: Texto de entrada inválido."
    if not summarizer_model:
        return "Erro: Modelo Summarizer (BERT) não carregado."

    # O bert-extractive-summarizer espera um texto com pelo menos algumas sentenças.
    # Adicionar uma verificação simples para evitar erros com textos muito curtos.
    min_sentences_for_bert_summarizer = 3
    sentences = nltk.sent_tokenize(text)
    if len(sentences) < min_sentences_for_bert_summarizer:
        # print(f"Aviso: Texto muito curto para sumarização extrativa significativa ({len(sentences)} sentenças). Retornando o texto original ou as primeiras sentenças.")
        # Para textos muito curtos, a sumarização extrativa pode não fazer muito sentido ou falhar.
        # Poderíamos retornar as primeiras N sentenças ou o próprio texto.
        return " ".join(sentences) # Ou simplesmente o 'text' original.

    try:
        if num_sentences is not None:
            summary = summarizer_model(text, num_sentences=num_sentences)
        else:
            summary = summarizer_model(text, ratio=ratio)
        return summary
    except Exception as e:
        return f"Erro durante a sumarização extrativa: {e}"
    



def gerar_resumos_para_csv(
    caminho_csv: str,
    t5_model,
    t5_tokenizer,
    bert_summarizer,
    min_len_abs=30,
    max_len_abs=120,
    beams_abs=4,
    num_sentences_ext=3,
    ratio_ext=None,
    caminho_saida: str = "conteudos_resumidos.csv"
):
    # Carregar o DataFrame
    df = pd.read_csv(caminho_csv, sep=';', dtype={
        'Url': 'string',
        'original': 'string',
        'processado': 'string',
    })

    # Verificar se os modelos estão carregados
    if not t5_model or not bert_summarizer:
        raise ValueError("Modelos T5 ou BERT não foram carregados corretamente.")

    resumos_t5 = []
    resumos_bert = []

    for i, texto in enumerate(df['original']):
        if not isinstance(texto, str) or texto.strip() == "":
            resumos_t5.append("")
            resumos_bert.append("")
            continue

        print(f"\nProcessando documento {i+1}/{len(df)}")

        # Resumo T5
        resumo_t5 = summarize_text_abstractive_t5(
            texto,
            t5_model,
            t5_tokenizer,
            min_length=min_len_abs,
            max_length=max_len_abs,
            num_beams=beams_abs
        )
        resumos_t5.append(resumo_t5)
        
        print("Resumo Abstrativo (T5):")
        print(resumo_t5)
        print("-" * 50)

        # Resumo BERT
        resumo_bert = summarize_text_extractive_bert(
            texto,
            bert_summarizer,
            num_sentences=num_sentences_ext,
            ratio=ratio_ext
        )
        resumos_bert.append(resumo_bert)
        
        print("Resumo Extrativo (BERT):")
        print(resumo_bert)
        print("=" * 70)

    # Adiciona as colunas ao DataFrame
    df['resumo_t5'] = resumos_t5
    df['resumo_bert'] = resumos_bert

    # Salva o novo CSV
    df.to_csv(caminho_saida, sep=';', index=False)
    print(f"\nArquivo salvo em: {caminho_saida}")


min_len_abs = 30
max_len_abs = 120 # Ajuste conforme o tamanho esperado do resumo
beams_abs = 4
gerar_resumos_para_csv('src/conteudos_processados.csv',
                       t5_model,
                       t5_tokenizer,
                       bert_summarizer,
                       min_len_abs,
                       max_len_abs,
                       beams_abs,
                       )