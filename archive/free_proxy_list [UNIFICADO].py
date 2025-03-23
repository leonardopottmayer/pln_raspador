import requests
from bs4 import BeautifulSoup

url = 'https://free-proxy-list.net/'

# Solicitação HTTP para obter o conteúdo da página
response = requests.get(url)
html_content = response.text

# Criar o objeto BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Localizar a tabela específica
table = soup.find('div', {'class': 'table-responsive fpl-list'}).find('table')

# Processar o cabeçalho da tabela
headers = [header.text for header in table.find_all('th')]

# Processar as linhas da tabela
rows = []
for row in table.find('tbody').find_all('tr'):
    cells = [cell.text for cell in row.find_all('td')]
    rows.append(cells)

# Exibir os dados coletados
print(headers)
for row in rows:
    print(row)