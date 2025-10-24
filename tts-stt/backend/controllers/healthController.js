const axios = require('axios');
const APIResponse = require('../models/responseModel');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

const checkHealth = async (req, res) => {
  try {
    // Check Python service health
    const pythonHealthResponse = await axios.get(
      `${PYTHON_API_URL}/health`,
      { timeout: 5000 }
    );

    const healthStatus = {
      backend: {
        status: 'healthy',
        uptime: process.uptime(),
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      },
      python_service: {
        status: 'healthy',
        response_time: pythonHealthResponse.headers['x-response-time'],
        data: pythonHealthResponse.data
      },
      overall_status: 'healthy'
    };

    res.json(APIResponse.success(healthStatus, 'All services healthy'));

  } catch (error) {
    console.error('Health check failed:', error.message);

    const healthStatus = {
      backend: {
        status: 'healthy',
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
      },
      python_service: {
        status: 'unhealthy',
        error: error.message
      },
      overall_status: 'degraded'
    };

    res.status(503).json(
      APIResponse.error('Service degraded', healthStatus, 503)
    );
  }
};

module.exports = {
  checkHealth
};
