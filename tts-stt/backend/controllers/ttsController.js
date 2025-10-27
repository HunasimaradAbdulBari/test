// tts-stt/backend/controllers/ttsController.js
const axios = require('axios');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const generateSpeech = async (req, res, next) => {
  try {
    const { text, language = 'en', speed = 1.0, pitch = 1.0 } = req.body;
    
    console.log('🔊 [Backend TTS] Request:', { 
      textLength: text?.length, 
      language,
      pythonUrl: PYTHON_API_URL 
    });
    
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

    console.log(`🔗 Calling Python API: ${PYTHON_API_URL}/tts`);
    
    // Forward to Python Flask API
    const response = await axios.post(
      `${PYTHON_API_URL}/tts`,
      { text, language, speed, pitch },
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000,
      }
    );

    console.log('✅ [Backend TTS] Python response:', response.data);
    
    // CRITICAL FIX: Ensure audio_url is properly formatted
    const pythonAudioUrl = response.data.audio_url;
    
    // If the URL is relative, prepend the Python API URL
    const fullAudioUrl = pythonAudioUrl.startsWith('http') 
      ? pythonAudioUrl 
      : `${PYTHON_API_URL}${pythonAudioUrl}`;
    
    console.log('🎵 Final audio URL:', fullAudioUrl);
    
    // Return response with all possible key names for compatibility
    res.json({
      success: true,
      message: 'Audio generated successfully',
      data: {
        audio_url: fullAudioUrl,
        audioUrl: fullAudioUrl,
        url: fullAudioUrl,
        language,
        text: text.substring(0, 100),
        metadata: {
          method: 'flask-gtts',
          text_length: text.length,
          ...(response.data.metadata || {})
        }
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ [Backend TTS] Error:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json(
        APIResponse.error('Speech service unavailable. Python service not reachable.')
      );
    }
    
    if (error.response) {
      console.error('Python API Error:', error.response.data);
      return res.status(error.response.status).json(
        APIResponse.error(error.response.data?.error || 'Python service error')
      );
    }
    
    res.status(500).json(APIResponse.error('Internal server error: ' + error.message));
  }
};

module.exports = { generateSpeech };