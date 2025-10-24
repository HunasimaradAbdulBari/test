const axios = require('axios');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const generateSpeech = async (req, res, next) => {
  try {
    const { text, language = 'en', speed = 1.0, pitch = 1.0 } = req.body;

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

    console.log(`🔊 Generating speech: ${text.substring(0, 50)}..., Language: ${language}`);

    // Forward to Python FastAPI
    const response = await axios.post(
      `${PYTHON_API_URL}/api/v1/tts`,
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

    const { audio_url, metadata } = response.data;

    res.json(APIResponse.ttsSuccess(audio_url, language, text, metadata));

  } catch (error) {
    console.error('TTS Controller Error:', error.message);

    if (error.response) {
      return res.status(error.response.status).json(
        APIResponse.error(
          error.response.data.detail || 'Speech generation service error',
          error.response.data
        )
      );
    }

    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json(
        APIResponse.error('Speech service unavailable')
      );
    }

    next(error);
  }
};

module.exports = {
  generateSpeech
};
