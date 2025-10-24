import whisper
from faster_whisper import WhisperModel
import os
import asyncio
from typing import Dict, Any
import librosa
import numpy as np

class WhisperService:
    def __init__(self):
        self.model = None
        self.model_name = os.getenv("WHISPER_MODEL", "base")
        self.device = os.getenv("WHISPER_DEVICE", "cpu")
        self.ready = False
        
        # Language mapping
        self.language_map = {
            "en": "english",
            "hi": "hindi", 
            "kn": "kannada",
            "ur": "urdu"
        }
    
    def load_model(self):
        """Load Whisper model (blocking operation)"""
        try:
            print(f"🔄 Loading Whisper model: {self.model_name}")
            self.model = WhisperModel(self.model_name, device=self.device)
            self.ready = True
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            # Fallback to standard whisper
            try:
                self.model = whisper.load_model(self.model_name)
                self.ready = True
                print("✅ Standard Whisper model loaded as fallback")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                self.ready = False
    
    def is_ready(self) -> bool:
        return self.ready and self.model is not None
    
    async def transcribe(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio file"""
        if not self.is_ready():
            raise Exception("Whisper service not ready")
        
        try:
            # Get full language name
            lang_full = self.language_map.get(language, "english")
            
            # Transcribe using faster-whisper
            if hasattr(self.model, 'transcribe'):
                # faster-whisper
                segments, info = self.model.transcribe(
                    audio_path, 
                    language=language,
                    beam_size=5
                )
                
                text = " ".join([segment.text.strip() for segment in segments])
                confidence = info.language_probability if hasattr(info, 'language_probability') else None
                
            else:
                # Standard whisper fallback
                result = self.model.transcribe(
                    audio_path,
                    language=language
                )
                text = result["text"].strip()
                confidence = None
            
            # Get audio duration
            duration = await self._get_audio_duration(audio_path)
            
            return {
                "text": text,
                "language": language,
                "confidence": confidence,
                "duration": duration
            }
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration using librosa"""
        try:
            y, sr = librosa.load(audio_path)
            duration = len(y) / sr
            return round(duration, 2)
        except:
            return None
