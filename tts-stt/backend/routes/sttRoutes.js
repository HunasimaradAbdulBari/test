const express = require('express');
const upload = require('../middleware/upload');
const { transcribeAudio } = require('../controllers/sttController');

const router = express.Router();

// POST /api/stt - Speech to Text
router.post('/stt', upload.single('audio'), transcribeAudio);

module.exports = router;
