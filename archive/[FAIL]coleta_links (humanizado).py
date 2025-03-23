from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import json
import random
import os
from selenium.webdriver.common.action_chains import ActionChains

# Corrigindo o seletor CSS - adicionando pontos antes das classes
CSS_SELECTOR_URLS = '.link_root__cF5pa.link_typeprimary__tABe6'

# Nome do arquivo para salvar os links
ARQUIVO_LINKS = "links_artigos_jusbrasil.json"

# Configuração do WebDriver com user-agent de navegador comum
chrome_options = Options()
# Configuração para tela cheia
chrome_options.add_argument("--start-maximized")  # Maximiza a janela do Chrome
chrome_options.add_argument("--disable-extensions")
# Adicionar um user-agent realista
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
# Configurações para evitar detecção de automação
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Inicializar o WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Modifica o navigator.webdriver para evitar detecção
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# URL de busca
url_base = "https://www.jusbrasil.com.br/artigos-noticias/busca?q=contrato"

# Função para carregar links previamente salvos (se existirem)
def carregar_links_salvos():
    if os.path.exists(ARQUIVO_LINKS):
        try:
            with open(ARQUIVO_LINKS, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Erro ao carregar arquivo JSON existente. Criando nova lista.")
    return []

# Lista para armazenar os links coletados - carregando dados existentes se houver
links_artigos = carregar_links_salvos()
print(f"Carregados {len(links_artigos)} links de coleta anterior.")

# Função para salvar os links no arquivo JSON
def salvar_links():
    try:
        with open(ARQUIVO_LINKS, "w", encoding="utf-8") as f:
            json.dump(links_artigos, f, ensure_ascii=False, indent=4)
        print(f"Links salvos em {ARQUIVO_LINKS}. Total: {len(links_artigos)}")
        return True
    except Exception as e:
        print(f"Erro ao salvar links: {e}")
        return False

# Função para mover mouse de forma segura (sem sair dos limites)
def mover_mouse_com_seguranca(elemento):
    try:
        # Usar move_to_element é mais seguro, pois ele se move para o centro do elemento
        action = ActionChains(driver)
        action.move_to_element(elemento).perform()
        time.sleep(random.uniform(0.3, 0.7))
        return True
    except WebDriverException as e:
        print(f"Erro ao mover o mouse: {e}")
        return False

# Função para rolar a página como um humano - versão mais segura
def rolar_pagina_naturalmente():
    try:
        # Rolar para baixo com menor quantidade de rolagens
        for _ in range(random.randint(2, 4)):
            # Usar valores mais conservadores para rolagem
            driver.execute_script(f"window.scrollBy(0, {random.randint(100, 200)});")
            time.sleep(random.uniform(0.5, 1.0))
        return True
    except Exception as e:
        print(f"Erro ao rolar página: {e}")
        return False

# Função para lidar com possíveis captchas
def verificar_captcha():
    try:
        # Procurar elementos comuns em páginas de captcha
        captcha_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'captcha') or contains(text(), 'Captcha') or contains(text(), 'verificação') or contains(text(), 'desafio')]")
        if captcha_elements:
            print("ALERTA: Possível captcha detectado! Aguardando 30 segundos para resolução manual...")
            # Salvar screenshot para verificação
            driver.save_screenshot("captcha_detectado.png")
            # Aguardar tempo para possível intervenção manual
            time.sleep(30)
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar captcha: {e}")
        return False

# Função para coletar links da página atual com comportamento mais natural
def coletar_links_pagina():
    links_obtidos_nesta_pagina = 0
    try:
        print("Aguardando carregamento dos elementos de link...")
        
        # Verificar se tem captcha
        if verificar_captcha():
            print("Continuando após verificação de captcha...")
        
        # Simular rolagem natural antes de procurar elementos
        rolar_pagina_naturalmente()
        
        # Esperamos com tempo variável - reduzindo para valores mais razoáveis
        tempo_espera = random.uniform(8, 12)
        WebDriverWait(driver, tempo_espera).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTOR_URLS))
        )
        
        # Pequena pausa aleatória
        time.sleep(random.uniform(1, 2))
        
        # Encontrar todos os elementos de link
        elementos_link = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTOR_URLS)
        print(f"Encontrados {len(elementos_link)} elementos de link na página")
        
        if len(elementos_link) == 0:
            print("Tentando outro seletor para verificação...")
            links_alternativos = driver.find_elements(By.TAG_NAME, "a")
            print(f"Encontrados {len(links_alternativos)} elementos <a> na página")
            
            # Mostrar alguns dos links encontrados para análise
            for i, link in enumerate(links_alternativos[:5]):
                print(f"Link alternativo {i+1}: {link.get_attribute('href')}")
        
        # Extrair URLs dos elementos
        for elemento in elementos_link:
            try:
                # Ocasionalmente, mover o mouse sobre o elemento (mas com menos frequência)
                if random.random() > 0.7:  # Apenas 30% das vezes
                    mover_mouse_com_seguranca(elemento)
                
                link = elemento.get_attribute("href")
                if link and link not in links_artigos:
                    links_artigos.append(link)
                    links_obtidos_nesta_pagina += 1
                    print(f"Link encontrado: {link}")
                    
                    # Salvar a cada novo link
                    if links_obtidos_nesta_pagina % 3 == 0:  # Aumentamos a frequência de salvamento
                        salvar_links()
            except Exception as e:
                print(f"Erro ao processar elemento de link: {e}")
                continue
        
        # Salvar todos os links após processar a página
        if links_obtidos_nesta_pagina > 0:
            salvar_links()
            
        return len(elementos_link) > 0
        
    except TimeoutException:
        print("Timeout ao esperar pelos links na página atual")
        # Salvar mesmo em caso de timeout
        if links_obtidos_nesta_pagina > 0:
            salvar_links()
        return False
    except Exception as e:
        print(f"Erro não esperado durante coleta de links: {e}")
        # Salvar em caso de qualquer erro
        if links_obtidos_nesta_pagina > 0:
            salvar_links()
        return False

# Navegar para a primeira página com comportamento natural
print(f"Navegando para a URL: {url_base}")
driver.get(url_base)

# Tempo de carregamento inicial variável - reduzido
tempo_inicial = random.uniform(3, 5)
print(f"Aguardando {tempo_inicial:.2f} segundos para carregamento inicial...")
time.sleep(tempo_inicial)

# Maximizar a janela para garantir tela cheia
driver.maximize_window()

# Simular interação inicial com a página
rolar_pagina_naturalmente()

# Contador de páginas
pagina_atual = 1
max_paginas = 50

# Verificar se há um arquivo de checkpoint para a última página acessada
ARQUIVO_CHECKPOINT = "ultima_pagina.txt"
if os.path.exists(ARQUIVO_CHECKPOINT):
    with open(ARQUIVO_CHECKPOINT, "r") as f:
        try:
            ultimo_checkpoint = int(f.read().strip())
            if 1 <= ultimo_checkpoint <= max_paginas:
                pagina_atual = ultimo_checkpoint
                print(f"Retomando da página {pagina_atual} conforme checkpoint.")
        except ValueError:
            print("Erro ao ler checkpoint. Iniciando da página 1.")

# Iterar pelas páginas com comportamento humano
while pagina_atual <= max_paginas:
    print(f"\nColetando links da página {pagina_atual}")
    
    # Salvar checkpoint da página atual
    with open(ARQUIVO_CHECKPOINT, "w") as f:
        f.write(str(pagina_atual))
    
    # Coletar links da página atual
    sucesso = coletar_links_pagina()
    if not sucesso:
        print(f"Falha ao coletar links da página {pagina_atual}")
        print("Tentando screenshot para análise...")
        try:
            driver.save_screenshot(f"pagina_{pagina_atual}.png")
            print(f"Screenshot salvo como pagina_{pagina_atual}.png")
        except Exception as e:
            print(f"Erro ao salvar screenshot: {e}")
        
        # Aguardar um tempo e tentar novamente em vez de pausar para intervenção
        print(f"Aguardando 15 segundos antes de tentar novamente a página {pagina_atual}...")
        time.sleep(15)
        
        # Segunda tentativa
        print(f"Tentando coletar links da página {pagina_atual} novamente...")
        sucesso = coletar_links_pagina()
        if not sucesso:
            print(f"Falha na segunda tentativa. Prosseguindo para a próxima página...")
    
    # Verificar se existe próxima página com abordagem mais natural
    try:
        print("Procurando botão de próxima página...")
        botao_proximo = driver.find_element(By.CSS_SELECTOR, "[aria-label='próxima página']")
        aria_disabled = botao_proximo.get_attribute("aria-disabled")
        
        print(f"Botão de próxima página encontrado. Estado aria-disabled: {aria_disabled}")
        
        # Se o botão estiver desabilitado, sair do loop
        if aria_disabled == "true":
            print("Última página alcançada.")
            break
        
        # Simular comportamento humano antes de clicar - usando método mais seguro
        print("Movendo para o botão de próxima página...")
        mover_mouse_com_seguranca(botao_proximo)
        
        # Adicionar pausa aleatória antes de clicar
        pausa_pre_clique = random.uniform(0.5, 1.5)
        print(f"Aguardando {pausa_pre_clique:.2f} segundos antes de clicar...")
        time.sleep(pausa_pre_clique)
        
        # Clicar no botão de próxima página
        print("Clicando no botão de próxima página...")
        botao_proximo.click()
        pagina_atual += 1
        
        # Atualizar checkpoint após avançar para a próxima página
        with open(ARQUIVO_CHECKPOINT, "w") as f:
            f.write(str(pagina_atual))
        
        # Tempo variável para carregar a próxima página - reduzido
        tempo_carregamento = random.uniform(2, 5)
        print(f"Aguardando {tempo_carregamento:.2f} segundos para carregar a nova página...")
        time.sleep(tempo_carregamento)
        
        # Verificar captcha após mudar de página
        verificar_captcha()
        
    except NoSuchElementException:
        print("Botão de próxima página não encontrado.")
        print("Elementos de navegação disponíveis:")
        try:
            nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav button")
            for i, elem in enumerate(nav_elements):
                print(f"Elemento de navegação {i+1}: {elem.get_attribute('outerHTML')}")
        except Exception as e:
            print(f"Erro ao listar elementos de navegação: {e}")
        break
    except Exception as e:
        print(f"Erro ao navegar para a próxima página: {e}")
        salvar_links()  # Salvamos o progresso
        print(f"Aguardando 15 segundos antes de tentar novamente...")
        time.sleep(15)
        # Tentativa de contornar o erro
        try:
            # Tentar recarregar a página atual
            driver.refresh()
            time.sleep(5)
            print("Página recarregada. Tentando novamente...")
        except Exception as refresh_error:
            print(f"Erro ao recarregar a página: {refresh_error}")
            # Se falhar completamente, vamos para a próxima página
            pagina_atual += 1
            print(f"Pulando para a página {pagina_atual}...")

print(f"\nColeta finalizada. Total de {len(links_artigos)} links coletados e salvos em {ARQUIVO_LINKS}")

# Fechar o navegador automaticamente
driver.quit()