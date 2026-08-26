import re
from typing import Dict, List, Any


class NLPService:
    """
    NLP Service encapsulating text processing algorithms, text cleanup,
    keyword extraction, and sentiment estimation.
    """

    @staticmethod
    def extract_text_stats(text: str) -> Dict[str, Any]:
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        words = cleaned_text.split()
        word_count = len(words)
        char_count = len(cleaned_text)

        # Keyword extraction stub (top unique words > 3 chars)
        word_freq: Dict[str, int] = {}
        for w in words:
            clean_word = re.sub(r'[^\w]', '', w).lower()
            if len(clean_word) > 3:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        sorted_keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]

        # Simple heuristic sentiment analysis stub
        positive_words = {'good', 'great', 'excellent', 'amazing', 'positive', 'successful', 'best', 'valuable'}
        negative_words = {'bad', 'poor', 'terrible', 'negative', 'failed', 'worst', 'error', 'issue'}
        
        pos_score = sum(1 for w in words if w.lower() in positive_words)
        neg_score = sum(1 for w in words if w.lower() in negative_words)
        total = pos_score + neg_score or 1

        return {
            "word_count": word_count,
            "char_count": char_count,
            "keywords": sorted_keywords,
            "sentiment": {
                "positive": round(pos_score / total, 2),
                "negative": round(neg_score / total, 2),
                "neutral": round(1.0 - ((pos_score + neg_score) / max(word_count, 1)), 2)
            }
        }
