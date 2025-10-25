const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const transcribeAudio = async (req, res, next) => {
  let tempFilePath = null;
  
  try {
    const { language = 'en' } = req.body;
    
    if (!req.file) {
      return res.status(400).json(
        APIResponse.error('No audio file provided')
      );
    }

    tempFilePath = req.file.path;
    console.log(`🎙️ [Backend] STT Request:`, {
      filename: req.file.filename,
      language,
      path: tempFilePath,
      size: req.file.size
    });

    // Create form data for Python API
    const formData = new FormData();
    formData.append('audio', fs.createReadStream(tempFilePath), {
      filename: req.file.filename,
      contentType: req.file.mimetype
    });
    formData.append('language', language);

    console.log(`🔗 Forwarding to Python API: ${PYTHON_API_URL}/api/v1/stt`);

    // Forward to Python Flask API
    const response = await axios.post(
      `${PYTHON_API_URL}/api/v1/stt`,
      formData,
      {
        headers: {
          ...formData.getHeaders(),
        },
        timeout: 30000, // 30 seconds
      }
    );

    console.log('✅ [Backend] Python STT response:', response.data);

    const { text, confidence, duration } = response.data;
    res.json(APIResponse.sttSuccess(text, language, confidence, duration));

  } catch (error) {
    console.error('❌ [Backend] STT Error:', error.message);
    
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
