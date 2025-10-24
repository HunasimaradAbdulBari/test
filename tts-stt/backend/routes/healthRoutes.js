const express = require('express');
const { checkHealth } = require('../controllers/healthController');

const router = express.Router();

// GET /api/health - Health check
router.get('/health', checkHealth);

module.exports = router;
