import os
import time
import random
import re
import hashlib
from urllib.parse import urlparse
import concurrent.futures

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Arquivos para controle e registro
ARQUIVO_LINKS = "links_jusbrasil.txt"  # Arquivo com os links para processar
ARQUIVO_SUCESSO = "links_coletados.txt"  # Links coletados com sucesso
ARQUIVO_FALHA = "links_nao_coletados.txt"  # Links que falharam na coleta
DIRETORIO_CONTEUDO = "conteudos"  # Diretório para salvar os arquivos de conteúdo

# Configurações para controle de acesso
MAX_WORKERS = 3  # Número máximo de threads simultâneas
TEMPO_ESPERA_MIN = 2  # Tempo mínimo de espera entre acessos (segundos)
TEMPO_ESPERA_MAX = 5  # Tempo máximo de espera entre acessos (segundos)
MAX_TENTATIVAS = 3  # Número máximo de tentativas por URL

def carregar_proxies():
    """
    Carrega a lista de proxies válidos do arquivo.
    """
    proxies = []
    try:
        with open("proxies_validos.txt", "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"Carregados {len(proxies)} proxies válidos.")
    except FileNotFoundError:
        print("Arquivo de proxies não encontrado. Prosseguindo sem proxies.")
    
    return proxies

def carregar_links():
    """
    Carrega a lista de links do arquivo.
    Retorna dois conjuntos: links já coletados e links pendentes.
    """
    if not os.path.exists(ARQUIVO_LINKS):
        print(f"Arquivo {ARQUIVO_LINKS} não encontrado.")
        return set(), set()
    
    # Carregar todos os links
    with open(ARQUIVO_LINKS, "r", encoding="utf-8") as f:
        todos_links = {line.strip() for line in f if line.strip()}
    
    # Carregar links já coletados com sucesso (se o arquivo existir)
    links_coletados = set()
    if os.path.exists(ARQUIVO_SUCESSO):
        with open(ARQUIVO_SUCESSO, "r", encoding="utf-8") as f:
            links_coletados = {line.strip() for line in f if line.strip()}
    
    # Carregar links que falharam (se o arquivo existir)
    links_falha = set()
    if os.path.exists(ARQUIVO_FALHA):
        with open(ARQUIVO_FALHA, "r", encoding="utf-8") as f:
            links_falha = {line.strip() for line in f if line.strip()}
    
    # Links pendentes são todos menos os já coletados e os que já falharam definitivamente
    links_pendentes = todos_links - links_coletados - links_falha
    
    print(f"Total de links carregados: {len(todos_links)}")
    print(f"Links já coletados com sucesso: {len(links_coletados)}")
    print(f"Links marcados como falha: {len(links_falha)}")
    print(f"Links pendentes para coleta: {len(links_pendentes)}")
    
    return links_coletados, links_pendentes

def gerar_nome_arquivo(url):
    """
    Gera um nome de arquivo baseado na URL, removendo caracteres inválidos
    e limitando o tamanho para evitar nomes muito longos.
    """
    # Extrair partes da URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Remover barras, substituir por underscore e limitar tamanho
    nome_base = path.replace('/', '_').strip('_')
    
    # Se o nome base for muito longo, usar um hash da URL
    if len(nome_base) > 100:
        hash_url = hashlib.md5(url.encode()).hexdigest()
        nome_base = nome_base[:50] + '_' + hash_url[:10]
    
    # Garantir que o nome seja seguro para o sistema de arquivos
    nome_base = re.sub(r'[\\/*?:"<>|]', "_", nome_base)
    
    return nome_base + ".txt"

def registrar_sucesso(url, conteudo):
    """
    Registra um URL coletado com sucesso e salva o conteúdo.
    """
    # Garantir que o diretório exista
    if not os.path.exists(DIRETORIO_CONTEUDO):
        os.makedirs(DIRETORIO_CONTEUDO)
    
    # Salvar o conteúdo em um arquivo
    nome_arquivo = gerar_nome_arquivo(url)
    caminho_arquivo = os.path.join(DIRETORIO_CONTEUDO, nome_arquivo)
    
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    
    # Registrar no arquivo de sucesso
    with open(ARQUIVO_SUCESSO, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")
    
    return caminho_arquivo

def registrar_falha(url, motivo):
    """
    Registra um URL que falhou na coleta.
    """
    # Registrar no arquivo de falhas
    with open(ARQUIVO_FALHA, "a", encoding="utf-8") as f:
        f.write(f"{url} | Motivo: {motivo}\n")

def limpar_texto(texto):
    """
    Limpa o texto removendo espaços extras e caracteres indesejados.
    """
    if not texto:
        return ""
    
    # Remover múltiplos espaços e quebras de linha
    texto = re.sub(r'\s+', ' ', texto)
    # Remover caracteres não imprimíveis
    texto = re.sub(r'[\x00-\x1F\x7F]', '', texto)
    # Substituir caracteres Unicode que podem causar problemas
    texto = texto.replace('\u200b', '')  # Zero width space
    
    return texto.strip()

def extrair_conteudo(driver, url):
    """
    Extrai o conteúdo do artigo da página.
    Retorna uma tupla (sucesso, conteudo_ou_erro).
    """
    try:
        # Esperar pelo carregamento do elemento principal
        wait = WebDriverWait(driver, 10)
        
        # Tentar encontrar o conteúdo usando o seletor fornecido
        try:
            conteudo_elemento = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".DocumentPage-content.fos-bottomref.publication-content"))
            )
            
            # Extrair o título, se disponível
            try:
                titulo_elemento = driver.find_element(By.CSS_SELECTOR, "h1.base-title")
                titulo = titulo_elemento.text
            except:
                # Tentar outras opções para o título
                try:
                    titulo_elemento = driver.find_element(By.CSS_SELECTOR, "h1")
                    titulo = titulo_elemento.text
                except:
                    titulo = "Título não encontrado"
            
            # Extrair a data de publicação, se disponível
            try:
                data_elemento = driver.find_element(By.CSS_SELECTOR, ".DocumentPage-date")
                data = data_elemento.text
            except:
                data = "Data não encontrada"
            
            # Extrair o autor, se disponível
            try:
                autor_elemento = driver.find_element(By.CSS_SELECTOR, ".DocumentPage-author")
                autor = autor_elemento.text
            except:
                autor = "Autor não encontrado"
            
            # Montar o conteúdo completo com metadados e texto
            conteudo_texto = conteudo_elemento.text
            
            conteudo_completo = (
                f"URL: {url}\n"
                f"Título: {titulo}\n"
                f"Data: {data}\n"
                f"Autor: {autor}\n"
                f"\n--- CONTEÚDO ---\n\n"
                f"{conteudo_texto}"
            )
            
            return True, limpar_texto(conteudo_completo)
            
        except Exception as e:
            # Se não encontrar o seletor específico, tentar uma abordagem mais genérica
            print(f"Seletor principal não encontrado para {url}, tentando alternativa...")
            
            # Tentar obter pelo menos algum conteúdo relevante
            try:
                # Verificar se é uma página de paywall ou bloqueio
                if "paywall" in driver.page_source.lower() or "assine" in driver.page_source.lower():
                    return False, "Conteúdo bloqueado por paywall"
                
                # Tentar extrair o corpo principal do texto
                corpo_texto = driver.find_element(By.TAG_NAME, "article").text
                if not corpo_texto:
                    corpo_texto = driver.find_element(By.TAG_NAME, "main").text
                
                return True, limpar_texto(corpo_texto)
            except:
                captura = driver.get_screenshot_as_base64()
                return False, f"Falha ao extrair conteúdo: {str(e)[:100]}"
    
    except Exception as e:
        return False, f"Erro geral: {str(e)[:100]}"

def processar_url(url, proxies):
    """
    Processa uma URL específica, extraindo seu conteúdo.
    """
    # Verificar se o link já foi coletado com sucesso
    if os.path.exists(ARQUIVO_SUCESSO):
        with open(ARQUIVO_SUCESSO, "r", encoding="utf-8") as f:
            if any(linha.strip() == url for linha in f):
                print(f"Link já coletado anteriormente, pulando: {url}")
                return True  # Considerar como sucesso, pois já foi coletado
    
    print(f"Processando: {url}")
    
    # Selecionar um proxy aleatório se disponível
    proxy = None
    if proxies:
        proxy = random.choice(proxies)
        print(f"Usando proxy: {proxy}")
    
    # Configurar o Chrome
    chrome_options = Options()
    
    # Adicionar proxy se disponível
    if proxy:
        chrome_options.add_argument(f"--proxy-server=http://{proxy}")
    
    # Configurações para evitar detecção de bot
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Configurações adicionais para melhorar performance e evitar bloqueios
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--incognito")
    
    # User agent aleatório para parecer mais humano
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Desabilitar imagens para carregamento mais rápido
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Tentar extrair o conteúdo com até MAX_TENTATIVAS
    for tentativa in range(MAX_TENTATIVAS):
        if tentativa > 0:
            print(f"Tentativa {tentativa+1}/{MAX_TENTATIVAS} para {url}")
            # Trocar o proxy nas novas tentativas se disponível
            if proxies:
                novo_proxy = random.choice([p for p in proxies if p != proxy])
                proxy = novo_proxy
                chrome_options = Options()  # Reiniciar as opções
                chrome_options.add_argument(f"--proxy-server=http://{proxy}")
                chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option("useAutomationExtension", False)
                print(f"Trocando para proxy: {proxy}")
        
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Evitar detecção de automação
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Acessar a URL
            print(f"Acessando: {url}")
            driver.get(url)
            
            # Aguardar carregamento com tempo aleatório para parecer mais humano
            tempo_espera = random.uniform(3, 6)
            print(f"Aguardando {tempo_espera:.2f} segundos para carregamento...")
            time.sleep(tempo_espera)
            
            # Rolar a página de forma suave para simular comportamento humano
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(0, scroll_height, random.randint(200, 500)):
                driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(random.uniform(0.1, 0.3))
            
            # Extrair o conteúdo
            sucesso, conteudo_ou_erro = extrair_conteudo(driver, url)
            
            if sucesso:
                # Registrar sucesso e salvar o conteúdo
                caminho_arquivo = registrar_sucesso(url, conteudo_ou_erro)
                print(f"✅ Sucesso: {url} - Salvo em {caminho_arquivo}")
                return True
            
            # Se falhou, mas não por erro de proxy ou acesso, não precisamos tentar novamente
            if "paywall" in conteudo_ou_erro or "Conteúdo bloqueado" in conteudo_ou_erro:
                registrar_falha(url, conteudo_ou_erro)
                print(f"❌ Falha permanente: {url} - {conteudo_ou_erro}")
                return False
        
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")
            conteudo_ou_erro = f"Erro: {str(e)[:100]}"
        
        finally:
            # Fechar o navegador
            if driver:
                driver.quit()
        
        # Esperar antes da próxima tentativa
        if tentativa < MAX_TENTATIVAS - 1:
            tempo_entre_tentativas = random.uniform(2, 4)
            print(f"Aguardando {tempo_entre_tentativas:.2f} segundos antes da próxima tentativa...")
            time.sleep(tempo_entre_tentativas)
    
    # Se chegou aqui, todas as tentativas falharam
    registrar_falha(url, conteudo_ou_erro)
    print(f"❌ Falha após {MAX_TENTATIVAS} tentativas: {url}")
    return False

def main():
    # Criar diretórios se não existirem
    if not os.path.exists(DIRETORIO_CONTEUDO):
        os.makedirs(DIRETORIO_CONTEUDO)
    
    # Carregar proxies válidos
    proxies = carregar_proxies()
    
    # Carregar links
    links_coletados, links_pendentes = carregar_links()
    
    # Verificar se há links para processar
    if not links_pendentes:
        print("Não há links pendentes para processar.")
        return
    
    # Converter conjunto para lista para poder ordenar e acessar por índice
    links_pendentes = list(links_pendentes)
    random.shuffle(links_pendentes)  # Embaralhar para distribuir os acessos
    
    print(f"Iniciando processamento de {len(links_pendentes)} links pendentes...")
    
    # Definir limite de links a processar (para evitar sobrecarga)
    limite_links = min(len(links_pendentes), 500)  # Limitar a 500 links conforme solicitado
    links_para_processar = links_pendentes[:limite_links]
    
    # Contar sucessos e falhas
    sucessos = 0
    falhas = 0
    
    # Processar links em paralelo com ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submeter apenas as tarefas para links que ainda não foram coletados com sucesso
        futuros = {}
        for url in links_para_processar:
            # Verificar novamente se o link já não foi coletado (pode ter sido coletado por outra instância do script)
            if os.path.exists(ARQUIVO_SUCESSO):
                with open(ARQUIVO_SUCESSO, "r", encoding="utf-8") as f:
                    links_ja_coletados = {line.strip() for line in f if line.strip()}
                
                if url in links_ja_coletados:
                    print(f"Link já coletado anteriormente, pulando: {url}")
                    continue
            
            # Se não foi coletado, submeter para processamento
            futuros[executor.submit(processar_url, url, proxies)] = url
        
        # Processar os resultados conforme são concluídos
        for futuro in concurrent.futures.as_completed(futuros):
            url = futuros[futuro]
            try:
                resultado = futuro.result()
                if resultado:
                    sucessos += 1
                else:
                    falhas += 1
                
                # Exibir progresso
                total_processado = sucessos + falhas
                percentual = (total_processado / len(futuros)) * 100 if futuros else 100
                print(f"Progresso: {total_processado}/{len(futuros)} ({percentual:.1f}%) - Sucessos: {sucessos}, Falhas: {falhas}")
                
                # Esperar um tempo aleatório entre as requisições para evitar bloqueios
                tempo_espera = random.uniform(TEMPO_ESPERA_MIN, TEMPO_ESPERA_MAX)
                time.sleep(tempo_espera)
                
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")
                falhas += 1
    
    print("\nProcessamento concluído!")
    print(f"Total de links processados nesta execução: {sucessos + falhas}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {falhas}")
    print(f"Conteúdos salvos em: {os.path.abspath(DIRETORIO_CONTEUDO)}")
    print(f"Registro de sucessos: {os.path.abspath(ARQUIVO_SUCESSO)}")
    print(f"Registro de falhas: {os.path.abspath(ARQUIVO_FALHA)}")

if __name__ == "__main__":
    main()