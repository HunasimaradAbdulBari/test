const express = require('express');
const { generateSpeech } = require('../controllers/ttsController');

const router = express.Router();

// POST /api/tts - Text to Speech
router.post('/tts', generateSpeech);

module.exports = router;
