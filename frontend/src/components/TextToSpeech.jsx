import React, { useState, useRef } from 'react';
import { useTextToSpeech } from '../hooks/useApi';
import env from '../config/environment';
import styles from '../styles/TextToSpeech.module.css';

const TextToSpeech = () => {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState(env.defaults.tts.voice);
  const [speed, setSpeed] = useState(env.defaults.tts.speed);
  const [provider, setProvider] = useState(env.defaults.tts.provider);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Advanced options
  const [model, setModel] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [instructions, setInstructions] = useState('');
  const [responseFormat, setResponseFormat] = useState('mp3');
  const [languageCode, setLanguageCode] = useState('en-US');

  const audioRef = useRef(null);

  const { result, loading, error, audioUrl, generateSpeech, reset } = useTextToSpeech();

  const voices = {
    openai: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
    google: [
      // Gemini Native TTS
      'natural_control', 'expressive', 'conversational',
      // Google Cloud TTS
      'en-US-Neural2-A', 'en-US-Neural2-B', 'en-US-Wavenet-A', 'en-US-Standard-A'
    ]
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
        model: model || null,
        system_prompt: systemPrompt,
        instructions: instructions,
        response_format: responseFormat,
        language_code: languageCode,
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
    <div className={styles.textToSpeech}>
      <h2 className={styles.title}>🎵 Text-to-Speech</h2>

      <form onSubmit={handleSubmit} className={`card ${styles.form}`}>
        {/* Text Input */}
        <div className="form-group">
          <label htmlFor="text" className="form-label">Text to Convert:</label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter the text you want to convert to speech..."
            rows={6}
            required
            className="form-input form-textarea"
          />

          {/* Sample Texts */}
          <div className={styles.sampleTexts}>
            <label className="text-sm text-secondary">Quick samples:</label>
            <div className={styles.sampleButtons}>
              {sampleTexts.map((sample, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setText(sample)}
                  className={styles.sampleBtn}
                >
                  Sample {index + 1}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className={styles.settingsGrid}>
          {/* Provider Selection */}
          <div className="form-group">
            <label htmlFor="provider" className="form-label">Provider:</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => {
                setProvider(e.target.value);
                setVoice(voices[e.target.value][0]); // Reset to first voice
              }}
              className="form-input form-select"
            >
              <option value="openai">OpenAI TTS</option>
              <option value="google">Google (Gemini + Cloud TTS)</option>
            </select>
          </div>

          {/* Voice Selection */}
          <div className="form-group">
            <label htmlFor="voice" className="form-label">Voice:</label>
            <select
              id="voice"
              value={voice}
              onChange={(e) => setVoice(e.target.value)}
              className="form-input form-select"
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
            <label htmlFor="speed" className="form-label">Speed ({speed}x):</label>
            <input
              id="speed"
              type="range"
              min="0.25"
              max="4"
              step="0.1"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="form-range"
            />
            <div className={styles.speedLabels}>
              <span>0.25x</span>
              <span>1.0x</span>
              <span>4.0x</span>
            </div>
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <div className="form-group">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="btn btn-outline btn-sm"
          >
            {showAdvanced ? '🔽 Hide Advanced Options' : '🔧 Show Advanced Options'}
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className={`${styles.advancedOptions} card`}>
            <h4>🔧 Advanced Options</h4>

            <div className={styles.settingsGrid}>
              {/* Model Selection */}
              <div className="form-group">
                <label htmlFor="model" className="form-label">Model (optional):</label>
                <input
                  id="model"
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder={provider === 'openai' ? 'tts-1 or tts-1-hd' : 'gemini-2.5-flash-preview-tts'}
                  className="form-input"
                />
                <small className="text-secondary">Leave empty for default model</small>
              </div>

              {/* Response Format */}
              <div className="form-group">
                <label htmlFor="responseFormat" className="form-label">Audio Format:</label>
                <select
                  id="responseFormat"
                  value={responseFormat}
                  onChange={(e) => setResponseFormat(e.target.value)}
                  className="form-input form-select"
                >
                  <option value="mp3">MP3</option>
                  <option value="wav">WAV</option>
                  <option value="opus">OPUS</option>
                  <option value="aac">AAC</option>
                  <option value="flac">FLAC</option>
                  <option value="pcm">PCM</option>
                </select>
              </div>

              {/* Language Code */}
              <div className="form-group">
                <label htmlFor="languageCode" className="form-label">Language Code:</label>
                <select
                  id="languageCode"
                  value={languageCode}
                  onChange={(e) => setLanguageCode(e.target.value)}
                  className="form-input form-select"
                >
                  <option value="en-US">English (US)</option>
                  <option value="en-GB">English (UK)</option>
                  <option value="vi-VN">Vietnamese</option>
                  <option value="ja-JP">Japanese</option>
                  <option value="ko-KR">Korean</option>
                  <option value="zh-CN">Chinese (Simplified)</option>
                  <option value="fr-FR">French</option>
                  <option value="de-DE">German</option>
                  <option value="es-ES">Spanish</option>
                </select>
              </div>
            </div>

            {/* Provider-specific options */}
            {provider === 'openai' && (
              <div className="form-group">
                <label htmlFor="instructions" className="form-label">Instructions (OpenAI):</label>
                <textarea
                  id="instructions"
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Additional instructions for voice style..."
                  rows={2}
                  className="form-input form-textarea"
                />
                <small className="text-secondary">Custom instructions for OpenAI TTS voice style</small>
              </div>
            )}

            {(provider === 'gemini' || provider === 'google') && (
              <div className="form-group">
                <label htmlFor="systemPrompt" className="form-label">System Prompt (Gemini):</label>
                <textarea
                  id="systemPrompt"
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  placeholder="System prompt for TTS style control..."
                  rows={2}
                  className="form-input form-textarea"
                />
                <small className="text-secondary">System prompt for Gemini TTS style control</small>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-success btn-lg"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Converting...
              </>
            ) : (
              '🎵 Convert to Speech'
            )}
          </button>

          <button
            type="button"
            onClick={handleReset}
            className="btn btn-secondary"
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
                  {result.model && (
                    <div className="info-item">
                      <strong>Model:</strong> {result.model}
                    </div>
                  )}
                  {result.speed && result.speed !== 1.0 && (
                    <div className="info-item">
                      <strong>Speed:</strong> {result.speed}x
                    </div>
                  )}
                  {result.language_code && result.language_code !== 'en-US' && (
                    <div className="info-item">
                      <strong>Language:</strong> {result.language_code}
                    </div>
                  )}
                </div>

                {/* Advanced parameters used */}
                {(result.instructions || result.system_prompt || result.prompt_prefix) && (
                  <div className={styles.usedParams}>
                    <h5>📋 Parameters Used:</h5>
                    {result.instructions && (
                      <div className="param-item">
                        <strong>Instructions:</strong> {result.instructions}
                      </div>
                    )}
                    {result.system_prompt && (
                      <div className="param-item">
                        <strong>System Prompt:</strong> {result.system_prompt}
                      </div>
                    )}
                    {result.prompt_prefix && (
                      <div className="param-item">
                        <strong>Prompt Prefix:</strong> {result.prompt_prefix}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Text Display */}
              <div className={styles.convertedText}>
                <h4>📝 Converted Text:</h4>
                <p>{result.text}</p>
              </div>

              {/* Available Voices */}
              {result.available_voices && (
                <div className={styles.availableVoices}>
                  <h4>🎭 Available Voices:</h4>
                  <pre>{JSON.stringify(result.available_voices, null, 2)}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="alert alert-error">
              ❌ Conversion failed: {result.error}
            </div>
          )}
        </div>
      )}

    </div>
  );
};

export default TextToSpeech;