import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import TextToSpeech from './components/TextToSpeech';
import AudioManager from './components/AudioManager';
import AboutUs from './components/AboutUs';
import NotificationManager, { useNotifications } from './components/common/NotificationManager';
// import { useHealthCheck, useApiInfo } from './hooks/useApi';
import env from './config/environment';
import styles from './styles/App.module.css';

// FOXAI logo from static folder
const foxaiLogo = '/static/logo/foxai-logo.png';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [generatedText, setGeneratedText] = useState('');
  
  // Notification system
  const { notifications, notify, removeNotification } = useNotifications();
  
  // Health check and API info hooks (available for future use)
  // const { status: healthStatus } = useHealthCheck();
  // const { info: apiInfo } = useApiInfo();

  // Simple tabs without complex configuration
  const tabs = [
    { id: 'home', label: 'Home', component: null },
    { id: 'generator', label: 'AI Chat', component: ChatInterface },
    { id: 'tts', label: 'Text-to-Conversation', component: TextToSpeech },
    { id: 'audio', label: 'Audio Files', component: AudioManager },
    { id: 'about', label: 'About Us', component: AboutUs },
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
      return <Component onTextGenerated={handleTextGenerated} notify={notify} />;
    } else if (activeTabData.id === 'tts') {
      return <Component generatedText={generatedText} notify={notify} />;
    }

    return <Component notify={notify} />;
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

            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🎵</div>
              <h3>Audio Files</h3>
              <p>Browse, download, and manage your generated audio files</p>
              <button
                onClick={() => setActiveTab('audio')}
                className={styles.featureButton}
              >
                View Files
              </button>
            </div>

            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🏢</div>
              <h3>About Us</h3>
              <p>Learn more about FOXAI and our comprehensive digital transformation solutions</p>
              <button
                onClick={() => setActiveTab('about')}
                className={styles.featureButton}
              >
                Learn More
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={styles.app}>
      {/* Notification Manager */}
      <NotificationManager 
        notifications={notifications} 
        onRemove={removeNotification} 
      />

      {/* Header with FOXAI logo and navigation tabs */}
      <div className={styles.chatTabSwitcher} data-active={activeTab}>
        {/* FOXAI Logo */}
        <div className={styles.headerLogo}>
          <img src={foxaiLogo} alt="FOXAI Logo" className={styles.logoImage} />
        </div>

        {/* Navigation Tabs */}
        <div className={styles.tabContainer}>
          <button
            onClick={() => setActiveTab('home')}
            className={`${styles.chatTab} ${activeTab === 'home' ? styles.active : ''}`}
          >
            Home
          </button>
          <button
            onClick={() => setActiveTab('generator')}
            className={`${styles.chatTab} ${activeTab === 'generator' ? styles.active : ''}`}
          >
            AI Chat
          </button>
          <button
            onClick={() => setActiveTab('tts')}
            className={`${styles.chatTab} ${activeTab === 'tts' ? styles.active : ''}`}
          >
            Text-to-Conversation
          </button>
          <button
            onClick={() => setActiveTab('audio')}
            className={`${styles.chatTab} ${activeTab === 'audio' ? styles.active : ''}`}
          >
            Audio Files
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`${styles.chatTab} ${activeTab === 'about' ? styles.active : ''}`}
          >
            About Us
          </button>
        </div>

        {/* Right side placeholder for future features */}
        <div style={{ width: '120px' }}></div>
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
        ) : activeTab === 'audio' ? (
          // Fullscreen for Audio Manager
          renderActiveComponent()
        ) : activeTab === 'about' ? (
          // Fullscreen for About Us
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