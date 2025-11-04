"""
PRODUCTION-READY Speech Engine with Fallback
- gTTS for TTS (working)
- Whisper for STT with fallback to Web Speech API
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

# Try to import Whisper (optional)
whisper_service = None
try:
    from optimized_whisper import whisper_service, initialize_whisper
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    print(f"\n📦 Attempting to load Whisper ({WHISPER_MODEL})...")
    whisper_ready = initialize_whisper(WHISPER_MODEL)
    if whisper_ready:
        print("✅ Whisper loaded successfully")
    else:
        print("⚠️  Whisper failed to load - using fallback")
        whisper_service = None
except Exception as e:
    print(f"⚠️  Whisper unavailable: {e}")
    print("   STT will use alternative methods")
    whisper_service = None

print("\n" + "="*80)
print("✅ SPEECH ENGINE READY")
print("="*80)
print(f"   • Languages: {len(ultimate_detector.LANGUAGES)}")
print(f"   • TTS: gTTS (fully operational)")
print(f"   • STT: {'Whisper' if whisper_service else 'Fallback mode'}")
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
# SPEECH-TO-TEXT (With Fallback)
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
        
        # Try Whisper first
        if whisper_service and whisper_service.is_ready:
            print("🤖 Using Whisper transcription...")
            
            # Convert if needed
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
                except Exception as e:
                    print(f"⚠️ Conversion failed: {e}")
            
            # Whisper transcription
            result = whisper_service.transcribe(str(audio_path), language=None)
            
            text = result['text']
            whisper_lang = result['language']
            confidence = result['confidence']
            
            # Verify with text detection
            text_lang, text_conf = ultimate_detector.detect_text_language(text, verbose=False)
            
            final_lang = whisper_lang
            final_confidence = confidence
            
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
            # FALLBACK: Return instructional message
            print("⚠️  Whisper unavailable - returning fallback response")
            
            return jsonify({
                "text": "[Please use browser's built-in speech recognition or install Whisper dependencies]",
                "detected_language": {
                    "code": "en",
                    "name": "English",
                    "native_name": "English",
                    "script": "Latin",
                    "confidence": 0.5
                },
                "metadata": {
                    "auto_detected": False,
                    "method": "fallback",
                    "message": "Whisper service unavailable. Please install: pip install openai-whisper torch torchaudio"
                }
            }), 200
        
    except Exception as e:
        print(f"❌ STT Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
    finally:
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
            "stt": "operational" if whisper_service else "fallback mode",
            "languages": len(ultimate_detector.LANGUAGES),
            "auto_detection": True
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "tts": "operational",
            "stt": "operational" if whisper_service else "degraded",
            "whisper": "loaded" if whisper_service else "unavailable"
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
    print(f"🎙️  STT: {'Whisper ready' if whisper_service else 'Fallback mode - install Whisper for full features'}")
    print(f"{'='*80}\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True,
        use_reloader=False
    )