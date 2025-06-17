from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np
import os

modelo_path = "modelo_juridico_finetuned"
modelo = SentenceTransformer(modelo_path if os.path.exists(modelo_path) else 'distiluse-base-multilingual-cased-v1')

df = pd.read_csv("data/Classificacao_Revisada.csv")
df = df[df['classe'] != 'nao_classificado'].reset_index(drop=True)

vetores = modelo.encode(df['Texto Original'].tolist())
index = faiss.IndexFlatL2(vetores.shape[1])
index.add(np.array(vetores))

def buscar_similares(texto):
    vetor = modelo.encode([texto])
    D, I = index.search(np.array(vetor), k=3)
    return [
        {
            "texto": df.loc[i, "Texto Original"],
            "classe": df.loc[i, "classe"],
            "similaridade": float(D[0][rank])
        }
        for rank, i in enumerate(I[0])
    ]

def sugerir_clausulas_por_entidade(entidades):
    return []
