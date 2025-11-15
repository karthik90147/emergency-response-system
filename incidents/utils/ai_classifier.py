import re
from textblob import TextBlob
import nltk
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class EmergencyClassifier:
    def __init__(self):
        self.emergency_keywords = {
            # ADDED 'collapsing' to catch structural failure as a strong FIRE indicator
            'FIRE': ['fire', 'smoke', 'burning', 'flames', 'blaze', 'explosion', 'blast', 'collapsing'],
            'MEDICAL': ['injured', 'hurt', 'pain', 'sick', 'blood', 'accident', 'heart attack', 
                       'unconscious', 'breathing', 'chest pain', 'ambulance', 'medical', 'trapped'],
            'ACCIDENT': ['accident', 'crash', 'collision', 'hit', 'vehicle', 'car', 'bike', 
                        'truck', 'fell', 'road'],
            'CRIME': ['robbery', 'theft', 'stolen', 'attack', 'assault', 'violence', 'police',
                     'threat', 'weapon', 'gun', 'knife', 'danger'],
            'NATURAL': ['earthquake', 'flood', 'storm', 'cyclone', 'landslide', 'disaster',
                       'tsunami', 'hurricane', 'tornado'],
        }
        
        self.severity_keywords = {
            # ADDED 'collapsing' and 'trapped' to ensure CRITICAL status
            'CRITICAL': ['dying', 'dead', 'critical', 'severe', 'extreme', 'urgent', 'emergency',
                        'life-threatening', 'unconscious', 'bleeding heavily', 'collapsing', 'trapped'],
            'HIGH': ['serious', 'major', 'significant', 'dangerous', 'urgent', 'injured',
                    'multiple', 'large'],
            'MEDIUM': ['moderate', 'some', 'minor injuries', 'smoke', 'small'],
            'LOW': ['minor', 'small', 'slight', 'little'],
        }
    
    def classify_emergency(self, text):
        """
        Classify emergency type and severity from text input
        Returns: (emergency_type, severity, confidence)
        """
        if not text:
            return 'OTHER', 'MEDIUM', 0.0
        
        text_lower = text.lower()
        
        # Count keyword matches for each emergency type
        type_scores = {}
        for etype, keywords in self.emergency_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[etype] = score
        
        # Determine emergency type
        if type_scores:
            emergency_type = max(type_scores, key=type_scores.get)
            max_score = type_scores[emergency_type]
            confidence = min(max_score / 3.0, 1.0)  # Normalize confidence
        else:
            emergency_type = 'OTHER'
            confidence = 0.3
        
        # Determine severity
        severity_scores = {}
        for severity, keywords in self.severity_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                severity_scores[severity] = score
        
        if severity_scores:
            severity = max(severity_scores, key=severity_scores.get)
        else:
            severity = 'MEDIUM'  # Default severity
        
        return emergency_type, severity, round(confidence, 2)
    
    def analyze_sentiment(self, text):
        """Analyze urgency based on sentiment"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Negative polarity often indicates more urgent situations
            if polarity < -0.5:
                return 'CRITICAL'
            elif polarity < 0:
                return 'HIGH'
            else:
                return 'MEDIUM'
        except:
            return 'MEDIUM'