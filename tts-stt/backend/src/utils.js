const fs = require('fs').promises;
const path = require('path');

// Delete file helper
async function deleteFile(filePath) {
  try {
    await fs.unlink(filePath);
    console.log(`✅ Deleted file: ${filePath}`);
    return true;
  } catch (error) {
    console.error(`❌ Error deleting file: ${filePath}`, error.message);
    return false;
  }
}

// Validate audio file
function validateAudioFile(file) {
  const allowedTypes = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/ogg'];
  
  if (!file) {
    return { valid: false, error: 'No file provided' };
  }
  
  if (!allowedTypes.includes(file.mimetype)) {
    return { valid: false, error: `Invalid file type: ${file.mimetype}` };
  }
  
  return { valid: true };
}

// Validate language
function validateLanguage(language, supportedLanguages) {
  if (!supportedLanguages.includes(language)) {
    return { valid: false, error: `Unsupported language: ${language}` };
  }
  return { valid: true };
}

// Validate text
function validateText(text) {
  if (!text || text.trim().length === 0) {
    return { valid: false, error: 'Text cannot be empty' };
  }
  
  if (text.length > 5000) {
    return { valid: false, error: 'Text exceeds 5000 characters' };
  }
  
  return { valid: true };
}

// Success response
function successResponse(data, message = 'Success') {
  return {
    success: true,
    message,
    data
  };
}

// Error response
function errorResponse(message, statusCode = 500) {
  return {
    success: false,
    message,
    statusCode
  };
}

module.exports = {
  deleteFile,
  validateAudioFile,
  validateLanguage,
  validateText,
  successResponse,
  errorResponse
};