from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import os

# Carregar os links dos artigos
with open("links_artigos_jusbrasil.json", "r", encoding="utf-8") as f:
    links_artigos = json.load(f)

# Configuração do WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")

# Inicializar o WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Criar pasta para salvar os textos, se não existir
if not os.path.exists("artigos_jusbrasil"):
    os.makedirs("artigos_jusbrasil")

# Coletar texto de cada artigo
for i, link in enumerate(links_artigos):
    try:
        print(f"Processando artigo {i+1}/{len(links_artigos)}: {link}")
        
        # Navegar para o link do artigo
        driver.get(link)
        time.sleep(3)  # Aguardar carregamento da página
        
        # Esperar que o conteúdo do artigo carregue
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # Extrair o título
        try:
            titulo = driver.find_element(By.TAG_NAME, "h1").text
        except:
            titulo = f"Artigo_{i+1}"
        
        # Extrair o conteúdo do artigo
        # O seletor exato pode variar dependendo da estrutura da página
        try:
            conteudo = driver.find_element(By.TAG_NAME, "article").text
        except:
            try:
                # Tentar um seletor alternativo se o primeiro falhar
                conteudo = driver.find_element(By.CLASS_NAME, "content").text
            except:
                conteudo = "Não foi possível extrair o conteúdo deste artigo."
        
        # Criar um dicionário com as informações do artigo
        artigo_info = {
            "titulo": titulo,
            "url": link,
            "conteudo": conteudo
        }
        
        # Salvar o artigo em um arquivo JSON
        nome_arquivo = f"artigos_jusbrasil/artigo_{i+1}.json"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(artigo_info, f, ensure_ascii=False, indent=4)
        
        print(f"Artigo salvo em {nome_arquivo}")
        
        # Breve pausa para não sobrecarregar o servidor
        time.sleep(2)
        
    except Exception as e:
        print(f"Erro ao processar o artigo {i+1}: {e}")

# Fechar o navegador
driver.quit()

print("\nColeta de artigos finalizada!")