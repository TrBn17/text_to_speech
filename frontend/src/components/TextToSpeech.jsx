import React, { useState, useRef } from 'react';
import { useTextToSpeech } from '../hooks/useApi';

const TextToSpeech = () => {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState('alloy');
  const [speed, setSpeed] = useState(1.0);
  const [provider, setProvider] = useState('openai');
  const audioRef = useRef(null);

  const { result, loading, error, audioUrl, generateSpeech, reset } = useTextToSpeech();

  const voices = {
    openai: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
    google: ['en-US-Neural2-A', 'en-US-Neural2-B', 'en-US-Wavenet-A'],
    gemini: ['default']
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!text.trim()) {
      alert('Please enter some text');
      return;
    }

    try {
      await generateSpeech({
        text: text.trim(),
        voice,
        speed,
        provider,
      });
    } catch (err) {
      console.error('TTS generation failed:', err);
    }
  };

  const handlePlayAudio = () => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play();
    }
  };

  const handleDownloadAudio = () => {
    if (audioUrl) {
      const link = document.createElement('a');
      link.href = audioUrl;
      link.download = `tts_${Date.now()}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleReset = () => {
    reset();
    setText('');
  };

  const sampleTexts = [
    "Hello, this is a sample text for text-to-speech conversion.",
    "Xin chào, đây là văn bản mẫu để chuyển đổi văn bản thành giọng nói.",
    "The quick brown fox jumps over the lazy dog.",
    "Artificial intelligence is transforming the way we work and live.",
    "Welcome to our text-to-speech demonstration. Please enjoy the audio output."
  ];

  return (
    <div className="text-to-speech">
      <h2>🎵 Text-to-Speech</h2>

      <form onSubmit={handleSubmit} className="tts-form">
        {/* Text Input */}
        <div className="form-group">
          <label htmlFor="text">Text to Convert:</label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter the text you want to convert to speech..."
            rows={6}
            required
          />

          {/* Sample Texts */}
          <div className="sample-texts">
            <label>Quick samples:</label>
            <div className="sample-buttons">
              {sampleTexts.map((sample, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setText(sample)}
                  className="sample-btn"
                >
                  Sample {index + 1}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="settings-grid">
          {/* Provider Selection */}
          <div className="form-group">
            <label htmlFor="provider">Provider:</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => {
                setProvider(e.target.value);
                setVoice(voices[e.target.value][0]); // Reset to first voice
              }}
            >
              <option value="openai">OpenAI</option>
              <option value="google">Google</option>
              <option value="gemini">Gemini</option>
            </select>
          </div>

          {/* Voice Selection */}
          <div className="form-group">
            <label htmlFor="voice">Voice:</label>
            <select
              id="voice"
              value={voice}
              onChange={(e) => setVoice(e.target.value)}
            >
              {voices[provider].map(v => (
                <option key={v} value={v}>
                  {v.charAt(0).toUpperCase() + v.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Speed Control */}
          <div className="form-group">
            <label htmlFor="speed">Speed ({speed}x):</label>
            <input
              id="speed"
              type="range"
              min="0.25"
              max="4"
              step="0.1"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
            />
            <div className="speed-labels">
              <span>0.25x</span>
              <span>1.0x</span>
              <span>4.0x</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="form-actions">
          <button
            type="submit"
            disabled={loading}
            className="generate-btn"
          >
            {loading ? '🔄 Converting...' : '🎵 Convert to Speech'}
          </button>

          <button
            type="button"
            onClick={handleReset}
            className="reset-btn"
          >
            🗑️ Reset
          </button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          ❌ Error: {error}
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="results-section">
          <h3>🎧 Audio Result</h3>

          {result.success ? (
            <div className="audio-result">
              {/* Audio Player */}
              {audioUrl && (
                <div className="audio-player">
                  <audio
                    ref={audioRef}
                    src={audioUrl}
                    controls
                    className="audio-element"
                  />

                  <div className="audio-controls">
                    <button
                      onClick={handlePlayAudio}
                      className="play-btn"
                    >
                      ▶️ Play Audio
                    </button>

                    <button
                      onClick={handleDownloadAudio}
                      className="download-btn"
                    >
                      💾 Download MP3
                    </button>
                  </div>
                </div>
              )}

              {/* Audio Info */}
              <div className="audio-info">
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Voice:</strong> {result.voice}
                  </div>
                  <div className="info-item">
                    <strong>Provider:</strong> {result.provider}
                  </div>
                  <div className="info-item">
                    <strong>Duration:</strong> {result.duration?.toFixed(1)}s
                  </div>
                  <div className="info-item">
                    <strong>Format:</strong> {result.audio_format?.toUpperCase()}
                  </div>
                </div>
              </div>

              {/* Text Display */}
              <div className="converted-text">
                <h4>📝 Converted Text:</h4>
                <p>{result.text}</p>
              </div>

              {/* Available Voices */}
              {result.available_voices && (
                <div className="available-voices">
                  <h4>🎭 Available Voices:</h4>
                  <pre>{JSON.stringify(result.available_voices, null, 2)}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="error-message">
              ❌ Conversion failed: {result.error}
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .text-to-speech {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }

        .tts-form {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin-bottom: 20px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }

        .form-group textarea,
        .form-group select,
        .form-group input {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .form-group textarea {
          resize: vertical;
          font-family: inherit;
        }

        .sample-texts {
          margin-top: 10px;
        }

        .sample-texts label {
          margin-bottom: 8px;
          font-size: 12px;
          color: #666;
        }

        .sample-buttons {
          display: flex;
          gap: 5px;
          flex-wrap: wrap;
        }

        .sample-btn {
          padding: 4px 8px;
          background: #e9ecef;
          border: 1px solid #ced4da;
          border-radius: 4px;
          cursor: pointer;
          font-size: 11px;
        }

        .sample-btn:hover {
          background: #dee2e6;
        }

        .settings-grid {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 20px;
          margin: 20px 0;
        }

        .speed-labels {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #666;
          margin-top: 5px;
        }

        .form-actions {
          display: flex;
          gap: 10px;
          justify-content: center;
          margin-top: 20px;
        }

        .generate-btn,
        .reset-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 4px;
          font-size: 16px;
          cursor: pointer;
          font-weight: bold;
        }

        .generate-btn {
          background: #28a745;
          color: white;
        }

        .generate-btn:hover:not(:disabled) {
          background: #218838;
        }

        .generate-btn:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .reset-btn {
          background: #6c757d;
          color: white;
        }

        .reset-btn:hover {
          background: #545b62;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          padding: 15px;
          border-radius: 4px;
          margin: 10px 0;
        }

        .results-section {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .audio-result {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .audio-player {
          text-align: center;
        }

        .audio-element {
          width: 100%;
          margin-bottom: 10px;
        }

        .audio-controls {
          display: flex;
          gap: 10px;
          justify-content: center;
        }

        .play-btn,
        .download-btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .play-btn {
          background: #007bff;
          color: white;
        }

        .play-btn:hover {
          background: #0056b3;
        }

        .download-btn {
          background: #28a745;
          color: white;
        }

        .download-btn:hover {
          background: #218838;
        }

        .audio-info {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 4px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
        }

        .info-item {
          padding: 5px 0;
        }

        .converted-text {
          background: #e7f3ff;
          padding: 15px;
          border-radius: 4px;
        }

        .converted-text p {
          margin: 10px 0 0 0;
          line-height: 1.5;
        }

        .available-voices {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 4px;
        }

        .available-voices pre {
          background: white;
          padding: 10px;
          border-radius: 4px;
          overflow-x: auto;
          font-size: 12px;
          margin: 10px 0 0 0;
        }

        @media (max-width: 768px) {
          .settings-grid {
            grid-template-columns: 1fr;
          }

          .info-grid {
            grid-template-columns: 1fr;
          }

          .audio-controls {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default TextToSpeech;