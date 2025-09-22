import React, { useState, useRef } from 'react';
import { useTextGeneration, useStreamingTextGeneration } from '../hooks/useApi';
import { useTextGenerationModels, useSystemPrompts } from '../hooks/useModels';
import env from '../config/environment';
import styles from '../styles/TextGenerator.module.css';

const TextGenerator = () => {
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

  // Debug: Log models and prompts data
  React.useEffect(() => {
    console.log('🔍 TextGenerator Debug:');
    console.log('Models:', models, 'Loading:', modelsLoading);
    console.log('Prompts:', prompts, 'Loading:', promptsLoading);
  }, [models, prompts, modelsLoading, promptsLoading]);

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

      <form onSubmit={handleSubmit} className={`card ${styles.form}`}>
        {/* Prompt Input */}
        <div className="form-group">
          <label htmlFor="prompt" className="form-label">Prompt:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt here... You can also upload files for analysis."
            rows={4}
            required
            className="form-input form-textarea"
          />
        </div>

        {/* File Upload */}
        <div className="form-group">
          <label htmlFor="files" className="form-label">Files (Optional):</label>
          <input
            id="files"
            ref={fileInputRef}
            type="file"
            multiple
            accept={env.upload.supportedTypes}
            onChange={handleFileChange}
            className="form-input"
            disabled={!env.features.fileUpload}
          />
          <small className="text-sm text-secondary">
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
                    className={styles.removeFileBtn}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Model Selection */}
        <div className="form-group">
          <label htmlFor="model" className="form-label">AI Model:</label>
          <select
            id="model"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="form-input form-select"
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
        <div className="form-group">
          <label htmlFor="systemPrompt" className="form-label">System Prompt:</label>
          <select
            id="systemPrompt"
            value={selectedPrompt}
            onChange={(e) => {
              setSelectedPrompt(e.target.value);
              if (e.target.value !== 'custom') {
                setCustomSystemPrompt('');
              }
            }}
            className="form-input form-select"
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

        {/* Custom System Prompt Input */}
        {selectedPrompt === 'custom' && (
          <div className="form-group">
            <label htmlFor="customPrompt" className="form-label">Custom System Prompt:</label>
            <textarea
              id="customPrompt"
              value={customSystemPrompt}
              onChange={(e) => setCustomSystemPrompt(e.target.value)}
              placeholder="Enter your custom system prompt here..."
              rows={3}
              className="form-input form-textarea"
            />
            <small className="text-sm text-secondary">
              Write your own system prompt to guide the AI's behavior and responses.
            </small>
          </div>
        )}

        {/* Settings Grid */}
        <div className={styles.settingsGrid}>
          <div className={styles.settingItem}>
            <label htmlFor="temperature" className="form-label">Temperature:</label>
            <input
              id="temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="form-range"
            />
            <span className="text-sm text-secondary">{temperature} (0=focused, 2=creative)</span>
          </div>

          <div className={styles.settingItem}>
            <label htmlFor="topP" className="form-label">Top P:</label>
            <input
              id="topP"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={topP}
              onChange={(e) => setTopP(parseFloat(e.target.value))}
              className="form-range"
            />
            <span className="text-sm text-secondary">{topP} (diversity)</span>
          </div>

          <div className={styles.settingItem}>
            <label htmlFor="maxTokens" className="form-label">Max Tokens:</label>
            <input
              id="maxTokens"
              type="number"
              min="1"
              max="8192"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className={`form-input ${styles.maxTokensInput}`}
            />
          </div>

          <div className={styles.settingItem}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={streamingMode}
                onChange={(e) => setStreamingMode(e.target.checked)}
                className="form-checkbox"
              />
              Enable Streaming
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className={styles.actions}>
          <button
            type="submit"
            disabled={currentLoading}
            className="btn btn-primary btn-lg"
          >
            {currentLoading ? (
              <>
                <span className="spinner"></span>
                Generating...
              </>
            ) : (
              '🚀 Generate Text'
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

      {/* File Processing Info */}
      {streamingMode && fileInfo.length > 0 && (
        <div className={`card ${styles.fileInfo}`}>
          <h3>📁 File Processing Results:</h3>
          {fileInfo.map((file, index) => (
            <div key={index} className={`${styles.fileResult} ${file.success ? styles.success : styles.error}`}>
              {file.success ? '✅' : '❌'} {file.filename} ({file.file_type})
              {file.success && ` - ${file.content_length} characters extracted`}
            </div>
          ))}
        </div>
      )}

      {/* Error Display */}
      {currentError && (
        <div className="alert alert-error">
          ❌ Error: {currentError}
        </div>
      )}

      {/* Results Display */}
      {streamingMode ? (
        // Streaming Results
        <div className={`card ${styles.resultsSection}`}>
          <h3>📝 Generated Text {currentLoading && '(Streaming...)'}</h3>
          <div className={styles.streamingOutput}>
            {content && (
              <pre className={styles.generatedContent}>{content}</pre>
            )}
            {currentLoading && (
              <div className={styles.streamingIndicator}>
                <span className="spinner"></span>
                Generating...
              </div>
            )}
            {isComplete && usage && (
              <div className={styles.usageInfo}>
                ✅ Generation complete. Usage: {JSON.stringify(usage)}
              </div>
            )}
          </div>
        </div>
      ) : (
        // Non-streaming Results
        result && (
          <div className={`card ${styles.resultsSection}`}>
            <h3>📝 Generated Text</h3>
            {result.success ? (
              <div>
                <pre className={styles.generatedContent}>{result.generated_text}</pre>

                {result.file_info && result.file_info.length > 0 && (
                  <div className={styles.fileInfo}>
                    <h4>📁 File Processing Results:</h4>
                    {result.file_info.map((file, index) => (
                      <div key={index} className={`${styles.fileResult} ${file.success ? styles.success : styles.error}`}>
                        {file.success ? '✅' : '❌'} {file.filename} ({file.file_type})
                        {file.success && ` - ${file.content_length} characters extracted`}
                      </div>
                    ))}
                  </div>
                )}

                {result.usage && (
                  <div className={styles.usageInfo}>
                    📊 Usage: {JSON.stringify(result.usage)}
                  </div>
                )}
              </div>
            ) : (
              <div className="alert alert-error">
                ❌ Generation failed: {result.error}
              </div>
            )}
          </div>
        )
      )}

    </div>
  );
};

export default TextGenerator;