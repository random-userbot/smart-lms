"""
Smart LMS - NLP Service
Sentiment analysis, bias correction, and text processing
"""

import yaml
import re
from typing import Dict, List, Optional
import numpy as np


class NLPService:
    """NLP service for feedback analysis and sentiment detection"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize NLP service"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.nlp_config = self.config['nlp']
        self.sentiment_model = self.nlp_config['sentiment_model']
        self.bias_correction_enabled = self.nlp_config['bias_correction']['enabled']
        
        # Initialize sentiment analyzer
        if self.sentiment_model == 'vader':
            self._init_vader()
        elif self.sentiment_model == 'distilbert':
            self._init_distilbert()
    
    def _init_vader(self):
        """Initialize VADER sentiment analyzer"""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
        except ImportError:
            raise ImportError("VADER not installed. Run: pip install vaderSentiment")
    
    def _init_distilbert(self):
        """Initialize DistilBERT sentiment analyzer"""
        try:
            from transformers import pipeline
            model_name = self.nlp_config['distilbert_model']
            self.distilbert = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=-1  # CPU
            )
        except ImportError:
            raise ImportError("Transformers not installed. Run: pip install transformers torch")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text
        
        Args:
            text: Raw text input
        
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores and label
        """
        if not text or len(text) < self.nlp_config['min_feedback_length']:
            return {
                'label': 'neutral',
                'positive': 0.0,
                'neutral': 1.0,
                'negative': 0.0,
                'compound': 0.0
            }
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        if self.sentiment_model == 'vader':
            return self._analyze_vader(cleaned_text)
        elif self.sentiment_model == 'distilbert':
            return self._analyze_distilbert(cleaned_text)
    
    def _analyze_vader(self, text: str) -> Dict:
        """Analyze sentiment using VADER with improved mixed sentiment handling"""
        scores = self.vader.polarity_scores(text)
        
        # Determine label with better mixed sentiment detection
        compound = scores['compound']
        pos = scores['pos']
        neg = scores['neg']
        
        # Check for mixed sentiment (both positive and negative present)
        is_mixed = (pos > 0.1 and neg > 0.1)
        
        if is_mixed:
            # For mixed sentiment, use a weighted approach
            # If positive outweighs negative significantly, label as positive
            if pos > neg * 1.3:  # 30% threshold
                label = 'positive'
            elif neg > pos * 1.3:
                label = 'negative'
            else:
                # Too close, use compound score
                label = 'positive' if compound >= 0 else 'negative'
        else:
            # Standard classification
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
        
        return {
            'label': label,
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'compound': scores['compound'],
            'is_mixed': is_mixed
        }
    
    def _analyze_distilbert(self, text: str) -> Dict:
        """Analyze sentiment using DistilBERT"""
        result = self.distilbert(text[:512])[0]  # Truncate to max length
        
        label = result['label'].lower()
        score = result['score']
        
        # Convert to VADER-like format
        if label == 'positive':
            return {
                'label': 'positive',
                'positive': score,
                'neutral': 1 - score,
                'negative': 0.0,
                'compound': score
            }
        elif label == 'negative':
            return {
                'label': 'negative',
                'positive': 0.0,
                'neutral': 1 - score,
                'negative': score,
                'compound': -score
            }
        else:
            return {
                'label': 'neutral',
                'positive': 0.0,
                'neutral': 1.0,
                'negative': 0.0,
                'compound': 0.0
            }
    
    def extract_topics(self, texts: List[str], top_n: int = 5) -> List[str]:
        """
        Extract key topics from a list of texts
        
        Args:
            texts: List of text documents
            top_n: Number of top topics to return
        
        Returns:
            List of top keywords/topics
        """
        try:
            from keybert import KeyBERT
            kw_model = KeyBERT()
            
            # Combine texts
            combined_text = " ".join([self.clean_text(t) for t in texts])
            
            # Extract keywords
            keywords = kw_model.extract_keywords(
                combined_text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n
            )
            
            return [kw[0] for kw in keywords]
        
        except ImportError:
            # Fallback: simple word frequency
            from collections import Counter
            words = []
            for text in texts:
                cleaned = self.clean_text(text)
                words.extend(cleaned.split())
            
            # Filter common words
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were'}
            filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
            
            # Get most common
            counter = Counter(filtered_words)
            return [word for word, count in counter.most_common(top_n)]
    
    def correct_bias(self, feedback_data: List[Dict], engagement_data: List[Dict], 
                    grades_data: List[Dict]) -> List[Dict]:
        """
        Apply bias correction to feedback ratings
        
        Args:
            feedback_data: List of feedback dictionaries with 'rating' and 'student_id'
            engagement_data: List of engagement logs with 'engagement_score' and 'student_id'
            grades_data: List of grade records with 'percentage' and 'student_id'
        
        Returns:
            List of feedback with corrected ratings
        """
        if not self.bias_correction_enabled:
            return feedback_data
        
        method = self.nlp_config['bias_correction']['method']
        
        if method == 'residual':
            return self._correct_bias_residual(feedback_data, engagement_data, grades_data)
        elif method == 'covariate':
            return self._correct_bias_covariate(feedback_data, engagement_data, grades_data)
        else:
            return feedback_data
    
    def _correct_bias_residual(self, feedback_data: List[Dict], 
                               engagement_data: List[Dict], 
                               grades_data: List[Dict]) -> List[Dict]:
        """
        Residual-based bias correction
        
        Regress feedback rating on grades and engagement, use residuals as corrected rating
        """
        if len(feedback_data) < 5:
            # Not enough data for regression
            return feedback_data
        
        # Create student-level aggregates
        student_engagement = {}
        for eng in engagement_data:
            sid = eng['student_id']
            if sid not in student_engagement:
                student_engagement[sid] = []
            student_engagement[sid].append(eng['engagement_score'])
        
        student_grades = {}
        for grade in grades_data:
            sid = grade['student_id']
            if sid not in student_grades:
                student_grades[sid] = []
            student_grades[sid].append(grade['percentage'])
        
        # Prepare data for regression
        X = []  # [avg_engagement, avg_grade]
        y = []  # feedback rating
        
        for feedback in feedback_data:
            sid = feedback['student_id']
            
            avg_engagement = np.mean(student_engagement.get(sid, [50])) / 100  # Normalize to 0-1
            avg_grade = np.mean(student_grades.get(sid, [50])) / 100  # Normalize to 0-1
            
            X.append([avg_engagement, avg_grade])
            y.append(feedback['rating'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Simple linear regression (y = b0 + b1*x1 + b2*x2)
        # Using least squares: beta = (X'X)^-1 X'y
        X_with_intercept = np.column_stack([np.ones(len(X)), X])
        
        try:
            beta = np.linalg.lstsq(X_with_intercept, y, rcond=None)[0]
            
            # Compute residuals
            y_pred = X_with_intercept @ beta
            residuals = y - y_pred
            
            # Corrected rating = mean rating + residual
            mean_rating = np.mean(y)
            
            # Apply correction to feedback
            corrected_feedback = []
            for i, feedback in enumerate(feedback_data):
                corrected = feedback.copy()
                corrected['rating_original'] = feedback['rating']
                corrected['rating_corrected'] = mean_rating + residuals[i]
                corrected['rating'] = corrected['rating_corrected']
                corrected_feedback.append(corrected)
            
            return corrected_feedback
        
        except np.linalg.LinAlgError:
            # Singular matrix, return original
            return feedback_data
    
    def _correct_bias_covariate(self, feedback_data: List[Dict], 
                               engagement_data: List[Dict], 
                               grades_data: List[Dict]) -> List[Dict]:
        """
        Covariate adjustment bias correction
        
        Include engagement and grades as covariates in the model
        """
        # For now, just add the covariates to the feedback data
        # The evaluation model will use them as features
        
        student_engagement = {}
        for eng in engagement_data:
            sid = eng['student_id']
            if sid not in student_engagement:
                student_engagement[sid] = []
            student_engagement[sid].append(eng['engagement_score'])
        
        student_grades = {}
        for grade in grades_data:
            sid = grade['student_id']
            if sid not in student_grades:
                student_grades[sid] = []
            student_grades[sid].append(grade['percentage'])
        
        corrected_feedback = []
        for feedback in feedback_data:
            corrected = feedback.copy()
            sid = feedback['student_id']
            
            corrected['avg_engagement'] = np.mean(student_engagement.get(sid, [50]))
            corrected['avg_grade'] = np.mean(student_grades.get(sid, [50]))
            
            corrected_feedback.append(corrected)
        
        return corrected_feedback
    
    def analyze_feedback_batch(self, feedback_texts: List[str]) -> Dict:
        """
        Analyze a batch of feedback texts
        
        Args:
            feedback_texts: List of feedback text strings
        
        Returns:
            Dictionary with aggregate sentiment analysis
        """
        if not feedback_texts:
            return {
                'total_count': 0,
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'avg_compound': 0.0,
                'topics': []
            }
        
        sentiments = [self.analyze_sentiment(text) for text in feedback_texts]
        
        # Count by label
        positive_count = sum(1 for s in sentiments if s['label'] == 'positive')
        neutral_count = sum(1 for s in sentiments if s['label'] == 'neutral')
        negative_count = sum(1 for s in sentiments if s['label'] == 'negative')
        
        # Average compound score
        avg_compound = np.mean([s['compound'] for s in sentiments])
        
        # Extract topics
        topics = self.extract_topics(feedback_texts)
        
        return {
            'total_count': len(feedback_texts),
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'positive_percentage': (positive_count / len(feedback_texts)) * 100,
            'neutral_percentage': (neutral_count / len(feedback_texts)) * 100,
            'negative_percentage': (negative_count / len(feedback_texts)) * 100,
            'avg_compound': avg_compound,
            'topics': topics,
            'sentiments': sentiments
        }
    
    def get_sentiment_trend(self, feedback_data: List[Dict]) -> List[Dict]:
        """
        Get sentiment trend over time
        
        Args:
            feedback_data: List of feedback dictionaries with 'timestamp' and 'text'
        
        Returns:
            List of sentiment scores over time
        """
        # Sort by timestamp
        sorted_feedback = sorted(feedback_data, key=lambda x: x.get('created_at', ''))
        
        trend = []
        for feedback in sorted_feedback:
            sentiment = self.analyze_sentiment(feedback['text'])
            trend.append({
                'timestamp': feedback.get('created_at'),
                'compound': sentiment['compound'],
                'label': sentiment['label']
            })
        
        return trend
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text using frequency analysis with improved cleaning
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
        
        Returns:
            List of keywords
        """
        if not text or len(text) < 10:
            return []
        
        # Clean text
        cleaned = self.clean_text(text)
        
        # Remove punctuation properly
        import string
        cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))
        
        # Split into words
        words = cleaned.split()
        
        # Expanded stopwords list
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 
            'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 
            'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 
            'why', 'how', 'very', 'too', 'more', 'most', 'some', 'any', 'much', 'many',
            'also', 'just', 'only', 'such', 'than', 'then', 'them', 'their', 'there',
            'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further',
            'once', 'here', 'there', 'all', 'both', 'each', 'few', 'other', 'another',
            'same', 'own', 'so', 'no', 'not', 'nor', 'now', 'because', 'while', 'during'
        }
        
        # Filter words - minimum length 4 characters
        filtered_words = [w for w in words if w not in stopwords and len(w) >= 4]
        
        # Count frequency
        from collections import Counter
        word_counts = Counter(filtered_words)
        
        # Get top keywords
        keywords = [word for word, count in word_counts.most_common(top_n)]
        
        return keywords
    
    def detect_themes(self, text: str) -> List[str]:
        """
        Detect common themes in feedback text with improved accuracy
        
        Args:
            text: Input feedback text
        
        Returns:
            List of detected themes
        """
        if not text or len(text) < 10:
            return []
        
        text_lower = text.lower()
        detected_themes = []
        
        # Define theme keywords with better categorization
        theme_keywords = {
            'content_quality': ['content', 'material', 'topic', 'subject', 'information', 'knowledge', 'curriculum'],
            'teaching_style': ['teaching', 'explanation', 'teach', 'instructor', 'professor', 'teacher', 'style'],
            'clarity': ['clear', 'unclear', 'understand', 'confusing', 'confused', 'clarity', 'understandable', 'comprehensible'],
            'pace': ['pace', 'speed', 'fast', 'slow', 'rushed', 'quick', 'tempo', 'timing'],
            'engagement': ['engaging', 'interesting', 'boring', 'engaged', 'attention', 'interactive', 'captivating', 'dull'],
            'examples': ['example', 'examples', 'demonstration', 'demo', 'case study', 'practical', 'practice', 'hands-on'],
            'visual_aids': ['slide', 'slides', 'visual', 'diagram', 'chart', 'presentation', 'graphics', 'illustrations'],
            'technical_issues': ['technical', 'audio', 'video', 'sound', 'buffering', 'loading', 'glitch', 'lag', 'quality was', 'connection'],
            'difficulty': ['difficult', 'hard', 'easy', 'challenging', 'complex', 'simple', 'tough', 'struggle'],
            'organization': ['organized', 'structure', 'organized', 'disorganized', 'flow', 'arrangement', 'layout'],
            'interaction': ['question', 'questions', 'interactive', 'discussion', 'participate', 'engage', 'dialogue'],
            'time_management': ['time', 'duration', 'length', 'long', 'short', 'overtime', 'finish'],
            'relevance': ['relevant', 'applicable', 'real-world', 'practical', 'useful', 'application']
        }
        
        # Check for each theme with better matching
        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if theme not in detected_themes:
                        detected_themes.append(theme)
                    break
        
        return detected_themes
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detect emotions in text (happiness, sadness, anger, frustration, confusion)
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with emotion scores (0-1 scale)
        """
        if not text or len(text) < 5:
            return {
                'happiness': 0.0,
                'sadness': 0.0,
                'anger': 0.0,
                'frustration': 0.0,
                'confusion': 0.0,
                'satisfaction': 0.0
            }
        
        text_lower = text.lower()
        
        # Emotion keyword dictionaries
        emotion_keywords = {
            'happiness': ['happy', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'enjoyed', 'fantastic', 'perfect', 'brilliant'],
            'sadness': ['sad', 'disappointed', 'unfortunate', 'depressed', 'unhappy', 'miserable', 'regret'],
            'anger': ['angry', 'furious', 'mad', 'outraged', 'irritated', 'annoyed', 'frustrating', 'terrible', 'awful'],
            'frustration': ['frustrated', 'struggling', 'difficult', 'challenging', 'stuck', 'lost', 'overwhelmed', 'stressed'],
            'confusion': ['confused', 'confusing', 'unclear', 'dont understand', "don't understand", 'lost', 'puzzled', 'bewildered'],
            'satisfaction': ['satisfied', 'content', 'pleased', 'good', 'nice', 'helpful', 'useful', 'appreciate']
        }
        
        # Count emotion indicators
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by number of keywords checked
            emotion_scores[emotion] = min(count / 3.0, 1.0)  # Cap at 1.0
        
        return emotion_scores
    
    def analyze_aspect_sentiment(self, text: str) -> Dict[str, Dict]:
        """
        Analyze sentiment for different aspects of the lecture
        
        Args:
            text: Input feedback text
        
        Returns:
            Dictionary with aspect-specific sentiment
        """
        text_lower = text.lower()
        
        aspects = {
            'content': ['content', 'material', 'topic', 'subject', 'curriculum'],
            'teaching': ['teaching', 'instructor', 'professor', 'teacher', 'explanation'],
            'delivery': ['delivery', 'presentation', 'communication', 'speaking'],
            'technical': ['audio', 'video', 'slides', 'quality', 'technical'],
            'engagement': ['engaging', 'interactive', 'interesting', 'boring'],
            'difficulty': ['difficult', 'easy', 'hard', 'challenging', 'complex']
        }
        
        # Sentiment indicators
        positive_words = ['good', 'great', 'excellent', 'clear', 'helpful', 'useful', 'easy', 'well']
        negative_words = ['bad', 'poor', 'unclear', 'confusing', 'difficult', 'terrible', 'awful']
        
        results = {}
        
        for aspect, keywords in aspects.items():
            # Check if aspect is mentioned
            mentioned = any(keyword in text_lower for keyword in keywords)
            
            if mentioned:
                # Look for sentiment words near the aspect keywords
                # Simplified: check overall sentiment when aspect is present
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    sentiment = 'positive'
                    score = 0.6 + (pos_count * 0.1)
                elif neg_count > pos_count:
                    sentiment = 'negative'
                    score = -(0.6 + (neg_count * 0.1))
                else:
                    sentiment = 'neutral'
                    score = 0.0
                
                results[aspect] = {
                    'sentiment': sentiment,
                    'score': max(min(score, 1.0), -1.0),  # Clamp between -1 and 1
                    'mentioned': True
                }
            else:
                results[aspect] = {
                    'sentiment': 'not_mentioned',
                    'score': 0.0,
                    'mentioned': False
                }
        
        return results
    
    def analyze_feedback_aggregate(self, feedbacks: List[Dict]) -> Dict:
        """
        Aggregate analysis of multiple feedbacks
        
        Args:
            feedbacks: List of feedback dictionaries
        
        Returns:
            Aggregated analysis results
        """
        if not feedbacks:
            return {
                'total_count': 0,
                'avg_sentiment_compound': 0.0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'common_themes': [],
                'top_keywords': []
            }
        
        sentiments = []
        all_keywords = []
        all_themes = []
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for feedback in feedbacks:
            # Get or analyze sentiment
            if 'nlp_analysis' in feedback and 'sentiment' in feedback['nlp_analysis']:
                sentiment = feedback['nlp_analysis']['sentiment']
            else:
                text = feedback.get('combined_text') or feedback.get('text', '')
                sentiment = self.analyze_sentiment(text)
            
            sentiments.append(sentiment['compound'])
            sentiment_counts[sentiment['label']] += 1
            
            # Collect keywords and themes
            if 'nlp_analysis' in feedback:
                all_keywords.extend(feedback['nlp_analysis'].get('keywords', []))
                all_themes.extend(feedback['nlp_analysis'].get('themes', []))
        
        # Calculate averages
        avg_compound = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        # Get most common keywords and themes
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        theme_counts = Counter(all_themes)
        
        return {
            'total_count': len(feedbacks),
            'avg_sentiment_compound': avg_compound,
            'sentiment_distribution': sentiment_counts,
            'common_themes': [theme for theme, count in theme_counts.most_common(10)],
            'top_keywords': [word for word, count in keyword_counts.most_common(20)]
        }
    
    def comprehensive_analysis(self, text: str) -> Dict:
        """
        Perform comprehensive NLP analysis on feedback text
        Includes sentiment, emotions, themes, keywords, and aspect-based sentiment
        
        Args:
            text: Input feedback text
        
        Returns:
            Complete analysis results
        """
        # Basic sentiment analysis
        sentiment = self.analyze_sentiment(text)
        
        # Emotion detection
        emotions = self.detect_emotions(text)
        
        # Theme detection
        themes = self.detect_themes(text)
        
        # Keyword extraction
        keywords = self.extract_keywords(text, top_n=10)
        
        # Aspect-based sentiment
        aspects = self.analyze_aspect_sentiment(text)
        
        # Determine dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if any(emotions.values()) else 'neutral'
        
        # Calculate overall quality score (0-100)
        quality_score = self._calculate_quality_score(sentiment, emotions, themes)
        
        return {
            'sentiment': sentiment,
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'themes': themes,
            'keywords': keywords,
            'aspect_sentiment': aspects,
            'quality_score': quality_score,
            'text_length': len(text),
            'word_count': len(text.split())
        }
    
    def _calculate_quality_score(self, sentiment: Dict, emotions: Dict, themes: List[str]) -> float:
        """
        Calculate overall feedback quality score based on multiple factors
        
        Args:
            sentiment: Sentiment analysis results
            emotions: Emotion detection results
            themes: Detected themes
        
        Returns:
            Quality score (0-100)
        """
        # Base score from sentiment (0-100 scale)
        base_score = ((sentiment['compound'] + 1) / 2) * 100
        
        # Adjust for specific emotions
        emotion_adjustment = 0
        if emotions.get('happiness', 0) > 0.5:
            emotion_adjustment += 10
        if emotions.get('frustration', 0) > 0.5:
            emotion_adjustment -= 15
        if emotions.get('confusion', 0) > 0.5:
            emotion_adjustment -= 10
        if emotions.get('satisfaction', 0) > 0.5:
            emotion_adjustment += 5
        
        # Adjust for negative themes
        negative_themes = ['technical_issues', 'difficulty']
        theme_penalty = sum(5 for theme in themes if theme in negative_themes)
        
        # Calculate final score
        final_score = base_score + emotion_adjustment - theme_penalty
        
        # Clamp between 0 and 100
        return max(0, min(100, final_score))


# Singleton instance
_nlp_service = None

def get_nlp_service() -> NLPService:
    """Get NLP service singleton"""
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPService()
    return _nlp_service
