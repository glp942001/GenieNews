# GenieNews Frontend

AI-powered weekly news hub built with React and Tailwind CSS.

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

This will start the development server at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── layout/
│   │   └── Header.jsx          # Purple header with GenieNews title
│   └── news/
│       ├── NewsCard.jsx         # Reusable news card component
│       └── NewsGrid.jsx         # Grid layout for news articles
├── styles/
│   └── index.css                # Global styles with Tailwind directives
├── App.jsx                      # Main application component
└── index.js                     # Application entry point
```

## Features

- **Modern UI**: Built with React 18 and Tailwind CSS
- **Responsive Grid Layout**: CSS Grid-based layout with varying card sizes
- **Component-Based**: Modular, reusable components
- **Fast Development**: Vite for lightning-fast HMR

## Tech Stack

- React 18.3
- Tailwind CSS 3.4
- Vite 5.2
- PostCSS & Autoprefixer

