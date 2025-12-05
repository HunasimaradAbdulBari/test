// tts-stt/backend/models/transcriptModel.js
// Simple in-memory storage for transcripts

class TranscriptStore {
  constructor() {
    // Store transcripts in memory (will be lost on server restart)
    // For production, use a database like MongoDB, PostgreSQL, etc.
    this.transcripts = [];
    this.maxTranscripts = 100; // Keep only last 100 transcripts
  }

  /**
   * Add a new transcript
   */
  add(text, language, timestamp) {
    const transcript = {
      id: Date.now().toString(),
      text,
      language,
      timestamp: timestamp || new Date().toISOString(),
      createdAt: new Date().toISOString(),
    };

    this.transcripts.unshift(transcript); // Add to beginning

    // Limit storage size
    if (this.transcripts.length > this.maxTranscripts) {
      this.transcripts = this.transcripts.slice(0, this.maxTranscripts);
    }

    return transcript;
  }

  /**
   * Get all transcripts
   */
  getAll() {
    return this.transcripts;
  }

  /**
   * Get transcripts by language
   */
  getByLanguage(language) {
    return this.transcripts.filter(t => t.language === language);
  }

  /**
   * Get transcript by ID
   */
  getById(id) {
    return this.transcripts.find(t => t.id === id);
  }

  /**
   * Delete transcript by ID
   */
  delete(id) {
    const index = this.transcripts.findIndex(t => t.id === id);
    if (index !== -1) {
      this.transcripts.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * Clear all transcripts
   */
  clear() {
    this.transcripts = [];
  }
}

// Create a single instance (singleton)
const transcriptStore = new TranscriptStore();

module.exports = transcriptStore;