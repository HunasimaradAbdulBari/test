const axios = require('axios');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const generateSpeech = async (req, res, next) => {
  try {
    const { text, language = 'en', speed = 1.0, pitch = 1.0 } = req.body;
    
    console.log('🔊 [Backend] TTS Request:', { text: text?.substring(0, 50) + '...', language });
    
    if (!text || text.trim().length === 0) {
      return res.status(400).json(
        APIResponse.error('Text is required')
      );
    }

    if (text.length > 5000) {
      return res.status(400).json(
        APIResponse.error('Text exceeds maximum length of 5000 characters')
      );
    }

    // FIXED: Use /tts instead of /api/v1/tts
    console.log(`🔗 Forwarding to Python API: ${PYTHON_API_URL}/tts`);
    
    // Forward to Python Flask API
    const response = await axios.post(
      `${PYTHON_API_URL}/tts`,  // ← Changed from /api/v1/tts
      {
        text,
        language,
        speed,
        pitch
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000, // 30 seconds
      }
    );

    console.log('✅ [Backend] Python response received:', response.data);
    
    // Get audio_url from response and prepend Python API URL
    const audio_url = response.data.audio_url;
    const full_audio_url = audio_url.startsWith('http') 
      ? audio_url 
      : `${PYTHON_API_URL}${audio_url}`;
    
    res.json(APIResponse.ttsSuccess(full_audio_url, language, text, {
      method: 'flask-gtts',
      text_length: text.length
    }));
    
  } catch (error) {
    console.error('❌ [Backend] TTS Error:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json(
        APIResponse.error('Speech service unavailable. Please ensure Python service is running on port 8000.')
      );
    }
    
    if (error.response) {
      return res.status(error.response.status).json(
        APIResponse.error(error.response.data?.error || 'Python service error')
      );
    }
    
    res.status(500).json(APIResponse.error('Internal server error'));
  }
};

module.exports = { generateSpeech };