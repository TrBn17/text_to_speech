// Environment Configuration Manager
// Centralized configuration for all environment variables

/**
 * Get environment variable with optional default value
 * @param {string} key - Environment variable key
 * @param {any} defaultValue - Default value if env var is not set
 * @returns {any} Environment variable value or default
 */
const getEnvVar = (key, defaultValue = undefined) => {
  const value = process.env[key];

  // Handle boolean conversion
  if (typeof defaultValue === 'boolean') {
    return value === 'true' || (value === undefined && defaultValue);
  }

  // Handle number conversion
  if (typeof defaultValue === 'number') {
    const parsed = parseInt(value, 10);
    return !isNaN(parsed) ? parsed : defaultValue;
  }

  // Return string value or default
  return value !== undefined ? value : defaultValue;
};

/**
 * Environment Configuration Object
 */
export const env = {
  // API Configuration
  api: {
    baseUrl: getEnvVar('REACT_APP_API_URL', 'http://localhost:8000'),
    timeout: getEnvVar('REACT_APP_API_TIMEOUT', 30000),
  },

  // Application Info
  app: {
    name: getEnvVar('REACT_APP_NAME', 'AI Text & Speech Platform'),
    version: getEnvVar('REACT_APP_VERSION', '1.0.0'),
    description: getEnvVar('REACT_APP_DESCRIPTION', 'Advanced AI-powered text generation and speech synthesis platform'),
    environment: getEnvVar('REACT_APP_ENV', 'development'),
    debug: getEnvVar('REACT_APP_DEBUG', false),
    siteUrl: getEnvVar('REACT_APP_SITE_URL', 'http://localhost:3000'),
    author: getEnvVar('REACT_APP_AUTHOR', 'AI Development Team'),
    keywords: getEnvVar('REACT_APP_KEYWORDS', 'AI,text generation,text-to-speech,OpenAI,Gemini'),
  },

  // Default Settings
  defaults: {
    maxTokens: getEnvVar('REACT_APP_DEFAULT_MAX_TOKENS', 16384),
    temperature: parseFloat(getEnvVar('REACT_APP_DEFAULT_TEMPERATURE', '0.3')),
    topP: parseFloat(getEnvVar('REACT_APP_DEFAULT_TOP_P', '0.9')),
    tts: {
      voice: getEnvVar('REACT_APP_DEFAULT_TTS_VOICE', 'alloy'),
      speed: parseFloat(getEnvVar('REACT_APP_DEFAULT_TTS_SPEED', '1.0')),
      provider: getEnvVar('REACT_APP_DEFAULT_TTS_PROVIDER', 'openai'),
    },
  },

  // Feature Flags
  features: {
    streaming: getEnvVar('REACT_APP_ENABLE_STREAMING', true),
    fileUpload: getEnvVar('REACT_APP_ENABLE_FILE_UPLOAD', true),
    tts: getEnvVar('REACT_APP_ENABLE_TTS', true),
    configManager: getEnvVar('REACT_APP_ENABLE_CONFIG_MANAGER', true),
    analytics: getEnvVar('REACT_APP_ENABLE_ANALYTICS', false),
    darkMode: getEnvVar('REACT_APP_ENABLE_DARK_MODE', false),
    animations: getEnvVar('REACT_APP_ENABLE_ANIMATIONS', true),
  },

  // File Upload Configuration
  upload: {
    maxFileSize: getEnvVar('REACT_APP_MAX_FILE_SIZE', 10485760), // 10MB
    maxFiles: getEnvVar('REACT_APP_MAX_FILES', 10),
    supportedTypes: getEnvVar('REACT_APP_SUPPORTED_FILE_TYPES', '.pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.bmp,.tiff'),
    get supportedTypesArray() {
      return this.supportedTypes.split(',').map(type => type.trim());
    },
  },

  // UI Configuration
  ui: {
    theme: getEnvVar('REACT_APP_THEME', 'default'),
    debounceDelay: getEnvVar('REACT_APP_DEBOUNCE_DELAY', 300),
  },

  // Performance Settings
  performance: {
    retryAttempts: getEnvVar('REACT_APP_RETRY_ATTEMPTS', 3),
    cacheTtl: getEnvVar('REACT_APP_CACHE_TTL', 300000), // 5 minutes
  },

  // Analytics (for future use)
  analytics: {
    id: getEnvVar('REACT_APP_ANALYTICS_ID', ''),
    sentryDsn: getEnvVar('REACT_APP_SENTRY_DSN', ''),
  },
};

/**
 * Validate required environment variables
 */
export const validateEnvironment = () => {
  const required = [
    'REACT_APP_API_URL',
  ];

  const missing = required.filter(key => !process.env[key]);

  if (missing.length > 0) {
    console.warn('Missing required environment variables:', missing);
  }

  return missing.length === 0;
};

/**
 * Get configuration for development
 */
export const isDevelopment = () => env.app.environment === 'development';

/**
 * Get configuration for production
 */
export const isProduction = () => env.app.environment === 'production';

/**
 * Debug logger that only works in development
 */
export const debugLog = (...args) => {
  if (env.app.debug && isDevelopment()) {
    console.log('[DEBUG]', ...args);
  }
};

/**
 * Export default configuration
 */
export default env;

// Validate environment on module load
if (isDevelopment()) {
  validateEnvironment();
  debugLog('Environment configuration loaded:', env);
}