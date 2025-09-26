import { useState, useEffect } from 'react';

import modelsApiService from '../services/modelsApi';

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

        const transformedModels = data.models?.map(model => ({
          value: model.id,
          label: `${model.name} (${model.provider})`,
          provider: model.provider_id,
          defaultVoice: model.default_voice,
          defaultSpeed: model.default_speed,
          audioFormat: model.audio_format
        })) || [];

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