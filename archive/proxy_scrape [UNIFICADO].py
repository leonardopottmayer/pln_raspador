import requests
from bs4 import BeautifulSoup

url = 'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=ipport&format=text&timeout=9610'

# Solicitação HTTP para obter o conteúdo da página
response = requests.get(url)
html_content = response.text
print(html_content)