from typing import Dict, Any
from fastapi import UploadFile
import os

def validate_audio_file(file: UploadFile) -> Dict[str, Any]:
    """Validate uploaded audio file"""
    max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
    
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > max_size:
        return {
            "valid": False,
            "error": f"File size exceeds maximum limit of {max_size / 1024 / 1024:.1f}MB"
        }
    
    # Check file type
    allowed_types = [
        "audio/webm", "audio/wav", "audio/mp3", 
        "audio/mpeg", "audio/m4a", "audio/ogg"
    ]
    
    if file.content_type and file.content_type not in allowed_types:
        return {
            "valid": False,
            "error": f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        }
    
    return {"valid": True}

def validate_text(text: str) -> Dict[str, Any]:
    """Validate text input"""
    if not text or not text.strip():
        return {
            "valid": False,
            "error": "Text is required"
        }
    
    if len(text) > 5000:
        return {
            "valid": False,
            "error": "Text exceeds maximum length of 5000 characters"
        }
    
    return {"valid": True}

def validate_language(language: str) -> Dict[str, Any]:
    """Validate language code"""
    supported_languages = os.getenv("SUPPORTED_LANGUAGES", "en,hi,kn,ur").split(",")
    
    if language not in supported_languages:
        return {
            "valid": False,
            "error": f"Unsupported language. Supported: {', '.join(supported_languages)}"
        }
    
    return {"valid": True}
