const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const config = require('./config');
const routes = require('./routes');

// Create Express app
const app = express();

// Ensure upload directory exists
if (!fs.existsSync(config.UPLOAD_DIR)) {
  fs.mkdirSync(config.UPLOAD_DIR, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, config.UPLOAD_DIR);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'audio-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: config.MAX_FILE_SIZE },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/ogg'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only audio files allowed.'));
    }
  }
});

// CORS Configuration - MUST BE FIRST
app.use(cors({
  origin: config.CORS_ORIGIN,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Body parsers - for JSON and URL-encoded data
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'Speech Backend API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/api/health',
      stt: 'POST /api/stt',
      tts: 'POST /api/tts'
    }
  });
});

// Health check route (no multer needed)
app.get('/api/health', routes);

// STT route - WITH multer middleware for file upload
app.post('/api/stt', upload.single('audio'), async (req, res, next) => {
  // The file is now available in req.file
  // Forward to the routes handler
  routes(req, res, next);
});

// TTS route - NO multer needed (just JSON)
app.post('/api/tts', routes);

// Mount other API routes (without multer)
app.use('/api', routes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('❌ Error:', err.message);
  
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        message: 'File too large. Maximum size is 10MB'
      });
    }
  }
  
  res.status(500).json({
    success: false,
    message: err.message || 'Internal server error'
  });
});

// Start server
const PORT = config.PORT;
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log('');
  console.log('🚀 ============================================');
  console.log(`✅ Express Backend Server Started`);
  console.log(`📡 Port: ${PORT}`);
  console.log(`🌍 Environment: ${config.NODE_ENV}`);
  console.log(`🔗 Python API: ${config.PYTHON_API_URL}`);
  console.log(`🎯 Local: http://localhost:${PORT}`);
  console.log(`🎯 Network: http://0.0.0.0:${PORT}`);
  console.log('🚀 ============================================');
  console.log('');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('👋 SIGTERM received. Shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('👋 SIGINT received. Shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});