import React, { useState, useRef, useEffect } from 'react';
import { useTextToSpeech } from '../hooks/useApi';
import { useTTSModels } from '../hooks/useModels';
import { apiService } from '../services/api';
import env from '../config/environment';
import Sidebar from './common/Sidebar';
import { SettingsSection } from './common/SettingsSection';
import { Select, Textarea, Slider } from './common/FormControls';
import styles from '../styles/TextToSpeech.module.css';

const TextToSpeech = ({ generatedText }) => {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState(env.defaults.tts.voice);
  const [speed, setSpeed] = useState(env.defaults.tts.speed);
  const [provider, setProvider] = useState(env.defaults.tts.provider);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // NotebookLM states
  const [activeTab, setActiveTab] = useState('tts');
  const [isGeneratingNotebook, setIsGeneratingNotebook] = useState(false);
  const [notebookResult, setNotebookResult] = useState(null);
  const [notebookError, setNotebookError] = useState(null);
  const [customText, setCustomText] = useState(''); // Custom text for NotebookLM

  // Advanced options
  const [model, setModel] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [instructions, setInstructions] = useState('');
  const [responseFormat, setResponseFormat] = useState('mp3');
  const [languageCode, setLanguageCode] = useState('en-US');

  const audioRef = useRef(null);

  const { result, loading, error, audioUrl, generateSpeech, reset } = useTextToSpeech();
  const { models: apiTtsModels, voices: apiVoices, loading: modelsLoading } = useTTSModels();

  // Ensure apiVoices is always an object
  const safeApiVoices = apiVoices || { openai: [], google: [] };

  // Auto-populate text from generated text
  useEffect(() => {
    if (generatedText && generatedText.trim()) {
      setText(generatedText);
    }
  }, [generatedText]);

  // Filter models by current provider
  const getModelsForProvider = () => {
    if (!apiTtsModels || apiTtsModels.length === 0) return [];
    return apiTtsModels.filter(modelOption => {
      if (provider === 'openai') {
        return modelOption.provider === 'openai_tts';
      } else if (provider === 'google') {
        return modelOption.provider === 'google_tts' || modelOption.provider === 'gemini_tts';
      }
      return false;
    });
  };

  // Get voices for current provider
  const getVoicesForProvider = () => {
    if (provider === 'openai') {
      const openaiVoices = safeApiVoices?.openai || ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];
      // Ensure all voices are strings
      return openaiVoices.map(voice => 
        typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
      );
    } else if (provider === 'google') {
      // Handle both string array and object array
      const googleVoices = safeApiVoices?.google || [
        'natural_control', 'expressive', 'conversational',
        'en-US-Neural2-A', 'en-US-Neural2-B', 'en-US-Wavenet-A', 'en-US-Standard-A'
      ];
      // If it's array of objects, extract the id/value
      return googleVoices.map(voice => 
        typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
      );
    }
    return [];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!text.trim()) {
      alert('Vui lòng nhập một số văn bản');
      return;
    }

    try {
      await generateSpeech({
        text: text.trim(),
        voice,
        speed,
        provider,
        model: model || null,
        system_prompt: systemPrompt,
        instructions: instructions,
        response_format: responseFormat,
        language_code: languageCode,
      });
    } catch (err) {
      console.error('TTS generation failed:', err);
    }
  };

  const handlePlayAudio = () => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play();
    }
  };

  const handleDownloadAudio = () => {
    if (audioUrl) {
      const link = document.createElement('a');
      link.href = audioUrl;
      link.download = `tts_${Date.now()}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleReset = () => {
    reset();
    setText('');
  };

  // NotebookLM functions
  const handleGenerateNotebookAudio = async () => {
    if (!customText.trim()) {
      setNotebookError('Vui lòng nhập một số văn bản để chuyển đổi thành âm thanh');
      return;
    }

    setIsGeneratingNotebook(true);
    setNotebookError(null);
    setNotebookResult(null);

    try {
      console.log('🚀 Starting NotebookLM audio generation...');
      console.log('📝 Using custom text (length:', customText.trim().length, 'chars)');
      
      const response = await apiService.generateNotebookLMAudio({
        custom_text: customText.trim()
      });
      
      console.log('✅ NotebookLM generation completed:', response);
      setNotebookResult(response);
      
    } catch (err) {
      console.error('❌ NotebookLM generation failed:', err);
      setNotebookError(err.message || 'Không thể tạo âm thanh');
    } finally {
      setIsGeneratingNotebook(false);
    }
  };

  const formatProcessingTime = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${remainingSeconds}s`;
  };

  const sampleTexts = [
    "Xin chào, đây là văn bản mẫu để chuyển đổi văn bản thành giọng nói.",
    "Con cáo nâu nhanh nhẹn nhảy qua con chó lười biếng.",
    "Trí tuệ nhân tạo đang thay đổi cách chúng ta làm việc và sống.",
    "Chào mừng đến với màn trình diễn chuyển văn bản thành giọng nói của chúng tôi.",
    "Công nghệ này giúp chúng ta có thể nghe nội dung thay vì chỉ đọc."
  ];

  return (
    <div className={styles.textToSpeech}>
      {/* Left Sidebar */}
      <Sidebar title="Cài đặt âm thanh">
        {/* Tab Navigation */}
        <SettingsSection title="">
          <div className={styles.tabNavigation}>
            <button
              onClick={() => setActiveTab('tts')}
              className={`${styles.tabButton} ${activeTab === 'tts' ? styles.active : ''}`}
            >
              Sử dụng API
            </button>
            <button
              onClick={() => setActiveTab('notebooklm')}
              className={`${styles.tabButton} ${activeTab === 'notebooklm' ? styles.active : ''}`}
            >
              Âm thanh hội thoại
            </button>
          </div>
        </SettingsSection>

          {/* Settings based on active tab */}
          {activeTab === 'tts' && (
            <>
              <SettingsSection title="Cấu hình nhà cung cấp">
                <div className={styles.settingGroup}>
                  <label htmlFor="provider">Nhà cung cấp</label>
                  <Select
                    value={provider}
                    onChange={(e) => {
                      const newProvider = e.target.value;
                      setProvider(newProvider);
                      let providerVoices = [];
                      if (newProvider === 'openai') {
                        const openaiVoices = safeApiVoices?.openai || ['alloy'];
                        providerVoices = openaiVoices.map(voice =>
                          typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
                        );
                      } else if (newProvider === 'google') {
                        const googleVoices = safeApiVoices?.google || ['natural_control'];
                        providerVoices = googleVoices.map(voice =>
                          typeof voice === 'string' ? voice : (voice?.id || voice?.value || voice?.name || 'unknown')
                        );
                      }
                      if (providerVoices.length > 0) {
                        setVoice(providerVoices[0]);
                      }
                    }}
                    options={[
                      { value: "openai", label: "OpenAI TTS" },
                      { value: "google", label: "Google (Gemini + Cloud TTS)" }
                    ]}
                  />
                </div>

                <div className={styles.settingGroup}>
                  <label htmlFor="voice">Giọng nói</label>
                  <Select
                    value={voice}
                    onChange={(e) => setVoice(e.target.value)}
                    options={getVoicesForProvider().map((v, index) => {
                      const voiceValue = typeof v === 'string' ? v : (v?.id || v?.value || v?.name || `voice-${index}`);
                      const voiceLabel = typeof v === 'string' ? v.charAt(0).toUpperCase() + v.slice(1) : (v?.label || v?.name || voiceValue);
                      return { value: voiceValue, label: voiceLabel };
                    })}
                  />
                </div>

                <div className={styles.settingGroup}>
                  <label>Tốc độ ({speed}x)</label>
                  <Slider
                    min={0.25}
                    max={4}
                    step={0.1}
                    value={speed}
                    onChange={(e) => setSpeed(parseFloat(e.target.value))}
                    valueFormatter={(v) => `${v}x`}
                  />
                </div>
              </SettingsSection>

              <SettingsSection title="">
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className={styles.advancedToggle}
                >
                  {showAdvanced ? 'Ẩn tùy chọn nâng cao' : 'Tùy chọn nâng cao'}
                </button>

                {showAdvanced && (
                  <SettingsSection title="Cài đặt nâng cao">
                    <div className={styles.settingGroup}>
                      <label htmlFor="model">Mô hình</label>
                      <Select
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        disabled={modelsLoading}
                        options={[
                          { value: "", label: "Mô hình mặc định" },
                          ...getModelsForProvider().map((modelOption) => ({
                            value: modelOption.value,
                            label: modelOption.label
                          }))
                        ]}
                      />
                    </div>

                    <div className={styles.settingGroup}>
                      <label htmlFor="responseFormat">Định dạng âm thanh</label>
                      <Select
                        value={responseFormat}
                        onChange={(e) => setResponseFormat(e.target.value)}
                        options={[
                          { value: "mp3", label: "MP3" },
                          { value: "wav", label: "WAV" },
                          { value: "opus", label: "OPUS" },
                          { value: "aac", label: "AAC" }
                        ]}
                      />
                    </div>

                    <div className={styles.settingGroup}>
                      <label htmlFor="languageCode">Ngôn ngữ</label>
                      <Select
                        value={languageCode}
                        onChange={(e) => setLanguageCode(e.target.value)}
                        options={[
                          { value: "en-US", label: "English (US)" },
                          { value: "en-GB", label: "English (UK)" },
                          { value: "vi-VN", label: "Tiếng Việt" },
                          { value: "ja-JP", label: "Tiếng Nhật" },
                          { value: "ko-KR", label: "Tiếng Hàn" },
                          { value: "zh-CN", label: "Tiếng Trung (Giản thể)" },
                          { value: "fr-FR", label: "Tiếng Pháp" },
                          { value: "de-DE", label: "Tiếng Đức" },
                          { value: "es-ES", label: "Tiếng Tây Ban Nha" }
                        ]}
                      />
                    </div>

                    {/* Provider-specific options */}
                    {provider === 'openai' && (
                      <div className={styles.settingGroup}>
                        <label htmlFor="instructions">Hướng dẫn (OpenAI)</label>
                        <Textarea
                          value={instructions}
                          onChange={(e) => setInstructions(e.target.value)}
                          placeholder="Hướng dẫn bổ sung cho phong cách giọng nói..."
                          rows={2}
                        />
                      </div>
                    )}

                    {(provider === 'google') && (
                      <div className={styles.settingGroup}>
                        <label htmlFor="systemPrompt">Lời nhắc hệ thống (Google)</label>
                        <Textarea
                          value={systemPrompt}
                          onChange={(e) => setSystemPrompt(e.target.value)}
                          placeholder="Lời nhắc hệ thống để điều khiển phong cách TTS..."
                          rows={2}
                        />
                      </div>
                    )}
                  </SettingsSection>
                )}
              </SettingsSection>

              <SettingsSection title="Hành động">
                <button
                  onClick={handleReset}
                  className={styles.clearButton}
                >
                  Đặt lại
                </button>
              </SettingsSection>
            </>
          )}

          {/* NotebookLM Settings */}
          {activeTab === 'notebooklm' && (
            <SettingsSection title="Cài đặt hội thoại">
              <div className={styles.infoBox} style={{ marginTop: '1rem' }}>
                <div>
                  <strong>FoxAI Native:</strong> Chuyển đổi văn bản của bạn thành cuộc hội thoại tự nhiên giữa hai người dẫn chương trình AI.
                </div>
              </div>
            </SettingsSection>
          )}
      </Sidebar>

      {/* Right Content Area */}
      <div className={styles.contentArea}>
        <div className={styles.contentHeader}>
          <h1 className={styles.contentTitle}>Chuyển văn bản thành hội thoại</h1>
        </div>

        <div className={styles.contentBody}>
          {/* TTS Tab Content */}
          {activeTab === 'tts' && (
            <>
              <form onSubmit={handleSubmit} className={styles.form}>
                {/* Text Input */}
                <div className={styles.formGroup}>
                  <label htmlFor="text" className={styles.label}>
                    Văn bản cần chuyển đổi
                    {generatedText && <span className={styles.labelNote}> (Tự động điền)</span>}
                  </label>
                  <textarea
                    id="text"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Nhập văn bản bạn muốn chuyển đổi thành giọng nói..."
                    rows={8}
                    required
                    className={styles.textarea}
                  />

                  {/* Sample Texts */}
                  <div className={styles.sampleTexts}>
                    <div className={styles.sampleLabel}>Mẫu nhanh:</div>
                    <div className={styles.sampleButtons}>
                      {sampleTexts.map((sample, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => setText(sample)}
                          className={styles.sampleButton}
                        >
                          Mẫu {index + 1}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className={styles.buttonGroup}>
                  <button
                    type="submit"
                    disabled={loading}
                    className={styles.generateButton}
                  >
                    {loading ? (
                      <>
                        <span className={styles.loadingSpinner}></span>
                        Đang chuyển đổi...
                      </>
                    ) : (
                      'Chuyển thành giọng nói'
                    )}
                  </button>
                </div>
              </form>

              {/* Error Display */}
              {error && (
                <div className={styles.error}>
                  Lỗi: {error}
                </div>
              )}

              {/* Results Display */}
              {result && (
                <div className={styles.resultCard}>
                  <h3 className={styles.resultTitle}>Kết quả âm thanh</h3>

                  {result.success ? (
                    <div>
                      {/* Audio Player */}
                      {audioUrl && (
                        <div>
                          <audio
                            ref={audioRef}
                            src={audioUrl}
                            controls
                            className={styles.audioPlayer}
                          />

                          <div className={styles.audioControls}>
                            <button
                              onClick={handlePlayAudio}
                              className={styles.downloadButton}
                            >
                              Phát âm thanh
                            </button>

                            <button
                              onClick={handleDownloadAudio}
                              className={styles.downloadButton}
                            >
                              Tải xuống MP3
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Audio Info */}
                      <div className={styles.audioInfo}>
                        <div className={styles.infoGrid}>
                          <div className={styles.infoItem}>
                            <strong>Giọng nói:</strong> {result.voice}
                          </div>
                          <div className={styles.infoItem}>
                            <strong>Nhà cung cấp:</strong> {result.provider}
                          </div>
                          <div className={styles.infoItem}>
                            <strong>Thời lượng:</strong> {result.duration?.toFixed(1)}s
                          </div>
                          <div className={styles.infoItem}>
                            <strong>Định dạng:</strong> {result.audio_format?.toUpperCase()}
                          </div>
                        </div>
                      </div>

                      {/* Text Display */}
                      <div className={styles.convertedText}>
                        <h4>Văn bản đã chuyển đổi:</h4>
                        <p>{result.text}</p>
                      </div>
                    </div>
                  ) : (
                    <div className={styles.errorResult}>
                      Chuyển đổi thất bại: {result.error}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* NotebookLM Tab Content */}
          {activeTab === 'notebooklm' && (
            <form onSubmit={(e) => { e.preventDefault(); handleGenerateNotebookAudio(); }} className={styles.form}>
              {/* Custom Text Input */}
              <div className={styles.formGroup}>
                <label htmlFor="customText" className={styles.label}>Văn bản cần chuyển đổi</label>
                <textarea
                  id="customText"
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder="Dán văn bản của bạn vào đây để chuyển đổi thành âm thanh hội thoại...

Nội dung ví dụ:
- Bài viết hoặc blog
- Báo cáo nghiên cứu
- Ghi chú cuộc họp
- Nội dung giáo dục
- Bất kỳ văn bản nào bạn muốn thành podcast hội thoại

AI sẽ tạo ra cuộc hội thoại tự nhiên giữa hai người dẫn chương trình thảo luận về nội dung của bạn."
                  rows={10}
                  className={styles.textarea}
                  disabled={isGeneratingNotebook}
                />
                <div className={styles.textStats}>
                  <small className={styles.textHelp}>
                    Dán bất kỳ nội dung văn bản nào để tạo podcast theo phong cách hội thoại
                  </small>
                  <small className={`${styles.charCount} ${customText.length > 10000 ? styles.warning : ''}`}>
                    {customText.length} ký tự {customText.length > 10000 && '(⚠️ Văn bản rất dài)'}
                  </small>
                </div>
              </div>

              {/* Generate Button */}
              <div className={styles.buttonGroup}>
                <button
                  type="submit"
                  disabled={isGeneratingNotebook || !customText.trim()}
                  className={styles.notebookButton}
                >
                  {isGeneratingNotebook ? (
                    <>
                      <span className={styles.loadingSpinner}></span>
                      Đang tạo âm thanh... (Có thể mất 5-15 phút)
                    </>
                  ) : (
                    'Tạo âm thanh hội thoại'
                  )}
                </button>
              </div>

              {/* Info */}
              <div className={styles.infoBox}>
                <div>
                  <strong>Cách hoạt động:</strong> Dán văn bản của bạn vào ô trên và nhấn "Generate Conversation Audio". Quá trình này sẽ tự động tạo ra một podcast phù hợp.
                </div>
              </div>
              <div className={styles.alternativeBox}>
                <span>🛠️</span>
                {/* <div>
                  <strong>Manual Alternative:</strong>:
                  <ol className={styles.manualSteps}>
                    <li>Visit <a href="https://notebooklm.google.com/" target="_blank" rel="noopener noreferrer">notebooklm.google.com</a></li>
                    <li>Create a new notebook</li>
                    <li>Add your text as "Copied text"</li>
                    <li>Generate an "Audio Overview"</li>
                    <li>Download the generated audio file</li>
                  </ol>
                </div> */}
              </div>
            </form>
          )}
        </div>

        {/* Loading Progress */}
        {isGeneratingNotebook && (
          <div className={styles.loadingCard}>
            <h3 className={styles.resultTitle}>Đang tạo âm thanh...</h3>
            <p className={styles.loadingText}>
              Tự động hóa trình duyệt đang diễn ra... Vui lòng đợi kiên nhẫn.
            </p>
          </div>
        )}

        {/* Error Display */}
        {notebookError && (
          <div className={styles.error}>
            <strong>Lỗi xảy ra</strong>
            <div className={styles.errorContent}>
              {notebookError.split('\n').map((line, index) => (
                <div key={index} className={styles.errorLine}>
                  {line}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Success Result */}
        {notebookResult && notebookResult.success && (
          <div className={styles.success}>
            <strong>Tạo âm thanh thành công!</strong>
            <div className={styles.successDetails}>
              <div>Tệp âm thanh: <code>{notebookResult.audio_url}</code></div>
              <div>Thời gian xử lý: {formatProcessingTime(notebookResult.processing_time)}</div>
              {notebookResult.text_info && (
                <div>Nội dung: {notebookResult.text_info.content_length} ký tự</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TextToSpeech;