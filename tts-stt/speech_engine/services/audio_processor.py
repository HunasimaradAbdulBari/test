import librosa
import soundfile as sf
from pydub import AudioSegment
import numpy as np
from pathlib import Path
import os

class AudioProcessor:
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
        
    async def preprocess_audio(self, input_path: str) -> str:
        """Preprocess audio file for better transcription"""
        try:
            input_path = Path(input_path)
            output_path = input_path.with_suffix('.wav')
            
            # Convert to WAV if needed
            if input_path.suffix.lower() != '.wav':
                audio = AudioSegment.from_file(str(input_path))
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(str(output_path), format="wav")
            else:
                # Load and resample
                y, sr = librosa.load(str(input_path), sr=16000, mono=True)
                sf.write(str(output_path), y, sr)
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Audio preprocessing error: {e}")
            return str(input_path)  # Return original if preprocessing fails
    
    def validate_audio_format(self, file_path: str) -> bool:
        """Validate if audio format is supported"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def get_audio_info(self, file_path: str) -> dict:
        """Get audio file information"""
        try:
            audio = AudioSegment.from_file(file_path)
            return {
                "duration": len(audio) / 1000.0,  # seconds
                "channels": audio.channels,
                "frame_rate": audio.frame_rate,
                "format": Path(file_path).suffix.lower()
            }
        except:
            return {}
