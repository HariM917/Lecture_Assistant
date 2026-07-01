"""
Sentiment Analysis Service
Analyzes emotional tone and sentiment of lecture content
"""
from typing import Dict, Any, List
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class SentimentScore:
    overall: float  # -1 (negative) to 1 (positive)
    confidence: float  # 0 to 1
    emotions: Dict[str, float]  # joy, sadness, anger, fear, surprise, neutral
    intensity: str  # low, medium, high
    keywords: List[str]  # sentiment-bearing words


class SentimentAnalysisService:
    """Analyze sentiment and emotions in lecture content"""

    def __init__(self):
        # Lexicon-based approach (no model download needed)
        self.positive_words = {
            'excellent': 1.0, 'amazing': 0.9, 'wonderful': 0.9, 'great': 0.8,
            'good': 0.7, 'nice': 0.6, 'fine': 0.5, 'beautiful': 0.9,
            'fantastic': 1.0, 'outstanding': 1.0, 'brilliant': 0.95,
            'clever': 0.8, 'interesting': 0.7, 'cool': 0.7, 'awesome': 0.9,
            'wonderful': 0.9, 'perfect': 1.0, 'love': 0.8, 'enjoy': 0.7,
            'fascinating': 0.85, 'impressive': 0.8, 'remarkable': 0.85
        }

        self.negative_words = {
            'terrible': -1.0, 'awful': -0.95, 'horrible': -1.0, 'bad': -0.7,
            'poor': -0.6, 'ugly': -0.8, 'hate': -0.9, 'disgusting': -1.0,
            'disappointing': -0.8, 'frustrating': -0.8, 'confusing': -0.6,
            'boring': -0.7, 'tedious': -0.7, 'difficult': -0.5,
            'problematic': -0.7, 'wrong': -0.6, 'failed': -0.8,
            'useless': -0.9, 'weak': -0.6, 'stupid': -0.9
        }

        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'delighted', 'cheerful', 'gleeful'],
            'sadness': ['sad', 'unhappy', 'depressed', 'sorrowful', 'miserable'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'enraged', 'hostile'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
            'surprise': ['surprised', 'amazed', 'shocked', 'astonished', 'stunned'],
            'neutral': ['neutral', 'okay', 'meh', 'average', 'normal']
        }

    def analyze(self, text: str, context: str = "lecture") -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            if not text or not text.strip():
                return self._empty_sentiment()

            words = text.lower().split()
            sentiment_scores = []
            sentiment_keywords = []
            emotion_counts = {emotion: 0 for emotion in self.emotion_keywords}

            # Score each word
            for word in words:
                word_clean = re.sub(r'[^\w]', '', word)

                if word_clean in self.positive_words:
                    sentiment_scores.append(self.positive_words[word_clean])
                    sentiment_keywords.append(word_clean)
                elif word_clean in self.negative_words:
                    sentiment_scores.append(self.negative_words[word_clean])
                    sentiment_keywords.append(word_clean)

                # Detect emotions
                for emotion, keywords in self.emotion_keywords.items():
                    if word_clean in keywords:
                        emotion_counts[emotion] += 1

            # Calculate overall sentiment
            if sentiment_scores:
                overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            else:
                overall_sentiment = 0.0

            # Normalize to -1 to 1 range
            overall_sentiment = max(-1.0, min(1.0, overall_sentiment))

            # Calculate confidence based on keyword density
            keyword_density = len(sentiment_keywords) / max(len(words), 1)
            confidence = min(keyword_density * 2, 1.0)  # Cap at 1.0

            # Determine dominant emotion
            total_emotions = sum(emotion_counts.values())
            emotions_normalized = {
                emotion: count / max(total_emotions, 1)
                for emotion, count in emotion_counts.items()
            }
            if total_emotions == 0:
                emotions_normalized['neutral'] = 1.0

            # Determine intensity
            intensity = self._get_intensity(abs(overall_sentiment))

            logger.info(f"Sentiment analysis: {overall_sentiment:.2f}, confidence: {confidence:.2f}")

            return {
                'overall': round(overall_sentiment, 3),
                'confidence': round(confidence, 3),
                'emotions': {k: round(v, 3) for k, v in emotions_normalized.items()},
                'intensity': intensity,
                'keywords': list(set(sentiment_keywords))[:10],  # Top 10 unique keywords
                'sentiment_label': self._get_sentiment_label(overall_sentiment),
                'context': context
            }

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._empty_sentiment()

    def batch_analyze(self, texts: List[str], context: str = "lecture") -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text, context) for text in texts]

    def analyze_by_sentences(self, text: str) -> Dict[str, Any]:
        """Break text into sentences and analyze each"""
        sentences = re.split(r'[.!?]+', text)
        sentiments = [self.analyze(sent.strip()) for sent in sentences if sent.strip()]

        if not sentiments:
            return self._empty_sentiment()

        overall = sum(s['overall'] for s in sentiments) / len(sentiments)
        avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)

        return {
            'overall': round(overall, 3),
            'average_confidence': round(avg_confidence, 3),
            'sentence_count': len(sentiments),
            'sentences': sentiments,
            'sentiment_label': self._get_sentiment_label(overall),
            'trend': self._get_sentiment_trend(sentiments)
        }

    def _get_sentiment_label(self, score: float) -> str:
        """Convert score to label"""
        if score > 0.5:
            return 'very_positive'
        elif score > 0.1:
            return 'positive'
        elif score > -0.1:
            return 'neutral'
        elif score > -0.5:
            return 'negative'
        else:
            return 'very_negative'

    def _get_intensity(self, abs_score: float) -> str:
        """Determine intensity level"""
        if abs_score > 0.7:
            return 'high'
        elif abs_score > 0.3:
            return 'medium'
        else:
            return 'low'

    def _get_sentiment_trend(self, sentiments: List[Dict]) -> str:
        """Detect if sentiment is improving or declining"""
        if len(sentiments) < 2:
            return 'stable'

        first_half_avg = sum(s['overall'] for s in sentiments[:len(sentiments)//2]) / max(len(sentiments)//2, 1)
        second_half_avg = sum(s['overall'] for s in sentiments[len(sentiments)//2:]) / max(len(sentiments) - len(sentiments)//2, 1)

        if second_half_avg > first_half_avg + 0.1:
            return 'improving'
        elif second_half_avg < first_half_avg - 0.1:
            return 'declining'
        else:
            return 'stable'

    def _empty_sentiment(self) -> Dict[str, Any]:
        """Return empty sentiment object"""
        return {
            'overall': 0.0,
            'confidence': 0.0,
            'emotions': {k: 0.0 for k in self.emotion_keywords},
            'intensity': 'neutral',
            'keywords': [],
            'sentiment_label': 'neutral',
            'context': 'lecture'
        }
