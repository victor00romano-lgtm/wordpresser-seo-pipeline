WordPresser: IA-Powered Content & SEO Automation Pipeline

O WordPresser é um pipeline inteligente de automação de conteúdo e SEO desenvolvido em Python. Ele foi projetado para transformar materiais factuais brutos (como arquivos PDF de editais e manuais) em artigos de blog ricos, visualmente atraentes e otimizados para conversão de vendas, publicando-os automaticamente no WordPress via REST API.

Diferente de geradores de texto genéricos, este sistema utiliza técnicas avançadas de engenharia de prompt híbrido (separa estilo de dados reais) e injeção semântica estruturada de mídias (vídeos, CTAs, links internos).

Arquitetura do Sistema

O projeto é 100% modular, seguindo boas práticas de design de software e separação de conceitos:

[ Documento PDF ] ──> (ContentAnalyzer via PyPDF + Gemini API)
                                    │
                                    ▼ (JSON estruturado com HTML limpo)
[ Parâmetros CLI ] ──> (MediaInjector: Alinhamento de blocos de conversão)
                                    │
                                    ▼ (Post HTML enriquecido e otimizado)
[ Biblioteca Mídia ] ──> (WordPressPublisher: Envio de imagens + postagem via REST API)


ContentAnalyzer: Extrai os dados factuais do PDF e envia para a API do Google Gemini, aplicando um estilo de escrita de alta conversão. Retorna um payload JSON validado.

MediaInjector: Fatiador dinâmico de HTML que posiciona estrategicamente elementos comerciais (botão de download, curso, vídeos explicativos, banners e links de SEO) ao longo dos parágrafos gerados.

WordPressPublisher: Gerencia a comunicação com a API REST do WordPress. Faz o upload da imagem de destaque (Capa), trata formatos de mídia (PNG/JPG/WEBP) e cria o rascunho com o SEO do Yoast estruturado.

Diferenciais Técnicos (Foco em Produção)

Headless & RPA Ready: Construído como uma ferramenta de CLI (Interface de Linha de Comando) limpa, ideal para automações em servidores, tarefas agendadas (Cron) ou integração em esteiras de CI/CD.

Prompt Híbrido Avançado: A API do Gemini recebe dados factuais de uma fonte e regras estéticas de outra, impedindo alucinações de dados nos artigos.

Garantia de JSON Semântico: Força o motor generativo a retornar rigorosamente dados estruturados (Response MIME Type: JSON), eliminando quebras comuns de parsing de IA.

Segurança e Isolamento: Arquivos de configuração separados das regras de negócio, facilitando a portabilidade do ambiente.

Tecnologias Utilizadas

Linguagem Principal: Python 3.10+

Processamento de Linguagem Natural: Google Gemini API (google-generativeai)

Leitura de Documentos: pypdf (PdfReader)

Comunicação Web & HTTP: requests com autenticação segura

Manipulação de Mídias: mimetypes para uploads dinâmicos de imagens no WordPress

Como Executar o Projeto

1. Pré-requisitos

Certifique-se de ter o Python instalado e uma API Key do Google Gemini, além de credenciais de aplicativo ativadas no seu WordPress.

2. Configuração do Ambiente

Clone o repositório e instale as dependências necessárias:

git clone [https://github.com/seu-usuario/wordpresser.git](https://github.com/seu-usuario/wordpresser.git)
cd wordpresser
pip install -r requirements.txt


3. Variáveis de Configuração

Crie um arquivo config.py na raiz do projeto contendo as suas chaves confidenciais (este arquivo já está configurado no .gitignore por motivos de segurança):

# config.py
GEMINI_API_KEY = "SUA_API_KEY_DO_GEMINI"
WP_URL = "[https://seu-blog.com](https://seu-blog.com)"
WP_USER = "seu_usuario"
WP_APP_PASSWORD = "sua_senha_de_aplicativo_wordpress"
PASTA_REPOSITORIO_THUMBS = "repo_thumbs"


4. Executando a Automação

Execute o script principal e preencha as informações solicitadas no terminal para iniciar o fluxo:

python main.py


Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.