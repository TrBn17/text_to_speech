# AI Text & Speech Platform - Frontend

React frontend application for the AI Text & Speech Platform.

## 🚀 Features

- **Text Generation**: AI-powered text generation with file upload support
- **Text-to-Speech**: Convert text to high-quality speech
- **File Processing**: Support for PDF, DOCX, images with OCR
- **Real-time Streaming**: Live text generation like ChatGPT
- **Configuration Management**: Easy model and voice configuration
- **Responsive Design**: Works on desktop and mobile

## 📋 Prerequisites

- Node.js 16+
- npm or yarn
- Backend API running on `http://localhost:8000`

## 🛠️ Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm start
```

3. **Open browser:**
Navigate to `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
```

### API Proxy

The `package.json` includes a proxy configuration to route API calls to the backend:

```json
{
  "proxy": "http://localhost:8000"
}
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ConfigManager.jsx    # Configuration management
│   │   ├── TextGenerator.jsx    # Text generation with streaming
│   │   └── TextToSpeech.jsx     # TTS functionality
│   ├── hooks/              # Custom React hooks
│   │   └── useApi.js           # API hooks
│   ├── services/           # API services
│   │   └── api.js              # API client
│   ├── App.jsx             # Main application
│   └── index.js            # Entry point
├── public/
│   └── index.html          # HTML template
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## 🎯 Usage

### Text Generation

1. Navigate to the "✨ Text Generator" tab
2. Enter your prompt
3. Optionally upload files (PDF, DOCX, images)
4. Choose streaming or regular mode
5. Click "🚀 Generate Text"

**Supported file types:**
- PDF documents
- Word documents (DOCX, DOC)
- Images (PNG, JPG, JPEG, BMP, TIFF) with OCR
- Plain text files

### Text-to-Speech

1. Navigate to the "🎵 Text-to-Speech" tab
2. Enter text to convert
3. Select voice and speed
4. Choose provider (OpenAI, Google, Gemini)
5. Click "🎵 Convert to Speech"
6. Play or download the generated audio

### Configuration

1. Navigate to the "⚙️ Configuration" tab
2. Use templates or customize settings:
   - **Model settings**: Choose AI model, temperature, top-p
   - **TTS settings**: Select voice, speed, provider
3. Save individual sections or all settings

## 🔌 API Integration

### API Service (`src/services/api.js`)

Centralized API client with methods for all endpoints:

```javascript
import { apiService } from './services/api';

// Configuration
const config = await apiService.getConfig();
await apiService.updateConfig(newConfig);

// Text generation
const result = await apiService.generateText({
  prompt: "Hello world",
  maxTokens: 100,
  files: [file1, file2]
});

// Streaming
const stream = apiService.generateTextStream({
  prompt: "Write a story",
  maxTokens: 500
});

for await (const chunk of stream) {
  console.log(chunk);
}

// Text-to-speech
const audio = await apiService.textToSpeech({
  text: "Hello world",
  voice: "alloy",
  speed: 1.0
});
```

### Custom Hooks (`src/hooks/useApi.js`)

React hooks for easy API integration:

```javascript
import { useTextGeneration, useStreamingTextGeneration, useConfig } from './hooks/useApi';

// Text generation
const { result, loading, error, generateText } = useTextGeneration();

// Streaming
const { content, fileInfo, generateStream } = useStreamingTextGeneration();

// Configuration
const { config, updateConfig } = useConfig();
```

## 🎨 Components

### ConfigManager

Complete configuration interface with:
- Template selection
- Model parameters (temperature, top-p, max tokens)
- TTS settings (voice, speed, provider)
- Quick update buttons
- Real-time preview

### TextGenerator

Advanced text generation with:
- File upload (drag & drop support)
- Streaming mode toggle
- Real-time output display
- File processing status
- Error handling

### TextToSpeech

Professional TTS interface with:
- Multiple voice options
- Speed control
- Provider selection
- Audio player with controls
- Download functionality

## 🔄 Development

### Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject configuration (not recommended)
npm run eject
```

### Adding New Features

1. **Create component** in `src/components/`
2. **Add API method** in `src/services/api.js`
3. **Create hook** in `src/hooks/useApi.js`
4. **Update main app** in `src/App.jsx`

### Styling

Components use `styled-jsx` for scoped CSS. Each component includes its own styles:

```jsx
<style jsx>{`
  .component {
    background: white;
    padding: 20px;
  }
`}</style>
```

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Static Hosting

The build folder can be deployed to:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront
- Any static hosting service

### Environment Setup

For production, update API URL:

```env
REACT_APP_API_URL=https://your-api-domain.com
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check backend is running on `http://localhost:8000`
   - Verify proxy configuration in `package.json`

2. **File Upload Not Working**
   - Check file size limits
   - Verify supported file types
   - Check browser console for errors

3. **Streaming Not Working**
   - Ensure modern browser with fetch streaming support
   - Check network connectivity
   - Verify API streaming endpoint

### Debug Mode

Enable detailed logging:

```javascript
// In src/services/api.js
const DEBUG = process.env.NODE_ENV === 'development';

if (DEBUG) {
  console.log('API Request:', endpoint, options);
}
```

## 📖 API Documentation

Detailed API documentation is available in:
- `API_DOCUMENTATION.md` - Complete API reference
- `src/services/api.js` - Implementation examples
- `src/hooks/useApi.js` - React integration patterns

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.