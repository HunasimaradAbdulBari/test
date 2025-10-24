from pydantic import BaseModel, Field
from fastapi import UploadFile, File, Form
from typing import Optional

class STTRequest(BaseModel):
    audio: UploadFile = File(...)
    language: str = Form(default="en")

class STTResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None
    duration: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a transcribed text.",
                "language": "en",
                "confidence": 0.95,
                "duration": 3.2
            }
        }
