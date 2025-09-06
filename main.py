#!/usr/bin/env python3
"""
MusicMood Analyzer - Sentiment Analysis System for Music Lyrics

Usage:
    python main.py "Song Name" "Artist"
    python main.py --artist "Artist" (for complete artist analysis)
    python main.py --interactive (interactive mode)
"""

import sys
import argparse
from src.musicmood import MusicMoodAnalyzer
import json


def print_analysis_result(result):
    """Prints analysis result in formatted way."""
    if 'erro' in result:
        print(f" Error: {result['erro']}")
        return
    
    print("\n" + "="*60)
    print(f"🎵 ANALYSIS: {result['titulo']} - {result['artista']}")
    print("="*60)
    
    if result.get('letra_encontrada'):
        print(f" Primary Sentiment: {result['sentimento_primario'].upper()}")
        if result.get('sentimento_secundario'):
            print(f" Secondary Sentiment: {result['sentimento_secundario'].upper()}")
        
        print(f" Score: {result['pontuacao_sentimento']:.3f}")
        print(f" Confidence: {result['confianca']:.3f}")
        
        if result.get('palavras_chave'):
            print(f"🔑 Keywords: {', '.join(result['palavras_chave'][:5])}")
        
        print(f" Summary: {result['resumo']}")
        
        print("\n Detected Emotions:")
        for emocao, score in result.get('emocoes_detectadas', {}).items():
            if score > 0.01:
                print(f"   {emocao.title()}: {score:.3f}")
        
        print(f"\nLyrics excerpt:")
        print(f"{result['letra'][:200]}...")
    
    print("\n" + "="*60)


def print_artist_analysis(result):
    """Prints complete artist analysis."""
    if 'erro' in result:
        print(f" Error: {result['erro']}")
        return
    
    print("\n" + "="*60)
    print(f"🎤 ARTIST ANALYSIS: {result['artista'].upper()}")
    print("="*60)
    
    print(f" Total songs analyzed: {result['total_musicas']}")
    print(f"🎭 Predominant sentiment: {result['sentimento_predominante'].upper()}")
    print(f" Average score: {result['pontuacao_media']:.3f}")
    
    print("\n Sentiment Distribution:")
    for sentimento, dados in result['distribuicao_sentimentos'].items():
        porcentagem = (dados['count'] / result['total_musicas']) * 100
        print(f"   {sentimento.title()}: {dados['count']} songs ({porcentagem:.1f}%)")
    
    if result.get('musica_mais_triste'):
        triste = result['musica_mais_triste']
        print(f"\n😢 Saddest song: {triste['titulo']} ({triste['pontuacao_sentimento']:.3f})")
    
    if result.get('musica_mais_feliz'):
        feliz = result['musica_mais_feliz']
        print(f"😊 Happiest song: {feliz['titulo']} ({feliz['pontuacao_sentimento']:.3f})")
    
    print("\n📊 Recent analyses:")
    for analise in result.get('ultimas_analises', [])[:3]:
        print(f"   • {analise['titulo']} - {analise['sentimento_primario']} ({analise['pontuacao_sentimento']:.3f})")
    
    print("\n" + "="*60)


def interactive_mode():
    """Interactive mode for music analysis."""
    print("\n🎵 MusicMood Analyzer - Interactive Mode")
    print("Type 'exit' to quit\n")
    
    with MusicMoodAnalyzer() as analyzer:
        while True:
            print("\nOptions:")
            print("1. Analyze song")
            print("2. Analyze artist")
            print("3. Exit")
            
            choice = input("\nChoose an option (1-3): ").strip()
            
            if choice == '1':
                song = input("Song name: ").strip()
                artist = input("Artist name: ").strip()
                
                if song and artist:
                    try:
                        result = analyzer.analyze_song(song, artist)
                        print_analysis_result(result)
                    except Exception as e:
                        print(f"❌ Error during analysis: {e}")
                else:
                    print("⚠️  Please provide both song name and artist.")
            
            elif choice == '2':
                artist = input("Artist name: ").strip()
                
                if artist:
                    try:
                        result = analyzer.get_artist_analysis(artist)
                        print_artist_analysis(result)
                    except Exception as e:
                        print(f"❌ Error during analysis: {e}")
                else:
                    print("⚠️  Please provide the artist name.")
            
            elif choice == '3' or choice.lower() == 'exit':
                print("👋 Thank you for using MusicMood Analyzer!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")


def main():
    parser = argparse.ArgumentParser(
        description='MusicMood Analyzer - Sentiment Analysis for Music Lyrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Numb" "Linkin Park"
  python main.py --artist "Linkin Park"
  python main.py --interactive
        """
    )
    
    parser.add_argument('song', nargs='?', help='Song name')
    parser.add_argument('artist', nargs='?', help='Artist name')
    parser.add_argument('--artist-analysis', '--artist', dest='artist_only', 
                       help='Analyze all songs from an artist')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Interactive mode')
    parser.add_argument('--force-refresh', '-f', action='store_true',
                       help='Force new analysis even if already exists in database')
    parser.add_argument('--json', action='store_true',
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Artist analysis
    if args.artist_only:
        with MusicMoodAnalyzer() as analyzer:
            try:
                result = analyzer.get_artist_analysis(args.artist_only)
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_artist_analysis(result)
            except Exception as e:
                print(f"❌ Error during analysis: {e}")
        return
    
    # Specific song analysis
    if args.song and args.artist:
        with MusicMoodAnalyzer() as analyzer:
            try:
                result = analyzer.analyze_song(args.song, args.artist, args.force_refresh)
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_analysis_result(result)
            except Exception as e:
                print(f"❌ Error during analysis: {e}")
        return
    
    # If reached here, insufficient arguments
    if len(sys.argv) == 1:
        # No arguments, enter interactive mode
        interactive_mode()
    else:
        parser.print_help()
        print("\n❌ Error: Provide both song name and artist, or use --interactive")
        sys.exit(1)


if __name__ == "__main__":
    main()
