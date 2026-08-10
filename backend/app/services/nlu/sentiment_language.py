import re
from typing import Dict, Any
from pydantic import BaseModel


class SentimentAnalysisResult(BaseModel):
    sentiment_score: float  # -1.0 to +1.0
    primary_emotion: str   # frustration, anger, confusion, satisfaction, urgency, anxiety, neutral
    detected_language: str # English, Hindi, Hinglish, Tamil, Telugu, Gujarati, Marathi
    is_code_switching: bool


HINGLISH_INDICATORS = [
    "mera", "meri", "kya", "hua", "nahi", "nahi hua", "batao", "kaise", "kab", "ho gaya",
    "paise", "aaya", "bheja", "karo", "do", "hai", "hain", "par", "se", "ko", "baare", "mein"
]

HINDI_INDICATORS = [
    "नमस्ते", "मेरा", "क्या", "हुआ", "नहीं", "बताएं", "पैसे", "खाता", "बैंक"
]

EMOTION_PATTERNS = {
    "anger": ["terrible", "worst bank", "useless", "lawyer", "sue", "legal action", "bakwas", "fraud", "stole"],
    "frustration": ["waiting", "weeks", "again", "not working", "stuck", "horrible", "frustrated", "gussa"],
    "urgency": ["immediately", "urgent", "asap", "emergency", "help now", "block now", "fast"],
    "confusion": ["dont understand", "confused", "why charged", "what is this", "samajh nahi aaya"],
    "satisfaction": ["thank you", "thanks", "great", "helpful", "awesome", "shukriya", "dhanyawad"]
}


class SentimentAndLanguageEngine:
    """
    Sentiment, Emotion & Hinglish Code-Switching Analyzer for NexBank Customer Conversations.
    """
    def analyze(self, text: str) -> SentimentAnalysisResult:
        lower_text = text.lower()
        
        # 1. Language & Code-Switching Detection
        is_hindi = any(word in text for word in HINDI_INDICATORS)
        hinglish_count = sum(1 for indicator in HINGLISH_INDICATORS if re.search(r'\b' + indicator + r'\b', lower_text))
        
        if is_hindi:
            detected_lang = "Hindi"
            is_code_switch = False
        elif hinglish_count >= 2:
            detected_lang = "Hinglish"
            is_code_switch = True
        else:
            detected_lang = "English"
            is_code_switch = False

        # 2. Emotion Classification
        detected_emotion = "neutral"
        for emotion, keywords in EMOTION_PATTERNS.items():
            if any(kw in lower_text for kw in keywords):
                detected_emotion = emotion
                break

        # 3. Sentiment Scoring (-1.0 to +1.0)
        score = 0.0
        if detected_emotion in ["anger", "frustration"]:
            score = -0.85
        elif detected_emotion in ["urgency", "confusion"]:
            score = -0.45
        elif detected_emotion == "satisfaction":
            score = +0.80

        # Fine-tune score with exclamation marks or multiple negative cues
        if "!" in text and score < 0:
            score = max(-1.0, score - 0.15)

        return SentimentAnalysisResult(
            sentiment_score=round(score, 2),
            primary_emotion=detected_emotion,
            detected_language=detected_lang,
            is_code_switching=is_code_switch
        )
