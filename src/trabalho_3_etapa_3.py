# 12

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# ======================
# 1. Carregar o CSV
# ======================
caminho_csv = "../saida/frases_features.csv"  # ajuste se necessário
df = pd.read_csv(caminho_csv)

# ======================
# 2. Limpeza e Rotulagem
# ======================
df['entidades_nomeadas'] = df['entidades_nomeadas'].fillna('').astype(str)

def gerar_classe(entidades_str):
    entidades_str = entidades_str.lower()
    if 'contrato' in entidades_str or 'rescisão' in entidades_str:
        return 'Contrato Geral'
    elif 'trabalho' in entidades_str or 'emprego' in entidades_str:
        return 'Trabalho/Emprego'
    elif 'locação' in entidades_str or 'imóvel' in entidades_str:
        return 'Locação'
    elif 'compra' in entidades_str or 'venda' in entidades_str:
        return 'Compra e Venda'
    elif 'assinatura' in entidades_str or 'testemunha' in entidades_str:
        return 'Assinatura/Testemunha'
    elif 'licitação' in entidades_str or 'pública' in entidades_str:
        return 'Licitações Públicas'
    elif 'nascimento' in entidades_str:
        return 'Registro Civil'
    elif 'falência' in entidades_str or 'recuperação' in entidades_str:
        return 'Falência/Recuperação'
    elif 'tributo' in entidades_str or 'imposto' in entidades_str:
        return 'Tributário'
    elif 'judicial' in entidades_str or 'ação' in entidades_str:
        return 'Processo Judicial'
    return 'Outro'

df['classe'] = df['entidades_nomeadas'].apply(gerar_classe)

# ======================
# 3. Vetorização
# ======================
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df['entidades_nomeadas'])

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['classe'])

# ======================
# 4. Treino/Teste
# ======================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ======================
# 5. Classificadores
# ======================
models = {
    'Naive Bayes': MultinomialNB(),
    'SVM': LinearSVC(),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
}

results = {}

for nome, modelo in models.items():
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    results[nome] = {
        'accuracy': accuracy_score(y_test, y_pred),
        'report': classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
    }

# ======================
# 6. Comparação de Métricas
# ======================
report_data = []

for nome, resultado in results.items():
    for classe, valores in resultado['report'].items():
        if isinstance(valores, dict) and classe in label_encoder.classes_:
            report_data.append({
                'Modelo': nome,
                'Classe': classe,
                'Precisao': valores['precision'],
                'Revocacao': valores['recall'],
                'F1-Score': valores['f1-score']
            })

df_resultados = pd.DataFrame(report_data)
print(df_resultados)

# ======================
# 7. Visualização opcional
# ======================
plt.figure(figsize=(12, 6))
sns.barplot(data=df_resultados, x='Classe', y='F1-Score', hue='Modelo')
plt.xticks(rotation=45, ha='right')
plt.title('Comparação de F1-Score por Classe e Modelo')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.barplot(data=df_resultados, x='Classe', y='Revocacao', hue='Modelo')
plt.xticks(rotation=45, ha='right')
plt.title('Comparação de Revocação por Classe e Modelo')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.barplot(data=df_resultados, x='Classe', y='Precisao', hue='Modelo')
plt.xticks(rotation=45, ha='right')
plt.title('Comparação de Precisão por Classe e Modelo')
plt.tight_layout()
plt.show()