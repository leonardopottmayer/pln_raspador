import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Treinamento direto ao carregar
class ClassificadorClausulas:
    def __init__(self):
        df = pd.read_csv("data/Classificacao_Revisada.csv")
        df = df[df['classe'] != 'nao_classificado']
        self.vectorizer = TfidfVectorizer(max_features=3000)
        X = self.vectorizer.fit_transform(df['Texto Original'])
        y = df['classe']
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)

    def prever_classe(self, texto):
        X_input = self.vectorizer.transform([texto])
        return self.model.predict(X_input)[0]

classificador_global = ClassificadorClausulas()

def classificar_clausula(texto):
    return classificador_global.prever_classe(texto)