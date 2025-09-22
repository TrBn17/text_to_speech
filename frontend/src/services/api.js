// API Service for Text-to-Speech Application
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper method for making requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Configuration endpoints
  async getConfig() {
    const response = await this.request('/config');
    return response.json();
  }

  async updateConfig(config) {
    const response = await this.request('/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.json();
  }

  async getTemplates() {
    const response = await this.request('/config/templates');
    return response.json();
  }

  // Text Generation endpoints
  async generateText({ prompt, maxTokens = 100, stream = false, files = [] }) {
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('max_tokens', maxTokens.toString());
    formData.append('stream', stream.toString());

    // Add files if any
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await this.request('/generate/text', {
      method: 'POST',
      body: formData,
    });

    if (stream) {
      return response; // Return response for streaming
    } else {
      return response.json();
    }
  }

  // Streaming text generation
  async *generateTextStream({ prompt, maxTokens = 100, files = [] }) {
    const response = await this.generateText({
      prompt,
      maxTokens,
      stream: true,
      files,
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
  async textToSpeech({ text, voice = 'alloy', speed = 1.0, provider = 'openai' }) {
    const response = await this.request('/tts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, voice, speed, provider }),
    });
    return response.json();
  }

  // Health check
  async healthCheck() {
    const response = await this.request('/health');
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