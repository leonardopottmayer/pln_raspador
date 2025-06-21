def render_html(resultado=None):
    html = """
    <html>
        <head><title>Análise Jurídica</title></head>
        <body>
            <h1>Analisador Jurídico</h1>
            <form method='post' action='/analise/'>
                <textarea name='texto' rows='10' cols='80'></textarea><br>
                <input type='submit' value='Analisar'>
            </form>
    """
    if resultado:
        html += "<h2>Classe Predita:</h2><p>" + resultado['classe_predita'] + "</p>"
        html += "<h2>Entidades:</h2><ul>" + ''.join([f"<li>{e}</li>" for e in resultado['entidades']]) + "</ul>"
        html += "<h2>Datas:</h2><ul>" + ''.join([f"<li>{d}</li>" for d in resultado['datas']]) + "</ul>"
        html += "<h2>Valores:</h2><ul>" + ''.join([f"<li>{v}</li>" for v in resultado['valores']]) + "</ul>"
        html += "<h2>Checklist:</h2><ul>" + ''.join([f"<li>{c}</li>" for c in resultado['checklist']]) + "</ul>"
        html += "<h2>Artigos sugeridos:</h2><ul>" + ''.join([f"<li>{a['texto']} ({a['classe']})</li>" for a in resultado['sugestoes']]) + "</ul>"
    html += "</body></html>"
    return html