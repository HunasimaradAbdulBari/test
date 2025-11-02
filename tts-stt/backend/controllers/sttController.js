const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const transcribeAudio = async (req, res, next) => {
  let tempFilePath = null;
  
  try {
    console.log('🎙️ [Backend STT] Request with AUTO-DETECTION');
    
    if (!req.file) {
      console.error('❌ No file in request');
      return res.status(400).json(
        APIResponse.error('No audio file provided')
      );
    }

    tempFilePath = req.file.path;
    console.log(`📁 File info:`, {
      filename: req.file.filename,
      originalname: req.file.originalname,
      mimetype: req.file.mimetype,
      size: req.file.size,
      path: tempFilePath
    });
    console.log('   (Language will be auto-detected)');

    // Verify file exists
    if (!fs.existsSync(tempFilePath)) {
      throw new Error('Uploaded file not found');
    }

    // Read file completely before sending
    const fileBuffer = fs.readFileSync(tempFilePath);
    console.log(`📦 File buffer size: ${fileBuffer.length} bytes`);

    // Create form data - NO LANGUAGE PARAMETER
    const formData = new FormData();
    formData.append('audio', fileBuffer, {
      filename: 'recording.webm',
      contentType: 'audio/webm',
    });
    // Language parameter removed - auto-detection

    console.log(`🔗 Forwarding to: ${PYTHON_API_URL}/stt`);

    // Forward to Python Flask API
    const response = await axios.post(
      `${PYTHON_API_URL}/stt`,
      formData,
      {
        headers: formData.getHeaders(),
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        timeout: 60000,
      }
    );

    console.log('✅ [Backend STT] Python response received');
    console.log(`   Detected: ${response.data.detected_language?.name || 'Unknown'}`);
    console.log(`   Text: ${response.data.text}`);

    const { text, detected_language, metadata } = response.data;
    
    // Return comprehensive response
    res.json({
      success: true,
      message: 'Transcription completed with auto-detected language',
      data: {
        text,
        transcription: text,
        detected_language,
        confidence: metadata?.confidence || detected_language?.confidence,
        duration: metadata?.duration,
        metadata: {
          ...metadata,
          auto_detected: true
        }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ [Backend STT] Error:', error.message);
    
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      return res.status(error.response.status).json(
        APIResponse.error(
          error.response.data?.error || 
          error.response.data?.detail || 
          'Python service error'
        )
      );
    }
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json(
        APIResponse.error('Speech service unavailable')
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
        console.error('⚠️ Failed to cleanup:', cleanupError.message);
      }
    }
  }
};

module.exports = { transcribeAudio };