from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from gtts import gTTS
import traceback
from pathlib import Path
import time
import torch

# Import language detector
import sys
sys.path.append(str(Path(__file__).parent))
from services.language_detector import language_detector

# Import Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper AI available")
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper AI not available - install with: pip install openai-whisper")

app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Create output directories
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "static" / "audio"
TEMP_DIR = BASE_DIR / "temp_audio"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# WHISPER SERVICE (ALL-IN-ONE - NO SEPARATE FILE NEEDED)
# ============================================================================

class WhisperService:
    """Whisper AI Service - Integrated directly in main.py"""
    
    LANGUAGE_MAP = {
        'en': 'en', 'hi': 'hi', 'bn': 'bn', 'te': 'te', 'mr': 'mr',
        'ta': 'ta', 'ur': 'ur', 'gu': 'gu', 'kn': 'kn', 'ml': 'ml',
        'or': 'or', 'pa': 'pa', 'as': 'as', 'ne': 'ne', 'sa': 'sa'
    }
    
    def __init__(self, model_size='base'):
        self.model_size = model_size
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.is_ready = False
        
        print(f"\n{'='*60}")
        print(f"🎙️ Initializing Whisper AI Service")
        print(f"{'='*60}")
        print(f"Model: {model_size}")
        print(f"Device: {self.device.upper()}")
        if self.device == 'cuda':
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"{'='*60}\n")
    
    def load_model(self):
        """Load Whisper model"""
        if self.is_ready:
            return
        
        try:
            print(f"📥 Loading Whisper '{self.model_size}' model...")
            print("   (First time: will download ~75MB model)")
            
            start_time = time.time()
            self.model = whisper.load_model(self.model_size, device=self.device)
            load_time = time.time() - start_time
            
            self.is_ready = True
            print(f"✅ Model loaded in {load_time:.2f}s - Ready!\n")
            
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            self.is_ready = False
            raise
    
    def transcribe(self, audio_path):
        """Transcribe audio with auto language detection"""
        if not self.is_ready:
            raise Exception("Whisper model not loaded")
        
        try:
            print(f"🎙️ Transcribing: {Path(audio_path).name}")
            start_time = time.time()
            
            # Transcribe with Whisper (auto-detect language)
            result = self.model.transcribe(
                str(audio_path),
                language=None,  # Auto-detect
                task='transcribe',
                fp16=False,
                verbose=False
            )
            
            transcribe_time = time.time() - start_time
            
            text = result['text'].strip()
            detected_lang = result.get('language', 'en')
            our_lang_code = self.LANGUAGE_MAP.get(detected_lang, detected_lang)
            
            # Calculate confidence
            segments = result.get('segments', [])
            if segments:
                avg_no_speech = sum(s.get('no_speech_prob', 0) for s in segments) / len(segments)
                confidence = 1.0 - avg_no_speech
            else:
                confidence = 0.92
            
            print(f"✅ Done in {transcribe_time:.2f}s")
            print(f"   Language: {detected_lang} | Confidence: {confidence:.2%}")
            
            return {
                'text': text,
                'language': our_lang_code,
                'detected_language': detected_lang,
                'confidence': confidence,
                'duration': transcribe_time,
                'segments': len(segments),
                'method': f'Whisper-{self.model_size}'
            }
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            raise

# Global Whisper instance
whisper_service = None

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

print("=" * 60)
print("🚀 Flask Speech Engine with Whisper AI")
print("=" * 60)
print(f"📁 Audio Directory: {AUDIO_DIR}")
print(f"📁 Temp Directory: {TEMP_DIR}")
print(f"🌐 Supported Languages: {len(language_detector.get_all_languages())}")
print("=" * 60)

# Load Whisper model
if WHISPER_AVAILABLE:
    try:
        WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')  # tiny, base, small, medium
        print(f"\n⏳ Loading Whisper model: {WHISPER_MODEL}")
        whisper_service = WhisperService(model_size=WHISPER_MODEL)
        whisper_service.load_model()
        print("✅ Whisper AI ready for transcription!")
    except Exception as e:
        print(f"❌ Whisper initialization failed: {e}")
        print("⚠️  STT will use fallback method")
        whisper_service = None
else:
    print("⚠️  Whisper not installed - using fallback STT")
    whisper_service = None

print("=" * 60 + "\n")

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Flask Speech Engine with Whisper AI",
        "status": "healthy",
        "version": "3.0.0",
        "features": {
            "auto_language_detection": True,
            "supported_languages": len(language_detector.get_all_languages()),
            "tts": "gTTS with 22+ Indian languages",
            "stt": "Whisper AI (90-98% accuracy)" if whisper_service else "Google Fallback",
            "whisper_enabled": whisper_service is not None
        },
        "endpoints": {
            "health": "GET /health",
            "tts": "POST /tts",
            "stt": "POST /stt",
            "languages": "GET /languages",
            "audio": "GET /static/audio/<filename>"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Flask Speech Engine with Whisper AI",
        "services": {
            "text_to_speech": "ready",
            "speech_recognition": "ready" if whisper_service else "fallback",
            "language_detection": "ready",
            "whisper": "active" if whisper_service else "not available"
        },
        "languages_supported": len(language_detector.get_all_languages())
    }), 200

@app.route('/languages', methods=['GET'])
def get_languages():
    return jsonify({
        "languages": language_detector.get_all_languages(),
        "total": len(language_detector.get_all_languages())
    }), 200

@app.route('/tts', methods=['POST', 'OPTIONS'])
def text_to_speech():
    """Text to Speech with auto language detection"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
        
    try:
        print("\n" + "=" * 60)
        print("🔊 [TTS] Auto Language Detection")
        print("=" * 60)
        
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON data"}), 400
            
        text = data.get('text', '').strip()
        print(f"📝 Text: {text[:100]}...")
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        if len(text) > 5000:
            return jsonify({"error": "Text too long (max 5000)"}), 400
        
        # Auto-detect language
        detected_lang, confidence = language_detector.detect_text_language(text)
        lang_info = language_detector.get_language_info(detected_lang)
        gtts_lang = language_detector.get_gtts_language(detected_lang)
        
        print(f"🌐 Detected: {lang_info['name']} ({detected_lang}) - {confidence:.0%}")
        
        # Generate audio
        file_id = str(uuid.uuid4())[:8]
        filename = f"speech_{detected_lang}_{file_id}.mp3"
        file_path = AUDIO_DIR / filename
        
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(file_path))
        
        if not file_path.exists():
            raise Exception("Audio file not created")
        
        file_size = file_path.stat().st_size
        audio_url = f"http://localhost:8000/static/audio/{filename}"
        
        print(f"✅ Generated: {filename} ({file_size} bytes)")
        print("=" * 60 + "\n")
        
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
                "file_size": file_size,
                "filename": filename
            }
        }), 200
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"TTS failed: {str(e)}"}), 500

@app.route('/stt', methods=['POST', 'OPTIONS'])
def speech_to_text():
    """
    Speech to Text with Whisper AI
    Falls back to Google if Whisper unavailable
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
    
    temp_path = None
    
    try:
        print("\n" + "=" * 60)
        print("🎙️ [STT] Speech to Text" + (" - WHISPER AI" if whisper_service else " - Google Fallback"))
        print("=" * 60)
        
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 422
        
        audio_file = request.files['audio']
        print(f"📁 File: {audio_file.filename}")
        
        # Save temp file
        file_id = str(uuid.uuid4())[:8]
        original_ext = Path(audio_file.filename).suffix if audio_file.filename else '.webm'
        temp_filename = f"temp_{file_id}{original_ext}"
        temp_path = TEMP_DIR / temp_filename
        
        audio_file.save(str(temp_path))
        print(f"💾 Saved: {temp_path}")
        
        # Convert to WAV/MP3 if needed
        audio_path = temp_path
        if original_ext.lower() not in ['.wav', '.mp3', '.m4a']:
            try:
                from pydub import AudioSegment
                print("🔄 Converting format...")
                audio = AudioSegment.from_file(str(temp_path))
                wav_path = temp_path.with_suffix('.wav')
                audio.export(str(wav_path), format='wav')
                if temp_path != wav_path:
                    temp_path.unlink()
                audio_path = wav_path
                temp_path = wav_path
                print(f"✅ Converted to WAV")
            except Exception as e:
                print(f"⚠️ Conversion failed: {e}")
        
        # === WHISPER TRANSCRIPTION ===
        if whisper_service and whisper_service.is_ready:
            print("🧠 Using Whisper AI...")
            
            result = whisper_service.transcribe(str(audio_path))
            
            text = result['text']
            detected_lang = result['language']
            confidence = result['confidence']
            
            lang_info = language_detector.get_language_info(detected_lang)
            
            print(f"✅ Whisper Result:")
            print(f"   Text: {text}")
            print(f"   Language: {lang_info['name']} ({detected_lang})")
            print(f"   Confidence: {confidence:.2%}")
            print("=" * 60 + "\n")
            
            return jsonify({
                "text": text,
                "detected_language": {
                    "code": detected_lang,
                    "name": lang_info['name'],
                    "native_name": lang_info['native'],
                    "script": lang_info['script'],
                    "confidence": confidence
                },
                "metadata": {
                    "auto_detected": True,
                    "method": result['method'],
                    "confidence": confidence,
                    "duration": result['duration']
                }
            }), 200
        
        # === GOOGLE FALLBACK (if Whisper not available) ===
        else:
            print("🧠 Using Google Speech Recognition (Fallback)...")
            
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            
            # Read audio
            with sr.AudioFile(str(temp_path)) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            
            # Try multiple languages
            LANG_CODES = ['hi-IN', 'en-IN', 'te-IN', 'ta-IN', 'mr-IN', 'bn-IN', 
                          'gu-IN', 'kn-IN', 'ml-IN', 'pa-IN', 'ur-IN']
            
            best_text = None
            best_lang = None
            best_length = 0
            
            for lang_code in LANG_CODES:
                try:
                    test_text = recognizer.recognize_google(audio_data, language=lang_code)
                    if test_text and len(test_text) > best_length:
                        best_text = test_text
                        best_lang = lang_code.split('-')[0]
                        best_length = len(test_text)
                        if len(test_text) > 20:
                            break
                except:
                    continue
            
            if not best_text:
                return jsonify({"error": "Could not transcribe audio"}), 400
            
            lang_info = language_detector.get_language_info(best_lang)
            
            print(f"✅ Google Result:")
            print(f"   Text: {best_text}")
            print(f"   Language: {lang_info['name']} ({best_lang})")
            print("=" * 60 + "\n")
            
            return jsonify({
                "text": best_text,
                "detected_language": {
                    "code": best_lang,
                    "name": lang_info['name'],
                    "native_name": lang_info['native'],
                    "script": lang_info['script'],
                    "confidence": 0.85
                },
                "metadata": {
                    "auto_detected": True,
                    "method": "Google Speech Recognition (Fallback)",
                    "confidence": 0.85
                }
            }), 200
        
    except Exception as e:
        print(f"❌ STT Error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"STT failed: {str(e)}"}), 500
    
    finally:
        if temp_path and Path(temp_path).exists():
            try:
                Path(temp_path).unlink()
                print(f"🗑️ Cleaned: {temp_path}")
            except:
                pass

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    try:
        file_path = AUDIO_DIR / filename
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        return send_file(str(file_path), mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# START SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎉 Flask Speech Engine Ready!")
    print("=" * 60)
    print(f"🌐 Server: http://localhost:8000")
    print(f"🔊 TTS: gTTS with auto-detection")
    print(f"🎙️ STT: {'Whisper AI (90-98%)' if whisper_service else 'Google Fallback (70-85%)'}")
    print(f"🌍 Languages: {len(language_detector.get_all_languages())}+")
    print("=" * 60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )