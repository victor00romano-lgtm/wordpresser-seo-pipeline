# modules/content_analyzer/analyzer.py
import os
import sys
import json
from pypdf import PdfReader
import google.generativeai as genai

# Garante o mapeamento de caminhos a partir da raiz do projeto para evitar falhas de importacao
caminho_deste_arquivo = os.path.abspath(__file__)
pasta_raiz_do_projeto = os.path.dirname(os.path.dirname(os.path.dirname(caminho_deste_arquivo)))
if pasta_raiz_do_projeto not in sys.path:
    sys.path.insert(0, pasta_raiz_do_projeto)

import config

class ContentAnalyzer:
    def __init__(self, usar_mock: bool = True):
        """
        usar_mock=True  -> Roda localmente sem gastar API (Perfeito para testar HTML/WordPress).
        usar_mock=False -> Ativa a conexao real com a API do Gemini na internet.
        """
        self.usar_mock = usar_mock
        
        if not self.usar_mock:
            print("🧠 [ANALYZER] Inicializando a API Real do Gemini...")
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                print(f"❌ Falha ao conectar na API do Gemini: {e}")
                self.model = None
        else:
            print("🤖 [MODO AVIAO] Mock ativo. Retornos locais configurados de forma estatica.")

    def _extrair_texto_pdf(self, caminho_pdf: str) -> str:
        """Le um arquivo PDF local e extrai todo o texto contido nele."""
        print(f"📄 [PYPDF] Extraindo texto de: {os.path.basename(caminho_pdf)}...")
        try:
            reader = PdfReader(caminho_pdf)
            texto_completo = ""
            for pagina in reader.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
            return texto_completo
        except Exception as e:
            print(f"❌ Erro ao ler o arquivo PDF: {e}")
            return ""

    def analisar_e_estruturar(self, arquivo_principal: str, diretorio: str = None) -> dict:
        """
        Analisa o arquivo principal para extrair as informacoes reais do artigo e utiliza
        os outros arquivos da pasta apenas como modelo de estrutura/estilo.
        
        :param arquivo_principal: Nome do arquivo PDF alvo (ex: 'artigo_concurso_alece_2026.pdf')
        :param diretorio: Caminho da pasta onde os arquivos PDF estao salvos
        """
        if diretorio is None:
            diretorio = "c:/Users/Intel Core I5/Desktop/Wordpresser/repo_text"

        caminho_completo_principal = os.path.join(diretorio, arquivo_principal)

        # ----------------------------------------------------------------------
        # CAMADA 1: INTERRUPTOR DO MOCK (Ambiente de Testes Isolado)
        # ----------------------------------------------------------------------
        if self.usar_mock:
            print(f"\n⚡ [MOCK ACTIVE] Simulando leitura do arquivo alvo: {arquivo_principal}")
            print(f"📂 [MOCK ACTIVE] Simulando coleta de formato a partir da pasta: {diretorio}")
            
            nome_amigavel = arquivo_principal.replace('.pdf', '').replace('_', ' ').title()
            return {
                "title": f"Analise Completa: {nome_amigavel} com Salarios Incriveis",
                "keyword": f"Estudar para {nome_amigavel}",
                "meta_description": f"Confira todas as novidades publicadas no documento {arquivo_principal} e garanta a sua aprovacao.",
                "tags": "concurso publico, edital 2026, plano de estudos, preparacao",
                "content_html": (
                    "<p>Uma excelente oportunidade acaba de ser anunciada com base nas diretrizes oficiais extraidas diretamente do documento original analisado pelo nosso sistema.</p>\n"
                    "<p>A estrutura de topicos, o tamanho ideal de paragrafos e o alinhamento de copywriting foram espelhados a partir dos melhores exemplos disponiveis no nosso repositorio de formatos.</p>\n"
                    "<p>Ao focar o seu cronograma de leitura nos pontos centrais deste edital, voce maximiza a retencao de dados complexos sem misturar informacoes de exames anteriores.</p>\n"
                    "<p>Recomendamos fortemente que inicie os seus simulados praticos o quanto antes, utilizando materiais de apoio atualizados de acordo com esta publicacao.</p>"
                )
            }

        # ----------------------------------------------------------------------
        # CAMADA 2: MOTOR DE PRODUCAO REAL (Conexao ao Gemini)
        # ----------------------------------------------------------------------
        print(f"\n📖 [ANALYZER] Lendo dados do material principal de referencia: {arquivo_principal}")
        
        # 1. Validacao e extracao do texto do arquivo alvo principal
        if not os.path.exists(caminho_completo_principal):
            raise FileNotFoundError(f"O arquivo principal '{arquivo_principal}' nao existe na pasta '{diretorio}'.")
            
        texto_principal = self._extrair_texto_pdf(caminho_completo_principal)
        if not texto_principal.strip():
            raise ValueError(f"O conteudo do arquivo '{arquivo_principal}' esta vazio ou nao pode ser interpretado.")

        # 2. Varredura de formato de outros arquivos do mesmo diretorio
        texto_referencia_formato = ""
        try:
            todos_arquivos = os.listdir(diretorio)
            outros_pdfs = [f for f in todos_arquivos if f.lower().endswith('.pdf') and f != arquivo_principal]
            
            if outros_pdfs:
                arquivo_modelo = outros_pdfs[0]
                print(f"🎨 [ESTILO] Mapeando o arquivo '{arquivo_modelo}' como gabarito exclusivo de formato e densidade.")
                caminho_modelo = os.path.join(diretorio, arquivo_modelo)
                
                # Obtemos apenas uma pequena amostra (2 paginas) para nao estourar o limite de tokens da API
                reader_modelo = PdfReader(caminho_modelo)
                paginas_amostra = reader_modelo.pages[:2]
                for pag in paginas_amostra:
                    txt = pag.extract_text()
                    if txt:
                        texto_referencia_formato += txt + "\n"
            else:
                print("⚠️ [ESTILO] Nenhum outro PDF localizado para servir de modelo. O Gemini usara o formato padrao.")
        except Exception as e:
            print(f"⚠️ Nao foi possivel recolher amostras de formatacao dos outros PDFs: {e}")

        # 3. Construcao do Prompt Hibrido (Conteudo factual vs. Estilo visual)
        prompt = (
            "Voce e um copywriter de alto nivel, especialista em SEO e redacao para blogs focados na venda de cursos e materiais para concursos publicos.\n"
            "O seu objetivo e criar um artigo unico com base apenas nos dados de um arquivo fonte, utilizando outro documento apenas como exemplo de estilo.\n\n"
        )
        
        if texto_referencia_formato.strip():
            prompt += (
                "--- MODELO DE ESTILO E FORMATO A COPIAR (Nao use estas informacoes no texto final) ---\n"
                "Observe apenas a quantidade de paragrafos, tom motivacional, densidade de escrita e marcas do HTML.\n"
                "Copie apenas o formato visual e de escrita, nunca utilize estes fatos:\n"
                f"{texto_referencia_formato[:1500]}\n"
                "----------------------------------------------------------------------------------\n\n"
            )

        prompt += (
            "--- INFORMACOES REAIS DO ARTIGO (Sua unica fonte de dados factuais) ---\n"
            "Crie o seu artigo usando unicamente os dados extraidos deste bloco. Se nao estiver aqui, nao invente:\n"
            f"{texto_principal}\n"
            "------------------------------------------------------------------------\n\n"
            
            "Você é um redator de SEO especialista em conversão e marketing educacional para concursos públicos. \n"
            "Sua tarefa é escrever um artigo de blog altamente engajador, persuasivo e visualmente rico sobre o tema solicitado.\n\n"
            "Para garantir que o artigo seja visualmente atraente no WordPress, você DEVE estruturar o conteúdo obrigatoriamente usando as seguintes regras de HTML:\n\n"
            "1. TÍTULOS E SUBTÍTULOS (SEO):\n"
            "   - Nunca use Markdown (como # ou ##). Use tags HTML para os títulos: <h2> para os títulos principais das seções e <h3> para tópicos internos.\n"
            "   - Aplique uma cor elegante aos títulos, por exemplo: <h2 style=\"color: #1E3A8A; margin-top: 30px;\">Título da Seção</h2>.\n\n"
            "2. LISTAS ORGANIZADAS:\n"
            "   - Sempre que explicar passos, dicas ou requisitos, utilize listas ordenadas (<ol><li>) ou listas com marcadores (<ul><li>).\n"
            "   - Estilize as listas com um pouco de espaçamento: <li style=\"margin-bottom: 8px;\">Texto</li>.\n\n"
            "3. TABELAS (QUADROS INFORMATIVOS):\n"
            "   - Sempre crie pelo menos uma tabela (quadro informativo de resumo) para dados cruciais como: cronograma, matérias que mais caem, distribuição de vagas ou salários.\n"
            "   - Use uma estrutura HTML limpa e bonita com bordas suaves e cabeçalho destacado. Exemplo de estilo:\n"
            "     <table style=\"width: 100%; border-collapse: collapse; margin: 25px 0;\">\n"
            "       <thead>\n"
            "         <tr style=\"background-color: #F3F4F6; text-align: left;\">\n"
            "           <th style=\"padding: 12px; border-bottom: 2px solid #E5E7EB; font-weight: bold;\">Coluna 1</th>\n"
            "           <th style=\"padding: 12px; border-bottom: 2px solid #E5E7EB; font-weight: bold;\">Coluna 2</th>\n"
            "         </tr>\n"
            "       </thead>\n"
            "       <tbody>\n"
            "         <tr>\n"
            "           <td style=\"padding: 12px; border-bottom: 1px solid #E5E7EB;\">Dado 1</td>\n"
            "           <td style=\"padding: 12px; border-bottom: 1px solid #E5E7EB;\">Dado 2</td>\n"
            "         </tr>\n"
            "       </tbody>\n"
            "     </table>\n\n"
            "4. CAIXAS DE DESTAQUE (CALLOUTS / BLOCOS DE ATENÇÃO):\n"
            "   - Para dicas de ouro ou alertas cruciais, use blocos destacados com fundo colorido sutil e borda lateral. Exemplo:\n"
            "     <div style=\"background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0; border-radius: 4px;\">\n"
            "       <strong>⚠️ Atenção:</strong> Insira aqui uma dica crucial de estudo!\n"
            "     </div>\n\n"
            "5. TEXTO EM NEGRITO E PARÁGRAFOS:\n"
            "   - Destaque termos importantes usando <strong>termo importante</strong> para melhorar a leitura dinâmica.\n"
            "   - Divida o texto em parágrafos curtos (máximo 4 linhas por parágrafo) para não cansar o leitor.\n\n"
            "6. RESTRIÇÃO CRÍTICA:\n"
            "   - Retorne APENAS o conteúdo HTML limpo, sem envolver em tags ```html ... ``` e sem as tags estruturais globais (como <html>, <head> ou <body>). Comece direto no conteúdo do artigo."
            "Formato de Saida Obrigatorio:\n"
            "Retorne exclusivamente um objeto JSON estruturado com a seguinte estrutura de chaves (nao use blocos de marcacao markdown):\n"
            "- 'title': Titulo atraente, focado em cliques (CTR elevado).\n"
            "- 'keyword': A palavra-chave em foco para indexacao.\n"
            "- 'meta_description': Resumo de SEO com limite rigoroso de 145 caracteres.\n"
            "- 'tags': Palavras-chave de indexacao separadas apenas por virgulas.\n"
            "- 'content_html': O corpo completo do artigo utilizando apenas tags <p> para separar os paragrafos. Nao utilize tags de cabecalho como h1, h2 ou h3 no meio do texto."
        )

        try:
            # Forca o motor do Gemini a estruturar a saida estritamente em formato JSON valido
            config_saida = {"response_mime_type": "application/json"}
            
            response = self.model.generate_content(
                prompt, 
                generation_config=config_saida
            )
            
            resposta_limpa = response.text.strip()
            
            # Limpeza caso o modelo persista em usar a formatacao markdown no JSON
            if resposta_limpa.startswith("```"):
                resposta_limpa = resposta_limpa.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                if resposta_limpa.startswith("json"):
                    resposta_limpa = resposta_limpa[4:].strip()

            return json.loads(resposta_limpa)
            
        except Exception as e:
            print(f"❌ Erro ao chamar a API ou ao converter o JSON: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"📄 Resposta em bruto recebida da IA: \n{response.text}")
            raise e

# ==============================================================================
# 🧪 Bloco de Execucao de Teste Isolado
# ==============================================================================
if __name__ == "__main__":
    print("\n🧪 [TESTE ISOLADO] Inicializando o teste do analisador...")
    
    # IMPORTANTE: Altere para usar_mock=False quando quiser fazer testes reais na API do Gemini!
    analisador = ContentAnalyzer(usar_mock=False)
    
    # Defina aqui o arquivo PDF principal da sua pasta que quer processar individualmente
    arquivo_alvo = input("defina o arquivo alvo: ")
    
    try:
        resultado_teste = analisador.analisar_e_estruturar(
            arquivo_principal=arquivo_alvo,
            diretorio=None  # Utilizara o caminho padrao configurado no metodo
        )
        
        print("\n" + "="*60)
        print("🎉 LEITURA E PARSING CONCLUIDOS COM SUCESSO:")
        print(f"📌 TITULO CRIADO: {resultado_teste.get('title')}")
        print(f"🔑 PALAVRA-CHAVE: {resultado_teste.get('keyword')}")
        print("-"*60)
        print("📝 CORPO HTML EXTRAIDO:")
        print(resultado_teste.get('content_html'))
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante o teste isolado: {e}")