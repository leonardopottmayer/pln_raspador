import requests

def is_proxy_working(proxy, test_url="http://example.com", timeout=5):
    """
    Verifica se um proxy está funcional fazendo uma requisição GET ao test_url.
    
    :param proxy: String no formato "IP:Porta".
    :param test_url: URL de teste para a requisição (padrão: http://example.com).
    :param timeout: Tempo máximo (em segundos) para considerar a requisição válida.
    :return: True se o proxy funcionou (status_code 200), False caso contrário.
    """
    proxies_dict = {
        "http":  f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    try:
        response = requests.get(test_url, proxies=proxies_dict, timeout=timeout)
        # Considerar proxy válido se o status_code for 200
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        # Se deu timeout ou outro erro, proxy não é utilizável
        return False

def validate_proxies_save(proxies, output_file="valid_proxies.txt"):
    """
    Valida cada proxy da lista, salvando as que funcionam em um arquivo de texto.
    
    :param proxies: Lista de proxies ["IP:Porta", "IP:Porta", ...].
    :param output_file: Nome do arquivo onde as proxies válidas serão salvas.
    """
    valid_proxies = []
    
    for proxy in proxies:
        print(f"Testando proxy: {proxy}...")
        if is_proxy_working(proxy):
            print(f"[OK] Proxy funcional: {proxy}")
            valid_proxies.append(proxy)
        else:
            print(f"[ERRO] Proxy falhou: {proxy}")
    
    # Salvar as proxies válidas no arquivo
    if valid_proxies:
        with open(output_file, "w", encoding="utf-8") as f:
            for vp in valid_proxies:
                f.write(vp + "\n")
        print(f"\nTotal de proxies válidas: {len(valid_proxies)}")
        print(f"Salvo no arquivo: {output_file}")
    else:
        print("\nNenhuma proxy válida encontrada. Nada foi salvo.")

if __name__ == "__main__":
    import requests
    from bs4 import BeautifulSoup

    url = 'https://free-proxy-list.net/'

    # Solicitação HTTP para obter o conteúdo da página
    response = requests.get(url)
    html_content = response.text

    # Criar o objeto BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Localizar a div e a tabela específica
    table_wrapper = soup.find('div', {'class': 'table-responsive fpl-list'})
    table = table_wrapper.find('table')

    # Processar o cabeçalho da tabela (opcional, se quiser ver quais colunas existem)
    headers = [header.text for header in table.find_all('th')]

    # Processar as linhas da tabela
    rows_data = []
    for row in table.find('tbody').find_all('tr'):
        cells = [cell.text for cell in row.find_all('td')]
        rows_data.append(cells)

    # Agora montamos a lista de proxies (IP:Porta)
    proxies_list = []
    for row in rows_data:
        ip   = row[0]  # IP Address
        port = row[1]  # Port
        proxy_string = f"{ip}:{port}"
        proxies_list.append(proxy_string)

    """
    # Exemplo de lista de proxies para teste (possivelmente inativas).
    proxies_list = [
        "84.54.219.194:8080",
        "45.167.124.244:999",
        "64.225.97.57:8080",
        "159.203.61.169:3128",
        "204.137.172.14:999",
        "5.78.52.141:8888",
        "138.117.77.212:999"
    ]
    
    # Valida as proxies e salva no arquivo 'valid_proxies.txt'"""
    validate_proxies_save(proxies_list, "valid_proxies.txt")
