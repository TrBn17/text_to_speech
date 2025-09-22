import React, { useState, useEffect } from 'react';
import { useConfig, useTemplates } from '../hooks/useApi';

const ConfigManager = () => {
  const { config, loading, error, updateConfig } = useConfig();
  const { templates } = useTemplates();

  const [formData, setFormData] = useState({
    model: '',
    system_prompt: '',
    model_parameters: {
      temperature: 0.7,
      top_p: 0.9,
      max_tokens: 100,
    },
    tts_parameters: {
      voice: 'alloy',
      speed: 1.0,
      provider: 'openai',
    },
  });

  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [saving, setSaving] = useState(false);

  // Update form data when config loads
  useEffect(() => {
    if (config) {
      setFormData({
        model: config.model || '',
        system_prompt: config.system_prompt || '',
        model_parameters: {
          temperature: config.model_parameters?.temperature || 0.7,
          top_p: config.model_parameters?.top_p || 0.9,
          max_tokens: config.model_parameters?.max_tokens || 100,
        },
        tts_parameters: {
          voice: config.tts_parameters?.voice || 'alloy',
          speed: config.tts_parameters?.speed || 1.0,
          provider: config.tts_parameters?.provider || 'openai',
        },
      });
    }
  }, [config]);

  const handleInputChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleDirectChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleTemplateSelect = (templateKey) => {
    if (!templates?.templates?.[templateKey]) return;

    const template = templates.templates[templateKey];
    setSelectedTemplate(templateKey);

    // Merge template data with current form data
    const newFormData = { ...formData };

    if (template.model) newFormData.model = template.model;
    if (template.system_prompt) newFormData.system_prompt = template.system_prompt;
    if (template.model_parameters) {
      newFormData.model_parameters = {
        ...newFormData.model_parameters,
        ...template.model_parameters,
      };
    }
    if (template.tts_parameters) {
      newFormData.tts_parameters = {
        ...newFormData.tts_parameters,
        ...template.tts_parameters,
      };
    }

    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await updateConfig(formData);
      alert('Configuration updated successfully!');
    } catch (err) {
      alert(`Failed to update configuration: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleQuickUpdate = async (section) => {
    setSaving(true);
    try {
      const partialConfig = { [section]: formData[section] };
      if (section === 'model_parameters' && formData.model) {
        partialConfig.model = formData.model;
      }
      if (section === 'model_parameters' && formData.system_prompt) {
        partialConfig.system_prompt = formData.system_prompt;
      }

      await updateConfig(partialConfig);
      alert(`${section} updated successfully!`);
    } catch (err) {
      alert(`Failed to update ${section}: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading">Loading configuration...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="config-manager">
      <h2>🔧 Configuration Manager</h2>

      {/* Template Selection */}
      {templates && (
        <div className="template-section">
          <h3>📋 Templates</h3>
          <select
            value={selectedTemplate}
            onChange={(e) => handleTemplateSelect(e.target.value)}
            className="template-select"
          >
            <option value="">Select a template...</option>
            {Object.keys(templates.templates).map(key => (
              <option key={key} value={key}>
                {key.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      )}

      <form onSubmit={handleSubmit} className="config-form">
        {/* Text Generation Config */}
        <div className="config-section">
          <h3>🤖 Text Generation</h3>

          <div className="form-group">
            <label>Model:</label>
            <input
              type="text"
              value={formData.model}
              onChange={(e) => handleDirectChange('model', e.target.value)}
              placeholder="e.g., gpt-3.5-turbo, gemini-2.5-flash"
            />
          </div>

          <div className="form-group">
            <label>System Prompt:</label>
            <textarea
              value={formData.system_prompt}
              onChange={(e) => handleDirectChange('system_prompt', e.target.value)}
              placeholder="You are a helpful assistant..."
              rows={3}
            />
          </div>

          <div className="form-group">
            <label>Temperature ({formData.model_parameters.temperature}):</label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={formData.model_parameters.temperature}
              onChange={(e) => handleInputChange('model_parameters', 'temperature', parseFloat(e.target.value))}
            />
            <small>Creativity level (0.0 = focused, 2.0 = creative)</small>
          </div>

          <div className="form-group">
            <label>Top-p ({formData.model_parameters.top_p}):</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={formData.model_parameters.top_p}
              onChange={(e) => handleInputChange('model_parameters', 'top_p', parseFloat(e.target.value))}
            />
            <small>Nucleus sampling (0.0 = focused, 1.0 = diverse)</small>
          </div>

          <div className="form-group">
            <label>Max Tokens:</label>
            <input
              type="number"
              min="1"
              max="8192"
              value={formData.model_parameters.max_tokens}
              onChange={(e) => handleInputChange('model_parameters', 'max_tokens', parseInt(e.target.value))}
            />
          </div>

          <button
            type="button"
            onClick={() => handleQuickUpdate('model_parameters')}
            disabled={saving}
            className="quick-update-btn"
          >
            Quick Update Text Config
          </button>
        </div>

        {/* TTS Config */}
        <div className="config-section">
          <h3>🎵 Text-to-Speech</h3>

          <div className="form-group">
            <label>Voice:</label>
            <select
              value={formData.tts_parameters.voice}
              onChange={(e) => handleInputChange('tts_parameters', 'voice', e.target.value)}
            >
              <option value="alloy">Alloy</option>
              <option value="echo">Echo</option>
              <option value="fable">Fable</option>
              <option value="onyx">Onyx</option>
              <option value="nova">Nova</option>
              <option value="shimmer">Shimmer</option>
            </select>
          </div>

          <div className="form-group">
            <label>Speed ({formData.tts_parameters.speed}):</label>
            <input
              type="range"
              min="0.25"
              max="4"
              step="0.1"
              value={formData.tts_parameters.speed}
              onChange={(e) => handleInputChange('tts_parameters', 'speed', parseFloat(e.target.value))}
            />
            <small>Speaking speed (0.25x - 4.0x)</small>
          </div>

          <div className="form-group">
            <label>Provider:</label>
            <select
              value={formData.tts_parameters.provider}
              onChange={(e) => handleInputChange('tts_parameters', 'provider', e.target.value)}
            >
              <option value="openai">OpenAI</option>
              <option value="google">Google</option>
              <option value="gemini">Gemini</option>
            </select>
          </div>

          <button
            type="button"
            onClick={() => handleQuickUpdate('tts_parameters')}
            disabled={saving}
            className="quick-update-btn"
          >
            Quick Update TTS Config
          </button>
        </div>

        {/* Save All Button */}
        <div className="form-actions">
          <button
            type="submit"
            disabled={saving}
            className="save-all-btn"
          >
            {saving ? 'Saving...' : 'Save All Configuration'}
          </button>
        </div>
      </form>

      {/* Current Config Display - Formatted */}
      {config && (
        <div className="current-config">
          <h3>📊 Current Configuration</h3>

          {config.current_configuration ? (
            <div className="config-display">
              {/* Current Settings */}
              <div className="config-section-display">
                <h4>{config.current_configuration["📄 Model Being Used"] ? "📄 Current Model" : "Current Settings"}</h4>
                {config.current_configuration["📄 Model Being Used"] && (
                  <div className="config-item">
                    <strong>Model:</strong> {config.current_configuration["📄 Model Being Used"]}
                  </div>
                )}
                {config.current_configuration["💬 System Prompt"] && (
                  <div className="config-item">
                    <strong>System Prompt:</strong> {config.current_configuration["💬 System Prompt"]}
                  </div>
                )}
              </div>

              {/* Text Generation Settings */}
              {config.current_configuration["🎛️ Text Generation Settings"] && (
                <div className="config-section-display">
                  <h4>🎛️ Text Generation Settings</h4>
                  {Object.entries(config.current_configuration["🎛️ Text Generation Settings"]).map(([key, value]) => (
                    <div key={key} className="config-item">
                      <strong>{key}:</strong> {value}
                    </div>
                  ))}
                </div>
              )}

              {/* TTS Settings */}
              {config.current_configuration["🎵 Text-to-Speech Settings"] && (
                <div className="config-section-display">
                  <h4>🎵 Text-to-Speech Settings</h4>
                  {Object.entries(config.current_configuration["🎵 Text-to-Speech Settings"]).map(([key, value]) => (
                    <div key={key} className="config-item">
                      <strong>{key}:</strong> {value}
                    </div>
                  ))}
                </div>
              )}

              {/* Available Options */}
              {config.available_options && (
                <div className="config-section-display">
                  <h4>📚 Available Options</h4>
                  {Object.entries(config.available_options).map(([category, options]) => (
                    <div key={category} className="config-category">
                      <strong>{category}:</strong>
                      {Object.entries(options).map(([provider, items]) => (
                        <div key={provider} className="config-subcategory">
                          <em>{provider}:</em> {Array.isArray(items) ? items.join(', ') : items}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}

              {/* Quick Templates Info */}
              {config.quick_templates && (
                <div className="config-section-display">
                  <h4>💡 Template Guide</h4>
                  {Object.entries(config.quick_templates).map(([key, value]) => (
                    <div key={key} className="config-item">
                      <strong>{key}:</strong> {
                        typeof value === 'object' ?
                          Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(', ') :
                          value
                      }
                    </div>
                  ))}
                </div>
              )}

              {/* Instructions */}
              {config.instructions && (
                <div className="config-section-display">
                  <h4>📋 How to Update</h4>
                  {Object.entries(config.instructions).map(([section, items]) => (
                    <div key={section} className="config-category">
                      <strong>{section}:</strong>
                      {Object.entries(items).map(([key, value]) => (
                        <div key={key} className="config-subcategory">
                          <em>{key}:</em> {value}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <pre className="raw-config">{JSON.stringify(config, null, 2)}</pre>
          )}
        </div>
      )}

      <style jsx>{`
        .config-manager {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }

        .template-section {
          margin-bottom: 30px;
          padding: 15px;
          background: #f5f5f5;
          border-radius: 8px;
        }

        .template-select {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .config-form {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }

        .config-section {
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: white;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .form-group small {
          display: block;
          margin-top: 5px;
          color: #666;
          font-size: 12px;
        }

        .quick-update-btn,
        .save-all-btn {
          background: #007bff;
          color: white;
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .quick-update-btn:hover,
        .save-all-btn:hover {
          background: #0056b3;
        }

        .quick-update-btn:disabled,
        .save-all-btn:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .form-actions {
          text-align: center;
          padding: 20px;
        }

        .current-config {
          margin-top: 30px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .current-config pre {
          background: #fff;
          padding: 15px;
          border-radius: 4px;
          overflow-x: auto;
          font-size: 12px;
        }

        .config-display {
          display: grid;
          gap: 20px;
        }

        .config-section-display {
          background: white;
          padding: 15px;
          border-radius: 6px;
          border: 1px solid #e0e0e0;
        }

        .config-section-display h4 {
          margin: 0 0 10px 0;
          color: #333;
          border-bottom: 2px solid #007bff;
          padding-bottom: 5px;
        }

        .config-item {
          margin: 8px 0;
          padding: 5px 0;
        }

        .config-item strong {
          color: #555;
          margin-right: 8px;
        }

        .config-category {
          margin: 10px 0;
          padding: 8px;
          background: #f8f9fa;
          border-radius: 4px;
        }

        .config-subcategory {
          margin: 4px 0 4px 15px;
          font-size: 14px;
        }

        .config-subcategory em {
          color: #666;
          margin-right: 5px;
        }

        .raw-config {
          background: #fff;
          padding: 15px;
          border-radius: 4px;
          overflow-x: auto;
          font-size: 12px;
        }

        .loading,
        .error {
          text-align: center;
          padding: 20px;
          margin: 20px 0;
        }

        .error {
          color: #d00;
          background: #ffe7e7;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default ConfigManager;