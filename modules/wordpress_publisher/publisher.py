import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import mimetypes

# ==============================================================================
# TRUQUE DO CAMINHO
# ==============================================================================
caminho_deste_arquivo = os.path.abspath(__file__)
pasta_raiz_do_projeto = os.path.dirname(os.path.dirname(os.path.dirname(caminho_deste_arquivo)))
if pasta_raiz_do_projeto not in sys.path:
    sys.path.insert(0, pasta_raiz_do_projeto)

import config

class WordPressPublisher:
    def __init__(self):
        self.url_site = config.WP_URL
        self.usuario = config.WP_USER
        self.senha_aplicativo = config.WP_APP_PASSWORD
        self.auth = HTTPBasicAuth(self.usuario, self.senha_aplicativo)
        print("⚙️ Módulo WordPressPublisher inicializado em modo Seguro.")

    def _enviar_imagem_wp(self, caminho_local, alt_text):
        if not os.path.exists(caminho_local):
            print(f"❌ Arquivo de imagem não localizado em: {caminho_local}")
            return None, None
        url_media = f"{self.url_site}/wp-json/wp/v2/media"
        nome_arquivo = os.path.basename(caminho_local)
        tipo_conteudo, _ = mimetypes.guess_type(caminho_local)
        if not tipo_conteudo: 
            tipo_conteudo = 'image/png'
        headers = {'Content-Disposition': f'attachment; filename={nome_arquivo}', 'Content-Type': tipo_conteudo}
        try:
            with open(caminho_local, 'rb') as img:
                resposta = requests.post(url_media, data=img, headers=headers, auth=self.auth)
            if resposta.status_code == 201:
                dados = resposta.json()
                requests.post(f"{url_media}/{dados['id']}", json={"alt_text": alt_text}, auth=self.auth)
                return dados['id'], dados['source_url']
        except Exception as e:
            print(f"❌ Erro no upload da imagem: {e}")
        return None, None

    def publicar_artigo(self, titulo, texto_gemini, keyword, metadesc, id_categoria=1591):
        print("\n🚀 [PUBLISHER] Iniciando Pipeline de Transmissão...")
        
        nome_imagem = input("👉 Nome da imagem de destaque (Capa) em 'repo_thumbs': ").strip()
        link_youtube = input("👉 URL do YouTube (Enter para pular): ").strip()
        link_extra = input("👉 URL do Link Extra (Enter para pular): ").strip()
        link_botao = input("URL do botão: ").strip()
        
        # Upload da Capa
        caminho_thumb = os.path.join(config.PASTA_REPOSITORIO_THUMBS, nome_imagem)
        id_thumb, _ = self._enviar_imagem_wp(caminho_thumb, f"Capa: {titulo}")
        if not id_thumb:
            print("❌ Cancelando envio: Imagem de destaque obrigatória.")
            return

        # ----------------------------------------------------------------------
        # PROCESSAMENTO E DISTRIBUIÇÃO DINÂMICA DE ELEMENTOS NO CONTEÚDO
        # ----------------------------------------------------------------------
        # Divide o texto do Gemini em parágrafos para injeções específicas
        paragrafos = [p + '</p>' for p in texto_gemini.split('</p>') if p.strip()]

        # 1. Injeção do Vídeo do YouTube após o 1º Parágrafo (Índice 0)
        if link_youtube:
            id_vid = link_youtube.split("v=")[-1].split("&")[0] if "v=" in link_youtube else link_youtube.split("/")[-1]
            # HTML do player com chamada/introdução persuasiva antes dele
            video_html = f"""
            <p style="margin-top: 25px; margin-bottom: 5px; font-weight: bold; color: #1E3A8A;">📺 Assista ao vídeo abaixo para conferir a nossa análise detalhada em vídeo:</p>
            <div style="position:relative; padding-bottom:56.25%; margin-bottom: 25px;">
                <iframe src="https://www.youtube.com/embed/{id_vid}" style="position:absolute; width:100%; height:100%; border:0;" allowfullscreen></iframe>
            </div>
            """
            if len(paragrafos) >= 1:
                paragrafos[0] = paragrafos[0] + "\n" + video_html
            else:
                paragrafos.append(video_html)

        # 2. Injeção do 1º Botão após o 2º Parágrafo (Índice 1)
        btn1_html = f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link_botao}" style="background-color: #1F2937; color: #fff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">🚀 Ver Cursos</a>
        </div """
        if len(paragrafos) >= 3:
            paragrafos[2] = paragrafos[2] + "\n" + btn1_html
        else:
            paragrafos.append(btn1_html)

        # 3. Injeção do 2º Botão após o 3º Parágrafo (Índice 2)
        btn2_html = f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link_botao}" style="background-color: #1F2937; color: #fff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">🚀 Ver Cursos</a>
        </div>
        """
        if len(paragrafos) >= 10:
            paragrafos[9] = paragrafos[9] + "\n" + btn2_html
        else:
            paragrafos.append(btn2_html)

        # Reconstrói o corpo principal com as injeções aplicadas
        corpo_html = "\n".join(paragrafos)

        # 4. Injeção de Rodapé (Livraria e Link Extra)
        livraria_html = ' Aproveite também para se preparar com os melhores materiais didáticos, <a href="https://flaviarita.com/livraria.aspx" target="_blank" style="color: #DC2626; font-weight: bold;">conheça nossa livraria</a>.'
        corpo_html += f'<p>{livraria_html}</p>'

        if link_extra:
            corpo_html += f'<p><a href="{link_extra}" target="_blank" style="color: #2563EB; font-weight: bold;">Clique aqui para mais informações</a></p>'

        # Envio do Post para o WordPress
        payload = {
            "title": titulo,
            "content": corpo_html,
            "status": "draft",
            "featured_media": id_thumb,
            "categories": [id_categoria],
            "meta": {
                "_yoast_wpseo_focuskw": keyword, 
                "_yoast_wpseo_metadesc": metadesc
            }
        }
        
        print("⏳ Transmitindo rascunho e metadados para o WordPress...")
        res = requests.post(f"{self.url_site}/wp-json/wp/v2/posts", json=payload, auth=self.auth)
        
        if res.status_code == 201:
            post_id = res.json()['id']
            link_painel = res.json().get('link')
            print(f"🎉 POST TRANSMITIDO COM SUCESSO! ID: {post_id}")
            print(f"🔗 Link para conferir o rascunho: {link_painel}")
        else:
            print(f"❌ Erro ao enviar post: {res.status_code} - {res.text}")

# ==========================================
# 🧪 Bloco de Teste Executável Direto
# ==========================================
if __name__ == "__main__":
    print("\n🧪 [TESTE INDEPENDENTE DO PUBLISHER] Inicializando...")
    
    # Simulação dos dados que viriam do Gemini no seu main.py
    titulo_teste = "Concurso ALECE 2026: Tudo o que você precisa saber"
    texto_teste = "<p>Conteúdo de teste gerado pela inteligência artificial focado em aprovação rápida.</p>"
    kw_teste = "Concurso ALECE 2026"
    desc_teste = "Veja análise do edital ALECE 2026 com cronograma completo de estudos."
    
    publisher = WordPressPublisher()
    publisher.publicar_artigo(titulo_teste, texto_teste, kw_teste, desc_teste)