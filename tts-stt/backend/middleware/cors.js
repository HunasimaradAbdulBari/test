const cors = require('cors');

const corsOptions = {
  origin: [
    'http://localhost:3000', // Next.js development
    'https://your-frontend.vercel.app', // Production frontend
    'https://your-frontend.onrender.com', // Render deployment
  ],
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Origin',
    'X-Requested-With',
    'Content-Type',
    'Accept',
    'Authorization',
    'Cache-Control'
  ],
};

module.exports = cors(corsOptions);
