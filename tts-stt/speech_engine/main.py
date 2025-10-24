from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from services.whisper_service import WhisperService
from services.tts_service import TTSService
from services.audio_processor import AudioProcessor
from models.stt_models import STTRequest, STTResponse
from models.tts_models import TTSRequest, TTSResponse
from utils.file_handler import FileHandler
from utils.validators import validate_audio_file, validate_text

# Create directories
os.makedirs("temp_audio", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# Initialize services
whisper_service = None
tts_service = None
audio_processor = None
file_handler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global whisper_service, tts_service, audio_processor, file_handler
    
    print("🚀 Initializing Speech Engine...")
    
    whisper_service = WhisperService()
    tts_service = TTSService()
    audio_processor = AudioProcessor()
    file_handler = FileHandler()
    
    # Load Whisper model
    await asyncio.to_thread(whisper_service.load_model)
    
    print("✅ Speech Engine initialized successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Speech Engine...")
    if file_handler:
        await file_handler.cleanup_old_files()

# Create FastAPI app
app = FastAPI(
    title="Multilingual Speech Engine",
    description="High-performance Speech-to-Text and Text-to-Speech API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000", 
        "https://your-frontend.vercel.app",
        "https://your-backend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "whisper": whisper_service.is_ready() if whisper_service else False,
            "tts": tts_service.is_ready() if tts_service else False,
            "audio_processor": True
        },
        "timestamp": file_handler.get_timestamp() if file_handler else None
    }

# Speech to Text endpoint
@app.post("/api/v1/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    try:
        # Validate audio file
        validation = validate_audio_file(request.audio)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Save uploaded file
        temp_path = await file_handler.save_temp_file(request.audio)
        
        try:
            # Process audio
            processed_path = await audio_processor.preprocess_audio(temp_path)
            
            # Transcribe
            result = await whisper_service.transcribe(processed_path, request.language)
            
            return STTResponse(
                text=result["text"],
                language=result["language"],
                confidence=result.get("confidence"),
                duration=result.get("duration")
            )
            
        finally:
            # Cleanup temp files
            await file_handler.cleanup_temp_files([temp_path])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# Text to Speech endpoint  
@app.post("/api/v1/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    try:
        # Validate text
        validation = validate_text(request.text)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Generate speech
        result = await tts_service.generate_speech(
            text=request.text,
            language=request.language,
            speed=request.speed,
            pitch=request.pitch
        )
        
        return TTSResponse(
            audio_url=result["audio_url"],
            language=result["language"],
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
