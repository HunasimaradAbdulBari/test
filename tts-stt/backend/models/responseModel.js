class APIResponse {
  static success(data, message = 'Success') {
    return {
      success: true,
      message,
      data,
      timestamp: new Date().toISOString()
    };
  }

  static error(message, error = null, statusCode = 500) {
    const response = {
      success: false,
      error: message,
      timestamp: new Date().toISOString()
    };

    if (process.env.NODE_ENV === 'development' && error) {
      response.details = error;
    }

    return response;
  }

  static sttSuccess(text, language, confidence = null, duration = null) {
    return this.success({
      text,
      language,
      confidence,
      duration,
      type: 'transcription'
    }, 'Transcription completed successfully');
  }

  static ttsSuccess(audioUrl, language, text, metadata = {}) {
    return this.success({
      audio_url: audioUrl,
      audioUrl: audioUrl, // Fallback for frontend compatibility
      url: audioUrl, // Another fallback
      language,
      text,
      metadata,
      type: 'synthesis'
    }, 'Audio generated successfully');
  }
}

module.exports = APIResponse;
