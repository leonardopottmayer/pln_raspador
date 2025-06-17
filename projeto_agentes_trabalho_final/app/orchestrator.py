from app.nlp import analisar_texto
from app.similarity import buscar_similares, sugerir_clausulas_por_entidade
from database.connection import SessionLocal
from models.schema import Entrada, Entidade, Sugestao, Base

Base.metadata.create_all(bind=SessionLocal().bind)

def processar_texto(texto):
    session = SessionLocal()
    analise = analisar_texto(texto)
    entidades = analise["entidades"]
    sugestoes_similares = buscar_similares(texto)
    sugestoes_clausulas = sugerir_clausulas_por_entidade(entidades)

    nova_entrada = Entrada(texto=texto)
    session.add(nova_entrada)
    session.commit()

    for ent_text, ent_label in entidades:
        session.add(Entidade(texto=ent_text, tipo=ent_label, entrada_id=nova_entrada.id))

    for artigo in sugestoes_similares:
        session.add(Sugestao(artigo=artigo["texto"], entrada_id=nova_entrada.id))

    session.commit()
    session.close()

    analise["sugestoes"] = sugestoes_similares
    analise["clausulas_sugeridas"] = sugestoes_clausulas
    return analise
