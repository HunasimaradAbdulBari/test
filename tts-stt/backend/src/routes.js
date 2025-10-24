const express = require('express');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const config = require('./config');
const { 
  deleteFile, 
  validateAudioFile, 
  validateLanguage, 
  validateText,
  successResponse, 
  errorResponse 
} = require('./utils');

const router = express.Router();

// Health Check
router.get('/health', async (req, res) => {
  try {
    // Check Python API health
    const pythonResponse = await axios.get(`${config.PYTHON_API_URL}/health`, {
      timeout: 5000
    }).catch(() => ({ data: { status: 'unreachable' } }));

    res.json(successResponse({
      status: 'healthy',
      backend: 'online',
      python_api: pythonResponse.data.status || 'unreachable',
      timestamp: new Date().toISOString()
    }));
  } catch (error) {
    res.status(503).json(errorResponse('Service unhealthy', 503));
  }
});

// Speech-to-Text
router.post('/stt', async (req, res) => {
  let filePath = null;

  try {
    // Validate file
    if (!req.file) {
      return res.status(400).json(errorResponse('No audio file provided', 400));
    }

    const fileValidation = validateAudioFile(req.file);
    if (!fileValidation.valid) {
      return res.status(400).json(errorResponse(fileValidation.error, 400));
    }

    filePath = req.file.path;
    const language = req.body.language || 'en';

    // Validate language
    const langValidation = validateLanguage(language, config.SUPPORTED_LANGUAGES);
    if (!langValidation.valid) {
      await deleteFile(filePath);
      return res.status(400).json(errorResponse(langValidation.error, 400));
    }

    console.log(`📝 Processing STT: ${language}, ${req.file.originalname}`);

    // Create form data for Python API
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('language', language);

    // Call Python API
    const response = await axios.post(
      `${config.PYTHON_API_URL}/stt`,
      formData,
      {
        headers: formData.getHeaders(),
        timeout: 60000,
        maxContentLength: Infinity,
        maxBodyLength: Infinity
      }
    );

    // Cleanup
    await deleteFile(filePath);

    // Return response
    res.json(successResponse(response.data, 'Transcription completed'));

  } catch (error) {
    console.error('❌ STT Error:', error.message);
    if (filePath) await deleteFile(filePath);
    
    const message = error.response?.data?.message || error.message || 'Transcription failed';
    res.status(500).json(errorResponse(message, 500));
  }
});

// Text-to-Speech
router.post('/tts', async (req, res) => {
  try {
    const { text, language, speed } = req.body;

    // Validate text
    const textValidation = validateText(text);
    if (!textValidation.valid) {
      return res.status(400).json(errorResponse(textValidation.error, 400));
    }

    // Validate language
    const langValidation = validateLanguage(language, config.SUPPORTED_LANGUAGES);
    if (!langValidation.valid) {
      return res.status(400).json(errorResponse(langValidation.error, 400));
    }

    console.log(`🔊 Processing TTS: ${language}, ${text.length} chars`);

    // Call Python API
    const response = await axios.post(
      `${config.PYTHON_API_URL}/tts`,
      { text, language, speed: speed || 1.0 },
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 60000
      }
    );

    // Return response
    res.json(successResponse(response.data, 'Audio generated successfully'));

  } catch (error) {
    console.error('❌ TTS Error:', error.message);
    
    const message = error.response?.data?.message || error.message || 'Speech generation failed';
    res.status(500).json(errorResponse(message, 500));
  }
});

module.exports = router;