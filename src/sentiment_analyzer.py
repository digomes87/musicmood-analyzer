import nltk
from textblob import TextBlob
import re
from typing import Dict, List, Optional


class SentimentAnalyzer:
    """Analyzes sentiments in song lyrics using natural language processing."""
    
    def __init__(self):
        self._download_nltk_data()
        self._load_emotion_keywords()
    
    def _download_nltk_data(self):
        """Downloads necessary NLTK data."""
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
        """Loads emotional keyword dictionaries."""
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
        
        # Intensifying words
        self.intensifiers = {
            'muito': 1.5, 'extremely': 1.8, 'really': 1.3, 'so': 1.2, 'very': 1.4,
            'totally': 1.6, 'completely': 1.7, 'absolutely': 1.8, 'incredibly': 1.6,
            'bastante': 1.3, 'extremamente': 1.8, 'realmente': 1.3, 'totalmente': 1.6,
            'completamente': 1.7, 'absolutamente': 1.8, 'incrivelmente': 1.6
        }
    
    def analyze_sentiment(self, lyrics: str) -> Dict:
        """Analyzes the main sentiment of song lyrics."""
        if not lyrics or len(lyrics.strip()) < 10:
            return {
                'sentimento_primario': 'neutro',
                'sentimento_secundario': None,
                'pontuacao_sentimento': 0.0,
                'palavras_chave': [],
                'confianca': 0.0,
                'emocoes_detectadas': {}
            }
        
        # Clean and preprocess text
        cleaned_lyrics = self._preprocess_text(lyrics)
        
        # TextBlob analysis
        blob = TextBlob(cleaned_lyrics)
        sentiment_obj = blob.sentiment
        polarity = float(sentiment_obj.polarity)  # type: ignore
        subjectivity = float(sentiment_obj.subjectivity)  # type: ignore
        
        # Emotional keyword analysis
        emotion_scores = self._analyze_emotion_keywords(cleaned_lyrics)
        
        # Contextual analysis
        context_score = self._analyze_context(cleaned_lyrics)
        
        # Combine analyses
        final_analysis = self._combine_analyses(polarity, emotion_scores, context_score)
        
        # Calculate confidence
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
        """Preprocesses text for analysis."""
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', ' ', text)
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove very short lines
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 3]
        return ' '.join(lines).strip().lower()
    
    def _analyze_emotion_keywords(self, text: str) -> Dict[str, float]:
        """Analyzes emotional keywords in text."""
        words = nltk.word_tokenize(text)
        emotion_scores = {emotion: 0.0 for emotion in self.emotion_keywords}
        
        for i, word in enumerate(words):
            # Check intensifiers
            intensity_multiplier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensity_multiplier = self.intensifiers[words[i-1]]
            
            # Count emotional word occurrences
            for emotion, keywords in self.emotion_keywords.items():
                if word in keywords:
                    emotion_scores[emotion] += intensity_multiplier
                # Check word variations
                for keyword in keywords:
                    if keyword in word or word in keyword:
                        emotion_scores[emotion] += 0.5 * intensity_multiplier
        
        # Normalize scores by text length
        total_words = len(words)
        if total_words > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = emotion_scores[emotion] / total_words * 100
        
        return emotion_scores
    
    def _analyze_context(self, text: str) -> Dict[str, float]:
        """Analyzes sentence context to detect sentiments."""
        sentences = nltk.sent_tokenize(text)
        context_scores = {emotion: 0.0 for emotion in self.emotion_keywords}
        
        for sentence in sentences:
            blob = TextBlob(sentence)
            sentiment_obj = blob.sentiment
            polarity = float(sentiment_obj.polarity)  # type: ignore
            
            # Map polarity to emotions
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
        """Combines different analyses for final result."""
        # Combine emotion and context scores
        combined_scores = {}
        for emotion in emotion_scores:
            combined_scores[emotion] = (
                emotion_scores[emotion] * 0.7 + 
                context_scores.get(emotion, 0) * 0.3
            )
        
        # Adjust based on general polarity
        if polarity < -0.2:
            combined_scores['tristeza'] *= 1.3
            combined_scores['raiva'] *= 1.2
        elif polarity > 0.2:
            combined_scores['felicidade'] *= 1.3
            combined_scores['esperança'] *= 1.2
        
        # Find primary and secondary emotions
        sorted_emotions = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_emotion = sorted_emotions[0][0] if sorted_emotions[0][1] > 0.1 else 'neutro'
        secondary_emotion = None
        
        if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0.05:
            secondary_emotion = sorted_emotions[1][0]
        
        # Calculate final score
        final_score = sorted_emotions[0][1] if sorted_emotions else 0.0
        
        # Extract relevant keywords
        keywords = self._extract_keywords(primary_emotion, secondary_emotion)
        
        return {
            'primary': primary_emotion,
            'secondary': secondary_emotion,
            'score': min(final_score, 1.0),  # Limit to 1.0
            'keywords': keywords
        }
    
    def _extract_keywords(self, primary: str, secondary: Optional[str]) -> List[str]:
        """Extracts relevant keywords for detected emotions."""
        keywords = []
        
        if primary in self.emotion_keywords:
            keywords.extend(self.emotion_keywords[primary][:5])  # Top 5 keywords
        
        if secondary and secondary in self.emotion_keywords:
            keywords.extend(self.emotion_keywords[secondary][:3])  # Top 3 keywords
        
        return keywords
    
    def _calculate_confidence(self, subjectivity: float, emotion_scores: Dict[str, float], 
                            text_length: int) -> float:
        """Calculates confidence in the analysis."""
        # Factors that influence confidence
        subjectivity_factor = subjectivity  # More subjective texts are more reliable
        emotion_strength = max(emotion_scores.values()) if emotion_scores else 0
        length_factor = min(text_length / 500, 1.0)  # Longer texts are more reliable
        
        confidence = (subjectivity_factor * 0.4 + 
                     emotion_strength * 0.4 + 
                     length_factor * 0.2)
        
        return min(confidence, 1.0)