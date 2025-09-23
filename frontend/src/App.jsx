import React, { useState } from 'react';
import TextGenerator from './components/TextGenerator';
import TextToSpeech from './components/TextToSpeech';
import { useHealthCheck, useApiInfo } from './hooks/useApi';
import env from './config/environment';
import styles from './styles/App.module.css';

function App() {
  const [activeTab, setActiveTab] = useState('generator');
  const [generatedText, setGeneratedText] = useState('');
  const { status: healthStatus } = useHealthCheck();
  const { info: apiInfo } = useApiInfo();

  // Simple tabs without complex configuration
  const tabs = [
    { id: 'generator', label: '✨ Text Generator', component: TextGenerator },
    { id: 'tts', label: '🎙️ Text-to-Conversation', component: TextToSpeech },
  ];

  const handleTextGenerated = (text) => {
    setGeneratedText(text);
    setActiveTab('tts'); // Auto-switch to TTS tab
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

  return (
    <div className={styles.app}>
      {/* Header */}
      <header className={styles.header}>
        <div className={`container ${styles.headerContent}`}>
          <h1 className={styles.title}>🤖 {env.app.name}</h1>
          <div className={styles.headerInfo}>
            {apiInfo && (
              <span className={styles.apiVersion}>v{apiInfo.version}</span>
            )}
            <div className={`${styles.healthStatus} ${healthStatus?.status === 'healthy' ? styles.healthy : styles.unhealthy}`}>
              {healthStatus?.status === 'healthy' ? '🟢 Online' : '🔴 Offline'}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className={styles.nav}>
        <div className={`container ${styles.navTabs}`}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${styles.navTab} ${activeTab === tab.id ? styles.active : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className={styles.main}>
        <div className="container">
          {renderActiveComponent()}
        </div>
      </main>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className="container">
          <p>🤖 AI Text Generator & Audio Converter</p>
        </div>
      </footer>

    </div>
  );
}

export default App;