from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import speech_recognition as sr
from gtts import gTTS
import traceback

app = Flask(__name__)
CORS(app)

# Initialize speech recognition
recognizer = sr.Recognizer()

# Create output directories
os.makedirs("static/audio", exist_ok=True)
os.makedirs("temp_audio", exist_ok=True)

# Language mapping for gTTS
LANGUAGE_MAP = {
    'en': 'en',
    'hi': 'hi', 
    'kn': 'kn',
    'ur': 'ur'
}

print("🚀 Flask Speech Engine Starting...")
print("📁 Directories created: static/audio, temp_audio")

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Flask Speech Engine API is running",
        "status": "healthy",
        "endpoints": [
            "GET /health",
            "POST /api/v1/tts", 
            "POST /api/v1/stt",
            "GET /static/audio/<filename>"
        ]
    })

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
    })

@app.route('/api/v1/tts', methods=['POST', 'OPTIONS'])
def text_to_speech():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
        
    try:
        print("🔊 [Flask] TTS request received")
        print(f"🔍 Request method: {request.method}")
        print(f"🔍 Content-Type: {request.content_type}")
        
        # Get JSON data
        data = request.get_json()
        if not data:
            print("❌ No JSON data received")
            return jsonify({"error": "No JSON data provided"}), 400
            
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        print(f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"🌍 Language: {language}")
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())[:8]
        filename = f"speech_{file_id}.mp3"
        file_path = os.path.join("static", "audio", filename)
        
        print(f"💾 Generating audio file: {filename}")
        
        try:
            # Use gTTS to generate speech
            tts = gTTS(text=text, lang=LANGUAGE_MAP.get(language, 'en'), slow=False)
            tts.save(file_path)
            
            # Verify file was created
            if not os.path.exists(file_path):
                raise Exception("Audio file was not created")
            
            file_size = os.path.getsize(file_path)
            audio_url = f"http://localhost:8000/static/audio/{filename}"
            
            print(f"✅ Audio generated: {audio_url} ({file_size} bytes)")
            
            return jsonify({
                "audio_url": audio_url,
                "language": language,
                "metadata": {
                    "method": "gTTS",
                    "file_size": file_size,
                    "duration": len(text) * 0.1,
                    "filename": filename
                }
            })
            
        except Exception as tts_error:
            print(f"❌ TTS Generation Error: {tts_error}")
            return jsonify({"error": f"TTS generation failed: {str(tts_error)}"}), 500
            
    except Exception as e:
        print(f"❌ TTS Request Error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Request processing failed: {str(e)}"}), 500

@app.route('/api/v1/stt', methods=['POST', 'OPTIONS'])
def speech_to_text():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
        
    temp_path = None
    try:
        print("🎙️ [Flask] STT request received")
        print(f"🔍 Files in request: {list(request.files.keys())}")
        
        if 'audio' not in request.files:
            print("❌ No audio file in request")
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')
        
        print(f"📁 File: {audio_file.filename}, Language: {language}")
        
        # Save uploaded file temporarily
        file_id = str(uuid.uuid4())[:8]
        temp_path = os.path.join("temp_audio", f"temp_{file_id}.wav")
        audio_file.save(temp_path)
        
        print(f"💾 Saved temp file: {temp_path}")
        
        try:
            # Use speech_recognition library
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
            
            print(f"✅ Recognized text: {text}")
            
            return jsonify({
                "text": text,
                "language": language,
                "confidence": 0.95,
                "duration": None
            })
            
        except sr.UnknownValueError:
            print("❌ Could not understand the audio")
            return jsonify({"error": "Could not understand the audio"}), 400
            
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            return jsonify({"error": f"Speech recognition service error: {str(e)}"}), 500
            
    except Exception as e:
        print(f"❌ STT Error: {e}")
        print(traceback.format_exc())
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
        print(f"📂 Serving audio file: {filename}")
        file_path = os.path.join("static", "audio", filename)
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return jsonify({"error": "Audio file not found"}), 404
        return send_file(file_path)
    except Exception as e:
        print(f"❌ File serve error: {e}")
        return jsonify({"error": "File serving error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask Speech Engine on http://localhost:8000")
    print("📂 Audio files will be served from /static/audio/")
    print("🎙️ Using Google Speech Recognition")
    print("🔊 Using gTTS for speech synthesis")
    print("🔗 Available endpoints:")
    print("   GET  / (root)")
    print("   GET  /health")
    print("   POST /api/v1/tts")
    print("   POST /api/v1/stt")
    print("   GET  /static/audio/<filename>")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
