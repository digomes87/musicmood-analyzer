import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class MusicDatabase:
    """Gerencia o banco de dados SQLite para armazenar análises de sentimento musical."""
    
    def __init__(self, db_path: str = "musicmood.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Inicializa o banco de dados e cria as tabelas necessárias."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS musicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    artista TEXT NOT NULL,
                    letra TEXT NOT NULL,
                    sentimento_primario TEXT NOT NULL,
                    sentimento_secundario TEXT,
                    pontuacao_sentimento REAL NOT NULL,
                    palavras_chave TEXT,
                    data_analise DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(titulo, artista)
                )
            """)
            conn.commit()
    
    def insert_music_analysis(self, 
                            titulo: str, 
                            artista: str, 
                            letra: str,
                            sentimento_primario: str,
                            pontuacao_sentimento: float,
                            sentimento_secundario: Optional[str] = None,
                            palavras_chave: Optional[str] = None) -> int:
        """Insere uma nova análise musical no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO musicas 
                    (titulo, artista, letra, sentimento_primario, sentimento_secundario, 
                     pontuacao_sentimento, palavras_chave, data_analise)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (titulo, artista, letra, sentimento_primario, sentimento_secundario,
                      pontuacao_sentimento, palavras_chave, datetime.now()))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Música já existe, atualiza os dados
                cursor.execute("""
                    UPDATE musicas 
                    SET letra = ?, sentimento_primario = ?, sentimento_secundario = ?,
                        pontuacao_sentimento = ?, palavras_chave = ?, data_analise = ?
                    WHERE titulo = ? AND artista = ?
                """, (letra, sentimento_primario, sentimento_secundario,
                      pontuacao_sentimento, palavras_chave, datetime.now(),
                      titulo, artista))
                conn.commit()
                return self.get_music_id(titulo, artista)
    
    def get_music_analysis(self, titulo: str, artista: str) -> Optional[Dict[str, Any]]:
        """Recupera a análise de uma música específica."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM musicas WHERE titulo = ? AND artista = ?
            """, (titulo, artista))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_music_id(self, titulo: str, artista: str) -> Optional[int]:
        """Recupera o ID de uma música específica."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM musicas WHERE titulo = ? AND artista = ?
            """, (titulo, artista))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_artist_analyses(self, artista: str) -> List[Dict[str, Any]]:
        """Recupera todas as análises de um artista específico."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM musicas WHERE artista = ? ORDER BY data_analise DESC
            """, (artista,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_sentiment_statistics(self, artista: Optional[str] = None) -> Dict[str, Any]:
        """Calcula estatísticas de sentimento para um artista ou geral."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if artista:
                cursor.execute("""
                    SELECT sentimento_primario, COUNT(*) as count, AVG(pontuacao_sentimento) as avg_score
                    FROM musicas WHERE artista = ?
                    GROUP BY sentimento_primario
                """, (artista,))
            else:
                cursor.execute("""
                    SELECT sentimento_primario, COUNT(*) as count, AVG(pontuacao_sentimento) as avg_score
                    FROM musicas
                    GROUP BY sentimento_primario
                """)
            
            results = cursor.fetchall()
            return {
                'sentiment_distribution': {row[0]: {'count': row[1], 'avg_score': row[2]} 
                                         for row in results},
                'total_songs': sum(row[1] for row in results)
            }
    
    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        pass  # sqlite3 connections are closed automatically with context manager