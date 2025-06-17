# Projeto Agentes Jurídicos com IA

Este projeto implementa uma arquitetura baseada em **três agentes de IA** para análise de textos jurídicos, sugestão de cláusulas e retorno de artigos relevantes, com persistência em banco de dados e interface web.

---

## 🧠 Arquitetura de Agentes

- **Agente 1 (NLP)**: Extração de entidades, datas, valores e cláusulas com spaCy + regex.
- **Agente 2 (Similaridade)**: Busca de artigos semelhantes com embeddings e FAISS, usando `Classificacao_Revisada.csv`.
- **Agente 0 (Orquestrador)**: Coordena entrada, processamento, persistência e resposta.

---

## 📂 Estrutura de Pastas

```
app/
├── main.py               # FastAPI + rotas
├── nlp.py                # Agente 1: NLP com spaCy
├── similarity.py         # Agente 2: Embeddings + FAISS
├── orchestrator.py       # Agente 0: Coordenação
├── checklist.py          # Heurísticas para termos comuns
├── web.py                # Interface web HTML
database/
├── connection.py         # Conexão PostgreSQL
models/
├── schema.py             # SQLAlchemy ORM
training/
├── train_finetune_embeddings.py  # Script de fine-tuning
data/
├── Classificacao_Revisada.csv    # Base jurídica rotulada
```

---

## ▶️ Como Rodar Localmente

### 1. Clonar o projeto
```bash
unzip projeto_agentes_ia_completo.zip
cd projeto_agentes_ia_completo
```

### 2. Subir com Docker
```bash
docker-compose up --build
```

Acesse `http://localhost:8000` para abrir a interface web.

---

## 🧪 Treinar o Modelo de Similaridade (opcional)
```bash
pip install -r requirements.txt
python training/train_finetune_embeddings.py
```

Isso criará a pasta `modelo_juridico_finetuned/`, usada automaticamente pelo sistema.

---

## 🗃️ Banco de Dados
- PostgreSQL via Docker
- Tabelas: `usuarios`, `entradas`, `entidades`, `sugestoes`

---

## 📈 Tecnologias
- FastAPI
- spaCy (`pt_core_news_lg`)
- sentence-transformers (`distiluse-base-multilingual-cased-v1`)
- FAISS
- SQLAlchemy
- PostgreSQL

---

## 👨‍⚖️ Base Jurídica
O sistema usa textos reais rotulados (coluna `classe`) como base de conhecimento. Não depende de `artigos.json` estático.

---
