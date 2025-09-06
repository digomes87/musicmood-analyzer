import nltk
from textblob import TextBlob
import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
import string


class SentimentAnalyzer:
    """Analisa sentimentos em letras de música usando processamento de linguagem natural."""
    
    def __init__(self):
        self._download_nltk_data()
        self._load_emotion_keywords()
    
    def _download_nltk_data(self):
        """Baixa dados necessários do NLTK."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def _load_emotion_keywords(self):
        """Carrega dicionários de palavras-chave emocionais."""
        self.emotion_keywords = {
            'tristeza': [
                'sad', 'cry', 'tears', 'pain', 'hurt', 'broken', 'lonely', 'empty',
                'depression', 'sorrow', 'grief', 'melancholy', 'despair', 'hopeless',
                'triste', 'chorar', 'lágrimas', 'dor', 'machucado', 'quebrado', 
                'sozinho', 'vazio', 'depressão', 'tristeza', 'desespero', 'sem esperança'
            ],
            'raiva': [
                'angry', 'rage', 'hate', 'mad', 'furious', 'pissed', 'annoyed',
                'frustrated', 'irritated', 'violence', 'fight', 'war', 'destroy',
                'raiva', 'ódio', 'bravo', 'furioso', 'irritado', 'frustrado',
                'violência', 'luta', 'guerra', 'destruir'
            ],
            'felicidade': [
                'happy', 'joy', 'smile', 'laugh', 'love', 'amazing', 'wonderful',
                'beautiful', 'perfect', 'great', 'awesome', 'fantastic', 'celebration',
                'feliz', 'alegria', 'sorriso', 'rir', 'amor', 'incrível', 'maravilhoso',
                'lindo', 'perfeito', 'ótimo', 'fantástico', 'celebração'
            ],
            'medo': [
                'fear', 'scared', 'afraid', 'terror', 'panic', 'anxiety', 'worried',
                'nervous', 'frightened', 'paranoid', 'insecure', 'vulnerable',
                'medo', 'assustado', 'com medo', 'terror', 'pânico', 'ansiedade',
                'preocupado', 'nervoso', 'amedrontado', 'paranoico', 'inseguro'
            ],
            'esperança': [
                'hope', 'dream', 'future', 'believe', 'faith', 'trust', 'optimistic',
                'positive', 'bright', 'light', 'tomorrow', 'better', 'heal',
                'esperança', 'sonho', 'futuro', 'acreditar', 'fé', 'confiança',
                'otimista', 'positivo', 'brilhante', 'luz', 'amanhã', 'melhor', 'curar'
            ],
            'nostalgia': [
                'remember', 'memory', 'past', 'yesterday', 'childhood', 'old',
                'miss', 'used to', 'before', 'back then', 'nostalgia', 'reminisce',
                'lembrar', 'memória', 'passado', 'ontem', 'infância', 'velho',
                'saudade', 'costumava', 'antes', 'naquela época', 'nostalgia'
            ]
        }
        
        # Palavras intensificadoras
        self.intensifiers = {
            'muito': 1.5, 'extremely': 1.8, 'really': 1.3, 'so': 1.2, 'very': 1.4,
            'totally': 1.6, 'completely': 1.7, 'absolutely': 1.8, 'incredibly': 1.6,
            'bastante': 1.3, 'extremamente': 1.8, 'realmente': 1.3, 'totalmente': 1.6,
            'completamente': 1.7, 'absolutamente': 1.8, 'incrivelmente': 1.6
        }
    
    def analyze_sentiment(self, lyrics: str) -> Dict:
        """Analisa o sentimento principal de uma letra de música."""
        if not lyrics or len(lyrics.strip()) < 10:
            return {
                'sentimento_primario': 'neutro',
                'sentimento_secundario': None,
                'pontuacao_sentimento': 0.0,
                'palavras_chave': [],
                'confianca': 0.0,
                'emocoes_detectadas': {}
            }
        
        # Limpa e preprocessa o texto
        cleaned_lyrics = self._preprocess_text(lyrics)
        
        # Análise com TextBlob
        blob = TextBlob(cleaned_lyrics)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Análise de palavras-chave emocionais
        emotion_scores = self._analyze_emotion_keywords(cleaned_lyrics)
        
        # Análise contextual
        context_score = self._analyze_context(cleaned_lyrics)
        
        # Combina as análises
        final_analysis = self._combine_analyses(polarity, emotion_scores, context_score)
        
        # Calcula confiança
        confidence = self._calculate_confidence(subjectivity, emotion_scores, len(cleaned_lyrics))
        
        return {
            'sentimento_primario': final_analysis['primary'],
            'sentimento_secundario': final_analysis['secondary'],
            'pontuacao_sentimento': final_analysis['score'],
            'palavras_chave': final_analysis['keywords'],
            'confianca': confidence,
            'emocoes_detectadas': emotion_scores
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocessa o texto para análise."""
        # Remove caracteres especiais mas mantém pontuação básica
        text = re.sub(r'[^\w\s.,!?;:-]', ' ', text)
        # Normaliza espaços
        text = re.sub(r'\s+', ' ', text)
        # Remove linhas muito curtas
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 3]
        return ' '.join(lines).strip().lower()
    
    def _analyze_emotion_keywords(self, text: str) -> Dict[str, float]:
        """Analisa palavras-chave emocionais no texto."""
        words = nltk.word_tokenize(text)
        emotion_scores = {emotion: 0.0 for emotion in self.emotion_keywords}
        
        for i, word in enumerate(words):
            # Verifica intensificadores
            intensity_multiplier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensity_multiplier = self.intensifiers[words[i-1]]
            
            # Conta ocorrências de palavras emocionais
            for emotion, keywords in self.emotion_keywords.items():
                if word in keywords:
                    emotion_scores[emotion] += intensity_multiplier
                # Verifica variações da palavra
                for keyword in keywords:
                    if keyword in word or word in keyword:
                        emotion_scores[emotion] += 0.5 * intensity_multiplier
        
        # Normaliza scores pelo comprimento do texto
        total_words = len(words)
        if total_words > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = emotion_scores[emotion] / total_words * 100
        
        return emotion_scores
    
    def _analyze_context(self, text: str) -> Dict[str, float]:
        """Analisa o contexto das frases para detectar sentimentos."""
        sentences = nltk.sent_tokenize(text)
        context_scores = {emotion: 0.0 for emotion in self.emotion_keywords}
        
        for sentence in sentences:
            blob = TextBlob(sentence)
            polarity = blob.sentiment.polarity
            
            # Mapeia polaridade para emoções
            if polarity < -0.3:
                context_scores['tristeza'] += abs(polarity)
                context_scores['raiva'] += abs(polarity) * 0.5
            elif polarity > 0.3:
                context_scores['felicidade'] += polarity
                context_scores['esperança'] += polarity * 0.7
            else:
                context_scores['nostalgia'] += 0.1
        
        return context_scores
    
    def _combine_analyses(self, polarity: float, emotion_scores: Dict[str, float], 
                         context_scores: Dict[str, float]) -> Dict:
        """Combina diferentes análises para resultado final."""
        # Combina scores de emoção e contexto
        combined_scores = {}
        for emotion in emotion_scores:
            combined_scores[emotion] = (
                emotion_scores[emotion] * 0.7 + 
                context_scores.get(emotion, 0) * 0.3
            )
        
        # Ajusta com base na polaridade geral
        if polarity < -0.2:
            combined_scores['tristeza'] *= 1.3
            combined_scores['raiva'] *= 1.2
        elif polarity > 0.2:
            combined_scores['felicidade'] *= 1.3
            combined_scores['esperança'] *= 1.2
        
        # Encontra emoções primária e secundária
        sorted_emotions = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_emotion = sorted_emotions[0][0] if sorted_emotions[0][1] > 0.1 else 'neutro'
        secondary_emotion = None
        
        if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0.05:
            secondary_emotion = sorted_emotions[1][0]
        
        # Calcula score final
        final_score = sorted_emotions[0][1] if sorted_emotions else 0.0
        
        # Extrai palavras-chave relevantes
        keywords = self._extract_keywords(primary_emotion, secondary_emotion)
        
        return {
            'primary': primary_emotion,
            'secondary': secondary_emotion,
            'score': min(final_score, 1.0),  # Limita a 1.0
            'keywords': keywords
        }
    
    def _extract_keywords(self, primary: str, secondary: Optional[str]) -> List[str]:
        """Extrai palavras-chave relevantes para as emoções detectadas."""
        keywords = []
        
        if primary in self.emotion_keywords:
            keywords.extend(self.emotion_keywords[primary][:5])  # Top 5 keywords
        
        if secondary and secondary in self.emotion_keywords:
            keywords.extend(self.emotion_keywords[secondary][:3])  # Top 3 keywords
        
        return keywords
    
    def _calculate_confidence(self, subjectivity: float, emotion_scores: Dict[str, float], 
                            text_length: int) -> float:
        """Calcula a confiança na análise."""
        # Fatores que influenciam a confiança
        subjectivity_factor = subjectivity  # Textos mais subjetivos são mais confiáveis
        emotion_strength = max(emotion_scores.values()) if emotion_scores else 0
        length_factor = min(text_length / 500, 1.0)  # Textos mais longos são mais confiáveis
        
        confidence = (subjectivity_factor * 0.4 + 
                     emotion_strength * 0.4 + 
                     length_factor * 0.2)
        
        return min(confidence, 1.0)