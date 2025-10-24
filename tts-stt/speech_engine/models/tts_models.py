from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TTSRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Text to convert to speech")
    language: str = Field(default="en", description="Language code")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech pitch")

class TTSResponse(BaseModel):
    audio_url: str
    language: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "http://localhost:8000/static/audio/speech_12345.mp3",
                "language": "en",
                "metadata": {
                    "duration": 2.5,
                    "voice": "en-IN-NeerjaNeural",
                    "file_size": 40960
                }
            }
        }
