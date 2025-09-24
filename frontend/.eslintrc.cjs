const isProd = process.env.NODE_ENV === 'production';

module.exports = {
  root: true,
  env: { browser: true, es2021: true, node: true },
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module', ecmaFeatures: { jsx: true } },
  settings: { react: { version: 'detect' } },
  plugins: ['react-hooks','prettier'],
  extends: [
    'react-app',
    'react-app/jest',
    'plugin:react-hooks/recommended',
    'plugin:prettier/recommended'
  ],
  rules: {
    // Formatting
    'prettier/prettier': ['error',{ endOfLine: 'auto' }],

    // React hooks
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // Import ordering (disable to avoid build block) – can re‑enable later
    'import/order': 'off',

    // Console allowed in dev, warned in prod
    'no-console': isProd ? 'warn' : 'off',

    // Unused vars: ignore React symbol (new JSX transform) & underscore prefix
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^(React|_)' }],
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^(React|_)' }],

    // Legacy Create React App rules (ensure off if noisy)
    'react/react-in-jsx-scope': 'off'
  }
};