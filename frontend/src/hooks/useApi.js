import { useState, useCallback, useEffect } from 'react';
import { apiService } from '../services/api';

// Configuration hooks
export function useConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchConfig = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getConfig();
      setConfig(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (newConfig) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.updateConfig(newConfig);
      setConfig(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  return {
    config,
    loading,
    error,
    fetchConfig,
    updateConfig,
  };
}

export function useTemplates() {
  const [templates, setTemplates] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getTemplates();
      setTemplates(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  return {
    templates,
    loading,
    error,
    fetchTemplates,
  };
}

// Text Generation hooks
export function useTextGeneration() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateText = useCallback(async ({ prompt, maxTokens, files, model, systemPrompt, customSystemPrompt, temperature, topP }) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiService.generateText({
        prompt,
        maxTokens,
        stream: false,
        files,
        model,
        systemPrompt,
        customSystemPrompt,
        temperature,
        topP,
      });
      setResult(response);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    result,
    loading,
    error,
    generateText,
    reset,
  };
}

export function useStreamingTextGeneration() {
  const [content, setContent] = useState('');
  const [fileInfo, setFileInfo] = useState([]);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isComplete, setIsComplete] = useState(false);

  const generateStream = useCallback(async ({ prompt, maxTokens, files, model, systemPrompt, customSystemPrompt, temperature, topP }) => {
    setLoading(true);
    setError(null);
    setContent('');
    setFileInfo([]);
    setUsage(null);
    setIsComplete(false);

    try {
      const stream = apiService.generateTextStream({
        prompt,
        maxTokens,
        files,
        model,
        systemPrompt,
        customSystemPrompt,
        temperature,
        topP,
      });

      for await (const event of stream) {
        switch (event.type) {
          case 'file_info':
            setFileInfo(event.files || []);
            break;
          case 'content':
            setContent(prev => prev + event.content);
            break;
          case 'done':
            setUsage(event.usage);
            setIsComplete(true);
            setLoading(false);
            break;
          case 'error':
            setError(event.error);
            setLoading(false);
            break;
          default:
            // Unknown event type, ignore
            break;
        }
      }
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setContent('');
    setFileInfo([]);
    setUsage(null);
    setError(null);
    setLoading(false);
    setIsComplete(false);
  }, []);

  return {
    content,
    fileInfo,
    usage,
    loading,
    error,
    isComplete,
    generateStream,
    reset,
  };
}

// Text-to-Speech hooks
export function useTextToSpeech() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);

  const generateSpeech = useCallback(async ({
    text,
    voice,
    speed,
    provider,
    model = null,
    system_prompt = '',
    instructions = '',
    response_format = 'mp3',
    prompt_prefix = '',
    voice_config = null,
    language_code = 'en-US'
  }) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setAudioUrl(null);

    try {
      const response = await apiService.textToSpeech({
        text,
        voice,
        speed,
        provider,
        model,
        system_prompt,
        instructions,
        response_format,
        prompt_prefix,
        voice_config,
        language_code,
      });

      setResult(response);

      if (response.success && response.audio_base64) {
        const url = apiService.createAudioUrl(response.audio_base64);
        setAudioUrl(url);
      }

      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
  }, [audioUrl]);

  // Cleanup audio URL on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  return {
    result,
    loading,
    error,
    audioUrl,
    generateSpeech,
    reset,
  };
}

// Health check hook
export function useHealthCheck() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.healthCheck();
      setStatus(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return {
    status,
    loading,
    error,
    checkHealth,
  };
}

// API info hook
export function useApiInfo() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchInfo = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getApiInfo();
      setInfo(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInfo();
  }, [fetchInfo]);

  return {
    info,
    loading,
    error,
    fetchInfo,
  };
}