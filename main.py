#!/usr/bin/env python3
"""
MusicMood Analyzer - Sistema de Análise de Sentimento em Letras de Música

Uso:
    python main.py "Nome da Música" "Artista"
    python main.py --artist "Artista" (para análise completa do artista)
    python main.py --interactive (modo interativo)
"""

import sys
import argparse
from src.musicmood import MusicMoodAnalyzer
import json


def print_analysis_result(result):
    """Imprime resultado da análise de forma formatada."""
    if 'erro' in result:
        print(f" Erro: {result['erro']}")
        return
    
    print("\n" + "="*60)
    print(f"🎵 ANÁLISE: {result['titulo']} - {result['artista']}")
    print("="*60)
    
    if result.get('letra_encontrada'):
        print(f" Sentimento Primário: {result['sentimento_primario'].upper()}")
        if result.get('sentimento_secundario'):
            print(f" Sentimento Secundário: {result['sentimento_secundario'].upper()}")
        
        print(f" Pontuação: {result['pontuacao_sentimento']:.3f}")
        print(f" Confiança: {result['confianca']:.3f}")
        
        if result.get('palavras_chave'):
            print(f"🔑 Palavras-chave: {', '.join(result['palavras_chave'][:5])}")
        
        print(f" Resumo: {result['resumo']}")
        
        print("\n Emoções Detectadas:")
        for emocao, score in result.get('emocoes_detectadas', {}).items():
            if score > 0.01:
                print(f"   {emocao.title()}: {score:.3f}")
        
        print(f"\nTrecho da letra:")
        print(f"{result['letra'][:200]}...")
    
    print("\n" + "="*60)


def print_artist_analysis(result):
    """Imprime análise completa do artista."""
    if 'erro' in result:
        print(f" Erro: {result['erro']}")
        return
    
    print("\n" + "="*60)
    print(f"🎤 ANÁLISE DO ARTISTA: {result['artista'].upper()}")
    print("="*60)
    
    print(f" Total de músicas analisadas: {result['total_musicas']}")
    print(f"🎭 Sentimento predominante: {result['sentimento_predominante'].upper()}")
    print(f" Pontuação média: {result['pontuacao_media']:.3f}")
    
    print("\n Distribuição de Sentimentos:")
    for sentimento, dados in result['distribuicao_sentimentos'].items():
        porcentagem = (dados['count'] / result['total_musicas']) * 100
        print(f"   {sentimento.title()}: {dados['count']} músicas ({porcentagem:.1f}%)")
    
    if result.get('musica_mais_triste'):
        triste = result['musica_mais_triste']
        print(f"\n Música mais triste: {triste['titulo']} ({triste['pontuacao_sentimento']:.3f})")
    
    if result.get('musica_mais_feliz'):
        feliz = result['musica_mais_feliz']
        print(f" Música mais feliz: {feliz['titulo']} ({feliz['pontuacao_sentimento']:.3f})")
    
    print("\n Últimas análises:")
    for analise in result.get('ultimas_analises', [])[:3]:
        print(f"   • {analise['titulo']} - {analise['sentimento_primario']} ({analise['pontuacao_sentimento']:.3f})")
    
    print("\n" + "="*60)


def interactive_mode():
    """Modo interativo para análise de músicas."""
    print("\n🎵 MusicMood Analyzer - Modo Interativo")
    print("Digite 'sair' para encerrar\n")
    
    with MusicMoodAnalyzer() as analyzer:
        while True:
            print("\nOpções:")
            print("1. Analisar música")
            print("2. Analisar artista")
            print("3. Sair")
            
            choice = input("\nEscolha uma opção (1-3): ").strip()
            
            if choice == '1':
                song = input("Nome da música: ").strip()
                artist = input("Nome do artista: ").strip()
                
                if song and artist:
                    try:
                        result = analyzer.analyze_song(song, artist)
                        print_analysis_result(result)
                    except Exception as e:
                        print(f" Erro durante análise: {e}")
                else:
                    print(" Por favor, forneça tanto o nome da música quanto o artista.")
            
            elif choice == '2':
                artist = input("Nome do artista: ").strip()
                
                if artist:
                    try:
                        result = analyzer.get_artist_analysis(artist)
                        print_artist_analysis(result)
                    except Exception as e:
                        print(f" Erro durante análise: {e}")
                else:
                    print(" Por favor, forneça o nome do artista.")
            
            elif choice == '3' or choice.lower() == 'sair':
                print(" Obrigado por usar o MusicMood Analyzer!")
                break
            
            else:
                print(" Opção inválida. Tente novamente.")


def main():
    parser = argparse.ArgumentParser(
        description='MusicMood Analyzer - Análise de Sentimento em Letras de Música',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py "Numb" "Linkin Park"
  python main.py --artist "Linkin Park"
  python main.py --interactive
        """
    )
    
    parser.add_argument('song', nargs='?', help='Nome da música')
    parser.add_argument('artist', nargs='?', help='Nome do artista')
    parser.add_argument('--artist-analysis', '--artist', dest='artist_only', 
                       help='Analisar todas as músicas de um artista')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Modo interativo')
    parser.add_argument('--force-refresh', '-f', action='store_true',
                       help='Força nova análise mesmo se já existir no banco')
    parser.add_argument('--json', action='store_true',
                       help='Saída em formato JSON')
    
    args = parser.parse_args()
    
    # Modo interativo
    if args.interactive:
        interactive_mode()
        return
    
    # Análise de artista
    if args.artist_only:
        with MusicMoodAnalyzer() as analyzer:
            try:
                result = analyzer.get_artist_analysis(args.artist_only)
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_artist_analysis(result)
            except Exception as e:
                print(f" Erro durante análise: {e}")
        return
    
    # Análise de música específica
    if args.song and args.artist:
        with MusicMoodAnalyzer() as analyzer:
            try:
                result = analyzer.analyze_song(args.song, args.artist, args.force_refresh)
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_analysis_result(result)
            except Exception as e:
                print(f" Erro durante análise: {e}")
        return
    
    # Se chegou aqui, argumentos insuficientes
    if len(sys.argv) == 1:
        # Sem argumentos, entra no modo interativo
        interactive_mode()
    else:
        parser.print_help()
        print("\n Erro: Forneça tanto o nome da música quanto o artista, ou use --interactive")
        sys.exit(1)


if __name__ == "__main__":
    main()
