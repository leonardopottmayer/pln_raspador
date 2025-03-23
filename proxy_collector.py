import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

def get_proxies_from_free_proxy_list():
    """Obtém proxies de free-proxy-list.net"""
    print("Obtendo proxies de free-proxy-list.net...")
    proxies = []
    try:
        url = 'https://free-proxy-list.net/'
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Localizar a tabela específica
        table = soup.find('div', {'class': 'table-responsive fpl-list'}).find('table')
        
        # Processar as linhas da tabela
        for row in table.find('tbody').find_all('tr'):
            cells = [cell.text for cell in row.find_all('td')]
            ip = cells[0]
            port = cells[1]
            proxy = f"{ip}:{port}"
            proxies.append(proxy)
            
        print(f"Encontrados {len(proxies)} proxies em free-proxy-list.net")
    except Exception as e:
        print(f"Erro ao obter proxies de free-proxy-list.net: {e}")
    
    return proxies

def get_proxies_from_proxyscrape():
    """Obtém proxies de proxyscrape.com"""
    print("Obtendo proxies de proxyscrape.com...")
    proxies = []
    try:
        url = 'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=ipport&format=text&timeout=9610'
        response = requests.get(url, timeout=10)
        
        # O conteúdo já vem no formato IP:PORTA, um por linha
        proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
        print(f"Encontrados {len(proxies)} proxies em proxyscrape.com")
    except Exception as e:
        print(f"Erro ao obter proxies de proxyscrape.com: {e}")
    
    return proxies

def test_proxy(proxy, timeout=5):
    """Testa se um proxy está funcionando"""
    proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }
    try:
        # Usando Google como site de teste
        start_time = time.time()
        response = requests.get('http://www.google.com', proxies=proxies, timeout=timeout)
        elapsed_time = time.time() - start_time
        if response.status_code == 200:
            print(f"✅ Proxy {proxy} está funcionando (tempo: {elapsed_time:.2f}s)")
            return True, proxy, elapsed_time
    except:
        pass
    
    print(f"❌ Proxy {proxy} não está funcionando")
    return False, proxy, None

def main():
    # Obtém proxies de ambas as fontes
    proxies_list_1 = ""#get_proxies_from_free_proxy_list()
    proxies_list_2 = get_proxies_from_proxyscrape()
    
    # Unifica as listas de proxies (elimina duplicatas)
    all_proxies = list(set(proxies_list_1 + proxies_list_2))
    print(f"Total de proxies únicos encontrados: {len(all_proxies)}")
    
    # Testa a validade dos proxies em paralelo
    valid_proxies = []
    print("Testando proxies (isso pode demorar um pouco)...")
    
    # Usando ThreadPoolExecutor para acelerar o processo de teste
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in all_proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            is_valid, proxy, elapsed_time = future.result()
            if is_valid:
                valid_proxies.append((proxy, elapsed_time))
    
    # Ordena os proxies válidos pelo tempo de resposta
    valid_proxies.sort(key=lambda x: x[1])
    
    # Salva os proxies válidos em um arquivo
    with open('proxies_validos.txt', 'w') as f:
        for proxy, elapsed_time in valid_proxies:
            f.write(f"{proxy}\n")
    
    print(f"\nProcesso concluído. {len(valid_proxies)} proxies válidos salvos em 'proxies_validos.txt'")
    
    # Exibe os 5 proxies mais rápidos (se houver)
    if valid_proxies:
        print("\nTop 5 proxies mais rápidos:")
        for i, (proxy, elapsed_time) in enumerate(valid_proxies[:5], 1):
            print(f"{i}. {proxy} - {elapsed_time:.2f}s")

if __name__ == "__main__":
    main()