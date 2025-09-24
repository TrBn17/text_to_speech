# AI Text & Speech Platform - Frontend

## 📋 Project Overview

Advanced AI-powered text generation and speech synthesis platform frontend built with React, TypeScript, and Tailwind CSS.

## 🚀 Features

- **AI Text Generation**: Integration with OpenAI GPT and Google Gemini models
- **Text-to-Speech**: Multiple TTS providers with customizable voice options
- **File Upload**: Support for various document formats (PDF, DOCX, TXT, images)
- **Real-time Streaming**: Live text generation with streaming support
- **Responsive Design**: Modern UI with Tailwind CSS and animations
- **Accessibility**: WCAG compliant with keyboard navigation
- **Performance**: Optimized with React Query, debouncing, and virtualization
- **Type Safety**: Full TypeScript support with strict type checking

## 🛠️ Tech Stack

### Core Dependencies
- **React 18.2** - Modern React with concurrent features
- **TypeScript 5.2** - Type safety and better developer experience
- **Tailwind CSS 3.3** - Utility-first CSS framework
- **Axios 1.6** - HTTP client with interceptors
- **React Query 3.39** - Server state management and caching
- **Zustand 4.4** - Lightweight state management
- **Framer Motion 10.16** - Smooth animations and transitions

### UI Components
- **React Router DOM 6.17** - Client-side routing
- **React Hot Toast 2.4** - Beautiful notifications
- **React Markdown 9.0** - Markdown rendering with syntax highlighting
- **React Dropzone 14.2** - File upload with drag & drop
- **React Window 1.8** - Virtualization for large lists
- **Recharts 2.8** - Data visualization and charts

### Developer Tools
- **ESLint 8.51** - Code linting with React hooks rules
- **Prettier 3.0** - Code formatting
- **Husky 8.0** - Git hooks for code quality
- **Lint-staged 15.0** - Run linters on staged files

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Format code
npm run format
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Development Server
PORT=3000

# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000

# Feature Flags
REACT_APP_ENABLE_STREAMING=true
REACT_APP_ENABLE_TTS=true
REACT_APP_ENABLE_FILE_UPLOAD=true

# File Upload Limits
REACT_APP_MAX_FILE_SIZE=10485760
REACT_APP_MAX_FILES=10
```

### TypeScript Configuration
- Strict type checking enabled
- Path mapping for clean imports
- React JSX transform
- ES2022 target with modern features

### Tailwind CSS
- Custom color palette with semantic naming
- Extended spacing and typography scales
- Component classes for reusable UI elements
- Dark mode support (planned)

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── common/          # Reusable UI components
│   ├── ChatInterface.tsx
│   └── TextToSpeech.tsx
├── hooks/               # Custom React hooks
│   ├── useApi.js
│   └── useModels.js
├── services/            # API services
│   ├── api.js
│   └── modelsApi.js
├── config/              # Configuration files
│   └── environment.js
├── styles/              # Global styles
│   ├── globals.css
│   └── *.module.css
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── App.tsx              # Root component
```

## 🧪 Testing

### Test Coverage Requirements
- Branches: 70%
- Functions: 70%
- Lines: 70%
- Statements: 70%

### Testing Tools
- **Jest** - Test runner and assertions
- **React Testing Library** - Component testing utilities
- **MSW** - Mock service worker for API mocking

## 🎨 UI/UX Guidelines

### Design System
- **Primary Colors**: Blue gradient (50-900)
- **Typography**: Inter for text, JetBrains Mono for code
- **Spacing**: Consistent 4px grid system
- **Animations**: Subtle transitions with Framer Motion

### Component Architecture
- Atomic design principles
- Compound component patterns
- Render props and custom hooks
- Error boundaries for resilience

## 📈 Performance Optimizations

- **Code Splitting**: Route-based lazy loading
- **Bundle Analysis**: Webpack analyzer for size optimization
- **Caching**: React Query for server state
- **Debouncing**: Input debouncing for API calls
- **Virtualization**: Large list rendering with react-window

## 🔒 Security

- **Content Security Policy**: XSS protection
- **HTTPS Enforcement**: Secure communication
- **Input Sanitization**: XSS prevention
- **File Upload Validation**: Type and size restrictions

## 🌐 Browser Support

### Production
- Chrome/Edge: Last 2 versions
- Firefox/Safari: Last 2 versions
- Mobile: iOS Safari 14+, Chrome Android 90+

### Development
- Latest Chrome, Firefox, Safari, Edge

## 🚀 Deployment

### Build Optimization
```bash
# Production build
npm run build

# Analyze bundle size
npm run analyze

# Serve locally
npm run start:prod
```

### Environment-specific builds
- Development: Source maps, hot reload
- Staging: Production build with debug info
- Production: Minified, optimized, no source maps

## 🔄 CI/CD Pipeline

### Pre-commit Hooks
- ESLint with auto-fix
- Prettier formatting
- Type checking
- Test execution

### GitHub Actions (planned)
- Automated testing
- Build verification
- Security scanning
- Deployment to staging/production

## 📊 Monitoring & Analytics

### Performance Metrics
- Core Web Vitals tracking
- Bundle size monitoring
- API response times
- Error rate tracking

### User Analytics (optional)
- Feature usage tracking
- User flow analysis
- A/B testing support

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open pull request

### Code Style
- Use TypeScript for all new code
- Follow ESLint and Prettier rules
- Write meaningful commit messages
- Add tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT API
- Google for Gemini API
- React team for amazing framework
- Tailwind CSS for utility-first CSS
- All open-source contributors