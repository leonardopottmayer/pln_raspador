import os
import spacy
import pandas as pd
from collections import Counter

nlp = spacy.load("pt_core_news_lg")

# Listas globais para armazenar os dados
dados_agregados = []
frases_dados = []
linhas_resultado = []  # Novo: lista para armazenar linhas que serão salvas no resultado.txt

def extrair_features(doc_text, doc_id, nome_arquivo):
    doc = nlp(doc_text)

    pos_counts = Counter([token.pos_ for token in doc])
    ent_types = Counter([ent.label_ for ent in doc.ents])
    dep_counts = Counter([token.dep_ for token in doc])

    features = {
        "arquivo": nome_arquivo,
        "documento_id": doc_id,
        "n_tokens": len(doc),
        "n_entidades": len(doc.ents),
    }

    # Agrega POS tags
    for tag in ["NOUN", "VERB", "ADJ", "PROPN"]:
        features[f"qtde_{tag}"] = pos_counts.get(tag, 0)

    # Agrega tipos de entidades
    for ent in ["PER", "ORG", "LOC"]:
        features[f"qtde_{ent}"] = ent_types.get(ent, 0)

    # Agrega relações de dependência sintática mais comuns
    for dep in ["nsubj", "obj", "amod", "advmod"]:
        features[f"qtde_{dep}"] = dep_counts.get(dep, 0)

    return features

def gerar_analises_texto(doc, nome_arquivo, doc_id):
    linhas_resultado.append(f"# Análises do arquivo: {nome_arquivo} (documento_id: {doc_id})\n")

    # ENTIDADES NOMEADAS + DEPENDÊNCIAS
    linhas_resultado.append("=== ENTIDADES NOMEADAS + DEPENDÊNCIAS ===\n")
    for ent in doc.ents:
        token_central = ent.root
        linhas_resultado.append(f"Entidade: {ent.text}\n")
        linhas_resultado.append(f" - Label: {ent.label_}\n")
        linhas_resultado.append(f" - Palavra base: {token_central.text}\n")
        linhas_resultado.append(f" - Função sintática: {token_central.dep_}\n")
        linhas_resultado.append(f" - Cabeça gramatical: {token_central.head.text}\n")
        linhas_resultado.append("\n")

    # OPINIÕES / POLARIDADE
    linhas_resultado.append("=== OPINIÕES / POLARIDADE ===\n")
    for token in doc:
        if token.pos_ == "ADJ":
            linhas_resultado.append(f"Adjetivo: {token.text} → relacionado a: {token.head.text} (função: {token.dep_})\n")

    # Conectores adversativos
    linhas_resultado.append("\n=== CONECTORES ADVERSATIVOS ===\n")
    for token in doc:
        if token.text.lower() in ["mas", "porém", "contudo"]:
            linhas_resultado.append(f"Conector adversativo identificado: '{token.text}' (pode inverter ou moderar o sentimento)\n")

    linhas_resultado.append("\n" + "="*80 + "\n\n")  # Separador entre arquivos

def processar_arquivo(nome_arquivo, conteudo, doc_id):
    # ---- Documento inteiro ----
    features_doc = extrair_features(conteudo, doc_id, nome_arquivo)
    dados_agregados.append(features_doc)

    # ---- Geração do texto para resultado.txt ----
    doc = nlp(conteudo)
    gerar_analises_texto(doc, nome_arquivo, doc_id)

    # ---- Por frases ----
    for sent_id, sent in enumerate(doc.sents):
        tokens = [token.lemma_.lower() for token in sent if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]
        entidades = [ent.text for ent in sent.ents]

        frases_dados.append({
            "arquivo": nome_arquivo,
            "doc_id": doc_id,
            "frase_id": sent_id + 1,
            "frase": sent.text.strip(),
            "substantivos/nomes_próprios": tokens,
            "entidades_nomeadas": entidades
        })

def percorrer_txts(diretorio):
    doc_id = 1
    for nome_arquivo in os.listdir(diretorio):
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        if os.path.isfile(caminho_arquivo) and nome_arquivo.lower().endswith('.txt'):
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                processar_arquivo(nome_arquivo, conteudo, doc_id)
                doc_id += 1

if __name__ == "__main__":
    pasta = "./conteudos/"
    percorrer_txts(pasta)

    # ---- Cria os DataFrames ----
    df_doc_features = pd.DataFrame(dados_agregados)
    df_frases = pd.DataFrame(frases_dados)

    # ---- Cria pasta de saída ----
    os.makedirs("./saida/", exist_ok=True)

    # ---- Salva os resultados ----
    df_doc_features.to_csv("./saida/documentos_features.csv", index=False, encoding='utf-8-sig')
    df_frases.to_csv("./saida/frases_features.csv", index=False, encoding='utf-8-sig')

    # ---- Salva o resultado.txt ----
    with open("./saida/resultado.txt", "w", encoding="utf-8") as f:
        f.writelines(linhas_resultado)

    print("Análises salvas em ./saida/ !")

    



        # ---- Análise Estatística Básica ----
    print("\n=== ANÁLISE ESTATÍSTICA BÁSICA ===\n")

    # Lê os CSVs gerados
    df_docs = pd.read_csv("./saida/documentos_features.csv", encoding="utf-8-sig")
    df_frases = pd.read_csv("./saida/frases_features.csv", encoding="utf-8-sig")

    # -------------------------
    # ENTIDADES MAIS FREQUENTES
    # -------------------------
    print(">>> Entidades nomeadas mais frequentes (PER, ORG, LOC):\n")
    entidades_contagem = (
        df_docs[["qtde_PER", "qtde_ORG", "qtde_LOC"]]
        .sum()
        .sort_values(ascending=False)
    )
    print(entidades_contagem)
    print("\nComentário: As entidades mais frequentes ajudam a entender quais atores (pessoas, organizações, lugares) predominam na base. Isso é crucial para identificar tendências ou focos temáticos nos textos.\n")

    # -------------------------
    # DISTRIBUIÇÃO TEMPORAL (por documento_id como proxy de tempo)
    # -------------------------
    print(">>> Frequência de entidades ao longo do tempo (documento_id como proxy temporal):\n")
    entidades_ao_tempo = df_docs[["documento_id", "qtde_PER", "qtde_ORG", "qtde_LOC"]]
    print(entidades_ao_tempo)
    print("\nComentário: Mesmo que não tenhamos datas explícitas, o documento_id serve como uma aproximação da ordem temporal dos documentos. Isso pode indicar mudanças na frequência de entidades ao longo da coleção de textos.\n")

    # -------------------------
    # FREQUÊNCIA DE ADJETIVOS (como indicador de polaridade/opinião)
    # -------------------------
    print(">>> Frequência total de adjetivos (indicadores de opinião/polaridade):\n")
    total_adjetivos = df_docs["qtde_ADJ"].sum()
    print(f"Total de adjetivos encontrados: {total_adjetivos}")
    print("\nComentário: Uma alta presença de adjetivos pode sugerir que os textos possuem bastante opinião ou juízo de valor, o que é relevante para análises de sentimento ou discurso.\n")

    # -------------------------
    # SUBSTANTIVOS/PROPN MAIS FREQUENTES (em frases)
    # -------------------------
    print(">>> Principais substantivos e nomes próprios (em frases):\n")
    from collections import Counter

    todos_substantivos = df_frases["substantivos/nomes_próprios"].dropna().tolist()
    todos_substantivos_flat = [item for sublist in eval(",".join([str(l) for l in todos_substantivos])) for item in sublist]

    substantivos_mais_frequentes = Counter(todos_substantivos_flat).most_common(10)
    for termo, freq in substantivos_mais_frequentes:
        print(f"{termo}: {freq}")
    print("\nComentário: Identificar os substantivos e nomes próprios mais frequentes permite entender os principais tópicos ou objetos de discussão na base de dados.\n")

    print(">>> Fim da análise estatística.\n")







    import matplotlib.pyplot as plt

    # ---- Análise Estatística Básica ----
    print("\n=== ANÁLISE ESTATÍSTICA BÁSICA ===\n")

    # Lê os CSVs gerados
    df_docs = pd.read_csv("./saida/documentos_features.csv", encoding="utf-8-sig")
    df_frases = pd.read_csv("./saida/frases_features.csv", encoding="utf-8-sig")

    # Criar pasta para os gráficos
    os.makedirs("./saida/graficos/", exist_ok=True)

    # -------------------------
    # ENTIDADES MAIS FREQUENTES
    # -------------------------
    entidades_contagem = (
        df_docs[["qtde_PER", "qtde_ORG", "qtde_LOC"]]
        .sum()
        .sort_values(ascending=False)
    )
    print(">>> Entidades nomeadas mais frequentes (PER, ORG, LOC):\n")
    print(entidades_contagem)

    plt.figure()
    entidades_contagem.plot(kind="bar")
    plt.title("Entidades Nomeadas Mais Frequentes")
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig("./saida/graficos/entidades_frequentes.png")
    plt.close()

    print("\nComentário: As entidades mais frequentes ajudam a entender quais atores (pessoas, organizações, lugares) predominam na base.\n")

    # -------------------------
    # FREQUÊNCIA DE ENTIDADES AO LONGO DO TEMPO
    # -------------------------
    entidades_ao_tempo = df_docs[["documento_id", "qtde_PER", "qtde_ORG", "qtde_LOC"]]
    print(">>> Frequência de entidades ao longo do tempo:\n")
    print(entidades_ao_tempo)

    plt.figure()
    for ent in ["qtde_PER", "qtde_ORG", "qtde_LOC"]:
        plt.plot(entidades_ao_tempo["documento_id"], entidades_ao_tempo[ent], marker='o', label=ent)
    plt.title("Frequência de Entidades ao Longo do Tempo (por documento_id)")
    plt.xlabel("Documento ID (proxy temporal)")
    plt.ylabel("Quantidade")
    plt.legend()
    plt.tight_layout()
    plt.savefig("./saida/graficos/entidades_ao_tempo.png")
    plt.close()

    print("\nComentário: Acompanhar a frequência ao longo do tempo revela tendências ou mudanças na ênfase de pessoas, organizações ou lugares.\n")

    # -------------------------
    # FREQUÊNCIA DE ADJETIVOS
    # -------------------------
    total_adjetivos = df_docs["qtde_ADJ"].sum()
    print(">>> Frequência total de adjetivos:\n")
    print(f"Total de adjetivos encontrados: {total_adjetivos}")

    plt.figure()
    df_docs["qtde_ADJ"].plot(kind="line", marker='o')
    plt.title("Distribuição de Adjetivos ao Longo do Tempo")
    plt.xlabel("Documento ID")
    plt.ylabel("Quantidade de Adjetivos")
    plt.tight_layout()
    plt.savefig("./saida/graficos/adjetivos_ao_tempo.png")
    plt.close()

    print("\nComentário: A quantidade de adjetivos pode indicar textos com caráter mais opinativo ou descritivo.\n")

    # -------------------------
    # SUBSTANTIVOS/NOMES PRÓPRIOS MAIS FREQUENTES
    # -------------------------
    from collections import Counter
    import ast

    todos_substantivos = df_frases["substantivos/nomes_próprios"].dropna().tolist()

    # Transformar string de lista em lista real (porque foi salvo como string no CSV)
    substantivos_flat = []
    for lista in todos_substantivos:
        try:
            termos = ast.literal_eval(lista)
            substantivos_flat.extend(termos)
        except:
            pass

    substantivos_mais_frequentes = Counter(substantivos_flat).most_common(10)

    print(">>> Principais substantivos e nomes próprios:\n")
    for termo, freq in substantivos_mais_frequentes:
        print(f"{termo}: {freq}")

    # Gráfico de barras para substantivos
    termos, frequencias = zip(*substantivos_mais_frequentes)

    plt.figure()
    plt.bar(termos, frequencias)
    plt.title("Substantivos/Nomes Próprios Mais Frequentes")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig("./saida/graficos/substantivos_frequentes.png")
    plt.close()

    print("\nComentário: Os substantivos/nomes próprios mais frequentes mostram os principais tópicos ou objetos de interesse da base.\n")

    print(">>> Fim da análise estatística. Gráficos salvos em ./saida/graficos/\n")
