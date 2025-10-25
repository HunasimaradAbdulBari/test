from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import speech_recognition as sr
from gtts import gTTS
import traceback
from pathlib import Path

app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize speech recognition
recognizer = sr.Recognizer()

# Create output directories
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "static" / "audio"
TEMP_DIR = BASE_DIR / "temp_audio"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Language mapping
LANGUAGE_MAP = {
    'en': 'en',
    'hi': 'hi', 
    'kn': 'kn',
    'ur': 'ur'
}

print("=" * 60)
print("🚀 Flask Speech Engine Starting...")
print("=" * 60)
print(f"📁 Audio Directory: {AUDIO_DIR}")
print(f"📁 Temp Directory: {TEMP_DIR}")
print("=" * 60)

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Flask Speech Engine API is running",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "tts": "POST /tts",
            "stt": "POST /stt",
            "audio": "GET /static/audio/<filename>"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    print("🏥 Health check requested")
    return jsonify({
        "status": "healthy",
        "message": "Flask Speech Engine is running",
        "service": "Flask TTS/STT",
        "services": {
            "speech_recognition": "ready",
            "text_to_speech": "ready",
            "method": "gTTS + SpeechRecognition"
        }
    }), 200

@app.route('/tts', methods=['POST', 'OPTIONS'])
def text_to_speech():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
        
    try:
        print("\n" + "=" * 60)
        print("🔊 [Flask TTS] Request received")
        print(f"   Content-Type: {request.content_type}")
        print(f"   Method: {request.method}")
        print("=" * 60)
        
        # Get JSON data
        data = request.get_json(force=True)
        
        if not data:
            print("❌ No JSON data received")
            return jsonify({"error": "No JSON data provided"}), 400
            
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        print(f"📝 Text length: {len(text)} characters")
        print(f"📝 Text preview: {text[:100]}...")
        print(f"🌍 Language: {language}")
        
        # Validation
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        if len(text) > 5000:
            return jsonify({"error": "Text exceeds maximum length of 5000 characters"}), 400
        
        if language not in LANGUAGE_MAP:
            return jsonify({"error": f"Unsupported language: {language}"}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())[:8]
        filename = f"speech_{file_id}.mp3"
        file_path = AUDIO_DIR / filename
        
        print(f"💾 Generating: {filename}")
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=LANGUAGE_MAP[language], slow=False)
        tts.save(str(file_path))
        
        # Verify file creation
        if not file_path.exists():
            raise Exception("Audio file was not created")
        
        file_size = file_path.stat().st_size
        duration_estimate = len(text) * 0.1  # Rough estimate
        
        # Generate audio URL
        audio_url = f"http://localhost:8000/static/audio/{filename}"
        
        print(f"✅ Success!")
        print(f"   File: {filename}")
        print(f"   Size: {file_size} bytes")
        print(f"   URL: {audio_url}")
        print("=" * 60 + "\n")
        
        return jsonify({
            "audio_url": audio_url,
            "language": language,
            "metadata": {
                "method": "gTTS",
                "file_size": file_size,
                "duration": duration_estimate,
                "filename": filename
            }
        }), 200
        
    except Exception as e:
        print(f"\n❌ TTS Error: {str(e)}")
        print(traceback.format_exc())
        print("=" * 60 + "\n")
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

@app.route('/stt', methods=['POST', 'OPTIONS'])
def speech_to_text():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
    
    temp_path = None
    try:
        print("\n" + "=" * 60)
        print("🎙️ [Flask STT] Request received")
        print("=" * 60)
        
        # Debug: Print all received data
        print(f"📋 Request method: {request.method}")
        print(f"📋 Content-Type: {request.content_type}")
        print(f"📋 Files in request: {list(request.files.keys())}")
        print(f"📋 Form data keys: {list(request.form.keys())}")
        
        # Check for audio file with detailed error
        if 'audio' not in request.files:
            error_msg = "No audio file in request"
            print(f"❌ {error_msg}")
            print(f"   Available files: {list(request.files.keys())}")
            print(f"   Available form: {list(request.form.keys())}")
            return jsonify({
                "error": error_msg,
                "received_files": list(request.files.keys()),
                "received_form": list(request.form.keys())
            }), 422
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')
        
        print(f"📁 Filename: {audio_file.filename}")
        print(f"📁 Content-Type: {audio_file.content_type}")
        print(f"🌍 Language: {language}")
        
        # Check if file is empty
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()
        audio_file.seek(0)  # Seek back to start
        
        print(f"📏 File size: {file_size} bytes")
        
        if file_size == 0:
            return jsonify({"error": "Audio file is empty"}), 422
        
        if not audio_file.filename:
            return jsonify({"error": "Invalid audio filename"}), 422
        
        # Save uploaded file temporarily
        file_id = str(uuid.uuid4())[:8]
        original_ext = Path(audio_file.filename).suffix if audio_file.filename else '.webm'
        temp_filename = f"temp_{file_id}{original_ext}"
        temp_path = TEMP_DIR / temp_filename
        
        print(f"💾 Saving to: {temp_path}")
        audio_file.save(str(temp_path))
        
        # Verify file was saved
        if not temp_path.exists():
            raise Exception("Failed to save uploaded file")
        
        saved_size = temp_path.stat().st_size
        print(f"✅ Saved successfully: {saved_size} bytes")
        
        # Convert to WAV if needed
        wav_path = temp_path
        if not str(temp_path).endswith('.wav'):
            try:
                print("🔄 Converting to WAV...")
                from pydub import AudioSegment
                audio = AudioSegment.from_file(str(temp_path))
                wav_path = temp_path.with_suffix('.wav')
                audio.export(str(wav_path), format='wav')
                
                # Clean up original file
                if temp_path.exists() and temp_path != wav_path:
                    temp_path.unlink()
                temp_path = wav_path
                print(f"✅ Converted to WAV: {wav_path}")
            except ImportError:
                print("⚠️ pydub not available, trying without conversion")
            except Exception as conv_error:
                print(f"⚠️ Conversion failed: {conv_error}")
                print("   Attempting to use original file...")
        
        # Transcribe using speech_recognition
        print("🔍 Starting transcription...")
        try:
            with sr.AudioFile(str(temp_path)) as source:
                print("📖 Reading audio file...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                print(f"✅ Audio loaded successfully")
        except Exception as audio_error:
            print(f"❌ Failed to read audio file: {audio_error}")
            return jsonify({
                "error": "Failed to read audio file",
                "detail": str(audio_error)
            }), 422
        
        print("🧠 Recognizing speech with Google API...")
        
        try:
            text = recognizer.recognize_google(
                audio_data,
                language=LANGUAGE_MAP.get(language, 'en')
            )
        except sr.UnknownValueError:
            print("❌ Speech not clear enough")
            return jsonify({
                "error": "Could not understand the audio",
                "detail": "Speech was not clear enough for transcription"
            }), 400
        except sr.RequestError as e:
            print(f"❌ Google API error: {e}")
            return jsonify({
                "error": "Speech recognition service error",
                "detail": str(e)
            }), 500
        
        print(f"✅ Transcription successful!")
        print(f"   Text: {text}")
        print("=" * 60 + "\n")
        
        return jsonify({
            "text": text,
            "language": language,
            "confidence": 0.95,
            "duration": None
        }), 200
        
    except Exception as e:
        print(f"\n❌ STT Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        print(traceback.format_exc())
        print("=" * 60 + "\n")
        return jsonify({
            "error": f"STT processing failed: {str(e)}",
            "type": type(e).__name__
        }), 500
        
    finally:
        # Clean up temp file
        if temp_path and Path(temp_path).exists():
            try:
                Path(temp_path).unlink()
                print(f"🗑️ Cleaned up: {temp_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Cleanup error: {cleanup_error}")

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    try:
        file_path = AUDIO_DIR / filename
        print(f"📂 Serving: {filename}")
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return jsonify({"error": "Audio file not found"}), 404
        
        return send_file(str(file_path), mimetype='audio/mpeg')
    except Exception as e:
        print(f"❌ Error serving file: {e}")
        return jsonify({"error": "File serving error"}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path,
        "method": request.method,
        "available_endpoints": [
            "GET /",
            "GET /health",
            "POST /tts",
            "POST /stt",
            "GET /static/audio/<filename>"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎉 Flask Speech Engine Ready!")
    print("=" * 60)
    print(f"🌐 Server: http://localhost:8000")
    print(f"🏥 Health: http://localhost:8000/health")
    print(f"🔊 TTS: POST http://localhost:8000/tts")
    print(f"🎙️ STT: POST http://localhost:8000/stt")
    print("=" * 60)
    
    # Print all registered routes
    print("\n📋 Registered Routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"   [{methods}] {rule.rule}")
    
    print("\n" + "=" * 60)
    print("📝 Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )