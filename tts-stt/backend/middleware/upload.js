const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
  console.log('📁 Created uploads directory:', uploadsDir);
}

// Storage configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const fileName = 'audio-' + uniqueSuffix + path.extname(file.originalname);
    console.log('💾 Saving file as:', fileName);
    cb(null, fileName);
  }
});

// File filter
const fileFilter = (req, file, cb) => {
  console.log('🔍 Checking file type:', file.mimetype);
  const allowedTypes = [
    'audio/webm',
    'audio/wav', 
    'audio/mp3',
    'audio/mpeg',
    'audio/m4a',
    'audio/ogg'
  ];
  
  if (allowedTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    console.error('❌ Invalid file type:', file.mimetype);
    cb(new Error('Invalid file type. Only audio files are allowed.'), false);
  }
};

const upload = multer({
  storage: storage,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10485760, // 10MB
  },
  fileFilter: fileFilter
});

module.exports = upload;
