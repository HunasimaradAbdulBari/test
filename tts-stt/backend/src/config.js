require('dotenv').config();

module.exports = {
  // Server
  PORT: process.env.PORT || 5000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  
  // Python API
  PYTHON_API_URL: process.env.PYTHON_API_URL || 'http://localhost:8000',
  
  // CORS
  CORS_ORIGIN: process.env.CORS_ORIGIN || 'http://localhost:3000',
  
  // File Upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  UPLOAD_DIR: './uploads',
  
  // Supported Languages
  SUPPORTED_LANGUAGES: ['en', 'hi', 'kn', 'ur']
};