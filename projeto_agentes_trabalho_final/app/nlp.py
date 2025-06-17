import spacy
import re
from app.checklist import aplicar_checklist

nlp = spacy.load("pt_core_news_lg")

def preprocessar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto

def extrair_entidades(texto):
    doc = nlp(texto)
    return [(ent.text, ent.label_) for ent in doc.ents]

def extrair_valores_datas(texto):
    datas = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', texto)
    valores = re.findall(r'R\$\s?[\d\.]+,\d{2}', texto)
    return datas, valores

def analisar_texto(texto):
    texto_limpo = preprocessar_texto(texto)
    entidades = extrair_entidades(texto_limpo)
    datas, valores = extrair_valores_datas(texto)
    checklist = aplicar_checklist(texto_limpo)
    return {
        "entidades": entidades,
        "datas": datas,
        "valores": valores,
        "checklist": checklist
    }
