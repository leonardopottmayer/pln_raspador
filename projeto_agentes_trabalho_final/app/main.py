from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from app.orchestrator import processar_texto
from app.web import render_html

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def form():
    return render_html()

@app.post("/analise/", response_class=HTMLResponse)
def analisar(texto: str = Form(...)):
    resultado = processar_texto(texto)
    return render_html(resultado)
