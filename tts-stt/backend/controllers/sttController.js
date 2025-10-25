const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const transcribeAudio = async (req, res, next) => {
  let tempFilePath = null;
  
  try {
    const { language = 'en' } = req.body;
    
    console.log('🎙️ [Backend] STT Request received');
    console.log('📋 Body:', req.body);
    console.log('📋 File present:', !!req.file);
    
    if (!req.file) {
      console.error('❌ No file in request');
      return res.status(400).json(
        APIResponse.error('No audio file provided')
      );
    }

    tempFilePath = req.file.path;
    console.log(`📁 File info:`, {
      filename: req.file.filename,
      mimetype: req.file.mimetype,
      size: req.file.size,
      path: tempFilePath,
      language: language
    });

    // Verify file exists
    if (!fs.existsSync(tempFilePath)) {
      throw new Error('Uploaded file not found');
    }

    // Create form data for Python API
    const formData = new FormData();
    
    // IMPORTANT: Create a read stream from the file
    const fileStream = fs.createReadStream(tempFilePath);
    
    // Append with proper options
    formData.append('audio', fileStream, {
      filename: req.file.originalname || 'recording.webm',
      contentType: req.file.mimetype || 'audio/webm',
      knownLength: req.file.size
    });
    
    formData.append('language', language);

    console.log(`🔗 Forwarding to: ${PYTHON_API_URL}/stt`);
    console.log(`📦 FormData headers:`, formData.getHeaders());

    // Forward to Python Flask API
    const response = await axios.post(
      `${PYTHON_API_URL}/stt`,
      formData,
      {
        headers: {
          ...formData.getHeaders(),
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        timeout: 60000, // 60 seconds for STT
      }
    );

    console.log('✅ [Backend] Python STT response:', response.data);

    const { text, confidence, duration } = response.data;
    res.json(APIResponse.sttSuccess(text, language, confidence, duration));

  } catch (error) {
    console.error('❌ [Backend] STT Error:', error.message);
    
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      return res.status(error.response.status).json(
        APIResponse.error(error.response.data?.error || 'Python service error')
      );
    }
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json(
        APIResponse.error('Speech service unavailable. Please ensure Python service is running on port 8000.')
      );
    }
    
    res.status(500).json(APIResponse.error('Internal server error: ' + error.message));
    
  } finally {
    // Clean up uploaded file
    if (tempFilePath && fs.existsSync(tempFilePath)) {
      try {
        fs.unlinkSync(tempFilePath);
        console.log('🗑️ Cleaned up temp file:', tempFilePath);
      } catch (cleanupError) {
        console.error('⚠️ Failed to cleanup temp file:', cleanupError.message);
      }
    }
  }
};

module.exports = { transcribeAudio };