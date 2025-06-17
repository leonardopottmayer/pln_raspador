# 01

import time
import random
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Arquivos para salvar o progresso
ARQUIVO_LINKS = "links_jusbrasil.txt"
ARQUIVO_CHECKPOINT = "ultima_pagina.txt"
ARQUIVO_PAGINAS_ERRO = "paginas_erro.txt"

def salvar_pagina_erro(pagina, motivo):
    """
    Salva informações sobre páginas que falharam em um arquivo de registro.
    
    :param pagina: Número da página que falhou.
    :param motivo: Motivo da falha.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(ARQUIVO_PAGINAS_ERRO, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | Página {pagina} | Motivo: {motivo}\n")
    print(f"Registro de erro da página {pagina} salvo em {ARQUIVO_PAGINAS_ERRO}")

def salvar_link(link):
    """
    Salva um link no arquivo de links.
    Se o link já existir no arquivo, ele não será duplicado.
    
    :param link: URL a ser salva no arquivo.
    """
    # Verifica se o arquivo já existe e lê os links existentes
    links_existentes = set()
    if os.path.exists(ARQUIVO_LINKS):
        with open(ARQUIVO_LINKS, "r", encoding="utf-8") as f:
            links_existentes = {line.strip() for line in f if line.strip()}
    
    # Se o link ainda não existir, adiciona ao arquivo
    if link not in links_existentes:
        with open(ARQUIVO_LINKS, "a", encoding="utf-8") as f:
            f.write(f"{link}\n")
        return True
    return False

def carregar_checkpoint():
    """
    Carrega o número da última página processada com sucesso.
    
    :return: Número da última página ou 1 se não houver checkpoint.
    """
    if os.path.exists(ARQUIVO_CHECKPOINT):
        try:
            with open(ARQUIVO_CHECKPOINT, "r") as f:
                ultima_pagina = int(f.read().strip())
                print(f"Checkpoint encontrado: última página processada foi {ultima_pagina}")
                return ultima_pagina
        except (ValueError, IOError) as e:
            print(f"Erro ao ler checkpoint: {e}. Iniciando da página 1.")
    
    return 1

def salvar_checkpoint(pagina):
    """
    Salva o número da página atual como checkpoint.
    
    :param pagina: Número da página a ser salva como checkpoint.
    """
    try:
        with open(ARQUIVO_CHECKPOINT, "w") as f:
            f.write(str(pagina))
        print(f"Checkpoint salvo: página {pagina}")
    except IOError as e:
        print(f"Erro ao salvar checkpoint: {e}")

def get_max_pages(url, proxies):
    """
    Acessa a URL inicial e tenta descobrir o número total de páginas.
    
    :param url: URL inicial para coletar o número de páginas.
    :param proxies: Lista de proxies no formato ["ip:porta", "ip:porta", ...].
    :return: Número estimado de páginas disponíveis.
    """
    print("Acessando URL inicial para descobrir o número total de páginas:", url)
    
    # Configurações para a primeira instância que detectará o número de páginas
    chrome_options = Options()
    # Usar um proxy aleatório para a verificação inicial
    proxy_inicial = random.choice(proxies)
    chrome_options.add_argument(f"--proxy-server=http://{proxy_inicial}")
    
    # Adicionar user-agent para parecer mais humano
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Configurações para evitar detecção
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--incognito")
    
    # Inicializa o driver com as opções
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    last_page = 50  # Um valor alto padrão para garantir que tente várias páginas
    
    print(f"Usando proxy {proxy_inicial} para verificação inicial de páginas")

    try:
        driver.get(url)
        time.sleep(random.uniform(3, 5))  # Aguardar carregamento inicial
        
        # Tenta obter o número máximo de páginas
        try:
            # Tentar diferentes seletores para a paginação
            paginacao_seletores = [
                "/html/body/div[1]/main/div[3]/div/div/div/div[2]/nav/div[1]/a[last()]/span",
                "//nav//a[last()]/span",
                "//div[contains(@class, 'pagination')]//a[last()]"
            ]
            
            for seletor in paginacao_seletores:
                try:
                    last_page_elements = driver.find_elements(By.XPATH, seletor)
                    if last_page_elements:
                        # Pegar o último elemento que parece ser um número
                        for element in last_page_elements:
                            texto = element.text.strip()
                            if texto.isdigit():
                                last_page = int(texto)
                                print(f"Número total de páginas: {last_page}")
                                break
                        if last_page > 1:  # Se encontramos um número válido, podemos parar
                            break
                except:
                    continue
            
            # Se não conseguir determinar o número de páginas
            if last_page == 50:
                print("Não foi possível determinar o número exato de páginas. Assumindo 50 páginas máximas.")
        except Exception as e:
            print("Erro ao obter número de páginas, assumindo 50 páginas máximas:", e)

    finally:
        driver.quit()
        
    return last_page

def processar_pagina(page, url_base, proxy, termo_busca):
    """
    Processa uma página específica para coletar links.
    
    :param page: Número da página a ser processada.
    :param url_base: URL base para a busca.
    :param proxy: Proxy a ser utilizado.
    :param termo_busca: Termo de busca utilizado na URL.
    :return: Tupla (sucesso, links_encontrados)
    """
    print(f"\n--- Processando Página {page} ---")
    print(f"Utilizando proxy: {proxy}")

    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server=http://{proxy}")
    
    # Adicionar user-agent para parecer mais humano
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Configurações para evitar detecção de automação
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Configurações adicionais para ajudar a evitar bloqueios
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--incognito")  # Modo anônimo
    
    # Desabilitar imagens para carregar mais rápido
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # Cria a instância do driver com o proxy escolhido
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Modifica o navigator.webdriver para evitar detecção
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    page_success = False
    links_na_pagina = 0
    erro_detalhes = "Motivo desconhecido"
    
    try:
        page_url = f"{url_base}?q={termo_busca}&p={page}"
        print(f"Acessando página: {page_url}")
        driver.get(page_url)

        # Manter um delay para não sobrecarregar o servidor e evitar bloqueios
        tempo_espera = random.uniform(5, 10)
        print(f"Aguardando {tempo_espera:.2f} segundos para carregamento da página...")
        time.sleep(tempo_espera)
        
        # Rolar a página suavemente para simular comportamento humano
        for _ in range(random.randint(2, 4)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
            time.sleep(random.uniform(0.5, 1.5))

        # Com base no exemplo fornecido, vamos usar o seletor CSS específico
        print("Tentando localizar links com seletor CSS específico...")
        elementos_link = driver.find_elements(By.CSS_SELECTOR, "a.link_root__cF5pa.link_typeprimary__tABe6")
        print(f"Encontrados {len(elementos_link)} elementos com o seletor CSS específico")
        
        # Se não encontrar elementos, tente um seletor mais amplo
        if not elementos_link or len(elementos_link) < 3:
            print("Usando seletor alternativo: links com classes específicas...")
            elementos_link = driver.find_elements(By.XPATH, "//a[contains(@class, 'link_root') and contains(@class, 'link_typeprimary')]")
            print(f"Encontrados {len(elementos_link)} elementos com o seletor alternativo")
        
        # Se ainda não encontrar, use um método mais genérico
        if not elementos_link or len(elementos_link) < 3:
            print("Tentando JavaScript para identificar os links específicos...")
            try:
                # Busca links com as classes específicas usando JavaScript
                elementos_link = driver.execute_script("""
                    return Array.from(document.querySelectorAll('a')).filter(function(a) {
                        return a.classList.contains('link_root__cF5pa') && 
                               a.classList.contains('link_typeprimary__tABe6');
                    });
                """)
                print(f"Encontrados {len(elementos_link)} elementos via JavaScript específico")
            except Exception as e:
                print(f"Erro ao executar JavaScript específico: {e}")
                erro_detalhes = f"Falha no JavaScript: {str(e)}"
        
        # Último recurso: capturar todos os links de artigos/notícias
        if not elementos_link or len(elementos_link) < 3:
            print("Tentando capturar qualquer link de artigo ou notícia...")
            try:
                elementos_link = driver.find_elements(By.XPATH, "//a[contains(@href, '/artigos/') or contains(@href, '/noticias/')]")
                print(f"Encontrados {len(elementos_link)} links de artigos/notícias")
            except Exception as e:
                print(f"Erro ao buscar links de artigos/notícias: {e}")
                erro_detalhes = f"Falha nos seletores alternativos: {str(e)}"
            
        print(f"Total de elementos de link encontrados na página: {len(elementos_link)}")
        
        if not elementos_link or len(elementos_link) == 0:
            erro_detalhes = "Nenhum elemento de link encontrado na página"
            
        # Extrair os links de cada elemento
        for elemento in elementos_link:
            try:
                # O modo de obtenção do href depende do tipo de objeto retornado
                href = None
                if isinstance(elemento, dict) and 'href' in elemento:  # Se for um dicionário de JavaScript
                    href = elemento['href']
                elif hasattr(elemento, 'get_attribute'):  # Se for um WebElement
                    href = elemento.get_attribute("href")
                elif isinstance(elemento, str):  # Se for diretamente uma string
                    href = elemento
                
                if href and ("/artigos/" in href or "/noticias/" in href):
                    # Salvar o link no arquivo
                    if salvar_link(href):
                        links_na_pagina += 1
                        print(f"Novo link encontrado e salvo: {href}")
                    else:
                        print(f"Link já existente: {href}")
            except Exception as e:
                print(f"Erro ao processar elemento de link: {e}")
                erro_detalhes = f"Falha ao extrair URL: {str(e)}"
        
        # Marcar como sucesso se encontrou pelo menos um link novo
        if links_na_pagina > 0:
            page_success = True
            print(f"Coleta bem-sucedida: {links_na_pagina} novos links salvos nesta página")
        else:
            erro_detalhes = "Nenhum novo link encontrado"
            print("Nenhum novo link encontrado nesta página")

    except Exception as e:
        erro_detalhes = str(e)
        print(f"Erro ao processar a página {page}: {e}")

    finally:
        driver.quit()
    
    # Se não teve sucesso, registra o erro em detalhes
    if not page_success:
        salvar_pagina_erro(page, erro_detalhes)
    
    return page_success, links_na_pagina

def get_links(url_base, proxies, paginas_a_processar):
    """
    Acessa a URL e processa as páginas selecionadas para coletar os links.
    
    :param url_base: URL base para a coleta.
    :param proxies: Lista de proxies no formato ["ip:porta", "ip:porta", ...].
    :param paginas_a_processar: Lista de números de páginas a serem processadas.
    :return: Número total de novos links coletados.
    """
    novos_links_total = 0
    paginas_com_erro = []
    
    # Ordena as páginas para processamento sequencial
    paginas_a_processar.sort()
    print(f"Páginas a serem processadas: {paginas_a_processar}")
    
    for page in paginas_a_processar:
        # Seleciona um proxy aleatório para esta página
        proxy = random.choice(proxies)
        
        tentativas = 0
        max_tentativas = 3  # Número máximo de tentativas por página
        sucesso = False
        
        while not sucesso and tentativas < max_tentativas:
            # Se não é a primeira tentativa, seleciona outro proxy
            if tentativas > 0:
                proxy = random.choice([p for p in proxies if p != proxy])
                print(f"Tentativa {tentativas+1}/{max_tentativas} para a página {page}")
                print(f"Usando proxy alternativo: {proxy}")
            
            sucesso, links_na_pagina = processar_pagina(page, url_base, proxy, termo_busca)
            novos_links_total += links_na_pagina
            
            if sucesso:
                # Salva a página como processada no checkpoint
                salvar_checkpoint(page)
            else:
                tentativas += 1
        
        # Se após todas as tentativas ainda não teve sucesso, registra a página com erro
        if not sucesso:
            motivo = f"Falha após {max_tentativas} tentativas com proxies diferentes"
            salvar_pagina_erro(page, motivo)
            paginas_com_erro.append(page)
        
        # Pausa entre páginas para parecer mais natural
        if page != paginas_a_processar[-1]:  # Se não for a última página
            pausa = random.uniform(2, 5)
            print(f"Aguardando {pausa:.2f} segundos antes de acessar a próxima página...")
            time.sleep(pausa)
    
    # Exibe resumo das páginas com erro no final
    if paginas_com_erro:
        print(f"\nATENÇÃO: {len(paginas_com_erro)} páginas apresentaram erros:")
        print(f"Páginas com erro: {paginas_com_erro}")
        print(f"Os detalhes foram salvos em {ARQUIVO_PAGINAS_ERRO}")
    
    return novos_links_total

def validar_entrada_paginas(entrada, max_pages):
    """
    Valida a entrada do usuário para as páginas a serem consultadas.
    
    :param entrada: String com páginas separadas por vírgula (ex: "1,3,5-7").
    :param max_pages: Número máximo de páginas disponíveis.
    :return: Lista de páginas a serem processadas.
    """
    paginas = set()
    
    if not entrada or entrada.lower() == "todas":
        # Se não especificar ou pedir "todas", retorna todas as páginas
        return list(range(1, max_pages + 1))
    
    try:
        # Divide a entrada por vírgulas
        partes = [parte.strip() for parte in entrada.split(",")]
        
        for parte in partes:
            if "-" in parte:  # É um intervalo (ex: 5-10)
                inicio, fim = parte.split("-")
                inicio, fim = int(inicio), int(fim)
                # Limita ao número máximo de páginas
                fim = min(fim, max_pages)
                # Adiciona todas as páginas no intervalo
                paginas.update(range(inicio, fim + 1))
            else:  # É um número único
                pagina = int(parte)
                if 1 <= pagina <= max_pages:
                    paginas.add(pagina)
    except ValueError as e:
        print(f"Erro ao processar entrada de páginas: {e}")
        print("Formato correto: números separados por vírgula (ex: 1,3,5) ou intervalos (ex: 2-4)")
        return []
    
    return sorted(list(paginas))

if __name__ == "__main__":
    # Caminho relativo para o arquivo valid_proxies.txt
    valid_proxies_path = "proxies_validos.txt"

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

    print(f"Carregados {len(valid_proxies)} proxies válidos.")
    
    # URL alvo para coleta dos links
    termo_busca = input("Digite o termo de busca (padrão: contrato): ") or "contrato"
    url_inicial = f"https://www.jusbrasil.com.br/artigos-noticias/busca"
    
    # Descobrir o número total de páginas disponíveis
    max_pages = get_max_pages(f"{url_inicial}?q={termo_busca}", valid_proxies)
    
    # Perguntar ao usuário quais páginas deseja processar
    ultima_pagina = carregar_checkpoint()
    print(f"\nNúmero máximo de páginas: {max_pages}")
    print(f"Última página processada anteriormente: {ultima_pagina - 1 if ultima_pagina > 1 else 'Nenhuma'}")
    
    print("\nOpções para seleção de páginas:")
    print("1. Digite números específicos separados por vírgula (ex: 1,3,5)")
    print("2. Digite intervalos (ex: 5-10)")
    print("3. Combine ambos (ex: 1,3,5-7,10)")
    print("4. Digite 'todas' para processar todas as páginas")
    print("5. Pressione Enter para continuar de onde parou")
    
    entrada_paginas = input("\nQuais páginas deseja consultar? ")
    
    if not entrada_paginas.strip():
        # Se não especificar, começa da última página processada
        paginas_a_processar = list(range(ultima_pagina, max_pages + 1))
        print(f"Continuando a partir da página {ultima_pagina} até a página {max_pages}")
    else:
        paginas_a_processar = validar_entrada_paginas(entrada_paginas, max_pages)
    
    if not paginas_a_processar:
        print("Nenhuma página válida selecionada. Encerrando.")
        exit(1)
    
    # Executa a coleta das páginas selecionadas
    try:
        total_novos_links = get_links(url_inicial, valid_proxies, paginas_a_processar)
        print(f"\nColeta concluída! {total_novos_links} novos links foram salvos em {ARQUIVO_LINKS}")
    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário. O progresso foi salvo.")
        
    # Conta quantos links foram coletados no total
    total_links = 0
    if os.path.exists(ARQUIVO_LINKS):
        with open(ARQUIVO_LINKS, "r", encoding="utf-8") as f:
            total_links = sum(1 for _ in f)
    
    print(f"\nTotal de links salvos no arquivo: {total_links}")
    print(f"Os links foram salvos em: {os.path.abspath(ARQUIVO_LINKS)}")
    print(f"O checkpoint foi salvo em: {os.path.abspath(ARQUIVO_CHECKPOINT)}")
    
    # Verificar se existem páginas com erro
    if os.path.exists(ARQUIVO_PAGINAS_ERRO):
        with open(ARQUIVO_PAGINAS_ERRO, "r", encoding="utf-8") as f:
            total_erros = sum(1 for _ in f)
        if total_erros > 0:
            print(f"Foram registradas {total_erros} ocorrências de erros em páginas.")
            print(f"Consulte o arquivo {os.path.abspath(ARQUIVO_PAGINAS_ERRO)} para ver os detalhes.")