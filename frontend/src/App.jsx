import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import TextToSpeech from './components/TextToSpeech';
import { useHealthCheck, useApiInfo } from './hooks/useApi';
import env from './config/environment';
import styles from './styles/App.module.css';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [generatedText, setGeneratedText] = useState('');
  const { status: healthStatus } = useHealthCheck();
  const { info: apiInfo } = useApiInfo();

  // Simple tabs without complex configuration
  const tabs = [
    { id: 'home', label: '🏠 Home', component: null },
    { id: 'generator', label: '💬 AI Chat', component: ChatInterface },
    { id: 'tts', label: 'Text-to-Conversation', component: TextToSpeech },
  ];

  const handleTextGenerated = (text) => {
    setGeneratedText(text);
    // Note: Auto-switch to TTS disabled for better chat experience
    // setActiveTab('tts'); // Auto-switch to TTS tab
  };

  const renderActiveComponent = () => {
    const activeTabData = tabs.find(tab => tab.id === activeTab);
    if (!activeTabData) return null;

    const Component = activeTabData.component;

    // Pass different props based on the component
    if (activeTabData.id === 'generator') {
      return <Component onTextGenerated={handleTextGenerated} />;
    } else if (activeTabData.id === 'tts') {
      return <Component generatedText={generatedText} />;
    }

    return <Component />;
  };

  const renderHomeContent = () => (
    <div className={styles.homeContainer}>
      <div className="container">
        <div className={styles.homeContent}>
          <h1 className={styles.homeTitle}>Welcome to {env.app.name}</h1>
          <p className={styles.homeDescription}>
            Your AI-powered text generation and audio conversion platform
          </p>

          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>💬</div>
              <h3>AI Chat</h3>
              <p>Interactive chat with advanced AI models for text generation</p>
              <button
                onClick={() => setActiveTab('generator')}
                className={styles.featureButton}
              >
                Start Chatting
              </button>
            </div>

            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🎙️</div>
              <h3>Text-to-Conversation</h3>
              <p>Convert text to natural speech and podcast-style conversations</p>
              <button
                onClick={() => setActiveTab('tts')}
                className={styles.featureButton}
              >
                Convert Audio
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={styles.app}>
      {/* Unified pill tab switcher - always visible for all tabs */}
      <div className={styles.chatTabSwitcher} data-active={activeTab}>
        <button
          onClick={() => setActiveTab('home')}
          className={`${styles.chatTab} ${activeTab === 'home' ? styles.active : ''}`}
        >
          🏠 Home
        </button>
        <button
          onClick={() => setActiveTab('generator')}
          className={`${styles.chatTab} ${activeTab === 'generator' ? styles.active : ''}`}
        >
          💬 AI Chat
        </button>
        <button
          onClick={() => setActiveTab('tts')}
          className={`${styles.chatTab} ${activeTab === 'tts' ? styles.active : ''}`}
        >
          Text-to-Conversation
        </button>
      </div>

      {/* Main Content */}
      <main className={`${styles.main} ${styles.withTabSwitcher}`}>
        {activeTab === 'home' ? (
          renderHomeContent()
        ) : activeTab === 'generator' ? (
          // Fullscreen for chat interface
          renderActiveComponent()
        ) : activeTab === 'tts' ? (
          // Fullscreen for TTS interface
          renderActiveComponent()
        ) : (
          // Container for other components
          <div className="container">
            {renderActiveComponent()}
          </div>
        )}
      </main>


    </div>
  );
}

export default App;