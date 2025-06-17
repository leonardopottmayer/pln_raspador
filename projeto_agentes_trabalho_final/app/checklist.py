TERMO_CLAUSULAS = [
    "rescisao",
    "prazo",
    "confidencialidade",
    "pagamento",
    "multa",
    "jurisdicao"
]

def aplicar_checklist(texto):
    encontrados = []
    for termo in TERMO_CLAUSULAS:
        if termo in texto:
            encontrados.append(termo)
    return encontrados
