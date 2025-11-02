"""
Advanced Language Detection Service
Supports all 22 official Indian languages + English
"""

from langdetect import detect, detect_langs, LangDetectException
import langid
from typing import Optional, Dict, List, Tuple
import re

class LanguageDetector:
    """
    Multi-strategy language detection for Indian languages
    """
    
    # Complete Indian language mapping
    INDIAN_LANGUAGES = {
        # Constitutional languages
        'en': {'name': 'English', 'native': 'English', 'gtts': 'en', 'script': 'Latin'},
        'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'gtts': 'hi', 'script': 'Devanagari'},
        'bn': {'name': 'Bengali', 'native': 'বাংলা', 'gtts': 'bn', 'script': 'Bengali'},
        'te': {'name': 'Telugu', 'native': 'తెలుగు', 'gtts': 'te', 'script': 'Telugu'},
        'mr': {'name': 'Marathi', 'native': 'मराठी', 'gtts': 'mr', 'script': 'Devanagari'},
        'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'gtts': 'ta', 'script': 'Tamil'},
        'ur': {'name': 'Urdu', 'native': 'اردو', 'gtts': 'ur', 'script': 'Arabic'},
        'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'gtts': 'gu', 'script': 'Gujarati'},
        'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'gtts': 'kn', 'script': 'Kannada'},
        'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'gtts': 'ml', 'script': 'Malayalam'},
        'or': {'name': 'Odia', 'native': 'ଓଡ଼ିଆ', 'gtts': 'or', 'script': 'Oriya'},
        'pa': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'gtts': 'pa', 'script': 'Gurmukhi'},
        'as': {'name': 'Assamese', 'native': 'অসমীয়া', 'gtts': 'as', 'script': 'Bengali'},
        'mai': {'name': 'Maithili', 'native': 'मैथिली', 'gtts': 'hi', 'script': 'Devanagari'},
        'sa': {'name': 'Sanskrit', 'native': 'संस्कृतम्', 'gtts': 'sa', 'script': 'Devanagari'},
        'ks': {'name': 'Kashmiri', 'native': 'कॉशुर', 'gtts': 'hi', 'script': 'Devanagari'},
        'ne': {'name': 'Nepali', 'native': 'नेपाली', 'gtts': 'ne', 'script': 'Devanagari'},
        'sd': {'name': 'Sindhi', 'native': 'سنڌي', 'gtts': 'sd', 'script': 'Arabic'},
        'kok': {'name': 'Konkani', 'native': 'कोंकणी', 'gtts': 'hi', 'script': 'Devanagari'},
        'mni': {'name': 'Manipuri', 'native': 'মৈতৈলোন্', 'gtts': 'hi', 'script': 'Bengali'},
        'bo': {'name': 'Bodo', 'native': 'बड़ो', 'gtts': 'hi', 'script': 'Devanagari'},
        'sat': {'name': 'Santali', 'native': 'ᱥᱟᱱᱛᱟᱲᱤ', 'gtts': 'hi', 'script': 'Ol Chiki'},
        'doi': {'name': 'Dogri', 'native': 'डोगरी', 'gtts': 'hi', 'script': 'Devanagari'},
    }
    
    # Script Unicode ranges for detection
    SCRIPT_RANGES = {
        'Devanagari': (0x0900, 0x097F),
        'Bengali': (0x0980, 0x09FF),
        'Gurmukhi': (0x0A00, 0x0A7F),
        'Gujarati': (0x0A80, 0x0AFF),
        'Oriya': (0x0B00, 0x0B7F),
        'Tamil': (0x0B80, 0x0BFF),
        'Telugu': (0x0C00, 0x0C7F),
        'Kannada': (0x0C80, 0x0CFF),
        'Malayalam': (0x0D00, 0x0D7F),
        'Arabic': (0x0600, 0x06FF),  # For Urdu
    }
    
    def __init__(self):
        """Initialize language detector"""
        print("🌐 Initializing Multi-Language Detector...")
        print(f"   Supported languages: {len(self.INDIAN_LANGUAGES)}")
    
    def detect_text_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text using multiple strategies
        Returns: (language_code, confidence)
        """
        if not text or len(text.strip()) < 3:
            return 'en', 0.5
        
        text = text.strip()
        
        # Strategy 1: Script detection (most reliable for Indian languages)
        script_lang = self._detect_by_script(text)
        if script_lang:
            print(f"📝 Script detection: {script_lang}")
            return script_lang, 0.95
        
        # Strategy 2: langdetect library
        try:
            detected = detect(text)
            if detected in self.INDIAN_LANGUAGES:
                print(f"📝 langdetect: {detected}")
                return detected, 0.85
        except LangDetectException:
            pass
        
        # Strategy 3: langid library
        try:
            detected, confidence = langid.classify(text)
            if detected in self.INDIAN_LANGUAGES:
                print(f"📝 langid: {detected} (conf: {confidence})")
                return detected, confidence
        except:
            pass
        
        # Strategy 4: Probability-based detection
        try:
            probs = detect_langs(text)
            for prob in probs:
                if prob.lang in self.INDIAN_LANGUAGES and prob.prob > 0.7:
                    print(f"📝 Probability detection: {prob.lang} ({prob.prob})")
                    return prob.lang, prob.prob
        except:
            pass
        
        # Default to English
        print("📝 Defaulting to English")
        return 'en', 0.6
    
    def _detect_by_script(self, text: str) -> Optional[str]:
        """
        Detect language by analyzing Unicode script ranges
        Most reliable for Indian languages
        """
        script_counts = {script: 0 for script in self.SCRIPT_RANGES}
        
        for char in text:
            code_point = ord(char)
            for script, (start, end) in self.SCRIPT_RANGES.items():
                if start <= code_point <= end:
                    script_counts[script] += 1
        
        # Find dominant script
        dominant_script = max(script_counts, key=script_counts.get)
        if script_counts[dominant_script] > 0:
            # Map script to language
            for lang_code, lang_info in self.INDIAN_LANGUAGES.items():
                if lang_info['script'] == dominant_script:
                    return lang_code
        
        return None
    
    def detect_audio_language(self, audio_path: str) -> Tuple[str, float]:
        """
        Detect language from audio file
        This is a placeholder - actual detection happens during transcription
        Returns: (language_code, confidence)
        """
        # For audio, we'll let Google Speech Recognition auto-detect
        # or use a more sophisticated approach
        return 'auto', 1.0
    
    def get_language_info(self, lang_code: str) -> Dict:
        """Get complete language information"""
        return self.INDIAN_LANGUAGES.get(lang_code, self.INDIAN_LANGUAGES['en'])
    
    def is_supported(self, lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code in self.INDIAN_LANGUAGES
    
    def get_all_languages(self) -> List[Dict]:
        """Get list of all supported languages"""
        return [
            {
                'code': code,
                **info
            }
            for code, info in self.INDIAN_LANGUAGES.items()
        ]
    
    def get_gtts_language(self, lang_code: str) -> str:
        """Get gTTS-compatible language code"""
        return self.INDIAN_LANGUAGES.get(lang_code, {}).get('gtts', 'en')
    
    def detect_with_fallback(self, text: str, default: str = 'en') -> str:
        """
        Detect language with fallback to default
        Returns only language code
        """
        try:
            lang_code, confidence = self.detect_text_language(text)
            if confidence > 0.6:
                return lang_code
        except Exception as e:
            print(f"⚠️ Language detection error: {e}")
        
        return default


# Global instance
language_detector = LanguageDetector()