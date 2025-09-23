import React, { useState, useRef } from 'react';
import { useTextGeneration, useStreamingTextGeneration } from '../hooks/useApi';
import { useTextGenerationModels, useSystemPrompts } from '../hooks/useModels';
import env from '../config/environment';
import styles from '../styles/TextGenerator.module.css';

const TextGenerator = ({ onTextGenerated }) => {
  const [prompt, setPrompt] = useState('');
  const [maxTokens, setMaxTokens] = useState(env.defaults.maxTokens);
  const [streamingMode, setStreamingMode] = useState(env.features.streaming);
  const [files, setFiles] = useState([]);
  const [selectedModel, setSelectedModel] = useState('gpt-4o-mini');
  const [selectedPrompt, setSelectedPrompt] = useState('text_generation');
  const [customSystemPrompt, setCustomSystemPrompt] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [topP, setTopP] = useState(0.9);
  const fileInputRef = useRef(null);

  // Load available models and prompts
  const { models, loading: modelsLoading } = useTextGenerationModels();
  const { prompts, loading: promptsLoading } = useSystemPrompts();

  // Non-streaming hook
  const { result, loading, error, generateText, reset } = useTextGeneration();

  // Streaming hook
  const {
    content,
    fileInfo,
    usage,
    loading: streamLoading,
    error: streamError,
    isComplete,
    generateStream,
    reset: resetStream,
  } = useStreamingTextGeneration();

  // Debug: Log models and prompts data
  React.useEffect(() => {
    console.log('🔍 TextGenerator Debug:');
    console.log('Models:', models, 'Loading:', modelsLoading);
    console.log('Prompts:', prompts, 'Loading:', promptsLoading);
  }, [models, prompts, modelsLoading, promptsLoading]);

  // Watch for completed text generation and call callback
  React.useEffect(() => {
    if (onTextGenerated) {
      // For non-streaming mode
      if (!streamingMode && result && result.success && result.generated_text) {
        onTextGenerated(result.generated_text);
      }
      // For streaming mode
      if (streamingMode && isComplete && content) {
        onTextGenerated(content);
      }
    }
  }, [result, isComplete, content, streamingMode, onTextGenerated]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);

    // Validate file count
    if (selectedFiles.length > env.upload.maxFiles) {
      alert(`Maximum ${env.upload.maxFiles} files allowed. Selected: ${selectedFiles.length}`);
      return;
    }

    // Validate file sizes
    const oversizedFiles = selectedFiles.filter(file => file.size > env.upload.maxFileSize);
    if (oversizedFiles.length > 0) {
      const maxSizeMB = (env.upload.maxFileSize / 1024 / 1024).toFixed(1);
      alert(`Files too large (max: ${maxSizeMB}MB): ${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }

    setFiles(selectedFiles);
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    const params = {
      prompt: prompt.trim(),
      maxTokens,
      files,
      model: selectedModel,
      systemPrompt: selectedPrompt,
      customSystemPrompt,
      temperature,
      topP,
    };

    try {
      if (streamingMode) {
        await generateStream(params);
      } else {
        await generateText(params);
      }
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };

  const handleReset = () => {
    if (streamingMode) {
      resetStream();
    } else {
      reset();
    }
    setPrompt('');
    setFiles([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const currentLoading = streamingMode ? streamLoading : loading;
  const currentError = streamingMode ? streamError : error;

  return (
    <div className={styles.textGenerator}>
      <h2 className={styles.title}>✨ Text Generator</h2>

      <div className={styles.card}>
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Prompt Input */}
          <div className={styles.formGroup}>
            <label htmlFor="prompt">Prompt:</label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt here... You can also upload files for analysis."
              rows={4}
              required
              className={styles.textarea}
            />
          </div>

          {/* File Upload */}
          <div className={styles.formGroup}>
            <label htmlFor="files">Files (Optional):</label>
            <div
              className={styles.fileInput}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                id="files"
                ref={fileInputRef}
                type="file"
                multiple
                accept={env.upload.supportedTypes}
                onChange={handleFileChange}
                style={{ display: 'none' }}
                disabled={!env.features.fileUpload}
              />
              {files.length > 0 ? (
                <span>📁 {files.length} file(s) selected</span>
              ) : (
                <span>📎 Click to upload files</span>
              )}
            </div>
            <small style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem', display: 'block' }}>
              {env.features.fileUpload
                ? `Supported: ${env.upload.supportedTypesArray.join(', ').toUpperCase()} (Max: ${env.upload.maxFiles} files, ${(env.upload.maxFileSize / 1024 / 1024).toFixed(1)}MB each)`
                : 'File upload is disabled'
              }
            </small>

          {files.length > 0 && (
            <div className={styles.fileList}>
              <h4>Selected Files:</h4>
              {files.map((file, index) => (
                <div key={index} className={styles.fileItem}>
                  <span>📎 {file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveFile(index)}
                    className={styles.removeFile}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

          {/* Settings Grid */}
          <div className={styles.settingsGrid}>
            {/* Model Selection */}
            <div className={styles.settingItem}>
              <label htmlFor="model">AI Model</label>
              <select
                id="model"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className={styles.select}
                disabled={modelsLoading}
              >
                {modelsLoading ? (
                  <option>Loading models...</option>
                ) : (
                  models.map(model => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* System Prompt Selection */}
            <div className={styles.settingItem}>
              <label htmlFor="systemPrompt">System Prompt</label>
              <select
                id="systemPrompt"
                value={selectedPrompt}
                onChange={(e) => {
                  setSelectedPrompt(e.target.value);
                  if (e.target.value !== 'custom') {
                    setCustomSystemPrompt('');
                  }
                }}
                className={styles.select}
                disabled={promptsLoading}
              >
                {promptsLoading ? (
                  <option>Loading prompts...</option>
                ) : (
                  <>
                    {prompts.map(prompt => (
                      <option key={prompt.value} value={prompt.value}>
                        {prompt.label}
                      </option>
                    ))}
                    <option value="custom">✏️ Custom Prompt</option>
                  </>
                )}
              </select>
            </div>

            {/* Max Tokens */}
            <div className={styles.settingItem}>
              <label htmlFor="maxTokens">Max Tokens</label>
              <input
                id="maxTokens"
                type="number"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                min="1"
                max="8000"
                className={styles.input}
              />
            </div>

            {/* Temperature Slider */}
            <div className={styles.settingItem}>
              <label>Temperature</label>
              <div className={styles.sliderContainer}>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className={styles.slider}
                />
                <span className={styles.sliderValue}>{temperature}</span>
              </div>
            </div>

            {/* Top P Slider */}
            <div className={styles.settingItem}>
              <label>Top P</label>
              <div className={styles.sliderContainer}>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={topP}
                  onChange={(e) => setTopP(parseFloat(e.target.value))}
                  className={styles.slider}
                />
                <span className={styles.sliderValue}>{topP}</span>
              </div>
            </div>
          </div>

          {/* Custom System Prompt Input */}
          {selectedPrompt === 'custom' && (
            <div className={styles.formGroup}>
              <label htmlFor="customPrompt">Custom System Prompt</label>
              <textarea
                id="customPrompt"
                value={customSystemPrompt}
                onChange={(e) => setCustomSystemPrompt(e.target.value)}
                placeholder="Enter your custom system prompt here..."
                rows={3}
                className={styles.textarea}
              />
              <small style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem', display: 'block' }}>
                Write your own system prompt to guide the AI's behavior and responses.
              </small>
            </div>
          )}

          {/* Streaming Checkbox */}
          <div className={styles.checkboxContainer}>
            <input
              type="checkbox"
              id="streaming"
              checked={streamingMode}
              onChange={(e) => setStreamingMode(e.target.checked)}
              className={styles.checkbox}
            />
            <label htmlFor="streaming" className={styles.checkboxLabel}>
              ⚡ Enable Streaming
            </label>
          </div>

          {/* Action Buttons */}
          <div className={styles.buttonGroup}>
            <button
              type="submit"
              disabled={currentLoading}
              className={styles.generateButton}
            >
              {currentLoading ? (
                <>
                  <span className={styles.loadingSpinner}></span>
                  Generating...
                </>
              ) : (
                '🚀 Generate Text'
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
      </div>

      {/* Error Display */}
      {currentError && (
        <div className={styles.error}>
          ❌ Error: {currentError}
        </div>
      )}

      {/* Results Display */}
      {streamingMode ? (
        // Streaming Results
        content && (
          <div className={styles.resultCard}>
            <h3 className={styles.resultTitle}>📝 Generated Text {currentLoading && '(Streaming...)'}</h3>
            <div className={styles.resultContent}>
              {content}
            </div>
            {isComplete && usage && (
              <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#6b7280' }}>
                ✅ Generation complete. Usage: {JSON.stringify(usage)}
              </div>
            )}
          </div>
        )
      ) : (
        // Non-streaming Results
        result && result.success && (
          <div className={styles.resultCard}>
            <h3 className={styles.resultTitle}>📝 Generated Text</h3>
            <div className={styles.resultContent}>
              {result.generated_text}
            </div>
          </div>
        )
      )}
    </div>
  );
};

export default TextGenerator;