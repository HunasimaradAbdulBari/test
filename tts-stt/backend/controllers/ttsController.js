const axios = require('axios');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const generateSpeech = async (req, res, next) => {
  try {
    const { text, speed = 1.0, pitch = 1.0 } = req.body;
    
    console.log('🔊 [Backend TTS] Request with AUTO-DETECTION');
    console.log(`   Text length: ${text?.length} characters`);
    console.log(`   Python URL: ${PYTHON_API_URL}`);
    
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
    console.log(`   (Language will be auto-detected)`);
    
    // Forward to Python Flask API - NO LANGUAGE PARAMETER
    const response = await axios.post(
      `${PYTHON_API_URL}/tts`,
      { text, speed, pitch },  // Language removed - auto-detection
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000,
      }
    );

    console.log('✅ [Backend TTS] Python response received');
    console.log(`   Detected: ${response.data.detected_language?.name || 'Unknown'}`);
    
    const pythonAudioUrl = response.data.audio_url;
    
    // Build full audio URL
    const fullAudioUrl = pythonAudioUrl.startsWith('http') 
      ? pythonAudioUrl 
      : `${PYTHON_API_URL}${pythonAudioUrl}`;
    
    console.log('🎵 Final audio URL:', fullAudioUrl);
    
    // Return comprehensive response
    res.json({
      success: true,
      message: 'Audio generated successfully with auto-detected language',
      data: {
        audio_url: fullAudioUrl,
        audioUrl: fullAudioUrl,
        url: fullAudioUrl,
        detected_language: response.data.detected_language,
        text: text.substring(0, 100),
        metadata: {
          method: 'flask-gtts',
          auto_detected: true,
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