import React, { useState, useRef, useEffect } from 'react';
import { useTextToSpeech } from '../hooks/useApi';
import { useTTSModels } from '../hooks/useModels';
import { apiService } from '../services/api';
import env from '../config/environment';
import styles from '../styles/TextToSpeech.module.css';

const TextToSpeech = ({ generatedText }) => {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState(env.defaults.tts.voice);
  const [speed, setSpeed] = useState(env.defaults.tts.speed);
  const [provider, setProvider] = useState(env.defaults.tts.provider);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // NotebookLM states
  const [activeTab, setActiveTab] = useState('tts');
  const [isGeneratingNotebook, setIsGeneratingNotebook] = useState(false);
  const [notebookResult, setNotebookResult] = useState(null);
  const [notebookError, setNotebookError] = useState(null);
  const [cacheKey, setCacheKey] = useState('latest');

  // Advanced options
  const [model, setModel] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [instructions, setInstructions] = useState('');
  const [responseFormat, setResponseFormat] = useState('mp3');
  const [languageCode, setLanguageCode] = useState('en-US');

  const audioRef = useRef(null);

  const { result, loading, error, audioUrl, generateSpeech, reset } = useTextToSpeech();
  const { models: apiTtsModels, voices: apiVoices, loading: modelsLoading, error: modelsError } = useTTSModels();

  // Ensure apiVoices is always an object
  const safeApiVoices = apiVoices || { openai: [], google: [] };

  // Auto-populate text from generated text
  useEffect(() => {
    if (generatedText && generatedText.trim()) {
      setText(generatedText);
    }
  }, [generatedText]);

  // Filter models by current provider
  const getModelsForProvider = () => {
    if (!apiTtsModels || apiTtsModels.length === 0) return [];
    return apiTtsModels.filter(modelOption => {
      if (provider === 'openai') {
        return modelOption.provider === 'openai_tts';
      } else if (provider === 'google') {
        return modelOption.provider === 'google_tts' || modelOption.provider === 'gemini_tts';
      }
      return false;
    });
  };

  // Get voices for current provider
  const getVoicesForProvider = () => {
    if (provider === 'openai') {
      const openaiVoices = safeApiVoices?.openai || ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];
      // Ensure all voices are strings
      return openaiVoices.map(voice => 
        typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
      );
    } else if (provider === 'google') {
      // Handle both string array and object array
      const googleVoices = safeApiVoices?.google || [
        'natural_control', 'expressive', 'conversational',
        'en-US-Neural2-A', 'en-US-Neural2-B', 'en-US-Wavenet-A', 'en-US-Standard-A'
      ];
      // If it's array of objects, extract the id/value
      return googleVoices.map(voice => 
        typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
      );
    }
    return [];
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

  // NotebookLM functions
  const handleGenerateNotebookAudio = async () => {
    setIsGeneratingNotebook(true);
    setNotebookError(null);
    setNotebookResult(null);

    try {
      console.log('🚀 Starting NotebookLM audio generation...');
      
      const response = await apiService.generateNotebookLMAudio({ cache_key: cacheKey });
      
      console.log('✅ NotebookLM generation completed:', response);
      setNotebookResult(response);
      
    } catch (err) {
      console.error('❌ NotebookLM generation failed:', err);
      setNotebookError(err.message || 'Failed to generate audio');
    } finally {
      setIsGeneratingNotebook(false);
    }
  };

  const formatProcessingTime = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${remainingSeconds}s`;
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
      <h2 className={styles.title}>🎙️ Text-to-Conversation</h2>

      {/* Tab Navigation */}
      <div className={styles.card}>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid #e2e8f0' }}>
          <button
            onClick={() => setActiveTab('tts')}
            style={{
              background: activeTab === 'tts' ? '#3b82f6' : 'transparent',
              color: activeTab === 'tts' ? 'white' : '#6b7280',
              border: 'none',
              padding: '0.75rem 1rem',
              borderRadius: '6px 6px 0 0',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.875rem',
              transition: 'all 0.2s ease'
            }}
          >
            🎵 Text-to-Speech
          </button>
          <button
            onClick={() => setActiveTab('notebooklm')}
            style={{
              background: activeTab === 'notebooklm' ? '#8b5cf6' : 'transparent',
              color: activeTab === 'notebooklm' ? 'white' : '#6b7280',
              border: 'none',
              padding: '0.75rem 1rem',
              borderRadius: '6px 6px 0 0',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.875rem',
              transition: 'all 0.2s ease'
            }}
          >
            🎙️ Conversation Audio
          </button>
        </div>

      {/* TTS Tab Content */}
      {activeTab === 'tts' && (
        <>
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Text Input */}
          <div className={styles.formGroup}>
            <label htmlFor="text">
              Text to Convert
              {generatedText && <span style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: '400' }}> (Auto-populated from Text Generator)</span>}
            </label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter the text you want to convert to speech..."
              rows={6}
              required
              className={styles.textarea}
            />

            {/* Sample Texts */}
            <div style={{ marginTop: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem' }}>Quick samples:</div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {sampleTexts.map((sample, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setText(sample)}
                    style={{
                      background: '#f3f4f6',
                      border: '1px solid #d1d5db',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
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
            <div className={styles.settingItem}>
              <label htmlFor="provider">Provider</label>
              <select
                id="provider"
                value={provider}
                onChange={(e) => {
                  const newProvider = e.target.value;
                  setProvider(newProvider);
                  // Reset to first voice for new provider
                  let providerVoices = [];
                  if (newProvider === 'openai') {
                    const openaiVoices = safeApiVoices?.openai || ['alloy'];
                    providerVoices = openaiVoices.map(voice =>
                      typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
                    );
                  } else if (newProvider === 'google') {
                    const googleVoices = safeApiVoices?.google || ['natural_control'];
                    providerVoices = googleVoices.map(voice =>
                      typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
                    );
                  }
                  if (providerVoices.length > 0) {
                    setVoice(providerVoices[0]);
                  }
                }}
                className={styles.select}
              >
                <option value="openai">OpenAI TTS</option>
                <option value="google">Google (Gemini + Cloud TTS)</option>
              </select>
            </div>

            {/* Voice Selection */}
            <div className={styles.settingItem}>
              <label htmlFor="voice">Voice</label>
              <select
                id="voice"
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className={styles.select}
              >
                {getVoicesForProvider().map((v, index) => {
                  const voiceValue = typeof v === 'string' ? v : (v?.id || v?.value || v?.name || `voice-${index}`);
                  const voiceLabel = typeof v === 'string' ? v.charAt(0).toUpperCase() + v.slice(1) : (v?.label || v?.name || voiceValue);
                  return (
                    <option key={voiceValue} value={voiceValue}>
                      {voiceLabel}
                  </option>
                );
              })}
            </select>
          </div>

            {/* Speed Control */}
            <div className={styles.settingItem}>
              <label>Speed</label>
              <div className={styles.sliderContainer}>
                <input
                  id="speed"
                  type="range"
                  min="0.25"
                  max="4"
                  step="0.1"
                  value={speed}
                  onChange={(e) => setSpeed(parseFloat(e.target.value))}
                  className={styles.slider}
                />
                <span className={styles.sliderValue}>{speed}x</span>
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
                <select
                  id="model"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="form-input form-select"
                  disabled={modelsLoading}
                >
                  <option value="">Default Model</option>
                  {getModelsForProvider().map((modelOption) => (
                    <option key={modelOption.value} value={modelOption.value}>
                      {modelOption.label}
                    </option>
                  ))}
                </select>
                <small className="text-secondary">
                  {modelsLoading ? 'Loading models...' : 'Leave empty for default model'}
                  {modelsError && <span className="text-danger"> - Error loading models</span>}
                </small>
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
          <div className={styles.buttonGroup}>
            <button
              type="submit"
              disabled={loading}
              className={styles.generateButton}
            >
              {loading ? (
                <>
                  <span className={styles.loadingSpinner}></span>
                  Converting...
                </>
              ) : (
                '🎵 Convert to Speech'
              )}
            </button>

            <button
              type="button"
              onClick={handleReset}
              className={styles.resetButton}
            >
              🗑️ Reset
            </button>
          </div>
        </form>

        {/* Error Display */}
        {error && (
          <div className={styles.error}>
            ❌ Error: {error}
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className={styles.resultCard}>
            <h3 className={styles.resultTitle}>🎧 Audio Result</h3>

            {result.success ? (
              <div>
                {/* Audio Player */}
                {audioUrl && (
                  <div>
                    <audio
                      ref={audioRef}
                      src={audioUrl}
                      controls
                      className={styles.audioPlayer}
                    />

                    <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={handlePlayAudio}
                        className={styles.downloadButton}
                      >
                        ▶️ Play Audio
                      </button>

                      <button
                        onClick={handleDownloadAudio}
                        className={styles.downloadButton}
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
        </>
      )}

        {/* NotebookLM Tab Content */}
        {activeTab === 'notebooklm' && (
          <form onSubmit={(e) => { e.preventDefault(); handleGenerateNotebookAudio(); }} className={styles.form}>
            <div className={styles.formGroup}>
              <label htmlFor="cacheSource">📦 Content Source</label>
              <select
                id="cacheSource"
                value={cacheKey}
                onChange={(e) => setCacheKey(e.target.value)}
                className={styles.select}
                disabled={isGeneratingNotebook}
              >
                <option value="latest">🕒 Latest Text Generation</option>
                <option value="text_generation_1758614659">📄 text_generation_1758614659 (5353 chars)</option>
                <option value="text_generation_1758612529">📄 text_generation_1758612529 (3459 chars)</option>
                <option value="text_generation_1758612492">📄 text_generation_1758612492 (3506 chars)</option>
              </select>
              <small style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem', display: 'block' }}>
                Generate conversation audio using NotebookLM automation from cached content
              </small>
            </div>

            {/* Generate Button */}
            <div className={styles.buttonGroup}>
              <button
                type="submit"
                disabled={isGeneratingNotebook}
                className={styles.notebookButton}
              >
                {isGeneratingNotebook ? (
                  <>
                    <span className={styles.loadingSpinner}></span>
                    Generating Audio... (This may take 5-15 minutes)
                  </>
                ) : (
                  '🎙️ Generate Conversation Audio'
                )}
              </button>
            </div>

            {/* Warning */}
            <div style={{
              background: '#fff7ed',
              border: '1px solid #fed7aa',
              color: '#c2410c',
              padding: '0.75rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              marginTop: '1rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.5rem'
            }}>
              <span>⚠️</span>
              <div>
                <strong>Important:</strong> This process will open a browser window 
              </div>
            </div>
          </form>
        )}
      </div>

      {/* Loading Progress */}
      {isGeneratingNotebook && (
        <div className={styles.resultCard}>
          <h3 className={styles.resultTitle}>🤖 Generating Audio...</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Browser automation in progress... Please wait patiently.
          </p>
        </div>
      )}

      {/* Error Display */}
      {notebookError && (
        <div className={styles.error}>
          ❌ Error: {notebookError}
        </div>
      )}

      {/* Success Result */}
      {notebookResult && notebookResult.success && (
        <div className={styles.success}>
          <strong>✅ Audio Generated Successfully!</strong>
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
            <div>🎵 Audio File: <code>{notebookResult.audio_url}</code></div>
            <div style={{ marginTop: '0.25rem' }}>⏱️ Processing Time: {formatProcessingTime(notebookResult.processing_time)}</div>
            {notebookResult.cache_info && (
              <div style={{ marginTop: '0.25rem' }}>📦 Source: {notebookResult.cache_info.cache_key}</div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default TextToSpeech;