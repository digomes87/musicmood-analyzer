from typing import Dict, Optional, List
import os
from .database import MusicDatabase
from .lyrics_fetcher import LyricsFetcher
from .sentiment_analyzer import SentimentAnalyzer


class MusicMoodAnalyzer:
    """Classe principal do sistema de análise de sentimento musical."""
    
    def __init__(self, db_path: str = "musicmood.db"):
        self.database = MusicDatabase(db_path)
        self.lyrics_fetcher = LyricsFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_song(self, song_title: str, artist: str, force_refresh: bool = False) -> Dict:
        """Analisa uma música completa: busca letra e analisa sentimento."""
        # Verifica se já existe análise no banco
        if not force_refresh:
            existing_analysis = self.database.get_music_analysis(song_title, artist)
            if existing_analysis:
                return self._format_analysis_result(existing_analysis)
        
        print(f"Analisando: {song_title} - {artist}")
        
        # Busca a letra
        print("Buscando letra...")
        lyrics = self.lyrics_fetcher.fetch_lyrics(artist, song_title)
        
        if not lyrics:
            return {
                'erro': 'Letra não encontrada',
                'titulo': song_title,
                'artista': artist,
                'letra_encontrada': False
            }
        
        print(f"Letra encontrada ({len(lyrics)} caracteres)")
        
        # Analisa o sentimento
        print("Analisando sentimento...")
        sentiment_result = self.sentiment_analyzer.analyze_sentiment(lyrics)
        
        # Salva no banco de dados
        palavras_chave_str = ', '.join(sentiment_result['palavras_chave'][:10])  # Limita a 10 palavras
        
        music_id = self.database.insert_music_analysis(
            titulo=song_title,
            artista=artist,
            letra=lyrics,
            sentimento_primario=sentiment_result['sentimento_primario'],
            sentimento_secundario=sentiment_result['sentimento_secundario'],
            pontuacao_sentimento=sentiment_result['pontuacao_sentimento'],
            palavras_chave=palavras_chave_str
        )
        
        # Formata resultado final
        result = {
            'id': music_id,
            'titulo': song_title,
            'artista': artist,
            'letra_encontrada': True,
            'letra': lyrics[:500] + '...' if len(lyrics) > 500 else lyrics,  # Trunca para exibição
            'sentimento_primario': sentiment_result['sentimento_primario'],
            'sentimento_secundario': sentiment_result['sentimento_secundario'],
            'pontuacao_sentimento': round(sentiment_result['pontuacao_sentimento'], 3),
            'confianca': round(sentiment_result['confianca'], 3),
            'palavras_chave': sentiment_result['palavras_chave'][:10],
            'emocoes_detectadas': {k: round(v, 3) for k, v in sentiment_result['emocoes_detectadas'].items()},
            'resumo': self._generate_summary(sentiment_result)
        }
        
        print("Análise concluída!")
        return result
    
    def get_artist_analysis(self, artist: str) -> Dict:
        """Retorna análise completa de um artista."""
        analyses = self.database.get_artist_analyses(artist)
        
        if not analyses:
            return {
                'artista': artist,
                'total_musicas': 0,
                'erro': 'Nenhuma música analisada para este artista'
            }
        
        # Calcula estatísticas
        stats = self.database.get_sentiment_statistics(artist)
        
        # Encontra música mais triste e mais feliz
        sorted_by_sentiment = sorted(analyses, key=lambda x: x['pontuacao_sentimento'])
        
        most_sad = None
        most_happy = None
        
        for analysis in sorted_by_sentiment:
            if analysis['sentimento_primario'] in ['tristeza', 'raiva', 'medo'] and not most_sad:
                most_sad = analysis
            elif analysis['sentimento_primario'] in ['felicidade', 'esperança'] and not most_happy:
                most_happy = analysis
        
        return {
            'artista': artist,
            'total_musicas': len(analyses),
            'distribuicao_sentimentos': stats['sentiment_distribution'],
            'musica_mais_triste': most_sad,
            'musica_mais_feliz': most_happy,
            'sentimento_predominante': max(stats['sentiment_distribution'].items(), 
                                         key=lambda x: x[1]['count'])[0],
            'pontuacao_media': round(sum(a['pontuacao_sentimento'] for a in analyses) / len(analyses), 3),
            'ultimas_analises': analyses[:5]  # 5 mais recentes
        }
    
    def compare_songs(self, songs: List[tuple]) -> Dict:
        """Compara sentimentos entre múltiplas músicas."""
        comparisons = []
        
        for song_title, artist in songs:
            analysis = self.database.get_music_analysis(song_title, artist)
            if analysis:
                comparisons.append({
                    'titulo': song_title,
                    'artista': artist,
                    'sentimento_primario': analysis['sentimento_primario'],
                    'pontuacao_sentimento': analysis['pontuacao_sentimento']
                })
        
        if not comparisons:
            return {'erro': 'Nenhuma música encontrada para comparação'}
        
        # Ordena por pontuação de sentimento
        comparisons.sort(key=lambda x: x['pontuacao_sentimento'], reverse=True)
        
        return {
            'total_comparadas': len(comparisons),
            'mais_positiva': comparisons[0],
            'mais_negativa': comparisons[-1],
            'comparacoes': comparisons
        }
    
    def search_by_sentiment(self, sentiment: str, limit: int = 10) -> List[Dict]:
        """Busca músicas por sentimento específico."""
        # Esta funcionalidade requer uma query mais específica no banco
        # Por simplicidade, vamos implementar uma versão básica
        pass
    
    def _format_analysis_result(self, db_result: Dict) -> Dict:
        """Formata resultado do banco de dados para exibição."""
        palavras_chave = db_result['palavras_chave'].split(', ') if db_result['palavras_chave'] else []
        
        return {
            'id': db_result['id'],
            'titulo': db_result['titulo'],
            'artista': db_result['artista'],
            'letra_encontrada': True,
            'letra': db_result['letra'][:500] + '...' if len(db_result['letra']) > 500 else db_result['letra'],
            'sentimento_primario': db_result['sentimento_primario'],
            'sentimento_secundario': db_result['sentimento_secundario'],
            'pontuacao_sentimento': round(db_result['pontuacao_sentimento'], 3),
            'palavras_chave': palavras_chave[:10],
            'data_analise': db_result['data_analise'],
            'resumo': f"{db_result['sentimento_primario'].title()} ({round(db_result['pontuacao_sentimento'] * 100, 1)}%)"
        }
    
    def _generate_summary(self, sentiment_result: Dict) -> str:
        """Gera resumo da análise de sentimento."""
        primary = sentiment_result['sentimento_primario']
        score = sentiment_result['pontuacao_sentimento']
        confidence = sentiment_result['confianca']
        keywords = sentiment_result['palavras_chave'][:5]
        
        summary = f"{primary.title()} ({round(score * 100, 1)}%)"
        
        if confidence > 0.7:
            summary += " - Alta confiança"
        elif confidence > 0.4:
            summary += " - Confiança moderada"
        else:
            summary += " - Baixa confiança"
        
        if keywords:
            summary += f" - Palavras-chave: {', '.join(keywords[:3])}"
        
        return summary
    
    def close(self):
        """Fecha conexões e limpa recursos."""
        self.lyrics_fetcher.close()
        self.database.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()