// Custom hooks for models API
import { useState, useEffect } from 'react';
import modelsApiService from '../services/modelsApi';

// Hook for text generation models
export const useTextGenerationModels = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await modelsApiService.getTextGenerationModels();
        const transformedModels = modelsApiService.transformModelsForUI(data);
        setModels(transformedModels);
      } catch (err) {
        setError(err.message);
        setModels([]);
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  return { models, loading, error };
};

// Hook for TTS models and voices
export const useTTSModels = () => {
  const [models, setModels] = useState([]);
  const [voices, setVoices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTTSData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await modelsApiService.getTTSModels();

        // Transform models
        const transformedModels = data.models?.map(model => ({
          value: model.id,
          label: `${model.name} (${model.provider})`,
          provider: model.provider_id,
          defaultVoice: model.default_voice,
          defaultSpeed: model.default_speed,
          audioFormat: model.audio_format
        })) || [];

        // Transform voices
        const transformedVoices = modelsApiService.transformVoicesForUI(data);

        setModels(transformedModels);
        setVoices(transformedVoices);
      } catch (err) {
        setError(err.message);
        setModels([]);
        setVoices({});
      } finally {
        setLoading(false);
      }
    };

    fetchTTSData();
  }, []);

  return { models, voices, loading, error };
};

// Hook for system prompts
export const useSystemPrompts = () => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await modelsApiService.getSystemPrompts();
        const transformedPrompts = modelsApiService.transformPromptsForUI(data);
        setPrompts(transformedPrompts);
      } catch (err) {
        setError(err.message);
        setPrompts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPrompts();
  }, []);

  return { prompts, loading, error };
};

// Hook for all models data
export const useAllModels = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllModels = async () => {
      try {
        setLoading(true);
        setError(null);
        const allData = await modelsApiService.getAllModels();
        setData(allData);
      } catch (err) {
        setError(err.message);
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAllModels();
  }, []);

  return { data, loading, error };
};

// Hook for model recommendations
export const useModelRecommendations = () => {
  const [recommendations, setRecommendations] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await modelsApiService.getRecommendations();
        setRecommendations(data.recommendations || {});
      } catch (err) {
        setError(err.message);
        setRecommendations({});
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  return { recommendations, loading, error };
};