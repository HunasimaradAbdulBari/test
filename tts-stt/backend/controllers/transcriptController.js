// tts-stt/backend/controllers/transcriptController.js
const transcriptStore = require('../models/transcriptModel');
const APIResponse = require('../models/responseModel');

/**
 * Save a new transcript
 * POST /api/transcripts
 */
const saveTranscript = async (req, res) => {
  try {
    const { text, language, timestamp } = req.body;

    // Validate input
    if (!text || text.trim().length === 0) {
      return res.status(400).json(
        APIResponse.error('Text is required')
      );
    }

    if (!language) {
      return res.status(400).json(
        APIResponse.error('Language is required')
      );
    }

    // Save transcript
    const transcript = transcriptStore.add(text.trim(), language, timestamp);

    console.log(`📝 Saved transcript: ${transcript.id} (${language})`);

    res.json(APIResponse.success(transcript, 'Transcript saved successfully'));

  } catch (error) {
    console.error('Error saving transcript:', error);
    res.status(500).json(APIResponse.error('Failed to save transcript'));
  }
};

/**
 * Get all transcripts
 * GET /api/transcripts
 */
const getTranscripts = async (req, res) => {
  try {
    const { language } = req.query;

    let transcripts;
    
    if (language) {
      transcripts = transcriptStore.getByLanguage(language);
    } else {
      transcripts = transcriptStore.getAll();
    }

    res.json(APIResponse.success({
      transcripts,
      count: transcripts.length
    }, 'Transcripts retrieved successfully'));

  } catch (error) {
    console.error('Error getting transcripts:', error);
    res.status(500).json(APIResponse.error('Failed to get transcripts'));
  }
};

/**
 * Delete a transcript
 * DELETE /api/transcripts/:id
 */
const deleteTranscript = async (req, res) => {
  try {
    const { id } = req.params;

    const deleted = transcriptStore.delete(id);

    if (!deleted) {
      return res.status(404).json(
        APIResponse.error('Transcript not found')
      );
    }

    res.json(APIResponse.success(null, 'Transcript deleted successfully'));

  } catch (error) {
    console.error('Error deleting transcript:', error);
    res.status(500).json(APIResponse.error('Failed to delete transcript'));
  }
};

module.exports = {
  saveTranscript,
  getTranscripts,
  deleteTranscript,
};