"""
Optimized Whisper Service with Indian Language Support
Configured for maximum accuracy on Indian languages
"""

import whisper
import torch
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import time
from typing import Dict, Tuple, Optional

class OptimizedWhisperForIndianLanguages:
    """
    Whisper optimized specifically for Indian language transcription
    """
    
    # Whisper language codes for Indian languages
    WHISPER_LANG_MAP = {
        'en': 'english',
        'hi': 'hindi',
        'bn': 'bengali',
        'te': 'telugu',
        'mr': 'marathi',
        'ta': 'tamil',
        'ur': 'urdu',
        'gu': 'gujarati',
        'kn': 'kannada',
        'ml': 'malayalam',
        'or': 'odia',
        'pa': 'punjabi',
        'as': 'assamese',
        'ne': 'nepali',
        'sd': 'sindhi',
        'ar': 'arabic'
    }
    
    def __init__(self, model_size='base'):
        """
        Initialize Whisper with optimal settings
        model_size: 'tiny', 'base', 'small', 'medium', 'large'
        """
        self.model_size = model_size
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.is_ready = False
        
        print(f"🚀 Initializing Whisper ({model_size}) on {self.device.upper()}")
        
        # Optimization settings
        if self.device == 'cuda':
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            print("   ✓ GPU optimizations enabled")
        
        self.load_model()
    
    def load_model(self):
        """Load Whisper model with error handling"""
        try:
            print(f"📥 Loading Whisper {self.model_size} model...")
            start = time.time()
            
            self.model = whisper.load_model(self.model_size, device=self.device)
            self.model.eval()
            
            # PyTorch 2.0+ compilation (if available)
            try:
                if hasattr(torch, 'compile') and self.device == 'cuda':
                    print("   ⚡ Compiling model with PyTorch 2.0...")
                    self.model = torch.compile(self.model, mode='reduce-overhead')
                    print("   ✓ Model compiled")
            except Exception as e:
                print(f"   ⚠ Compilation skipped: {e}")
            
            load_time = time.time() - start
            self.is_ready = True
            
            print(f"✅ Whisper loaded in {load_time:.2f}s")
            print(f"   Supported languages: {len(self.WHISPER_LANG_MAP)}")
            
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            self.is_ready = False
            raise
    
    def transcribe(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        task: str = 'transcribe'
    ) -> Dict:
        """
        Transcribe audio with optimal settings for Indian languages
        
        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detect)
            task: 'transcribe' or 'translate'
        
        Returns:
            Dictionary with text, language, confidence, etc.
        """
        if not self.is_ready:
            raise Exception("Whisper not ready")
        
        try:
            print(f"\n🎙️ Transcribing: {Path(audio_path).name}")
            start_time = time.time()
            
            # Preprocess audio for better accuracy
            audio = self._preprocess_audio(audio_path)
            print(f"   ✓ Audio preprocessed")
            
            # Transcription options optimized for Indian languages
            options = {
                'task': task,
                'fp16': self.device == 'cuda',
                'verbose': False,
                'beam_size': 5,  # Higher = more accurate but slower
                'best_of': 5,
                'temperature': 0.0,  # Greedy decoding
                'compression_ratio_threshold': 2.4,
                'logprob_threshold': -1.0,
                'no_speech_threshold': 0.6,
                'condition_on_previous_text': True,  # Better for long audio
            }
            
            # Add language if specified
            if language:
                whisper_lang = self._get_whisper_language(language)
                if whisper_lang:
                    options['language'] = whisper_lang
                    print(f"   → Language: {whisper_lang}")
                else:
                    print(f"   → Auto-detecting language")
            else:
                print(f"   → Auto-detecting language")
            
            # Transcribe
            with torch.inference_mode():
                result = self.model.transcribe(audio, **options)
            
            duration = time.time() - start_time
            
            # Extract results
            text = result['text'].strip()
            detected_lang = result.get('language', 'en')
            
            # Calculate confidence from segments
            confidence = self._calculate_confidence(result)
            
            # Map Whisper language back to our codes
            lang_code = self._map_whisper_to_code(detected_lang)
            
            print(f"✅ Transcription complete ({duration:.2f}s)")
            print(f"   Language: {detected_lang} → {lang_code}")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Text: {text[:100]}...")
            
            return {
                'text': text,
                'language': lang_code,
                'detected_language': detected_lang,
                'confidence': confidence,
                'duration': duration,
                'segments': len(result.get('segments', [])),
                'method': f'Whisper-{self.model_size}'
            }
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _preprocess_audio(self, audio_path: str) -> np.ndarray:
        """
        Preprocess audio for optimal Whisper performance
        - Convert to 16kHz mono
        - Remove silence
        - Normalize
        - Apply noise reduction
        """
        try:
            # Load with librosa (automatic resampling to 16kHz)
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            # Remove leading/trailing silence (aggressive)
            audio, _ = librosa.effects.trim(
                audio,
                top_db=20,  # More aggressive than default 60
                frame_length=2048,
                hop_length=512
            )
            
            # Normalize amplitude
            audio = librosa.util.normalize(audio)
            
            # Apply simple noise reduction
            audio = self._reduce_noise(audio)
            
            # Ensure minimum length (0.5 seconds)
            if len(audio) < sr * 0.5:
                audio = np.pad(audio, (0, int(sr * 0.5) - len(audio)))
            
            return audio
            
        except Exception as e:
            print(f"⚠️ Preprocessing failed: {e}, using raw audio")
            # Fallback to Whisper's built-in loader
            return whisper.load_audio(audio_path)
    
    def _reduce_noise(self, audio: np.ndarray, threshold_percentile: int = 15) -> np.ndarray:
        """Simple noise gate - reduces low-amplitude noise"""
        threshold = np.percentile(np.abs(audio), threshold_percentile)
        audio_copy = audio.copy()
        audio_copy[np.abs(audio_copy) < threshold] *= 0.3  # Reduce by 70%
        return audio_copy
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence from Whisper segments"""
        segments = result.get('segments', [])
        
        if not segments:
            return 0.85  # Default
        
        # Use average log probability and no-speech probability
        avg_logprob = np.mean([s.get('avg_logprob', -1) for s in segments])
        avg_no_speech = np.mean([s.get('no_speech_prob', 0) for s in segments])
        
        # Convert to confidence
        prob = np.exp(avg_logprob)
        confidence = prob * (1 - avg_no_speech)
        
        return min(0.99, max(0.5, confidence))
    
    def _get_whisper_language(self, lang_code: str) -> Optional[str]:
        """Convert our language code to Whisper language name"""
        return self.WHISPER_LANG_MAP.get(lang_code)
    
    def _map_whisper_to_code(self, whisper_lang: str) -> str:
        """Map Whisper language name back to our code"""
        for code, name in self.WHISPER_LANG_MAP.items():
            if name.lower() == whisper_lang.lower():
                return code
        return 'en'  # Default
    
    def supports_language(self, lang_code: str) -> bool:
        """Check if language is supported by Whisper"""
        return lang_code in self.WHISPER_LANG_MAP


# Global instance
whisper_service = None

def initialize_whisper(model_size='base'):
    """Initialize global Whisper instance"""
    global whisper_service
    try:
        whisper_service = OptimizedWhisperForIndianLanguages(model_size)
        return True
    except Exception as e:
        print(f"❌ Whisper initialization failed: {e}")
        return False