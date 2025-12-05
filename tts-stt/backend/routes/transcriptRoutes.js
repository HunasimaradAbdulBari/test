// tts-stt/backend/routes/transcriptRoutes.js
const express = require('express');
const {
  saveTranscript,
  getTranscripts,
  deleteTranscript,
} = require('../controllers/transcriptController');

const router = express.Router();

// POST /api/transcripts - Save a new transcript
router.post('/transcripts', saveTranscript);

// GET /api/transcripts - Get all transcripts (optionally filtered by language)
router.get('/transcripts', getTranscripts);

// DELETE /api/transcripts/:id - Delete a transcript
router.delete('/transcripts/:id', deleteTranscript);

module.exports = router;