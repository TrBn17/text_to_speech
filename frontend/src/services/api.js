// API Service for Text-to-Speech Application
import env, { debugLog } from '../config/environment';

class ApiService {
  constructor() {
    this.baseURL = env.api.baseUrl;
    this.timeout = env.api.timeout;
    debugLog('API Service initialized with baseURL:', this.baseURL);
  }

  // Helper method for making requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      console.log(`🌐 Making API request to: ${url}`, options);
      debugLog(`Making API request to: ${url}`, options);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      console.log(`✅ API request successful: ${url}`);
      debugLog(`API request successful: ${url}`);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error.name === 'AbortError') {
        const timeoutError = new Error(`Request timeout after ${this.timeout}ms`);
        timeoutError.code = 'TIMEOUT';
        debugLog(`API timeout [${endpoint}]:`, timeoutError);
        throw timeoutError;
      }

      console.error(`❌ API Error [${endpoint}]:`, error);
      debugLog(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Configuration endpoints
  async getConfig() {
    const response = await this.request('/api/config');
    return response.json();
  }

  async updateConfig(config) {
    const response = await this.request('/api/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.json();
  }

  async getTemplates() {
    const response = await this.request('/api/config/templates');
    return response.json();
  }

  // Text Generation endpoints
  async generateText({ prompt, maxTokens = 100, stream = false, files = [], model = 'gpt-4o-mini', systemPrompt = 'text_generation', customSystemPrompt = '', temperature = 0.7, topP = 0.9 }) {
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('max_tokens', maxTokens.toString());
    formData.append('stream', stream.toString());
    formData.append('model', model);
    formData.append('system_prompt', systemPrompt);  // Fixed: use system_prompt instead of systemPrompt
    formData.append('custom_system_prompt', customSystemPrompt);  // Fixed: use custom_system_prompt instead of customSystemPrompt
    formData.append('temperature', temperature.toString());
    formData.append('top_p', topP.toString());

    // Add files if any
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await this.request('/api/generate/text', {
      method: 'POST',
      body: formData,
    });

    if (stream) {
      return response; // Return response for streaming
    } else {
      const jsonResponse = await response.json();
      console.log('✅ Text generation JSON response:', jsonResponse);
      debugLog('✅ Text generation JSON response:', jsonResponse);
      return jsonResponse;
    }
  }

  // Streaming text generation
  async *generateTextStream({ prompt, maxTokens = 100, files = [], model = 'gpt-4o-mini', systemPrompt = 'text_generation', customSystemPrompt = '', temperature = 0.7, topP = 0.9 }) {
    const response = await this.generateText({
      prompt,
      maxTokens,
      stream: true,
      files,
      model,
      systemPrompt,
      customSystemPrompt,
      temperature,
      topP,
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data;
            } catch (e) {
              // Ignore malformed JSON
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // Text-to-Speech endpoints
  async textToSpeech({
    text,
    voice = 'alloy',
    speed = 1.0,
    provider = 'openai',
    model = null,
    system_prompt = '',
    instructions = '',
    response_format = 'mp3',
    prompt_prefix = '',
    voice_config = null,
    language_code = 'en-US'
  }) {
    const requestBody = {
      text,
      voice,
      speed,
      provider
    };

    // Add optional parameters only if they have values
    if (model) requestBody.model = model;
    if (system_prompt) requestBody.system_prompt = system_prompt;
    if (instructions) requestBody.instructions = instructions;
    if (response_format && response_format !== 'mp3') requestBody.response_format = response_format;
    if (prompt_prefix) requestBody.prompt_prefix = prompt_prefix;
    if (voice_config) requestBody.voice_config = voice_config;
    if (language_code && language_code !== 'en-US') requestBody.language_code = language_code;

    debugLog('🎵 TTS request body:', requestBody);

    const response = await this.request('/api/tts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    const jsonResponse = await response.json();
    debugLog('✅ TTS JSON response:', jsonResponse);
    return jsonResponse;
  }

  // Health check
  async healthCheck() {
    const response = await this.request('/health');
    return response.json();
  }

  // NotebookLM Audio Generation
  async generateNotebookLMAudio({ custom_text }) {
    if (!custom_text || !custom_text.trim()) {
      throw new Error('Custom text is required');
    }
    
    const response = await this.request('/api/notebooklm/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ custom_text: custom_text.trim() }),
    });
    return response.json();
  }

  // API info
  async getApiInfo() {
    const response = await this.request('/');
    return response.json();
  }

  // Utility methods
  convertBase64ToBlob(base64, mimeType = 'audio/mp3') {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);

    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }

    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  createAudioUrl(base64Audio) {
    const blob = this.convertBase64ToBlob(base64Audio);
    return URL.createObjectURL(blob);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;