import time
import random
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_links(url, proxies):
    """
    Acessa a URL e percorre todas as páginas para coletar os links.
    A cada página, utiliza um proxy diferente (selecionado aleatoriamente).
    
    :param url: URL inicial para coletar o número de páginas.
    :param proxies: Lista de proxies no formato ["ip:porta", "ip:porta", ...].
    :return: Lista de links coletados de todas as páginas.
    """
    print("Acessando URL inicial:", url)
    
    # Antes de tudo, precisamos abrir uma instância só para descobrir o total de páginas.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    links = []
    last_page = 1  # Valor padrão caso não seja possível encontrar o número de páginas

    try:
        driver.get(url)
        
        # Tenta obter o número máximo de páginas
        try:
            last_page_element = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/main/div[3]/div/div/div/div[2]/nav/div[1]/a[last()]/span"
            )
            last_page = int(last_page_element.text)
            print(f"Número total de páginas: {last_page}")
        except Exception as e:
            print("Erro ao obter número de páginas, assumindo apenas 1 página:", e)

    finally:
        driver.quit()

    # Agora, para cada página, vamos abrir uma nova instância de navegador
    # com um proxy diferente
    for page in range(1, last_page + 1):
        proxy = random.choice(proxies)  # Seleciona um proxy aleatório
        print(f"\n--- Página {page}/{last_page} ---")
        print(f"Utilizando proxy: {proxy}")

        chrome_options = Options()
        chrome_options.add_argument(f"--proxy-server=http://{proxy}")

        # Cria a instância do driver com o proxy escolhido
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            page_url = f"https://www.jusbrasil.com.br/artigos-noticias/busca?q=contrato&p={page}"
            print(f"Acessando página: {page_url}")
            driver.get(page_url)

            # Manter um delay para não sobrecarregar o servidor e evitar bloqueios
            time.sleep(10)  # Ajuste conforme necessário

            # Buscar elementos com a classe especificada
            elements = driver.find_elements(By.CLASS_NAME, "link_root__cF5pa.link_typeprimary__tABe6")
            print("Elementos principais encontrados na página:", len(elements))
            
            # Extrair os links de cada elemento
            for element in elements:
                href = element.get_attribute("href")
                if href:
                    links.append(href)

        except Exception as e:
            print(f"Erro ao processar a página {page_url}: {e}")

        finally:
            driver.quit()

    return links

if __name__ == "__main__":
    # Caminho relativo para o arquivo valid_proxies.txt (uma pasta acima)
    valid_proxies_path = os.path.join("valid_proxies.txt")

    # Lê a lista de proxies válidas do arquivo
    valid_proxies = []
    try:
        with open(valid_proxies_path, "r", encoding="utf-8") as f:
            valid_proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{valid_proxies_path}' não encontrado. Execute primeiro o 'proxy_validator.py' (ou verifique o caminho).")
        exit(1)

    if not valid_proxies:
        print(f"Nenhuma proxy válida encontrada em '{valid_proxies_path}'. Encerrando.")
        exit(1)

    # URL alvo para coleta dos links
    url_inicial = "https://www.jusbrasil.com.br/artigos-noticias/busca?q=contrato"

    # Executa a coleta
    todos_os_links = get_links(url_inicial, valid_proxies)

    print("\n--- Links coletados ---")
    for link in todos_os_links:
        print(link)
