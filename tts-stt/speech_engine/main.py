from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import speech_recognition as sr
from gtts import gTTS
import traceback

app = Flask(__name__)

# Enable CORS for all routes
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
AUDIO_DIR = os.path.join(os.getcwd(), "static", "audio")
TEMP_DIR = os.path.join(os.getcwd(), "temp_audio")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Language mapping for gTTS
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
            "tts": "POST /api/v1/tts",
            "stt": "POST /api/v1/stt",
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

@app.route('/api/v1/tts', methods=['POST', 'OPTIONS'])
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
        
        # Get JSON data - be flexible with content type
        data = None
        if request.is_json:
            data = request.get_json()
        elif request.data:
            import json
            try:
                data = json.loads(request.data.decode('utf-8'))
            except:
                pass
        
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
        file_path = os.path.join(AUDIO_DIR, filename)
        
        print(f"💾 Generating: {filename}")
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=LANGUAGE_MAP[language], slow=False)
        tts.save(file_path)
        
        # Verify file creation
        if not os.path.exists(file_path):
            raise Exception("Audio file was not created")
        
        file_size = os.path.getsize(file_path)
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

@app.route('/api/v1/stt', methods=['POST', 'OPTIONS'])
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
        
        # Check for audio file
        if 'audio' not in request.files:
            print("❌ No audio file in request")
            print(f"   Files received: {list(request.files.keys())}")
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')
        
        print(f"📁 File: {audio_file.filename}")
        print(f"📁 Content-Type: {audio_file.content_type}")
        print(f"🌍 Language: {language}")
        
        if not audio_file.filename:
            return jsonify({"error": "Invalid audio file"}), 400
        
        # Save uploaded file temporarily
        file_id = str(uuid.uuid4())[:8]
        original_ext = os.path.splitext(audio_file.filename)[1]
        temp_filename = f"temp_{file_id}{original_ext}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        audio_file.save(temp_path)
        print(f"💾 Saved to: {temp_path}")
        
        # Convert to WAV if needed (speech_recognition requires WAV)
        if not temp_path.endswith('.wav'):
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(temp_path)
                wav_path = temp_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_path, format='wav')
                
                # Clean up original file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                temp_path = wav_path
                print(f"🔄 Converted to WAV: {wav_path}")
            except Exception as conv_error:
                print(f"⚠️ Conversion warning: {conv_error}")
                print("   Attempting to use file as-is...")
        
        # Transcribe using speech_recognition
        with sr.AudioFile(temp_path) as source:
            print("🔍 Processing audio...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        print("🧠 Recognizing speech...")
        
        # Use Google Speech Recognition
        text = recognizer.recognize_google(
            audio_data,
            language=LANGUAGE_MAP.get(language, 'en')
        )
        
        print(f"✅ Success!")
        print(f"   Transcribed: {text}")
        print("=" * 60 + "\n")
        
        return jsonify({
            "text": text,
            "language": language,
            "confidence": 0.95,
            "duration": None
        }), 200
        
    except sr.UnknownValueError:
        print("❌ Could not understand the audio")
        print("=" * 60 + "\n")
        return jsonify({"error": "Could not understand the audio"}), 400
        
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}")
        print("=" * 60 + "\n")
        return jsonify({"error": f"Speech recognition service error: {str(e)}"}), 500
        
    except Exception as e:
        print(f"❌ STT Error: {str(e)}")
        print(traceback.format_exc())
        print("=" * 60 + "\n")
        return jsonify({"error": f"STT processing failed: {str(e)}"}), 500
        
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print(f"🗑️ Cleaned up: {temp_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Cleanup error: {cleanup_error}")

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    try:
        file_path = os.path.join(AUDIO_DIR, filename)
        print(f"📂 Serving: {filename}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return jsonify({"error": "Audio file not found"}), 404
        
        return send_file(file_path, mimetype='audio/mpeg')
    except Exception as e:
        print(f"❌ Error serving file: {e}")
        return jsonify({"error": "File serving error"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path,
        "method": request.method,
        "available_endpoints": [
            "GET /",
            "GET /health",
            "POST /api/v1/tts",
            "POST /api/v1/stt",
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
    print(f"🔊 TTS: POST http://localhost:8000/api/v1/tts")
    print(f"🎙️ STT: POST http://localhost:8000/api/v1/stt")
    print("=" * 60)
    
    # Print all registered routes for debugging
    print("\n📋 Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule}")
    
    print("\n" + "=" * 60)
    print("📝 Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    # Run with threaded mode for better concurrency
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )