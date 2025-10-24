"""
Ultra-Simplified Speech Engine
Combines STT (Whisper) and TTS (Edge-TTS + gTTS) in ONE file
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import whisper
import edge_tts
from gtts import gTTS
import uvicorn
import os
import uuid
import asyncio
from pathlib import Path
from datetime import datetime
import shutil

# ============================================
# CONFIGURATION
# ============================================

class Config:
    # Directories
    TEMP_DIR = "./temp_audio"
    STATIC_DIR = "./static"
    AUDIO_DIR = "./static/audio"
    
    # Whisper
    WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
    
    # Supported Languages
    LANGUAGES = {
        "en": {"name": "English", "voice": "en-IN-NeerjaNeural"},
        "hi": {"name": "Hindi", "voice": "hi-IN-SwaraNeural"},
        "kn": {"name": "Kannada", "voice": "kn-IN-GaganNeural"},
        "ur": {"name": "Urdu", "voice": "ur-PK-AsadNeural"}
    }
    
    # Audio Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

config = Config()

# Create directories
for directory in [config.TEMP_DIR, config.STATIC_DIR, config.AUDIO_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# ============================================
# INITIALIZE MODELS
# ============================================

print("🔄 Loading Whisper model...")
whisper_model = whisper.load_model(config.WHISPER_MODEL)
print("✅ Whisper model loaded!")

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Speech Engine API",
    description="Simple STT and TTS API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# ============================================
# PYDANTIC MODELS
# ============================================

class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    speed: float = 1.0

class TTSResponse(BaseModel):
    audio_url: str
    language: str
    text_length: int

class STTResponse(BaseModel):
    text: str
    language: str

# ============================================
# UTILITY FUNCTIONS
# ============================================

def cleanup_file(file_path: str):
    """Delete temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Deleted: {file_path}")
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")

async def generate_unique_filename(extension: str = "mp3") -> tuple:
    """Generate unique filename and path"""
    filename = f"{uuid.uuid4()}.{extension}"
    filepath = os.path.join(config.AUDIO_DIR, filename)
    return filename, filepath

# ============================================
# SPEECH-TO-TEXT (STT)
# ============================================

@app.post("/stt", response_model=STTResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Convert speech to text using Whisper
    """
    temp_path = None
    
    try:
        # Validate language
        if language not in config.LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
        
        # Save uploaded file
        temp_path = os.path.join(config.TEMP_DIR, f"{uuid.uuid4()}.webm")
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"📝 Transcribing audio: {language}")
        
        # Transcribe with Whisper
        result = whisper_model.transcribe(
            temp_path,
            language=language if language != "en" else None,
            fp16=False
        )
        
        text = result["text"].strip()
        detected_language = result.get("language", language)
        
        print(f"✅ Transcription completed: {len(text)} characters")
        
        # Cleanup
        cleanup_file(temp_path)
        
        return STTResponse(
            text=text,
            language=detected_language
        )
        
    except Exception as e:
        if temp_path:
            cleanup_file(temp_path)
        print(f"❌ STT Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TEXT-TO-SPEECH (TTS)
# ============================================

async def generate_edge_tts(text: str, language: str, speed: float) -> str:
    """Generate speech using Edge-TTS"""
    try:
        voice = config.LANGUAGES[language]["voice"]
        filename, filepath = await generate_unique_filename("mp3")
        
        # Calculate rate
        rate = f"+{int((speed - 1) * 100)}%" if speed >= 1 else f"{int((speed - 1) * 100)}%"
        
        # Generate speech
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(filepath)
        
        print(f"✅ Edge-TTS: Generated {filename}")
        return filename
        
    except Exception as e:
        print(f"⚠️  Edge-TTS failed: {e}")
        raise

def generate_gtts(text: str, language: str) -> str:
    """Generate speech using gTTS (fallback)"""
    try:
        # Language mapping for gTTS
        gtts_langs = {"en": "en", "hi": "hi", "kn": "kn", "ur": "ur"}
        tts_lang = gtts_langs.get(language, "en")
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(config.AUDIO_DIR, filename)
        
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(filepath)
        
        print(f"✅ gTTS: Generated {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ gTTS failed: {e}")
        raise

@app.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Edge-TTS (with gTTS fallback)
    """
    try:
        # Validate
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        if request.language not in config.LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")
        
        print(f"🔊 Generating speech: {request.language}, {len(request.text)} chars")
        
        # Try Edge-TTS first
        try:
            filename = await generate_edge_tts(request.text, request.language, request.speed)
            method = "Edge-TTS"
        except Exception as e:
            print(f"⚠️  Edge-TTS failed, trying gTTS: {e}")
            # Fallback to gTTS
            filename = generate_gtts(request.text, request.language)
            method = "gTTS"
        
        print(f"✅ Speech generated using {method}")
        
        return TTSResponse(
            audio_url=f"/static/audio/{filename}",
            language=request.language,
            text_length=len(request.text)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Speech Engine",
        "timestamp": datetime.now().isoformat(),
        "whisper_model": config.WHISPER_MODEL,
        "supported_languages": list(config.LANGUAGES.keys())
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Speech Engine API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "stt": "POST /stt",
            "tts": "POST /tts",
            "docs": "/docs"
        }
    }

# ============================================
# STARTUP & SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    print("")
    print("🚀 ============================================")
    print("✅ Speech Engine Started")
    print(f"🎤 Whisper Model: {config.WHISPER_MODEL}")
    print(f"🌍 Languages: {', '.join(config.LANGUAGES.keys())}")
    print(f"📡 API Docs: http://localhost:8000/docs")
    print("🚀 ============================================")
    print("")

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Speech Engine shutting down...")

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )