Os dados utilizados neste trabalho foram extraidos do site https://www.jusbrasil.com.br/.

Decidimos extratir todas as postagens presentes na busca pelo termo "Contrato" (https://www.jusbrasil.com.br/artigos-noticias/busca?q=Contrato". A busca retornava 50 páginas, com 10 postagens cada uma.

Por conta do volume de dados a serem extraídos e como o site é protegido pela Cloudflare, foi necessário implementar o uso de proxies para a coleta de dados.

A implementação da extração foi dividida em dois arquivos.

# coleta_links.py
Acessa cada uma das 50 páginas, extrai os links das postagens e armazena-os no arquivo "links_jusbrasil.txt". Como a coleta levava um pouco de tempo, também armazenava em um arquivo de texto a última página visitada.

# jusbrasil-content-scraper.py
Percorre cada um dos links presentes no arquivo "links_jusbrasil.txt", acessando cada a página e coletando os dados presentes no elemento principal do post. Os dados coletads eram então gravados na pasta conteudos. O arquivo gerado contém o link, autor e conteudo do post.
