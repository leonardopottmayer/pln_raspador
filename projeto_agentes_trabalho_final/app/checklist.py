TERMO_CLAUSULAS = [
    "rescisão",
    "prazo",
    "confidencialidade",
    "pagamento",
    "multa",
    "jurisdição"
]

def aplicar_checklist(texto):
    encontrados = []
    for termo in TERMO_CLAUSULAS:
        if termo in texto:
            encontrados.append(termo)
    return encontrados
