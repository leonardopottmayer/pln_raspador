# 11

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report)
from imblearn.over_sampling import RandomOverSampler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold, cross_val_predict

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalMaxPooling1D, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


# 🔗 Carregamento dos Dados
df = pd.read_csv('src/conteudos_processados.csv', sep=';')
df_classe = pd.read_csv('src/Classificacao_Revisada.csv', sep=';')

df['classe'] = df_classe['classe']

categorias = df['classe'].unique()
mapa_classes = {cat: idx for idx, cat in enumerate(categorias)}
df['classe_num'] = df['classe'].map(mapa_classes)

print("Mapa de Classes:", mapa_classes)

# 🔍 Limpeza
df['processado'].fillna(' ', inplace=True)
df.dropna(subset=['processado'], inplace=True)

X = df['processado']
y = df['classe_num']


vocab_size = 10000
max_length = 100
oov_token = "<OOV>"

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(X)

X_seq = tokenizer.texts_to_sequences(X)
X_pad = pad_sequences(X_seq, maxlen=max_length, padding='post', truncating='post')


vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, ngram_range=(1,2))
X_tfidf = vectorizer.fit_transform(X)


ros = RandomOverSampler(random_state=42)
X_pad_res, y_res = ros.fit_resample(X_pad, y)         # Para Redes Neurais
X_tfidf_res, y_res_tfidf = ros.fit_resample(X_tfidf, y) # Para NB e SVM


print("\nDistribuição após balanceamento:")
print(pd.Series(y_res).value_counts())


skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


def avaliar_sklearn(modelo, nome, X, y):
    print(f"\n===== Avaliando {nome} =====")
    y_pred = cross_val_predict(modelo, X, y, cv=skf)

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, average='weighted')
    rec = recall_score(y, y_pred, average='weighted')
    f1 = f1_score(y, y_pred, average='weighted')

    print(f"Acurácia: {acc:.4f}")
    print(f"Precisão: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-Score: {f1:.4f}\n")

    print(classification_report(y, y_pred, zero_division=0))

    cm = confusion_matrix(y, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Matriz de Confusão - {nome}')
    plt.xlabel('Previsto')
    plt.ylabel('Real')
    plt.show()


def criar_modelo(input_length, num_classes, vocab_size):
    modelo = Sequential([
        Embedding(input_dim=vocab_size, output_dim=64, input_length=input_length),
        GlobalMaxPooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    modelo.compile(optimizer='adam',
                   loss='sparse_categorical_crossentropy',
                   metrics=['accuracy'])
    return modelo


def avaliar_rede_neural(X, y):
    print("\n===== Avaliando Rede Neural =====")
    y_true_total = []
    y_pred_total = []

    num_classes = len(np.unique(y))

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n--- Fold {fold + 1} ---")

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        modelo = criar_modelo(input_length=max_length, num_classes=num_classes, vocab_size=vocab_size)

        modelo.fit(X_train, y_train,
                   epochs=10,
                   batch_size=32,
                   validation_data=(X_test, y_test),
                   verbose=0)

        y_pred_proba = modelo.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)

        y_true_total.extend(y_test)
        y_pred_total.extend(y_pred)

        acc = accuracy_score(y_test, y_pred)
        print(f"Acurácia no Fold {fold + 1}: {acc:.4f}")

    acc = accuracy_score(y_true_total, y_pred_total)
    prec = precision_score(y_true_total, y_pred_total, average='weighted')
    rec = recall_score(y_true_total, y_pred_total, average='weighted')
    f1 = f1_score(y_true_total, y_pred_total, average='weighted')

    print(f"\nAcurácia: {acc:.4f}")
    print(f"Precisão: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-Score: {f1:.4f}")

    print("\nRelatório de Classificação:")
    print(classification_report(y_true_total, y_pred_total, zero_division=0))

    cm = confusion_matrix(y_true_total, y_pred_total)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Purples')
    plt.title('Matriz de Confusão - Rede Neural')
    plt.xlabel('Previsto')
    plt.ylabel('Real')
    plt.show()


# Execução dos Modelos

# Naive Bayes
nb_model = MultinomialNB()
avaliar_sklearn(nb_model, "Naive Bayes", X_tfidf_res, y_res_tfidf)

# SVM Linear
svm_model = SVC(kernel='linear', C=1.0, class_weight='balanced', probability=True)
avaliar_sklearn(svm_model, "SVM Linear", X_tfidf_res, y_res_tfidf)

# Rede Neural
avaliar_rede_neural(X_pad_res, y_res)
