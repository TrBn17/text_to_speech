import React, { useState, useRef, useEffect } from 'react';
import { useTextToSpeech } from '../hooks/useApi';
import { useTTSModels } from '../hooks/useModels';
import { apiService } from '../services/api';
import env from '../config/environment';
import Sidebar from './common/Sidebar';
import { SettingsSection } from './common/SettingsSection';
import { Select, Textarea, Slider } from './common/FormControls';
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
  const [customText, setCustomText] = useState(''); // Custom text for NotebookLM

  // Advanced options
  const [model, setModel] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [instructions, setInstructions] = useState('');
  const [responseFormat, setResponseFormat] = useState('mp3');
  const [languageCode, setLanguageCode] = useState('en-US');

  const audioRef = useRef(null);

  const { result, loading, error, audioUrl, generateSpeech, reset } = useTextToSpeech();
  const { models: apiTtsModels, voices: apiVoices, loading: modelsLoading } = useTTSModels();

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
    if (!customText.trim()) {
      setNotebookError('Please enter some text to convert to audio');
      return;
    }

    setIsGeneratingNotebook(true);
    setNotebookError(null);
    setNotebookResult(null);

    try {
      console.log('🚀 Starting NotebookLM audio generation...');
      console.log('📝 Using custom text (length:', customText.trim().length, 'chars)');
      
      const response = await apiService.generateNotebookLMAudio({
        custom_text: customText.trim()
      });
      
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
      {/* Left Sidebar */}
      <Sidebar title="🎙️ Audio Settings">
        {/* Tab Navigation */}
        <SettingsSection title="">
          <div className={styles.tabNavigation}>
            <button
              onClick={() => setActiveTab('tts')}
              className={`${styles.tabButton} ${activeTab === 'tts' ? styles.active : ''}`}
            >
              🎵 Text-to-Speech
            </button>
            <button
              onClick={() => setActiveTab('notebooklm')}
              className={`${styles.tabButton} ${activeTab === 'notebooklm' ? styles.active : ''}`}
            >
              🎙️ Conversation Audio
            </button>
          </div>
        </SettingsSection>

          {/* Settings based on active tab */}
          {activeTab === 'tts' && (
            <>
              <SettingsSection title="Provider Configuration">
                <div className={styles.settingGroup}>
                  <label htmlFor="provider">Provider</label>
                  <Select
                    value={provider}
                    onChange={(e) => {
                      const newProvider = e.target.value;
                      setProvider(newProvider);
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
                    options={[
                      { value: "openai", label: "OpenAI TTS" },
                      { value: "google", label: "Google (Gemini + Cloud TTS)" }
                    ]}
                  />
                </div>

                <div className={styles.settingGroup}>
                  <label htmlFor="voice">Voice</label>
                  <Select
                    value={voice}
                    onChange={(e) => setVoice(e.target.value)}
                    options={getVoicesForProvider().map((v, index) => {
                      const voiceValue = typeof v === 'string' ? v : (v?.id || v?.value || v?.name || `voice-${index}`);
                      const voiceLabel = typeof v === 'string' ? v.charAt(0).toUpperCase() + v.slice(1) : (v?.label || v?.name || voiceValue);
                      return { value: voiceValue, label: voiceLabel };
                    })}
                  />
                </div>

                <div className={styles.settingGroup}>
                  <label>Speed ({speed}x)</label>
                  <Slider
                    min={0.25}
                    max={4}
                    step={0.1}
                    value={speed}
                    onChange={(e) => setSpeed(parseFloat(e.target.value))}
                    valueFormatter={(v) => `${v}x`}
                  />
                </div>
              </SettingsSection>

              <SettingsSection title="">
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className={styles.advancedToggle}
                >
                  {showAdvanced ? '🔽 Hide Advanced' : '🔧 Advanced Options'}
                </button>

                {showAdvanced && (
                  <SettingsSection title="Advanced Settings">
                    <div className={styles.settingGroup}>
                      <label htmlFor="model">Model</label>
                      <Select
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        disabled={modelsLoading}
                        options={[
                          { value: "", label: "Default Model" },
                          ...getModelsForProvider().map((modelOption) => ({
                            value: modelOption.value,
                            label: modelOption.label
                          }))
                        ]}
                      />
                    </div>

                    <div className={styles.settingGroup}>
                      <label htmlFor="responseFormat">Audio Format</label>
                      <Select
                        value={responseFormat}
                        onChange={(e) => setResponseFormat(e.target.value)}
                        options={[
                          { value: "mp3", label: "MP3" },
                          { value: "wav", label: "WAV" },
                          { value: "opus", label: "OPUS" },
                          { value: "aac", label: "AAC" }
                        ]}
                      />
                    </div>

                    <div className={styles.settingGroup}>
                      <label htmlFor="languageCode">Language</label>
                      <Select
                        value={languageCode}
                        onChange={(e) => setLanguageCode(e.target.value)}
                        options={[
                          { value: "en-US", label: "English (US)" },
                          { value: "en-GB", label: "English (UK)" },
                          { value: "vi-VN", label: "Vietnamese" },
                          { value: "ja-JP", label: "Japanese" },
                          { value: "ko-KR", label: "Korean" },
                          { value: "zh-CN", label: "Chinese (Simplified)" },
                          { value: "fr-FR", label: "French" },
                          { value: "de-DE", label: "German" },
                          { value: "es-ES", label: "Spanish" }
                        ]}
                      />
                    </div>

                    {/* Provider-specific options */}
                    {provider === 'openai' && (
                      <div className={styles.settingGroup}>
                        <label htmlFor="instructions">Instructions (OpenAI)</label>
                        <Textarea
                          value={instructions}
                          onChange={(e) => setInstructions(e.target.value)}
                          placeholder="Additional instructions for voice style..."
                          rows={2}
                        />
                      </div>
                    )}

                    {(provider === 'google') && (
                      <div className={styles.settingGroup}>
                        <label htmlFor="systemPrompt">System Prompt (Google)</label>
                        <Textarea
                          value={systemPrompt}
                          onChange={(e) => setSystemPrompt(e.target.value)}
                          placeholder="System prompt for TTS style control..."
                          rows={2}
                        />
                      </div>
                    )}
                  </SettingsSection>
                )}
              </SettingsSection>

              <SettingsSection title="Actions">
                <button
                  onClick={handleReset}
                  className={styles.clearButton}
                >
                  🗑️ Reset
                </button>
              </SettingsSection>
            </>
          )}

          {/* NotebookLM Settings */}
          {activeTab === 'notebooklm' && (
            <SettingsSection title="Conversation Settings">
              <div className={styles.infoBox} style={{ marginTop: '1rem' }}>
                <span>💡</span>
                <div>
                  <strong>NotebookLM:</strong> Converts your text into a natural conversation between two AI hosts.
                </div>
              </div>
            </SettingsSection>
          )}
      </Sidebar>

      {/* Right Content Area */}
      <div className={styles.contentArea}>
        <div className={styles.contentHeader}>
          <h1 className={styles.contentTitle}>Text-to-Conversation</h1>
        </div>

        <div className={styles.contentBody}>
          {/* TTS Tab Content */}
          {activeTab === 'tts' && (
            <>
              <form onSubmit={handleSubmit} className={styles.form}>
                {/* Text Input */}
                <div className={styles.formGroup}>
                  <label htmlFor="text" className={styles.label}>
                    Text to Convert
                    {generatedText && <span className={styles.labelNote}> (Auto-populated)</span>}
                  </label>
                  <textarea
                    id="text"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Enter the text you want to convert to speech..."
                    rows={8}
                    required
                    className={styles.textarea}
                  />

                  {/* Sample Texts */}
                  <div className={styles.sampleTexts}>
                    <div className={styles.sampleLabel}>Quick samples:</div>
                    <div className={styles.sampleButtons}>
                      {sampleTexts.map((sample, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => setText(sample)}
                          className={styles.sampleButton}
                        >
                          Sample {index + 1}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

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

                          <div className={styles.audioControls}>
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
                      <div className={styles.audioInfo}>
                        <div className={styles.infoGrid}>
                          <div className={styles.infoItem}>
                            <strong>Voice:</strong> {result.voice}
                          </div>
                          <div className={styles.infoItem}>
                            <strong>Provider:</strong> {result.provider}
                          </div>
                          <div className={styles.infoItem}>
                            <strong>Duration:</strong> {result.duration?.toFixed(1)}s
                          </div>
                          <div className={styles.infoItem}>
                            <strong>Format:</strong> {result.audio_format?.toUpperCase()}
                          </div>
                        </div>
                      </div>

                      {/* Text Display */}
                      <div className={styles.convertedText}>
                        <h4>📝 Converted Text:</h4>
                        <p>{result.text}</p>
                      </div>
                    </div>
                  ) : (
                    <div className={styles.errorResult}>
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
              {/* Custom Text Input */}
              <div className={styles.formGroup}>
                <label htmlFor="customText" className={styles.label}>✏️ Text to Convert</label>
                <textarea
                  id="customText"
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder="Paste your text here that you want to convert to conversation audio...

Example content:
- Articles or blog posts
- Research papers
- Meeting notes
- Educational content
- Any text you want as a podcast conversation

The AI will create a natural conversation between two hosts discussing your content."
                  rows={10}
                  className={styles.textarea}
                  disabled={isGeneratingNotebook}
                />
                <div className={styles.textStats}>
                  <small className={styles.textHelp}>
                    Paste any text content to generate a conversation-style podcast
                  </small>
                  <small className={`${styles.charCount} ${customText.length > 10000 ? styles.warning : ''}`}>
                    {customText.length} characters {customText.length > 10000 && '(⚠️ Very long text)'}
                  </small>
                </div>
              </div>

              {/* Generate Button */}
              <div className={styles.buttonGroup}>
                <button
                  type="submit"
                  disabled={isGeneratingNotebook || !customText.trim()}
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

              {/* Info */}
              <div className={styles.infoBox}>
                <span>💡</span>
                <div>
                  <strong>How it works:</strong> NotebookLM will take your text and create a natural conversation-style podcast between two AI hosts discussing the content.
                </div>
              </div>

              {/* Warning */}
              <div className={styles.warningBox}>
                <span>⚠️</span>
                <div>
                  <strong>Important:</strong> This process will open a browser window and may take 5-15 minutes to complete.
                </div>
              </div>

              {/* Manual Alternative */}
              <div className={styles.alternativeBox}>
                <span>🛠️</span>
                <div>
                  <strong>Manual Alternative:</strong> If automation fails, you can:
                  <ol className={styles.manualSteps}>
                    <li>Visit <a href="https://notebooklm.google.com/" target="_blank" rel="noopener noreferrer">notebooklm.google.com</a></li>
                    <li>Create a new notebook</li>
                    <li>Add your text as "Copied text"</li>
                    <li>Generate an "Audio Overview"</li>
                    <li>Download the generated audio file</li>
                  </ol>
                </div>
              </div>
            </form>
          )}
        </div>

        {/* Loading Progress */}
        {isGeneratingNotebook && (
          <div className={styles.loadingCard}>
            <h3 className={styles.resultTitle}>🤖 Generating Audio...</h3>
            <p className={styles.loadingText}>
              Browser automation in progress... Please wait patiently.
            </p>
          </div>
        )}

        {/* Error Display */}
        {notebookError && (
          <div className={styles.error}>
            <strong>❌ NotebookLM Error</strong>
            <div className={styles.errorContent}>
              {notebookError.split('\n').map((line, index) => (
                <div key={index} className={styles.errorLine}>
                  {line}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Success Result */}
        {notebookResult && notebookResult.success && (
          <div className={styles.success}>
            <strong>✅ Audio Generated Successfully!</strong>
            <div className={styles.successDetails}>
              <div>🎵 Audio File: <code>{notebookResult.audio_url}</code></div>
              <div>⏱️ Processing Time: {formatProcessingTime(notebookResult.processing_time)}</div>
              {notebookResult.text_info && (
                <div>📄 Content: {notebookResult.text_info.content_length} characters</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TextToSpeech;