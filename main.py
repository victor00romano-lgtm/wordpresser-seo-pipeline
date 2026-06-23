# main.py
import os
import sys

# Garante que o Python enxergue a pasta raiz e a pasta modules corretamente
caminho_raiz = os.path.dirname(os.path.abspath(__file__))
if caminho_raiz not in sys.path:
    sys.path.insert(0, caminho_raiz)

# Importações limpas e diretas das classes
from modules.content_analyzer.analyzer import ContentAnalyzer
from modules.wordpress_publisher.publisher import WordPressPublisher

def rodar_pipeline_automacao():
    print("🚀 Inicializando Monólito Modular de Automação...")
    
    # 1. Instancia os módulos independentes
    analyzer = ContentAnalyzer(usar_mock=False)
    publisher = WordPressPublisher()
    
    # 2. Executa o processamento (o próprio analyzer já sabe onde o PDF está)
    print("\n🧠 [Módulo Analyzer] Processando conteúdo direto do Analyzer...")
    try:
        # Chamada sem argumentos, deixando o analyzer usar o que já está fixo nele
        arquivo_alvo = input("defina o arquivo alvo: ")
        resultado = analyzer.analisar_e_estruturar(arquivo_principal=arquivo_alvo,diretorio=None) 
        print(f"📌 Título Otimizado Gerado: '{resultado['title']}'")
        print(f"🏷️ Tags recomendadas: {resultado.get('tags')}")
    except Exception as e:
        print(f"❌ Erro ao processar dados com o Gemini: {e}")
        return

    # 3. Transmite o payload final estruturado diretamente para o WordPress
    print("\n📤 [Módulo Publisher] Enviando mídia e artigo estruturado para o WordPress...")
    try:
        link_post = publisher.publicar_artigo(
            titulo=resultado["title"],
            texto_gemini=resultado["content_html"],
            keyword=resultado["keyword"],
            metadesc=resultado["meta_description"]
        )

        print("\n" + "="*60)
        print("🎉 PIPELINE EXECUTADO COM SUCESSO NO MONÓLITO MODULAR!")
        print(f"🔗 Acesse seu rascunho otimizado aqui: {link_post}")
        print("="*60)
    except Exception as e:
        print(f"❌ Erro na integração/publicação com o WordPress: {e}")


if __name__ == "__main__":
    print("=== 🚀 SISTEMA AUTOMATIZADO WORDPRESSER (MODO DIRETO) ===")
    
    # Dispara o ecossistema sem passar caminhos, deixando o analyzer no comando
    rodar_pipeline_automacao()