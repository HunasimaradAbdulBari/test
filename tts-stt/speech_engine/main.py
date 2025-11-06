"""
FIXED: main.py - Native Language Transcription (No Translation)
Optimized for Speed - Transcribes in Original Language Script
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

# Whisper initialization - OPTIMIZED FOR SPEED
whisper_service = None
WHISPER_AVAILABLE = False

print("\n" + "="*80)
print("🚀 INITIALIZING OPTIMIZED SPEECH ENGINE")
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
    
    print("\n3️⃣ Loading Whisper model (OPTIMIZED)...")
    # Use 'base' for speed/accuracy balance
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    print(f"   Model: {WHISPER_MODEL}")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    whisper_model = whisper.load_model(WHISPER_MODEL, device=device)
    whisper_model.eval()
    
    # Optimized Whisper wrapper
    class OptimizedWhisperService:
        def __init__(self, model, device):
            self.model = model
            self.device = device
            self.is_ready = True
            print(f"   ✅ Whisper loaded - Native language transcription enabled!")
        
        def transcribe(self, audio_path, language_hint=None):
            """
            FIXED: Transcribe in native language (NO TRANSLATION)
            """
            import numpy as np
            
            try:
                # Optimized transcription options for SPEED
                options = {
                    'task': 'transcribe',  # CRITICAL: transcribe (not translate)
                    'fp16': self.device == 'cuda',
                    'verbose': False,
                    'beam_size': 3,  # Reduced from 5 for speed
                    'best_of': 3,    # Reduced from 5 for speed
                    'temperature': 0.0,
                    'compression_ratio_threshold': 2.4,
                    'logprob_threshold': -1.0,
                    'no_speech_threshold': 0.6,
                }
                
                # CRITICAL FIX: Only add language if we have a hint
                # Let Whisper auto-detect otherwise
                if language_hint:
                    whisper_lang_map = {
                        'en': 'english', 'hi': 'hindi', 'kn': 'kannada',
                        'ta': 'tamil', 'te': 'telugu', 'ml': 'malayalam',
                        'mr': 'marathi', 'gu': 'gujarati', 'bn': 'bengali',
                        'pa': 'punjabi', 'ur': 'urdu', 'or': 'odia',
                        'as': 'assamese', 'ne': 'nepali', 'ar': 'arabic'
                    }
                    
                    if language_hint in whisper_lang_map:
                        options['language'] = whisper_lang_map[language_hint]
                        print(f"   🎯 Language hint: {whisper_lang_map[language_hint]}")
                
                print(f"   🔄 Transcribing in native language...")
                
                # Transcribe
                with torch.inference_mode():
                    result = self.model.transcribe(str(audio_path), **options)
                
                text = result['text'].strip()
                detected_lang = result.get('language', 'en')
                
                # Calculate confidence
                segments = result.get('segments', [])
                if segments:
                    avg_logprob = np.mean([s.get('avg_logprob', -1) for s in segments])
                    confidence = min(0.99, max(0.5, np.exp(avg_logprob)))
                else:
                    confidence = 0.85
                
                # Map to our language codes
                lang_code_map = {
                    'english': 'en', 'hindi': 'hi', 'kannada': 'kn',
                    'tamil': 'ta', 'telugu': 'te', 'malayalam': 'ml',
                    'marathi': 'mr', 'gujarati': 'gu', 'bengali': 'bn',
                    'punjabi': 'pa', 'urdu': 'ur', 'odia': 'or',
                    'assamese': 'as', 'nepali': 'ne', 'arabic': 'ar'
                }
                final_lang_code = lang_code_map.get(detected_lang, 'en')
                
                print(f"   ✅ Transcribed successfully!")
                print(f"   Language: {detected_lang} -> {final_lang_code}")
                print(f"   Confidence: {confidence:.2%}")
                print(f"   Text: {text[:100]}...")
                
                return {
                    'text': text,
                    'language': final_lang_code,
                    'confidence': confidence,
                    'duration': len(text) / 150 * 60,
                    'method': f'Whisper-{WHISPER_MODEL}-native'
                }
                
            except Exception as e:
                print(f"❌ Whisper transcription error: {e}")
                traceback.print_exc()
                raise
    
    whisper_service = OptimizedWhisperService(whisper_model, device)
    WHISPER_AVAILABLE = True
    print(f"\n{'='*80}")
    print("✅ WHISPER READY - NATIVE LANGUAGE TRANSCRIPTION")
    print("="*80)

except ImportError as e:
    print(f"\n⚠️  Whisper dependencies not installed: {e}")
    WHISPER_AVAILABLE = False

except Exception as e:
    print(f"\n⚠️  Whisper initialization failed: {e}")
    traceback.print_exc()
    WHISPER_AVAILABLE = False

print("\n" + "="*80)
print("✅ SPEECH ENGINE READY")
print("="*80)
print(f"   • Languages: {len(ultimate_detector.LANGUAGES)}")
print(f"   • TTS: gTTS (operational)")
print(f"   • STT: {'Optimized Whisper (' + WHISPER_MODEL + ')' if WHISPER_AVAILABLE else 'Fallback'}")
print("="*80 + "\n")

# ============================================================================
# TEXT-TO-SPEECH (PERFECT - DO NOT TOUCH)
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
# SPEECH-TO-TEXT (OPTIMIZED - NATIVE LANGUAGE OUTPUT)
# ============================================================================

@app.route('/stt', methods=['POST', 'OPTIONS'])
def speech_to_text():
    """OPTIMIZED: Fast transcription in native language (NO TRANSLATION)"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    temp_path = None
    
    try:
        print(f"\n{'='*60}")
        print("🎙️ [STT] OPTIMIZED - Native Language Transcription")
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
        
        if WHISPER_AVAILABLE and whisper_service and whisper_service.is_ready:
            print("🤖 Using Optimized Whisper...")
            
            start_time = time.time()
            
            # Convert to WAV if needed (for consistency)
            audio_path = temp_path
            if ext.lower() not in ['.wav']:
                try:
                    from pydub import AudioSegment
                    print("🔄 Converting to WAV...")
                    audio = AudioSegment.from_file(str(temp_path))
                    audio = audio.set_frame_rate(16000).set_channels(1)
                    wav_path = temp_path.with_suffix('.wav')
                    audio.export(str(wav_path), format='wav')
                    if temp_path != wav_path:
                        temp_path.unlink()
                    audio_path = wav_path
                    temp_path = wav_path
                    print(f"   ✅ Converted to: {wav_path.name}")
                except Exception as e:
                    print(f"⚠️ Conversion failed: {e}, using original")
            
            # SINGLE PASS: Let Whisper auto-detect and transcribe in native language
            result = whisper_service.transcribe(str(audio_path))
            
            text = result['text']
            detected_lang = result['language']
            confidence = result['confidence']
            
            processing_time = time.time() - start_time
            
            # Verify with text-based detection for accuracy
            if text and len(text) > 10:
                text_lang, text_conf = ultimate_detector.detect_text_language(
                    text, 
                    verbose=False
                )
                
                print(f"   🔍 Cross-check:")
                print(f"      Whisper: {detected_lang}")
                print(f"      Text: {text_lang} ({text_conf:.1%})")
                
                # Use text detection if it has higher confidence
                if text_conf > 0.85 and text_conf > confidence:
                    detected_lang = text_lang
                    confidence = text_conf
                    print(f"   ✅ Using text-verified language: {text_lang}")
            
            lang_info = ultimate_detector.get_language_info(detected_lang)
            
            print(f"✅ TRANSCRIBED in {processing_time:.2f}s")
            print(f"   Language: {lang_info['name']}")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Text: {text[:100]}...")
            print(f"{'='*60}\n")
            
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
                    "duration": result['duration'],
                    "processing_time": processing_time,
                    "native_transcription": True
                }
            }), 200
        
        else:
            print("⚠️  Whisper unavailable - returning fallback")
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
                    "message": "Whisper not available",
                    "fallback": True
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
        "name": "Optimized Speech Engine - Native Language Transcription",
        "version": "8.0.0",
        "status": "operational",
        "features": {
            "tts": "operational (gTTS)",
            "stt": "optimized native transcription" if WHISPER_AVAILABLE else "fallback",
            "languages": len(ultimate_detector.LANGUAGES),
            "auto_detection": True,
            "native_transcription": True,
            "no_translation": True
        },
        "whisper_status": {
            "available": WHISPER_AVAILABLE,
            "model": WHISPER_MODEL if WHISPER_AVAILABLE else None,
            "device": whisper_service.device if WHISPER_AVAILABLE and whisper_service else None,
            "optimization": "Native language output (no translation)" if WHISPER_AVAILABLE else None
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "tts": "operational",
            "stt": "optimized" if WHISPER_AVAILABLE else "degraded",
            "whisper": "native transcription" if WHISPER_AVAILABLE else "unavailable"
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
    print("🎉 STARTING OPTIMIZED SPEECH ENGINE")
    print(f"{'='*80}")
    print(f"📡 Server: http://localhost:8000")
    print(f"🎯 TTS: Perfect (gTTS with auto-detection)")
    print(f"🎙️  STT: {'Optimized (' + WHISPER_MODEL + ') - Native Language' if WHISPER_AVAILABLE else 'Fallback'}")
    
    if not WHISPER_AVAILABLE:
        print(f"\n💡 To enable Whisper STT:")
        print(f"   pip install torch openai-whisper pydub")
    else:
        print(f"\n✅ Whisper configured for:")
        print(f"   • Native language transcription (NO translation)")
        print(f"   • Optimized for speed (beam_size=3)")
        print(f"   • Auto language detection")
    
    print(f"{'='*80}\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True,
        use_reloader=False
    )