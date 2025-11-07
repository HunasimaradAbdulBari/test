"""
FIXED: Ultimate Language Detector
Key Fix: Hindi vs Nepali detection (both use Devanagari)
"""

import re
from typing import Tuple, Dict, Optional
import unicodedata

class UltimateLanguageDetector:
    """
    Production-grade language detection for Indian subcontinent
    FIXED: Better Hindi vs Nepali distinction
    """
    
    # Complete language database
    LANGUAGES = {
        'en': {
            'name': 'English', 
            'native': 'English', 
            'gtts': 'en', 
            'whisper': 'en',
            'script': 'Latin',
            'unicode_range': [(0x0041, 0x007A), (0x0061, 0x007A)],
            'keywords': ['the', 'is', 'are', 'and', 'of', 'to', 'in', 'it', 'you', 'that'],
            'common_words': ['hello', 'how', 'what', 'where', 'when', 'why', 'who']
        },
        'hi': {
            'name': 'Hindi', 
            'native': 'हिन्दी', 
            'gtts': 'hi', 
            'whisper': 'hi',
            'script': 'Devanagari',
            'unicode_range': [(0x0900, 0x097F)],
            # HINDI-SPECIFIC keywords (different from Nepali)
            'keywords': ['है', 'और', 'का', 'के', 'में', 'से', 'को', 'की', 'ने', 'यह', 'था', 'हैं', 'पर'],
            'common_words': ['नमस्ते', 'कैसे', 'क्या', 'कहाँ', 'कब', 'क्यों', 'कौन', 'अच्छा', 'बहुत', 'लोग'],
            'consonants': ['क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ', 'ट', 'ठ'],
            'vowels': ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ'],
            # HINDI-SPECIFIC patterns
            'unique_patterns': ['मैं', 'तुम', 'हम', 'आप', 'वह', 'यह']
        },
        'bn': {
            'name': 'Bengali', 
            'native': 'বাংলা', 
            'gtts': 'bn', 
            'whisper': 'bn',
            'script': 'Bengali',
            'unicode_range': [(0x0980, 0x09FF)],
            'keywords': ['এবং', 'আর', 'এই', 'সে', 'যে', 'তা', 'কি', 'না', 'হয়', 'করে'],
            'common_words': ['হ্যালো', 'কেমন', 'কী', 'কোথায়', 'কখন', 'কেন', 'কে'],
            'consonants': ['ক', 'খ', 'গ', 'ঘ', 'চ', 'ছ', 'জ', 'ঝ', 'ট', 'ঠ'],
            'vowels': ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'এ', 'ঐ', 'ও', 'ঔ']
        },
        'te': {
            'name': 'Telugu', 
            'native': 'తెలుగు', 
            'gtts': 'te', 
            'whisper': 'te',
            'script': 'Telugu',
            'unicode_range': [(0x0C00, 0x0C7F)],
            'keywords': ['అని', 'కూడా', 'ఉంది', 'చేసి', 'లో', 'కి', 'నుండి', 'తో', 'గా'],
            'common_words': ['హలో', 'ఎలా', 'ఏమి', 'ఎక్కడ', 'ఎప్పుడు', 'ఎందుకు', 'ఎవరు'],
            'consonants': ['క', 'ఖ', 'గ', 'ఘ', 'చ', 'ఛ', 'జ', 'ఝ', 'ట', 'ఠ'],
            'vowels': ['అ', 'ఆ', 'ఇ', 'ఈ', 'உ', 'ఊ', 'ఎ', 'ఏ', 'ఒ', 'ఓ']
        },
        'mr': {
            'name': 'Marathi', 
            'native': 'मराठी', 
            'gtts': 'mr', 
            'whisper': 'mr',
            'script': 'Devanagari',
            'unicode_range': [(0x0900, 0x097F)],
            'keywords': ['आणि', 'असे', 'होते', 'आहे', 'मी', 'तू', 'तो', 'ती', 'हे', 'ते'],
            'common_words': ['नमस्कार', 'कसे', 'काय', 'कुठे', 'केव्हा', 'का', 'कोण'],
            'unique_chars': ['ळ', 'ऱ']
        },
        'ta': {
            'name': 'Tamil', 
            'native': 'தமிழ்', 
            'gtts': 'ta', 
            'whisper': 'ta',
            'script': 'Tamil',
            'unicode_range': [(0x0B80, 0x0BFF)],
            'keywords': ['என்று', 'உள்ள', 'இருந்த', 'மற்றும்', 'ஒரு', 'அந்த', 'இந்த'],
            'common_words': ['வணக்கம்', 'எப்படி', 'என்ன', 'எங்கே', 'எப்போது', 'ஏன்', 'யார்'],
            'consonants': ['க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம'],
            'vowels': ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ']
        },
        'ur': {
            'name': 'Urdu', 
            'native': 'اردو', 
            'gtts': 'ur', 
            'whisper': 'ur',
            'script': 'Arabic',
            'unicode_range': [(0x0600, 0x06FF), (0x0750, 0x077F)],
            'keywords': ['ہے', 'اور', 'کے', 'میں', 'کی', 'کو', 'سے', 'نے', 'پر', 'کا'],
            'common_words': ['ہیلو', 'کیسے', 'کیا', 'کہاں', 'کب', 'کیوں', 'کون'],
            'direction': 'rtl'
        },
        'gu': {
            'name': 'Gujarati', 
            'native': 'ગુજરાતી', 
            'gtts': 'gu', 
            'whisper': 'gu',
            'script': 'Gujarati',
            'unicode_range': [(0x0A80, 0x0AFF)],
            'keywords': ['છે', 'અને', 'ને', 'માં', 'નો', 'ની', 'એ', 'તે', 'હું', 'તું'],
            'common_words': ['નમસ્તે', 'કેવી', 'શું', 'ક્યાં', 'ક્યારે', 'શા માટે', 'કોણ'],
            'consonants': ['ક', 'ખ', 'ગ', 'ઘ', 'ચ', 'છ', 'જ', 'ઝ', 'ટ', 'ઠ']
        },
        'kn': {
            'name': 'Kannada', 
            'native': 'ಕನ್ನಡ', 
            'gtts': 'kn', 
            'whisper': 'kn',
            'script': 'Kannada',
            'unicode_range': [(0x0C80, 0x0CFF)],
            'keywords': ['ಮತ್ತು', 'ಆಗಿದೆ', 'ಇದೆ', 'ಆಗಿ', 'ನಲ್ಲಿ', 'ಗೆ', 'ನಿಂದ', 'ಅಲ್ಲಿ'],
            'common_words': ['ನಮಸ್ಕಾರ', 'ಹೇಗೆ', 'ಏನು', 'ಎಲ್ಲಿ', 'ಯಾವಾಗ', 'ಏಕೆ', 'ಯಾರು'],
            'consonants': ['ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಟ', 'ಠ'],
            'vowels': ['ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಎ', 'ಏ', 'ಐ', 'ಒ']
        },
        'ml': {
            'name': 'Malayalam', 
            'native': 'മലയാളം', 
            'gtts': 'ml', 
            'whisper': 'ml',
            'script': 'Malayalam',
            'unicode_range': [(0x0D00, 0x0D7F)],
            'keywords': ['ആണ്', 'ഉം', 'എന്ന', 'ആയി', 'ൽ', 'ന്', 'യുടെ', 'ക്ക്'],
            'common_words': ['ഹലോ', 'എങ്ങനെ', 'എന്താണ്', 'എവിടെ', 'എപ്പോൾ', 'എന്തുകൊണ്ട്', 'ആര്'],
            'consonants': ['ക', 'ഖ', 'ഗ', 'ഘ', 'ച', 'ഛ', 'ജ', 'ഝ', 'ട', 'ഠ'],
            'unique_chars': ['ൺ', 'ൻ', 'ർ', 'ൽ', 'ൾ', 'ൿ']
        },
        'or': {
            'name': 'Odia', 
            'native': 'ଓଡ଼ିଆ', 
            'gtts': 'or', 
            'whisper': 'or',
            'script': 'Odia',
            'unicode_range': [(0x0B00, 0x0B7F)],
            'keywords': ['ଏବଂ', 'ଅଛି', 'କରି', 'ରେ', 'କୁ', 'ର', 'ଯାଏ', 'ସେ'],
            'common_words': ['ନମସ୍କାର', 'କେମିତି', 'କଣ', 'କେଉଁଠି', 'କେବେ', 'କାହିଁକି', 'କିଏ'],
            'unique_chars': ['ଡ଼', 'ଢ଼']
        },
        'pa': {
            'name': 'Punjabi', 
            'native': 'ਪੰਜਾਬੀ', 
            'gtts': 'pa', 
            'whisper': 'pa',
            'script': 'Gurmukhi',
            'unicode_range': [(0x0A00, 0x0A7F)],
            'keywords': ['ਹੈ', 'ਅਤੇ', 'ਦਾ', 'ਦੇ', 'ਨੂੰ', 'ਵਿੱਚ', 'ਤੋਂ', 'ਨਾਲ'],
            'common_words': ['ਸਤ ਸ੍ਰੀ ਅਕਾਲ', 'ਕਿਵੇਂ', 'ਕੀ', 'ਕਿੱਥੇ', 'ਕਦੋਂ', 'ਕਿਉਂ', 'ਕੌਣ'],
            'consonants': ['ਕ', 'ਖ', 'ਗ', 'ਘ', 'ਚ', 'ਛ', 'ਜ', 'ਝ', 'ਟ', 'ਠ']
        },
        'as': {
            'name': 'Assamese', 
            'native': 'অসমীয়া', 
            'gtts': 'as', 
            'whisper': 'as',
            'script': 'Bengali',
            'unicode_range': [(0x0980, 0x09FF)],
            'keywords': ['আৰু', 'আছে', 'কৰি', 'ত', 'ৰ', 'এই', 'সেই'],
            'common_words': ['নমস্কাৰ', 'কেনেকৈ', 'কি', 'ক\'ত', 'কেতিয়া', 'কিয়', 'কোন'],
            'unique_chars': ['ৰ', 'ৱ']
        },
        # 'ne': {
        #     'name': 'Nepali', 
        #     'native': 'नेपाली', 
        #     'gtts': 'ne', 
        #     'whisper': 'ne',
        #     'script': 'Devanagari',
        #     'unicode_range': [(0x0900, 0x097F)],
        #     # NEPALI-SPECIFIC keywords (different from Hindi)
        #     'keywords': ['छ', 'र', 'को', 'मा', 'ले', 'लाई', 'बाट', 'एक', 'गर्न', 'हुन्छ'],
        #     'common_words': ['नमस्ते', 'कस्तो', 'के', 'कहाँ', 'कहिले', 'किन', 'को', 'राम्रो'],
        #     # NEPALI-SPECIFIC patterns
        #     'unique_patterns': ['छ', 'हुन्छ', 'गर्न', 'भन्न']
        # },
        'sd': {
            'name': 'Sindhi', 
            'native': 'سنڌي', 
            'gtts': 'sd', 
            'whisper': 'sd',
            'script': 'Arabic',
            'unicode_range': [(0x0600, 0x06FF)],
            'keywords': ['آهي', '۽', 'جو', 'جي', 'کي', '۾', 'تي'],
            'direction': 'rtl'
        },
        'sa': {
            'name': 'Sanskrit', 
            'native': 'संस्कृतम्', 
            'gtts': 'sa', 
            'whisper': 'sa',
            'script': 'Devanagari',
            'unicode_range': [(0x0900, 0x097F)],
            'keywords': ['अस्ति', 'च', 'एव', 'तु', 'वा', 'किम्', 'कुत्र'],
            'unique_pattern': r'[ः।॥]'
        },
        'ar': {
            'name': 'Arabic', 
            'native': 'العربية', 
            'gtts': 'ar', 
            'whisper': 'ar',
            'script': 'Arabic',
            'unicode_range': [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
            'keywords': ['هو', 'هي', 'في', 'من', 'إلى', 'على', 'هذا', 'ذلك', 'التي', 'الذي'],
            'common_words': ['مرحبا', 'كيف', 'ماذا', 'أين', 'متى', 'لماذا', 'من'],
            'direction': 'rtl'
        }
    }
    
    def __init__(self):
        print(f"🌍 Ultimate Language Detector - {len(self.LANGUAGES)} languages")
        self._build_detection_cache()
    
    def _build_detection_cache(self):
        """Pre-compute detection patterns"""
        self.script_map = {}
        for lang, info in self.LANGUAGES.items():
            for start, end in info['unicode_range']:
                for code in range(start, end + 1):
                    if code not in self.script_map:
                        self.script_map[code] = []
                    self.script_map[code].append(lang)
    
    def detect_text_language(self, text: str, verbose: bool = True) -> Tuple[str, float]:
        """
        FIXED: Better Hindi vs Nepali detection
        """
        if not text or len(text.strip()) < 2:
            return 'en', 0.5
        
        text = text.strip()
        
        if verbose:
            print(f"\n🔍 Detecting language for: {text[:100]}...")
        
        # Strategy 1: Unicode Script Analysis
        script_result = self._detect_by_unicode(text)
        if script_result[1] > 0.85:
            if verbose:
                print(f"   ✓ Unicode: {script_result[0]} ({script_result[1]:.2%})")
            return script_result
        
        # Strategy 2: Keyword Matching
        keyword_result = self._detect_by_keywords(text)
        if keyword_result[1] > 0.80:
            if verbose:
                print(f"   ✓ Keywords: {keyword_result[0]} ({keyword_result[1]:.2%})")
            return keyword_result
        
        # Strategy 3: Pattern Analysis
        pattern_result = self._detect_by_patterns(text)
        if pattern_result[1] > 0.75:
            if verbose:
                print(f"   ✓ Patterns: {pattern_result[0]} ({pattern_result[1]:.2%})")
            return pattern_result
        
        # Strategy 4: Language-specific features
        feature_result = self._detect_by_features(text)
        if feature_result[1] > 0.70:
            if verbose:
                print(f"   ✓ Features: {feature_result[0]} ({feature_result[1]:.2%})")
            return feature_result
        
        # Combined
        best_lang, best_conf = self._combined_detection(
            script_result, keyword_result, pattern_result, feature_result
        )
        
        if verbose:
            print(f"   → Combined: {best_lang} ({best_conf:.2%})")
        
        return best_lang, best_conf
    
    def _detect_by_unicode(self, text: str) -> Tuple[str, float]:
        """Detect by Unicode - FIXED Hindi vs Nepali"""
        lang_counts = {lang: 0 for lang in self.LANGUAGES}
        total_chars = 0
        
        for char in text:
            if char.isalpha() or ord(char) > 127:
                total_chars += 1
                code = ord(char)
                
                if code in self.script_map:
                    for lang in self.script_map[code]:
                        lang_counts[lang] += 1
        
        if total_chars == 0:
            return 'en', 0.5
        
        best_lang = max(lang_counts, key=lang_counts.get)
        confidence = lang_counts[best_lang] / total_chars
        
        # CRITICAL FIX: Hindi vs Nepali distinction
        if best_lang in ['hi', 'mr', 'ne', 'sa'] and confidence > 0.5:
            # Check Hindi-specific patterns
            hindi_score = 0
            nepali_score = 0
            
            # Hindi indicators
            if 'मैं' in text or 'तुम' in text or 'हम' in text:
                hindi_score += 3
            if 'हैं' in text or 'था' in text or 'थी' in text:
                hindi_score += 2
            if 'और' in text:
                hindi_score += 1
                
            # Nepali indicators
            if 'छ' in text or 'हुन्छ' in text:
                nepali_score += 3
            if 'गर्न' in text or 'भन्न' in text:
                nepali_score += 2
            if re.search(r'[को|मा|ले]', text):
                nepali_score += 1
            
            # Marathi unique chars
            if 'ळ' in text or 'ऱ' in text:
                best_lang = 'mr'
            # Sanskrit punctuation
            elif re.search(r'[ः।॥]', text):
                best_lang = 'sa'
            # FIXED: Prioritize Hindi if Hindi score is higher
            elif hindi_score > nepali_score:
                best_lang = 'hi'
            elif nepali_score > hindi_score:
                best_lang = 'ne'
            else:
                # Default to Hindi (more common)
                best_lang = 'hi'
        
        return best_lang, min(0.99, confidence)
    
    def _detect_by_keywords(self, text: str) -> Tuple[str, float]:
        """Keyword matching"""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        best_lang = None
        best_score = 0
        
        for lang, info in self.LANGUAGES.items():
            if 'keywords' not in info:
                continue
            
            keywords = set(info['keywords'])
            matches = len(words & keywords)
            substring_matches = sum(1 for kw in keywords if kw in text_lower)
            
            score = matches + (substring_matches * 0.5)
            
            if score > best_score:
                best_score = score
                best_lang = lang
        
        if best_lang and best_score > 0:
            confidence = min(0.95, (best_score / 5) * 0.9 + 0.1)
            return best_lang, confidence
        
        return 'en', 0.4
    
    def _detect_by_patterns(self, text: str) -> Tuple[str, float]:
        """Pattern detection"""
        scores = {}
        
        for lang, info in self.LANGUAGES.items():
            score = 0.0
            
            # Common words
            if 'common_words' in info:
                for word in info['common_words']:
                    if word in text:
                        score += 2.0
            
            # Consonants/vowels
            if 'consonants' in info:
                consonant_count = sum(text.count(c) for c in info['consonants'])
                if consonant_count > 0:
                    score += min(3.0, consonant_count * 0.5)
            
            if 'vowels' in info:
                vowel_count = sum(text.count(c) for c in info['vowels'])
                if vowel_count > 0:
                    score += min(2.0, vowel_count * 0.3)
            
            # Unique characters
            if 'unique_chars' in info:
                for char in info['unique_chars']:
                    if char in text:
                        score += 5.0
            
            # NEW: Unique patterns (for Hindi/Nepali)
            if 'unique_patterns' in info:
                for pattern in info['unique_patterns']:
                    if pattern in text:
                        score += 3.0
            
            # RTL direction
            if info.get('direction') == 'rtl':
                if any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
                    score += 3.0
            
            scores[lang] = score
        
        if scores:
            best_lang = max(scores, key=scores.get)
            max_score = scores[best_lang]
            if max_score > 0:
                confidence = min(0.95, max_score / 10)
                return best_lang, confidence
        
        return 'en', 0.3
    
    def _detect_by_features(self, text: str) -> Tuple[str, float]:
        """Advanced features"""
        # English
        english_indicators = sum([
            text.count(' the '),
            text.count(' is '),
            text.count(' and '),
            text.count(' to '),
            text.count(' of ')
        ])
        if english_indicators > 2:
            return 'en', 0.85
        
        # Language-specific
        if re.search(r'[ः।॥]', text):
            return 'sa', 0.80
        
        if 'ൺ' in text or 'ൻ' in text or 'ർ' in text:
            return 'ml', 0.85
        
        if 'ଡ଼' in text or 'ଢ଼' in text:
            return 'or', 0.85
        
        if 'ৰ' in text or 'ৱ' in text:
            return 'as', 0.85
        
        if 'ळ' in text or 'ऱ' in text:
            return 'mr', 0.85
        
        return 'en', 0.2
    
    def _combined_detection(self, *results) -> Tuple[str, float]:
        """Weighted combination"""
        weights = [0.4, 0.3, 0.2, 0.1]
        
        lang_scores = {}
        for result, weight in zip(results, weights):
            lang, conf = result
            if lang not in lang_scores:
                lang_scores[lang] = 0
            lang_scores[lang] += conf * weight
        
        if lang_scores:
            best_lang = max(lang_scores, key=lang_scores.get)
            avg_confidence = lang_scores[best_lang]
            return best_lang, min(0.95, avg_confidence)
        
        return 'en', 0.6
    
    def get_language_info(self, code: str) -> Dict:
        """Get language info"""
        return self.LANGUAGES.get(code, self.LANGUAGES['en'])
    
    def get_gtts_language(self, code: str) -> str:
        """Get gTTS code"""
        return self.LANGUAGES.get(code, {}).get('gtts', 'en')
    
    def get_whisper_language(self, code: str) -> str:
        """Get Whisper code"""
        return self.LANGUAGES.get(code, {}).get('whisper', 'en')
    
    def validate_language(self, code: str) -> bool:
        """Validate language"""
        return code in self.LANGUAGES
    
    def get_all_languages(self) -> Dict:
        """Get all languages"""
        return self.LANGUAGES


# Global instance
ultimate_detector = UltimateLanguageDetector()