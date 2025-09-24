// Models API Service - Simple and clean
import env, { debugLog } from '../config/environment';

class ModelsApiService {
  constructor() {
    this.baseURL = env.api.baseUrl;
    debugLog('Models API Service initialized with baseURL:', this.baseURL);
  }

  async request(endpoint) {
    const url = `${this.baseURL}${endpoint}`;
    debugLog(`Fetching models from: ${url}`);

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      debugLog(`Models API response:`, data);
      return data;
    } catch (error) {
      debugLog(`Models API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Get TTS models and voices - only what's needed for TTS app
  async getTTSModels() {
    return this.request('/api/models/tts');
  }

  // Get text generation models
  async getTextGenerationModels() {
    return this.request('/api/models/text-generation');
  }

  // Get system prompts for text generation
  async getSystemPrompts() {
    return this.request('/api/models/system-prompts');
  }

  // Get all models data
  async getAllModels() {
    return this.request('/api/models/all');
  }

  // Get TTS prompts
  async getTTSPrompts() {
    return this.request('/api/models/tts/prompts');
  }

  // Save TTS prompt
  async saveTTSPrompt(promptName, promptText) {
    const url = `${this.baseURL}/api/models/tts/prompts/${promptName}`;
    debugLog(`Saving TTS prompt to: ${url}`);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: promptText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      debugLog(`TTS prompt saved:`, data);
      return data;
    } catch (error) {
      debugLog(`Save TTS prompt error:`, error);
      throw error;
    }
  }

  // Delete TTS prompt
  async deleteTTSPrompt(promptName) {
    const url = `${this.baseURL}/api/models/tts/prompts/${promptName}`;
    debugLog(`Deleting TTS prompt from: ${url}`);

    try {
      const response = await fetch(url, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      debugLog(`TTS prompt deleted:`, data);
      return data;
    } catch (error) {
      debugLog(`Delete TTS prompt error:`, error);
      throw error;
    }
  }

  // Transform voices for TTS UI
  transformVoicesForUI(ttsData) {
    if (!ttsData || !ttsData.voices) return {};

    const transformed = {};

    // OpenAI voices
    if (ttsData.voices.openai) {
      transformed.openai = ttsData.voices.openai.map(voice => ({
        value: voice,
        label: voice.charAt(0).toUpperCase() + voice.slice(1),
        provider: 'OpenAI'
      }));
    }

    // Google voices
    if (ttsData.voices.google) {
      transformed.google = ttsData.voices.google.map(voice => ({
        value: voice.id || voice,
        label: voice.name ? `${voice.name} (${voice.language})` : voice,
        provider: 'Google',
        language: voice.language || 'en-US'
      }));
    }

    return transformed;
  }

  // Transform text generation models for UI
  transformModelsForUI(modelsData) {
    if (!modelsData || !modelsData.models) return [];

    return modelsData.models.map(model => ({
      value: model.id,
      label: `${model.name} (${model.provider})`,
      provider: model.provider,
      maxTokens: model.max_tokens,
      defaultTemperature: model.default_temperature,
      defaultTopP: model.default_top_p,
      supportsStreaming: model.supports_streaming,
      supportsVision: model.supports_vision
    }));
  }

  // Transform system prompts for UI
  transformPromptsForUI(promptsData) {
    if (!promptsData || !promptsData.prompts) return [];

    return promptsData.prompts.map(prompt => ({
      value: prompt.id,
      label: prompt.name,
      text: prompt.text,
      category: prompt.category || 'default'
    }));
  }

  // Mock method for recommendations (can be implemented later)
  async getRecommendations() {
    return {
      recommendations: {
        textGeneration: {
          recommended: 'gpt-4o-mini',
          reason: 'Good balance of performance and cost'
        },
        tts: {
          recommended: 'tts-1-hd',
          reason: 'High quality audio with reasonable speed'
        }
      }
    };
  }
}

// Export singleton instance
export const modelsApiService = new ModelsApiService();
export default modelsApiService;