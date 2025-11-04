"""
FIXED: main.py - Production Speech Engine
Replace content of: tts-stt/speech_engine/main.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from gtts import gTTS
import traceback
from pathlib import Path
import time

# Import language detector
from ultimate_language_detector import ultimate_detector

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Directories
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "static" / "audio"
TEMP_DIR = BASE_DIR / "temp_audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Whisper initialization - with PROPER error handling
whisper_service = None
WHISPER_AVAILABLE = False

print("\n" + "="*80)
print("🚀 INITIALIZING SPEECH ENGINE")
print("="*80)

# Try to import and initialize Whisper
try:
    print("\n1️⃣ Checking PyTorch...")
    import torch
    print(f"   ✅ PyTorch {torch.__version__}")
    print(f"   Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    
    print("\n2️⃣ Checking Whisper...")
    import whisper
    print(f"   ✅ Whisper available")
    
    print("\n3️⃣ Loading Whisper model...")
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'tiny')  # Use tiny for faster loading
    print(f"   Model: {WHISPER_MODEL}")
    
    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    whisper_model = whisper.load_model(WHISPER_MODEL, device=device)
    whisper_model.eval()
    
    # Create wrapper class
    class WhisperService:
        def __init__(self, model, device):
            self.model = model
            self.device = device
            self.is_ready = True
            print(f"   ✅ Whisper loaded successfully!")
        
        def transcribe(self, audio_path, language=None):
            """Transcribe audio with Whisper"""
            import numpy as np
            
            try:
                # Whisper transcription options
                options = {
                    'task': 'transcribe',
                    'fp16': self.device == 'cuda',
                    'verbose': False,
                    'beam_size': 5,
                    'best_of': 5,
                    'temperature': 0.0
                }
                
                if language:
                    options['language'] = language
                
                # Transcribe
                with torch.inference_mode():
                    result = self.model.transcribe(audio_path, **options)
                
                text = result['text'].strip()
                detected_lang = result.get('language', 'en')
                
                # Calculate confidence from segments
                segments = result.get('segments', [])
                if segments:
                    avg_logprob = np.mean([s.get('avg_logprob', -1) for s in segments])
                    confidence = min(0.99, max(0.5, np.exp(avg_logprob)))
                else:
                    confidence = 0.85
                
                return {
                    'text': text,
                    'language': detected_lang,
                    'confidence': confidence,
                    'duration': len(text) / 150 * 60,  # Rough estimate
                    'method': f'Whisper-{WHISPER_MODEL}'
                }
                
            except Exception as e:
                print(f"❌ Whisper transcription error: {e}")
                raise
    
    # Initialize service
    whisper_service = WhisperService(whisper_model, device)
    WHISPER_AVAILABLE = True
    print(f"\n{'='*80}")
    print("✅ WHISPER READY!")
    print("="*80)

except ImportError as e:
    print(f"\n⚠️  Whisper dependencies not installed: {e}")
    print("   STT will use fallback mode")
    print("   To enable Whisper:")
    print("   1. pip install torch torchvision torchaudio")
    print("   2. pip install openai-whisper")
    WHISPER_AVAILABLE = False

except Exception as e:
    print(f"\n⚠️  Whisper initialization failed: {e}")
    print("   STT will use fallback mode")
    traceback.print_exc()
    WHISPER_AVAILABLE = False

print("\n" + "="*80)
print("✅ SPEECH ENGINE READY")
print("="*80)
print(f"   • Languages: {len(ultimate_detector.LANGUAGES)}")
print(f"   • TTS: gTTS (fully operational)")
print(f"   • STT: {'Whisper (' + os.getenv('WHISPER_MODEL', 'tiny') + ')' if WHISPER_AVAILABLE else 'Fallback mode'}")
print("="*80 + "\n")

# ============================================================================
# TEXT-TO-SPEECH (Fully Working)
# ============================================================================

@app.route('/tts', methods=['POST', 'OPTIONS'])
def text_to_speech():
    """Generate speech with automatic language detection"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        print(f"\n{'='*60}")
        print("🔊 [TTS] Request")
        print(f"{'='*60}")
        
        data = request.get_json(force=True)
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        if len(text) > 5000:
            return jsonify({"error": "Text too long"}), 400
        
        print(f"📝 Text: {text[:80]}...")
        
        # Detect language
        detected_lang, confidence = ultimate_detector.detect_text_language(text, verbose=True)
        lang_info = ultimate_detector.get_language_info(detected_lang)
        gtts_lang = ultimate_detector.get_gtts_language(detected_lang)
        
        print(f"\n🌐 Detected: {lang_info['name']} ({confidence:.2%})")
        
        # Generate audio
        file_id = str(uuid.uuid4())[:8]
        filename = f"speech_{detected_lang}_{file_id}.mp3"
        file_path = AUDIO_DIR / filename
        
        print(f"🎵 Generating audio...")
        start = time.time()
        
        tts = gTTS(text=text, lang=gtts_lang, slow=False, lang_check=False)
        tts.save(str(file_path))
        
        duration = time.time() - start
        
        if not file_path.exists():
            raise Exception("Audio generation failed")
        
        file_size = file_path.stat().st_size
        audio_url = f"http://localhost:8000/static/audio/{filename}"
        
        print(f"✅ Success! ({duration:.2f}s, {file_size/1024:.1f}KB)")
        print(f"   URL: {audio_url}")
        print(f"{'='*60}\n")
        
        return jsonify({
            "audio_url": audio_url,
            "detected_language": {
                "code": detected_lang,
                "name": lang_info['name'],
                "native_name": lang_info['native'],
                "script": lang_info['script'],
                "confidence": confidence
            },
            "metadata": {
                "method": "gTTS",
                "auto_detected": True,
                "generation_time": duration,
                "file_size": file_size
            }
        }), 200
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# SPEECH-TO-TEXT (With Whisper or Fallback)
# ============================================================================

@app.route('/stt', methods=['POST', 'OPTIONS'])
def speech_to_text():
    """Transcribe speech - Whisper or Fallback"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    temp_path = None
    
    try:
        print(f"\n{'='*60}")
        print("🎙️ [STT] Request")
        print(f"{'='*60}")
        
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 422
        
        audio_file = request.files['audio']
        
        # Save temp file
        file_id = str(uuid.uuid4())[:8]
        ext = Path(audio_file.filename).suffix if audio_file.filename else '.webm'
        temp_filename = f"temp_{file_id}{ext}"
        temp_path = TEMP_DIR / temp_filename
        
        audio_file.save(str(temp_path))
        print(f"💾 Saved: {temp_path.name}")
        
        # Check if Whisper is available
        if WHISPER_AVAILABLE and whisper_service and whisper_service.is_ready:
            print("🤖 Using Whisper transcription...")
            
            # Convert to WAV if needed for better compatibility
            audio_path = temp_path
            if ext.lower() not in ['.wav', '.mp3', '.m4a', '.flac']:
                try:
                    from pydub import AudioSegment
                    print("🔄 Converting to WAV...")
                    audio = AudioSegment.from_file(str(temp_path))
                    wav_path = temp_path.with_suffix('.wav')
                    audio.export(str(wav_path), format='wav')
                    if temp_path != wav_path:
                        temp_path.unlink()
                    audio_path = wav_path
                    temp_path = wav_path
                    print(f"   ✅ Converted to: {wav_path.name}")
                except Exception as e:
                    print(f"⚠️ Conversion failed: {e}, using original")
            
            # Whisper transcription
            result = whisper_service.transcribe(str(audio_path), language=None)
            
            text = result['text']
            whisper_lang = result['language']
            confidence = result['confidence']
            
            # Verify with text detection
            text_lang, text_conf = ultimate_detector.detect_text_language(text, verbose=False)
            
            final_lang = whisper_lang
            final_confidence = confidence
            
            # If text detection has high confidence and differs, use it
            if text_conf > 0.85 and text_lang != whisper_lang:
                final_lang = text_lang
                final_confidence = (confidence + text_conf) / 2
            
            lang_info = ultimate_detector.get_language_info(final_lang)
            
            print(f"✅ Transcribed: {lang_info['name']} ({final_confidence:.2%})")
            print(f"   Text: {text[:100]}...")
            
            return jsonify({
                "text": text,
                "detected_language": {
                    "code": final_lang,
                    "name": lang_info['name'],
                    "native_name": lang_info['native'],
                    "script": lang_info['script'],
                    "confidence": final_confidence
                },
                "metadata": {
                    "auto_detected": True,
                    "method": result['method'],
                    "duration": result['duration']
                }
            }), 200
        
        else:
            # FALLBACK: Return message for browser-based STT
            print("⚠️  Whisper unavailable - returning fallback response")
            
            return jsonify({
                "text": "",
                "detected_language": {
                    "code": "en",
                    "name": "English",
                    "native_name": "English",
                    "script": "Latin",
                    "confidence": 0.0
                },
                "metadata": {
                    "auto_detected": False,
                    "method": "fallback",
                    "message": "Whisper not available. Install: pip install torch openai-whisper",
                    "fallback": True
                }
            }), 200
        
    except Exception as e:
        print(f"❌ STT Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Cleanup
        if temp_path and Path(temp_path).exists():
            try:
                Path(temp_path).unlink()
            except:
                pass

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "name": "Ultimate Speech Engine",
        "version": "5.0.0",
        "status": "operational",
        "features": {
            "tts": "operational (gTTS)",
            "stt": "operational" if WHISPER_AVAILABLE else "fallback mode",
            "languages": len(ultimate_detector.LANGUAGES),
            "auto_detection": True,
            "whisper": "loaded" if WHISPER_AVAILABLE else "not available"
        },
        "whisper_status": {
            "available": WHISPER_AVAILABLE,
            "model": os.getenv('WHISPER_MODEL', 'tiny') if WHISPER_AVAILABLE else None,
            "device": whisper_service.device if WHISPER_AVAILABLE and whisper_service else None
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "tts": "operational",
            "stt": "operational" if WHISPER_AVAILABLE else "degraded",
            "whisper": "loaded" if WHISPER_AVAILABLE else "unavailable"
        }
    }), 200

@app.route('/languages', methods=['GET'])
def list_languages():
    return jsonify({
        "total": len(ultimate_detector.LANGUAGES),
        "languages": [
            {
                "code": code,
                "name": info['name'],
                "native_name": info['native']
            }
            for code, info in ultimate_detector.LANGUAGES.items()
        ]
    }), 200

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    try:
        file_path = AUDIO_DIR / filename
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        return send_file(str(file_path), mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"\n{'='*80}")
    print("🎉 STARTING SPEECH ENGINE")
    print(f"{'='*80}")
    print(f"📡 Server: http://localhost:8000")
    print(f"🎯 TTS: Fully operational with auto-detection")
    print(f"🎙️  STT: {'Whisper ready' if WHISPER_AVAILABLE else 'Fallback mode'}")
    if not WHISPER_AVAILABLE:
        print(f"\n💡 To enable Whisper STT:")
        print(f"   1. pip install torch torchvision torchaudio")
        print(f"   2. pip install openai-whisper")
        print(f"   3. Restart this server")
    print(f"{'='*80}\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True,
        use_reloader=False
    )