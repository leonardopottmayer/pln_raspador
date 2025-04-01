# Web Scraper para Artigos Jurídicos do JusBrasil

Este projeto consiste em um web scraper desenvolvido para coletar artigos do site [JusBrasil](https://www.jusbrasil.com.br/). A implementação foi dividida em duas etapas principais, cada uma executada por um script Python dedicado.

## Contexto

Os dados utilizados neste trabalho foram extraídos do site https://www.jusbrasil.com.br/.

Decidimos extrair todas as postagens presentes na busca pelo termo "Contrato" (https://www.jusbrasil.com.br/artigos-noticias/busca?q=Contrato). A busca retornava 50 páginas, com 10 postagens cada uma.

Por conta do volume de dados a serem extraídos e como o site é protegido pela Cloudflare, foi necessário implementar o uso de proxies para a coleta de dados.

## Estrutura do Projeto

A implementação da extração foi dividida em dois arquivos:

### 1. coleta_links.py

Este script acessa cada uma das 50 páginas de resultados da busca, extrai os links das postagens e armazena-os no arquivo "links_jusbrasil.txt". Para garantir a continuidade em caso de interrupção, o script também armazena em um arquivo de texto a última página visitada com sucesso.

#### Funcionalidades principais:

- **Uso de proxies**: Utiliza uma lista de proxies válidos para evitar bloqueios do Cloudflare
- **Gestão de checkpoints**: Salva a última página processada, permitindo retomar a coleta a partir deste ponto
- **Tratamento de erros**: Registra páginas que apresentaram erros no arquivo "paginas_erro.txt"
- **Detecção de duplicatas**: Evita salvar links duplicados
- **Personalização da coleta**: Permite ao usuário selecionar páginas específicas para processamento
- **Simulação de comportamento humano**: 
  - Utiliza tempos de espera aleatórios
  - Implementa rolagem suave da página
  - Alterna entre diferentes user-agents
  - Utiliza modo anônimo (incognito)

### 2. jusbrasil-content-scraper.py

Este script acessa cada um dos links armazenados no arquivo "links_jusbrasil.txt", extrai o conteúdo principal de cada postagem e salva os dados coletados em arquivos individuais na pasta "conteudos". Os arquivos gerados contêm o link, autor, título, data e o conteúdo completo do post.

#### Funcionalidades principais:

- **Processamento paralelo**: Utiliza ThreadPoolExecutor para processar múltiplos links simultaneamente
- **Gestão de tentativas**: Realiza até 3 tentativas para cada link que falha
- **Registro de sucesso/falha**: Mantém registro dos links processados com sucesso (links_coletados.txt) e dos que falharam (links_nao_coletados.txt)
- **Extração inteligente**: Tenta diferentes seletores CSS/XPath para localizar o conteúdo em diferentes formatos de página
- **Identificação de paywalls**: Detecta e registra quando o conteúdo está bloqueado por paywall
- **Simulação de comportamento humano**:
  - Rolagem suave da página
  - Tempos de espera variáveis
  - Rotação de proxies e user-agents
  - Técnicas anti-detecção de automação

## Arquivos Utilizados e Gerados

### Arquivos de Entrada:
- **proxies_validos.txt**: Lista de proxies válidos (coletados manualmente da plataforma proxyscrape)

### Arquivos de Controle:
- **links_jusbrasil.txt**: Lista de URLs de artigos a serem coletados
- **ultima_pagina.txt**: Checkpoint da última página processada
- **paginas_erro.txt**: Registro de páginas que apresentaram erros na coleta de links

### Arquivos de Saída:
- **links_coletados.txt**: URLs processadas com sucesso
- **links_nao_coletados.txt**: URLs que falharam na coleta de conteúdo
- **conteudos/**: Diretório contendo os arquivos de texto com o conteúdo coletado


## Como Usar

### Pré-requisitos
1. Instale as dependências necessárias:
   ```
   pip install selenium webdriver-manager
   ```
2. Prepare um arquivo de proxies válidos:
   - Crie um arquivo chamado "proxies_validos.txt" com um proxy por linha no formato "ip:porta"
