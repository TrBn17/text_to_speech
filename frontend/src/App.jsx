import React, { useState } from 'react';
import TextGenerator from './components/TextGenerator';
import TextToSpeech from './components/TextToSpeech';
import { useHealthCheck, useApiInfo } from './hooks/useApi';
import env from './config/environment';
import styles from './styles/App.module.css';

function App() {
  const [activeTab, setActiveTab] = useState('generator');
  const { status: healthStatus } = useHealthCheck();
  const { info: apiInfo } = useApiInfo();

  // Simple tabs without complex configuration
  const tabs = [
    { id: 'generator', label: '✨ Text Generator', component: TextGenerator },
    { id: 'tts', label: '🎵 Text-to-Speech', component: TextToSpeech },
  ];

  const renderActiveComponent = () => {
    const activeTabData = tabs.find(tab => tab.id === activeTab);
    if (!activeTabData) return null;

    const Component = activeTabData.component;
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
        <div className={`container ${styles.footerContent}`}>
          <div className={styles.footerSection}>
            <h4>🚀 Features</h4>
            <ul>
              <li>✨ AI Text Generation with file upload</li>
              <li>🎵 Text-to-Speech conversion</li>
              <li>📁 PDF, DOCX, Image processing</li>
              <li>⚡ Real-time streaming</li>
              <li>⚙️ Flexible configuration</li>
            </ul>
          </div>

          <div className={styles.footerSection}>
            <h4>📋 Supported Files</h4>
            <ul>
              <li>📄 PDF Documents</li>
              <li>📝 Word Documents (DOCX, DOC)</li>
              <li>🖼️ Images (PNG, JPG, JPEG, BMP, TIFF)</li>
              <li>📄 Text Files (TXT)</li>
            </ul>
          </div>

          <div className={styles.footerSection}>
            <h4>🎭 AI Models</h4>
            <ul>
              <li>🤖 OpenAI GPT Models</li>
              <li>🧠 Google Gemini</li>
              <li>🎵 OpenAI TTS</li>
              <li>🔊 Google (Gemini + Cloud TTS)</li>
            </ul>
          </div>

          <div className={styles.footerSection}>
            <h4>🔗 API Endpoints</h4>
            <ul>
              <li><code>GET /config</code> - Get configuration</li>
              <li><code>POST /config</code> - Update configuration</li>
              <li><code>POST /generate/text</code> - Generate text</li>
              <li><code>POST /tts</code> - Text to speech</li>
            </ul>
          </div>
        </div>

        <div className={`container ${styles.footerBottom}`}>
          <p>
            💡 <strong>Pro Tip:</strong> Upload multiple files for comprehensive analysis.
            Enable streaming for real-time responses.
          </p>
          <p>
            🔧 Configure your models, voices, and parameters directly in each tab's settings.
          </p>
        </div>
      </footer>

    </div>
  );
}

export default App;