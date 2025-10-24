const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const transcribeAudio = async (req, res, next) => {
  try {
    const { language = 'en' } = req.body;
    
    if (!req.file) {
      return res.status(400).json(
        APIResponse.error('No audio file provided')
      );
    }

    console.log(`🎙️ Transcribing audio: ${req.file.filename}, Language: ${language}`);

    // Create form data for Python API
    const formData = new FormData();
    formData.append('audio', fs.createReadStream(req.file.path));
    formData.append('language', language);

    // Forward to Python FastAPI
    const response = await axios.post(
      `${PYTHON_API_URL}/api/v1/stt`,
      formData,
      {
        headers: {
          ...formData.getHeaders(),
        },
        timeout: 60000, // 60 seconds
      }
    );

    // Clean up uploaded file
    fs.unlinkSync(req.file.path);

    const { text, confidence, duration } = response.data;

    res.json(APIResponse.sttSuccess(text, language, confidence, duration));

  } catch (error) {
    // Clean up file on error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    console.error('STT Controller Error:', error.message);

    if (error.response) {
      return res.status(error.response.status).json(
        APIResponse.error(
          error.response.data.detail || 'Transcription service error',
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
  transcribeAudio
};
