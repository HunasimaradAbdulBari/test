const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // Multer errors
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        error: 'File too large',
        message: 'Audio file exceeds maximum size limit'
      });
    }
    return res.status(400).json({
      error: 'File upload error',
      message: err.message
    });
  }

  // Custom errors
  if (err.status) {
    return res.status(err.status).json({
      error: err.message || 'Bad Request'
    });
  }

  // Default server error
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
};

module.exports = errorHandler;
