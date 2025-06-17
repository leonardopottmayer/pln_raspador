# training/train_finetune_embeddings.py
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Carregar CSV
df = pd.read_csv("data/Classificacao_Revisada.csv")
df = df[df['classe'] != 'nao_classificado']

# Codificar rótulos como números
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(df['classe'])

# Criar exemplos para fine-tuning
train_examples = [
    InputExample(texts=[text], label=float(label))
    for text, label in zip(df['Texto Original'], labels)
]

# Dataloader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Carregar modelo base
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

# Loss
train_loss = losses.CosineSimilarityLoss(model)

# Treinar modelo
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=10)

# Salvar modelo
model.save("modelo_juridico_finetuned")
