import React, { useState } from 'react';
import ConfigManager from './components/ConfigManager';
import TextGenerator from './components/TextGenerator';
import TextToSpeech from './components/TextToSpeech';
import { useHealthCheck, useApiInfo } from './hooks/useApi';

function App() {
  const [activeTab, setActiveTab] = useState('generator');
  const { status: healthStatus } = useHealthCheck();
  const { info: apiInfo } = useApiInfo();

  const tabs = [
    { id: 'generator', label: '✨ Text Generator', component: TextGenerator },
    { id: 'tts', label: '🎵 Text-to-Speech', component: TextToSpeech },
    { id: 'config', label: '⚙️ Configuration', component: ConfigManager },
  ];

  const renderActiveComponent = () => {
    const activeTabData = tabs.find(tab => tab.id === activeTab);
    if (!activeTabData) return null;

    const Component = activeTabData.component;
    return <Component />;
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 AI Text & Speech Platform</h1>
          <div className="header-info">
            {apiInfo && (
              <span className="api-version">v{apiInfo.version}</span>
            )}
            <div className={`health-status ${healthStatus?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
              {healthStatus?.status === 'healthy' ? '🟢 Online' : '🔴 Offline'}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        <div className="nav-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        <div className="main-content">
          {renderActiveComponent()}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>🚀 Features</h4>
            <ul>
              <li>✨ AI Text Generation with file upload</li>
              <li>🎵 Text-to-Speech conversion</li>
              <li>📁 PDF, DOCX, Image processing</li>
              <li>⚡ Real-time streaming</li>
              <li>⚙️ Flexible configuration</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>📋 Supported Files</h4>
            <ul>
              <li>📄 PDF Documents</li>
              <li>📝 Word Documents (DOCX, DOC)</li>
              <li>🖼️ Images (PNG, JPG, JPEG, BMP, TIFF)</li>
              <li>📄 Text Files (TXT)</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>🎭 AI Models</h4>
            <ul>
              <li>🤖 OpenAI GPT Models</li>
              <li>🧠 Google Gemini</li>
              <li>🎵 OpenAI TTS</li>
              <li>🔊 Google Cloud TTS</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>🔗 API Endpoints</h4>
            <ul>
              <li><code>GET /config</code> - Get configuration</li>
              <li><code>POST /config</code> - Update configuration</li>
              <li><code>POST /generate/text</code> - Generate text</li>
              <li><code>POST /tts</code> - Text to speech</li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>
            💡 <strong>Pro Tip:</strong> Upload multiple files for comprehensive analysis.
            Enable streaming for real-time responses.
          </p>
          <p>
            🔧 Configure your models, voices, and parameters in the Configuration tab.
          </p>
        </div>
      </footer>

      <style jsx>{`
        .app {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .app-header {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          padding: 1rem 0;
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .header-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-content h1 {
          margin: 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .header-info {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .api-version {
          background: #e9ecef;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
        }

        .health-status {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
        }

        .health-status.healthy {
          background: #d4edda;
          color: #155724;
        }

        .health-status.unhealthy {
          background: #f8d7da;
          color: #721c24;
        }

        .app-nav {
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          padding: 0;
          position: sticky;
          top: 80px;
          z-index: 90;
        }

        .nav-tabs {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
          display: flex;
          gap: 0;
        }

        .nav-tab {
          background: none;
          border: none;
          padding: 15px 20px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 600;
          color: #6c757d;
          border-bottom: 3px solid transparent;
          transition: all 0.3s ease;
        }

        .nav-tab:hover {
          color: #495057;
          background: rgba(0, 0, 0, 0.05);
        }

        .nav-tab.active {
          color: #007bff;
          border-bottom-color: #007bff;
          background: rgba(0, 123, 255, 0.1);
        }

        .app-main {
          flex: 1;
          padding: 40px 0;
        }

        .main-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }

        .app-footer {
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 40px 0 20px;
          margin-top: auto;
        }

        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 30px;
        }

        .footer-section h4 {
          margin: 0 0 15px 0;
          color: #fff;
        }

        .footer-section ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .footer-section li {
          padding: 5px 0;
          color: #ccc;
        }

        .footer-section code {
          background: rgba(255, 255, 255, 0.1);
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 12px;
        }

        .footer-bottom {
          max-width: 1200px;
          margin: 30px auto 0;
          padding: 20px;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
          text-align: center;
        }

        .footer-bottom p {
          margin: 5px 0;
          color: #ccc;
          font-size: 14px;
        }

        @media (max-width: 768px) {
          .header-content {
            flex-direction: column;
            gap: 10px;
          }

          .header-content h1 {
            font-size: 1.5rem;
          }

          .nav-tabs {
            overflow-x: auto;
            padding: 0 10px;
          }

          .nav-tab {
            white-space: nowrap;
            padding: 12px 16px;
            font-size: 14px;
          }

          .main-content {
            padding: 0 10px;
          }

          .footer-content {
            grid-template-columns: 1fr;
            gap: 20px;
          }

          .app-nav {
            top: 120px;
          }
        }
      `}</style>
    </div>
  );
}

export default App;