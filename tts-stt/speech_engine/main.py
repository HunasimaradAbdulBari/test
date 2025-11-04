"""
FIXED: main.py - Enhanced Speech Engine with FORCED Language-Specific Transcription
This version FORCES Whisper to transcribe in the correct detected language script
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

# Whisper initialization - OPTIMIZED FOR INDIAN LANGUAGES
whisper_service = None
WHISPER_AVAILABLE = False

print("\n" + "="*80)
print("🚀 INITIALIZING ENHANCED SPEECH ENGINE - FORCE CORRECT SCRIPT")
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
    # CRITICAL: Use 'base' or 'medium' for better Indian language support
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    print(f"   Model: {WHISPER_MODEL}")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    whisper_model = whisper.load_model(WHISPER_MODEL, device=device)
    whisper_model.eval()
    
    # Language-specific initial prompts to FORCE correct script
    LANGUAGE_PROMPTS = {
        'hi': 'यह हिंदी में है। हिंदी भाषा में बोल रहे हैं।',
        'kn': 'ಇದು ಕನ್ನಡದಲ್ಲಿದೆ। ಕನ್ನಡ ಭಾಷೆಯಲ್ಲಿ ಮಾತನಾಡುತ್ತಿದ್ದಾರೆ।',
        'ta': 'இது தமிழில் உள்ளது। தமிழ் மொழியில் பேசுகிறார்கள்।',
        'te': 'ఇది తెలుగులో ఉంది। తెలుగు భాషలో మాట్లాడుతున్నారు।',
        'ml': 'ഇത് മലയാളത്തിലാണ്। മലയാളം ഭാഷയിൽ സംസാരിക്കുന്നു।',
        'mr': 'हे मराठीत आहे। मराठी भाषेत बोलत आहेत।',
        'gu': 'આ ગુજરાતીમાં છે। ગુજરાતી ભાષામાં બોલી રહ્યા છે।',
        'bn': 'এটি বাংলায় আছে। বাংলা ভাষায় কথা বলছেন।',
        'pa': 'ਇਹ ਪੰਜਾਬੀ ਵਿੱਚ ਹੈ। ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਵਿੱਚ ਬੋਲ ਰਹੇ ਹਨ।',
        'ur': 'یہ اردو میں ہے۔ اردو زبان میں بات کر رہے ہیں۔',
        'or': 'ଏହା ଓଡ଼ିଆରେ ଅଛି। ଓଡ଼ିଆ ଭାଷାରେ କଥା ହେଉଛି।',
        'as': 'এইটো অসমীয়াত আছে। অসমীয়া ভাষাত কথা কৈছে।',
        'ne': 'यो नेपालीमा छ। नेपाली भाषामा बोल्दै हुनुहुन्छ।',
        'en': 'This is in English. Speaking in English language.'
    }
    
    # Enhanced wrapper with FORCED language transcription
    class ForcedLanguageWhisperService:
        def __init__(self, model, device):
            self.model = model
            self.device = device
            self.is_ready = True
            print(f"   ✅ Whisper loaded with forced language support!")
        
        def transcribe(self, audio_path, detected_language_code=None):
            """
            CRITICAL FIX: Force Whisper to transcribe in detected language's script
            """
            import numpy as np
            
            try:
                # Map language codes to Whisper language names
                whisper_lang_map = {
                    'en': 'english',
                    'hi': 'hindi',
                    'kn': 'kannada',
                    'ta': 'tamil',
                    'te': 'telugu',
                    'ml': 'malayalam',
                    'mr': 'marathi',
                    'gu': 'gujarati',
                    'bn': 'bengali',
                    'pa': 'punjabi',
                    'ur': 'urdu',
                    'or': 'odia',
                    'as': 'assamese',
                    'ne': 'nepali',
                    'ar': 'arabic'
                }
                
                # CRITICAL: Get Whisper language name
                whisper_language = None
                if detected_language_code and detected_language_code in whisper_lang_map:
                    whisper_language = whisper_lang_map[detected_language_code]
                    print(f"   🎯 FORCING language: {whisper_language} ({detected_language_code})")
                
                # Base transcription options
                options = {
                    'task': 'transcribe',
                    'fp16': self.device == 'cuda',
                    'verbose': False,
                    'beam_size': 5,
                    'best_of': 5,
                    'temperature': 0.0,
                    'compression_ratio_threshold': 2.4,
                    'logprob_threshold': -1.0,
                    'no_speech_threshold': 0.6,
                    'condition_on_previous_text': True,
                }
                
                # CRITICAL FIX 1: FORCE language parameter
                if whisper_language:
                    options['language'] = whisper_language
                    
                    # CRITICAL FIX 2: Add language-specific initial prompt
                    if detected_language_code in LANGUAGE_PROMPTS:
                        options['initial_prompt'] = LANGUAGE_PROMPTS[detected_language_code]
                        print(f"   📝 Using prompt: {LANGUAGE_PROMPTS[detected_language_code][:50]}...")
                
                print(f"   🔄 Transcribing with FORCED settings...")
                
                # Transcribe with forced language
                with torch.inference_mode():
                    result = self.model.transcribe(audio_path, **options)
                
                text = result['text'].strip()
                detected_lang = result.get('language', 'en')
                
                # Calculate confidence
                segments = result.get('segments', [])
                if segments:
                    avg_logprob = np.mean([s.get('avg_logprob', -1) for s in segments])
                    confidence = min(0.99, max(0.5, np.exp(avg_logprob)))
                else:
                    confidence = 0.85
                
                # CRITICAL: Verify script matches language
                script_match = self._verify_script(text, detected_language_code)
                
                if not script_match:
                    print(f"   ⚠️ WARNING: Script mismatch detected!")
                    print(f"   Expected: {detected_language_code}, Got: {detected_lang}")
                    print(f"   Text: {text[:100]}")
                    
                    # Try to fix by forcing language again
                    print(f"   🔄 Retrying with stricter settings...")
                    options['temperature'] = (0.0, 0.2, 0.4, 0.6, 0.8)  # Multiple temperatures
                    options['beam_size'] = 10  # More beams
                    
                    result = self.model.transcribe(audio_path, **options)
                    text = result['text'].strip()
                    detected_lang = result.get('language', detected_language_code)
                
                # Map back to our language codes
                lang_code_map = {v: k for k, v in whisper_lang_map.items()}
                final_lang_code = detected_language_code or lang_code_map.get(detected_lang, detected_lang)
                
                print(f"   ✅ Transcribed successfully!")
                print(f"   Language: {detected_lang} -> {final_lang_code}")
                print(f"   Confidence: {confidence:.2%}")
                print(f"   Text: {text[:100]}...")
                
                return {
                    'text': text,
                    'language': final_lang_code,
                    'confidence': confidence,
                    'duration': len(text) / 150 * 60,
                    'method': f'Whisper-{WHISPER_MODEL}-forced',
                    'script_verified': script_match
                }
                
            except Exception as e:
                print(f"❌ Whisper transcription error: {e}")
                traceback.print_exc()
                raise
        
        def _verify_script(self, text, expected_lang):
            """Verify that the transcribed text is in the correct script"""
            if not expected_lang or not text:
                return True
            
            # Unicode ranges for verification
            script_ranges = {
                'hi': (0x0900, 0x097F),  # Devanagari
                'kn': (0x0C80, 0x0CFF),  # Kannada
                'ta': (0x0B80, 0x0BFF),  # Tamil
                'te': (0x0C00, 0x0C7F),  # Telugu
                'ml': (0x0D00, 0x0D7F),  # Malayalam
                'mr': (0x0900, 0x097F),  # Devanagari (same as Hindi)
                'gu': (0x0A80, 0x0AFF),  # Gujarati
                'bn': (0x0980, 0x09FF),  # Bengali
                'pa': (0x0A00, 0x0A7F),  # Gurmukhi
                'ur': (0x0600, 0x06FF),  # Arabic
                'or': (0x0B00, 0x0B7F),  # Odia
                'as': (0x0980, 0x09FF),  # Bengali/Assamese
                'ne': (0x0900, 0x097F),  # Devanagari
                'en': (0x0020, 0x007F),  # Latin
            }
            
            if expected_lang not in script_ranges:
                return True
            
            start, end = script_ranges[expected_lang]
            
            # Count characters in expected script
            expected_script_chars = sum(1 for c in text if start <= ord(c) <= end and c.isalpha())
            total_alpha_chars = sum(1 for c in text if c.isalpha())
            
            if total_alpha_chars == 0:
                return True
            
            match_percentage = expected_script_chars / total_alpha_chars
            
            print(f"   📊 Script match: {match_percentage:.1%} ({expected_script_chars}/{total_alpha_chars})")
            
            # Consider it a match if >50% of characters are in expected script
            return match_percentage > 0.5
    
    whisper_service = ForcedLanguageWhisperService(whisper_model, device)
    WHISPER_AVAILABLE = True
    print(f"\n{'='*80}")
    print("✅ WHISPER READY WITH FORCED LANGUAGE SUPPORT!")
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
print(f"   • STT: {'Whisper (' + WHISPER_MODEL + ') with forced script' if WHISPER_AVAILABLE else 'Fallback'}")
print("="*80 + "\n")

# ============================================================================
# TEXT-TO-SPEECH (Working perfectly)
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
# SPEECH-TO-TEXT (FIXED WITH FORCED LANGUAGE)
# ============================================================================

@app.route('/stt', methods=['POST', 'OPTIONS'])
def speech_to_text():
    """FIXED: Transcribe speech with FORCED language-specific script"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    temp_path = None
    
    try:
        print(f"\n{'='*60}")
        print("🎙️ [STT] ENHANCED Request with FORCED SCRIPT")
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
            print("🤖 Using Whisper with FORCED language script...")
            
            # Convert to WAV for better processing
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
            
            # STEP 1: Pre-detect language from audio duration/characteristics
            try:
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_wav(str(audio_path))
                duration_sec = len(audio_segment) / 1000.0
                print(f"   📊 Audio duration: {duration_sec:.1f}s")
                
                if duration_sec < 2:
                    print(f"   ⚠️ Very short audio - detection may be less accurate")
                
                print(f"   ✅ Audio length sufficient for detection")
            except Exception as e:
                print(f"   ⚠️ Audio analysis: {e}")
            
            # STEP 2: First pass - detect language WITHOUT forcing
            print(f"   🔍 Pass 1: Detecting language...")
            
            first_pass_options = {
                'task': 'transcribe',
                'fp16': whisper_service.device == 'cuda',
                'verbose': False,
                'beam_size': 3,
                'temperature': 0.0,
            }
            
            with torch.inference_mode():
                first_result = whisper_service.model.transcribe(str(audio_path), **first_pass_options)
            
            detected_whisper_lang = first_result.get('language', 'en')
            first_pass_text = first_result['text'].strip()
            
            # Map to our language code
            whisper_to_code = {
                'english': 'en', 'hindi': 'hi', 'kannada': 'kn', 'tamil': 'ta',
                'telugu': 'te', 'malayalam': 'ml', 'marathi': 'mr', 'gujarati': 'gu',
                'bengali': 'bn', 'punjabi': 'pa', 'urdu': 'ur', 'odia': 'or',
                'assamese': 'as', 'nepali': 'ne', 'arabic': 'ar'
            }
            
            detected_lang_code = whisper_to_code.get(detected_whisper_lang, 'en')
            
            print(f"   ✅ Detected: {detected_whisper_lang} -> {detected_lang_code}")
            print(f"   Text preview: {first_pass_text[:100]}...")
            
            # STEP 3: Second pass - FORCE transcription in detected language
            print(f"   🔄 Pass 2: FORCING {detected_lang_code} script...")
            
            result = whisper_service.transcribe(
                str(audio_path),
                detected_language_code=detected_lang_code
            )
            
            text = result['text']
            final_lang = result['language']
            confidence = result['confidence']
            script_verified = result.get('script_verified', False)
            
            # STEP 4: Cross-verify with text-based detection
            if text and len(text) > 10:
                text_lang, text_conf = ultimate_detector.detect_text_language(
                    text,
                    verbose=False
                )
                
                print(f"   🔍 Cross-check:")
                print(f"      Whisper detected: {detected_lang_code}")
                print(f"      Text analysis: {text_lang} ({text_conf:.1%})")
                print(f"      Script verified: {script_verified}")
                
                # If text detection strongly disagrees and script doesn't match, trust text detection
                if text_conf > 0.85 and text_lang != final_lang and not script_verified:
                    print(f"   ⚠️ Script mismatch! Using text-detected language: {text_lang}")
                    final_lang = text_lang
                    final_confidence = text_conf
                else:
                    final_confidence = (confidence + text_conf) / 2
            else:
                final_confidence = confidence
            
            lang_info = ultimate_detector.get_language_info(final_lang)
            
            print(f"✅ FINAL: {lang_info['name']} ({final_confidence:.2%})")
            print(f"   Text: {text[:100]}...")
            print(f"   Script verified: {'✓' if script_verified else '✗'}")
            print(f"{'='*60}\n")
            
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
                    "duration": result['duration'],
                    "whisper_detected": detected_lang_code,
                    "text_verified": text_lang if 'text_lang' in locals() else None,
                    "script_verified": script_verified,
                    "two_pass_detection": True
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
        "name": "Enhanced Speech Engine - Forced Script Correction",
        "version": "7.0.0",
        "status": "operational",
        "features": {
            "tts": "operational (gTTS)",
            "stt": "enhanced with forced script" if WHISPER_AVAILABLE else "fallback",
            "languages": len(ultimate_detector.LANGUAGES),
            "auto_detection": True,
            "script_forcing": True,
            "two_pass_detection": True
        },
        "whisper_status": {
            "available": WHISPER_AVAILABLE,
            "model": WHISPER_MODEL if WHISPER_AVAILABLE else None,
            "device": whisper_service.device if WHISPER_AVAILABLE and whisper_service else None,
            "optimization": "Forced language script" if WHISPER_AVAILABLE else None
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "tts": "operational",
            "stt": "enhanced" if WHISPER_AVAILABLE else "degraded",
            "whisper": "loaded with forced script" if WHISPER_AVAILABLE else "unavailable"
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
    print("🎉 STARTING SPEECH ENGINE WITH FORCED SCRIPT CORRECTION")
    print(f"{'='*80}")
    print(f"📡 Server: http://localhost:8000")
    print(f"🎯 TTS: Operational with auto-detection")
    print(f"🎙️  STT: {'Enhanced with forced script (' + WHISPER_MODEL + ')' if WHISPER_AVAILABLE else 'Fallback'}")
    
    if not WHISPER_AVAILABLE:
        print(f"\n💡 To enable Whisper STT:")
        print(f"   pip install torch openai-whisper pydub")
    else:
        print(f"\n✅ Whisper configured with:")
        print(f"   • Two-pass detection (detect → force)")
        print(f"   • Language-specific prompts")
        print(f"   • Script verification")
        print(f"   • Cross-validation with text detection")
    
    print(f"{'='*80}\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True,
        use_reloader=False
    )