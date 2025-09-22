import React, { useState, useRef } from 'react';
import { useTextGeneration, useStreamingTextGeneration } from '../hooks/useApi';

const TextGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [maxTokens, setMaxTokens] = useState(500);
  const [streamingMode, setStreamingMode] = useState(true);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);

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
    <div className="text-generator">
      <h2>✨ Text Generator</h2>

      <form onSubmit={handleSubmit} className="generator-form">
        {/* Prompt Input */}
        <div className="form-group">
          <label htmlFor="prompt">Prompt:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt here... You can also upload files for analysis."
            rows={4}
            required
          />
        </div>

        {/* File Upload */}
        <div className="form-group">
          <label htmlFor="files">Files (Optional):</label>
          <input
            id="files"
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.bmp,.tiff"
            onChange={handleFileChange}
          />
          <small>Supported: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG, BMP, TIFF</small>

          {files.length > 0 && (
            <div className="file-list">
              <h4>Selected Files:</h4>
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <span>📎 {file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveFile(index)}
                    className="remove-file-btn"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settings */}
        <div className="form-group settings">
          <div className="setting-item">
            <label htmlFor="maxTokens">Max Tokens:</label>
            <input
              id="maxTokens"
              type="number"
              min="1"
              max="8192"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
            />
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={streamingMode}
                onChange={(e) => setStreamingMode(e.target.checked)}
              />
              Enable Streaming
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="form-actions">
          <button
            type="submit"
            disabled={currentLoading}
            className="generate-btn"
          >
            {currentLoading ? 'Generating...' : '🚀 Generate Text'}
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

      {/* File Processing Info */}
      {streamingMode && fileInfo.length > 0 && (
        <div className="file-info">
          <h3>📁 File Processing Results:</h3>
          {fileInfo.map((file, index) => (
            <div key={index} className={`file-result ${file.success ? 'success' : 'error'}`}>
              {file.success ? '✅' : '❌'} {file.filename} ({file.file_type})
              {file.success && ` - ${file.content_length} characters extracted`}
            </div>
          ))}
        </div>
      )}

      {/* Error Display */}
      {currentError && (
        <div className="error-message">
          ❌ Error: {currentError}
        </div>
      )}

      {/* Results Display */}
      {streamingMode ? (
        // Streaming Results
        <div className="results-section">
          <h3>📝 Generated Text {currentLoading && '(Streaming...)'}</h3>
          <div className="streaming-output">
            {content && (
              <pre className="generated-content">{content}</pre>
            )}
            {currentLoading && (
              <div className="streaming-indicator">⏳ Generating...</div>
            )}
            {isComplete && usage && (
              <div className="usage-info">
                ✅ Generation complete. Usage: {JSON.stringify(usage)}
              </div>
            )}
          </div>
        </div>
      ) : (
        // Non-streaming Results
        result && (
          <div className="results-section">
            <h3>📝 Generated Text</h3>
            {result.success ? (
              <div>
                <pre className="generated-content">{result.generated_text}</pre>

                {result.file_info && result.file_info.length > 0 && (
                  <div className="file-info">
                    <h4>📁 File Processing Results:</h4>
                    {result.file_info.map((file, index) => (
                      <div key={index} className={`file-result ${file.success ? 'success' : 'error'}`}>
                        {file.success ? '✅' : '❌'} {file.filename} ({file.file_type})
                        {file.success && ` - ${file.content_length} characters extracted`}
                      </div>
                    ))}
                  </div>
                )}

                {result.usage && (
                  <div className="usage-info">
                    📊 Usage: {JSON.stringify(result.usage)}
                  </div>
                )}
              </div>
            ) : (
              <div className="error-message">
                ❌ Generation failed: {result.error}
              </div>
            )}
          </div>
        )
      )}

      <style jsx>{`
        .text-generator {
          max-width: 900px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }

        .generator-form {
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
        .form-group input[type="file"],
        .form-group input[type="number"] {
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

        .form-group small {
          display: block;
          margin-top: 5px;
          color: #666;
          font-size: 12px;
        }

        .file-list {
          margin-top: 10px;
          padding: 10px;
          background: #f8f9fa;
          border-radius: 4px;
        }

        .file-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 5px 0;
          border-bottom: 1px solid #eee;
        }

        .file-item:last-child {
          border-bottom: none;
        }

        .remove-file-btn {
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 50%;
          width: 20px;
          height: 20px;
          cursor: pointer;
          font-size: 12px;
        }

        .settings {
          display: flex;
          gap: 20px;
          align-items: center;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 4px;
        }

        .setting-item label {
          margin-bottom: 0;
          font-weight: normal;
        }

        .setting-item input[type="number"] {
          width: 100px;
          margin-left: 10px;
        }

        .form-actions {
          display: flex;
          gap: 10px;
          justify-content: center;
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
          background: #007bff;
          color: white;
        }

        .generate-btn:hover:not(:disabled) {
          background: #0056b3;
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

        .file-info,
        .results-section {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin-bottom: 20px;
        }

        .file-result {
          padding: 8px;
          margin: 5px 0;
          border-radius: 4px;
        }

        .file-result.success {
          background: #d4edda;
          color: #155724;
        }

        .file-result.error {
          background: #f8d7da;
          color: #721c24;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          padding: 15px;
          border-radius: 4px;
          margin: 10px 0;
        }

        .streaming-output {
          position: relative;
        }

        .generated-content {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 4px;
          white-space: pre-wrap;
          font-family: 'Courier New', monospace;
          max-height: 400px;
          overflow-y: auto;
          border: 1px solid #dee2e6;
        }

        .streaming-indicator {
          text-align: center;
          padding: 10px;
          color: #007bff;
          font-style: italic;
        }

        .usage-info {
          margin-top: 10px;
          padding: 10px;
          background: #e7f3ff;
          border-radius: 4px;
          font-size: 12px;
          color: #0c5460;
        }
      `}</style>
    </div>
  );
};

export default TextGenerator;