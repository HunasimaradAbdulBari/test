import edge_tts
from gtts import gTTS
import asyncio
import os
import uuid
from typing import Dict, Any
import aiofiles
from pathlib import Path

class TTSService:
    def __init__(self):
        self.voice_map = {
            "en": "en-IN-NeerjaNeural",
            "hi": "hi-IN-SwaraNeural", 
            "kn": "kn-IN-GaganNeural",
            "ur": "ur-PK-AsadNeural"
        }
        
        self.output_dir = Path("static/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def is_ready(self) -> bool:
        return True
    
    async def generate_speech(
        self, 
        text: str, 
        language: str = "en",
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> Dict[str, Any]:
        """Generate speech from text"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())[:8]
            filename = f"speech_{file_id}.mp3"
            file_path = self.output_dir / filename
            
            print(f"🔊 Generating speech for language: {language}")
            
            # Try Edge-TTS first
            try:
                await self._generate_edge_tts(text, language, str(file_path), speed)
                method = "edge-tts"
                print(f"✅ Edge-TTS generation successful")
            except Exception as e:
                print(f"⚠️ Edge-TTS failed: {e}, trying gTTS...")
                await self._generate_gtts(text, language, str(file_path))
                method = "gtts"
                print(f"✅ gTTS generation successful")
            
            # Verify file was created
            if not file_path.exists():
                raise Exception(f"Audio file was not created: {file_path}")
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Get audio duration (approximate)
            duration = self._estimate_duration(text, speed)
            
            # Build audio URL - use environment variable or default
            host = os.getenv("HOST", "0.0.0.0")
            port = os.getenv("PORT", "8000")
            
            # For local development, use localhost
            if host == "0.0.0.0":
                host = "localhost"
            
            audio_url = f"http://{host}:{port}/static/audio/{filename}"
            
            print(f"📁 Audio file created: {file_path}")
            print(f"🔗 Audio URL: {audio_url}")
            
            return {
                "audio_url": audio_url,
                "language": language,
                "metadata": {
                    "method": method,
                    "voice": self.voice_map.get(language, "default"),
                    "file_size": file_size,
                    "duration": duration,
                    "speed": speed,
                    "pitch": pitch,
                    "filename": filename
                }
            }
            
        except Exception as e:
            print(f"❌ TTS generation error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Speech generation failed: {str(e)}")
    
    async def _generate_edge_tts(self, text: str, language: str, output_path: str, speed: float):
        """Generate speech using Edge-TTS"""
        voice = self.voice_map.get(language, "en-US-AriaNeural")
        
        # Create rate string for speed control
        rate = f"{int((speed - 1) * 50):+d}%"
        
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
    
    async def _generate_gtts(self, text: str, language: str, output_path: str):
        """Generate speech using gTTS (fallback)"""
        # gTTS language mapping
        gtts_lang_map = {
            "en": "en",
            "hi": "hi",
            "kn": "kn", 
            "ur": "ur"
        }
        
        gtts_lang = gtts_lang_map.get(language, "en")
        
        # Run gTTS in thread pool
        def generate_gtts():
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(output_path)
        
        await asyncio.to_thread(generate_gtts)
    
    def _estimate_duration(self, text: str, speed: float) -> float:
        """Estimate audio duration based on text length and speed"""
        # Rough estimation: 150 words per minute at normal speed
        words = len(text.split())
        base_duration = (words / 150) * 60  # seconds
        adjusted_duration = base_duration / speed
        return round(adjusted_duration, 2)