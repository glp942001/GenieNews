# GenieNews Frontend

React + Vite frontend for the GenieNews AI-powered news platform.

## Features

- **News Feed**: Browse AI-curated news articles
- **AI Chat**: Interactive assistant for news discussions
- **Audio Player**: Listen to daily news briefings
- **Responsive Design**: Mobile-friendly interface
- **Modern UI**: Tailwind CSS styling

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Nginx**: Production web server

## Prerequisites

- Node.js 18+ and npm

## Local Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file from the example:

```bash
cp env.example .env
```

For local development, set:

```
VITE_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

### 5. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── chat/         # AI chat components
│   │   ├── common/       # Shared components
│   │   ├── layout/       # Layout components
│   │   └── news/         # News-related components
│   ├── pages/            # Page components
│   ├── services/         # API service layer
│   ├── styles/           # Global styles
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── App.jsx          # Main app component
│   └── index.jsx        # Entry point
├── public/              # Static assets
├── Dockerfile           # Production container
├── fly.toml             # Fly.io configuration
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── package.json         # Dependencies

```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Environment Variables

### Development

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

### Production

Set in `fly.toml` or via flyctl:

```
VITE_API_URL=https://genienews-backend.fly.dev
```

## API Integration

The frontend communicates with the backend via `src/services/api.js`:

### Available API Functions

- `fetchTopArticles(limit)` - Get top articles
- `fetchArticle(id)` - Get single article
- `generateArticleSummary(articleId)` - Generate AI summary
- `sendChatMessage(message, history)` - Send chat message
- `generateDailyAudioSegment()` - Get/generate audio briefing

### Example Usage

```javascript
import { fetchTopArticles } from './services/api';

const { success, articles, error } = await fetchTopArticles(10);
if (success) {
  console.log(articles);
}
```

## Components

### News Components

- `NewsGrid` - Grid layout for articles
- `NewsCard` - Individual article card
- `AudioPlayer` - Audio briefing player
- `VideoPlayer` - Video player component

### Chat Components

- `AIChat` - AI chat interface

### Layout Components

- `Header` - App navigation header

### Common Components

- `Toast` - Notification component

## Routing

Routes are defined in `src/App.jsx`:

- `/` - Home page (AI News)
- `/fintech-news` - Fintech-specific news
- `/credit-genie-news` - Credit-specific news

## Styling

The app uses Tailwind CSS for styling. Configuration is in `tailwind.config.js`.

### Key Design Elements

- **Colors**: Purple accent (#8B5CF6)
- **Font**: System font stack
- **Layout**: Responsive grid system
- **Components**: Card-based design

## Deployment

### Deploy to Fly.io

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/

2. Login to Fly.io:
   ```bash
   flyctl auth login
   ```

3. Create app (first time only):
   ```bash
   cd frontend
   flyctl apps create genienews-frontend
   ```

4. Deploy:
   ```bash
   flyctl deploy --app genienews-frontend
   ```

5. Open in browser:
   ```bash
   flyctl open --app genienews-frontend
   ```

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment guide.

## Docker

### Build Image

```bash
docker build -t genienews-frontend .
```

### Run Container

```bash
docker run -p 8080:8080 genienews-frontend
```

The app will be available at `http://localhost:8080`

## Troubleshooting

### Backend Connection Issues

If the frontend can't connect to the backend:

1. Check `VITE_API_URL` in `.env`
2. Ensure backend is running
3. Check CORS settings in backend
4. Verify network connectivity

### Build Errors

If build fails:

1. Clear node_modules: `rm -rf node_modules`
2. Clear cache: `rm -rf node_modules/.vite`
3. Reinstall: `npm install`
4. Rebuild: `npm run build`

### Development Server Issues

If dev server won't start:

1. Check if port 3000 is in use
2. Try a different port: `npm run dev -- --port 3001`
3. Clear cache and restart

## Development Tips

### Hot Module Replacement

Vite supports HMR out of the box. Changes to components will update instantly without full page reload.

### Component Development

Use React DevTools for debugging components:
- Install browser extension
- Inspect component tree
- Debug props and state

### API Testing

Test API calls in the browser console:

```javascript
import { fetchTopArticles } from './services/api';
const result = await fetchTopArticles();
console.log(result);
```

## Performance Optimization

### Code Splitting

Vite automatically code-splits routes. Large components can be lazy-loaded:

```javascript
const HeavyComponent = lazy(() => import('./HeavyComponent'));
```

### Image Optimization

- Use WebP format when possible
- Lazy load images below the fold
- Serve appropriate sizes for different devices

### Bundle Size

Check bundle size:

```bash
npm run build -- --mode production
```

Analyze with Vite bundle analyzer if needed.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally with `npm run dev`
4. Build and test: `npm run build && npm run preview`
5. Submit a pull request

## License

MIT License
