import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useTextGeneration, useStreamingTextGeneration } from '../hooks/useApi';
import { useTextGenerationModels } from '../hooks/useModels';
import env from '../config/environment';
import Sidebar from './common/Sidebar';
import { SettingsSection } from './common/SettingsSection';
import { Select, Input, Textarea, Slider, CheckboxLabel } from './common/FormControls';
import AutoResizeTextarea from './common/AutoResizeTextarea';
import styles from '../styles/ChatInterface.module.css';

const ChatInterface = ({ onTextGenerated }) => {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [streamingMode, setStreamingMode] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedModel, setSelectedModel] = useState('gemini-2.0-flash-exp');
  const [temperature, setTemperature] = useState(0.7);
  const [topP, setTopP] = useState(0.9);
  const [maxTokens, setMaxTokens] = useState(env.defaults.maxTokens);
  const [systemPrompt, setSystemPrompt] = useState('text_generation');
  const [customSystemPrompt, setCustomSystemPrompt] = useState('');

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Load available models
  const { models, loading: modelsLoading } = useTextGenerationModels();

  // Non-streaming hook
  const { result, loading, error, generateText, reset } = useTextGeneration();

  // Streaming hook
  const {
    content,
    usage,
    loading: streamLoading,
    error: streamError,
    isComplete,
    generateStream,
    reset: resetStream,
  } = useStreamingTextGeneration();

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, content]);

  // Handle non-streaming response
  useEffect(() => {
    if (!streamingMode && result && result.response) {
      const newMessage = {
        id: Date.now(),
        type: 'assistant',
        content: result.response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, newMessage]);

      if (onTextGenerated) {
        onTextGenerated(result.response);
      }

      reset();
    }
  }, [result, streamingMode, onTextGenerated, reset]);

  // Handle streaming response
  useEffect(() => {
    if (streamingMode && isComplete && content) {
      const newMessage = {
        id: Date.now(),
        type: 'assistant',
        content: content,
        timestamp: new Date(),
        usage: usage,
      };
      setMessages(prev => [...prev, newMessage]);

      if (onTextGenerated) {
        onTextGenerated(content);
      }

      resetStream();
    }
  }, [isComplete, content, usage, streamingMode, onTextGenerated, resetStream]);

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
    console.log('🚀 Chat form submitted!');

    if (!prompt.trim()) {
      return;
    }

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: prompt.trim(),
      timestamp: new Date(),
      files: files.length > 0 ? [...files] : undefined,
    };

    setMessages(prev => [...prev, userMessage]);

    const params = {
      prompt: prompt.trim(),
      maxTokens,
      files,
      model: selectedModel,
      systemPrompt: systemPrompt,
      customSystemPrompt: systemPrompt === 'custom' ? customSystemPrompt : '',
      temperature,
      topP: topP,
    };

    try {
      console.log('🚀 Submitting chat with params:', params);

      if (streamingMode) {
        console.log('📡 Using streaming mode...');
        await generateStream(params);
      } else {
        console.log('📡 Using non-streaming mode...');
        await generateText(params);
      }
    } catch (err) {
      console.error('Chat generation failed:', err);

      // Add error message
      const errorMessage = {
        id: Date.now(),
        type: 'error',
        content: `Error: ${err.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    // Clear input
    setPrompt('');
    setFiles([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    reset();
    resetStream();
  };

  const currentLoading = streamingMode ? streamLoading : loading;
  const currentError = streamingMode ? streamError : error;

  return (
    <div className={styles.chatInterface}>
      {/* Left Sidebar */}
      <Sidebar title="AI Settings">
        <SettingsSection title="Model Configuration">
          <div className={styles.settingGroup}>
            <label htmlFor="model">AI Model</label>
            <Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={modelsLoading}
              options={modelsLoading ? 
                [{ value: "", label: "Loading..." }] :
                models.map(model => ({ value: model.value, label: model.label }))
              }
            />
          </div>

          <div className={styles.settingGroup}>
            <label htmlFor="maxTokens">Max Tokens</label>
            <Input
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              min="1"
              max="8000"
            />
          </div>

          <div className={styles.settingGroup}>
            <label>Temperature ({temperature})</label>
            <Slider
              min={0}
              max={2}
              step={0.1}
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
            />
          </div>

          <div className={styles.settingGroup}>
            <label>Top P</label>
            <Slider
              min={0}
              max={1}
              step={0.1}
              value={topP}
              onChange={(e) => setTopP(parseFloat(e.target.value))}
            />
          </div>

          <div className={styles.settingGroup}>
            <CheckboxLabel
              checked={streamingMode}
              onChange={(e) => setStreamingMode(e.target.checked)}
            >
              Enable Streaming
            </CheckboxLabel>
          </div>
        </SettingsSection>

        <SettingsSection title="System Prompts">
          <div className={styles.settingGroup}>
            <label htmlFor="systemPrompt">System Prompt Type</label>
            <Select
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              options={[
                { value: "text_generation", label: "Text Generation" },
                { value: "creative_writing", label: "Creative Writing" },
                { value: "code_assistant", label: "Code Assistant" },
                { value: "business_analyst", label: "Business Analyst" },
                { value: "educational_tutor", label: "Educational Tutor" },
                { value: "custom", label: "Custom Prompt" }
              ]}
            />
          </div>

          {systemPrompt === 'custom' && (
            <div className={styles.settingGroup}>
              <label htmlFor="customSystemPrompt">Custom System Prompt</label>
              <Textarea
                value={customSystemPrompt}
                onChange={(e) => setCustomSystemPrompt(e.target.value)}
                placeholder="Enter your custom system prompt..."
                rows={3}
              />
            </div>
          )}
        </SettingsSection>

        <SettingsSection title="Actions">
          <button
            type="button"
            onClick={handleClearChat}
            className={styles.clearButton}
          >
            🗑️ Clear Chat
          </button>
        </SettingsSection>
      </Sidebar>

      {/* Right Chat Area */}
      <div className={styles.chatArea}>
        <div className={styles.chatHeader}>
          <h1 className={styles.chatTitle}>What can I help with?</h1>
        </div>

        {/* Chat Messages */}
        <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <div key={message.id} className={`${styles.message} ${styles[message.type]}`}>
            <div className={styles.messageHeader}>
              <span className={styles.messageRole}>
                {message.type === 'user' ? '👤 You' : message.type === 'assistant' ? '🤖 AI' : '❌ Error'}
              </span>
              <span className={styles.messageTime}>
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>

            <div className={styles.messageContent}>
              {message.type === 'assistant' ? (
                <div className={styles.markdown}>
                  <ReactMarkdown>
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className={styles.plainText}>
                  {message.content}
                </div>
              )}
            </div>

            {message.files && (
              <div className={styles.messageFiles}>
                <strong>Files:</strong> {message.files.map(f => f.name).join(', ')}
              </div>
            )}

            {message.usage && (
              <div className={styles.messageUsage}>
                Usage: {JSON.stringify(message.usage)}
              </div>
            )}
          </div>
        ))}

        {/* Streaming content */}
        {streamingMode && streamLoading && content && (
          <div className={`${styles.message} ${styles.assistant} ${styles.streaming}`}>
            <div className={styles.messageHeader}>
              <span className={styles.messageRole}>🤖 AI</span>
              <span className={styles.messageTime}>Typing...</span>
            </div>
            <div className={styles.messageContent}>
              <div className={styles.markdown}>
                <ReactMarkdown>
                  {content}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className={styles.inputForm}>
        {/* File Upload */}
        {files.length > 0 && (
          <div className={styles.filePreview}>
            {files.map((file, index) => (
              <div key={index} className={styles.fileItem}>
                <span>📎 {file.name}</span>
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

        <div className={styles.inputContainer}>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={env.upload.supportedTypes}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            disabled={!env.features.fileUpload}
          />

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className={styles.fileButton}
            disabled={!env.features.fileUpload || currentLoading}
          >
            📎
          </button>

          <AutoResizeTextarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type your message here... (Shift+Enter for new line)"
            className={styles.messageInput}
            disabled={currentLoading}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            minRows={1}
            maxRows={6}
          />

          <button
            type="submit"
            disabled={currentLoading || !prompt.trim()}
            className={styles.sendButton}
          >
            {currentLoading ? '⏳' : '🚀'}
          </button>
        </div>

          {currentError && (
            <div className={styles.error}>
              ❌ Error: {currentError}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;