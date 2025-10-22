/**
 * API service for fetching articles from the GenieNews backend
 */

// Use environment variable for API URL, fallback to relative path for production
// In production on Sevalla, the frontend and backend are served from the same domain
const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : (import.meta.env.DEV ? 'http://localhost:8000/api' : '/api');

// Debug logging to help troubleshoot
console.log('API Configuration:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_BASE_URL: API_BASE_URL,
  NODE_ENV: import.meta.env.MODE
});

/**
 * Calculate time ago from published date
 */
function getTimeAgo(publishedAt) {
  const now = new Date();
  const published = new Date(publishedAt);
  const diffMs = now - published;
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffHours < 1) {
    const diffMins = Math.floor(diffMs / (1000 * 60));
    return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  } else {
    const diffWeeks = Math.floor(diffDays / 7);
    return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`;
  }
}

/**
 * Transform backend article data to frontend format
 */
function transformArticle(backendArticle) {
  // Use detailed summary for longer excerpts, fallback to short summary
  let excerpt = '';
  if (backendArticle.summary_detailed && backendArticle.summary_detailed.length > 100) {
    // Use detailed summary for rich excerpts
    excerpt = backendArticle.summary_detailed;
  } else if (backendArticle.summary_short) {
    // Fallback to short summary
    excerpt = backendArticle.summary_short;
  } else {
    // Last resort: use title as excerpt
    excerpt = backendArticle.title;
  }

  const transformed = {
    id: backendArticle.id,
    headline: backendArticle.title,
    source: backendArticle.source_name || 'Unknown Source',
    timeAgo: getTimeAgo(backendArticle.published_at),
    summary: excerpt, // Now using longer, more detailed content
    tags: backendArticle.ai_tags || [],
    url: backendArticle.url,
    imageUrl: backendArticle.cover_media?.url || null,
    relevanceScore: backendArticle.relevance_score || 0
  };
  
  // Debug logging
  console.log(`Article ${transformed.id}:`, {
    title: transformed.headline.substring(0, 50),
    hasCoverMedia: !!backendArticle.cover_media,
    imageUrl: transformed.imageUrl,
    coverMediaUrl: backendArticle.cover_media?.url,
    coverMediaData: backendArticle.cover_media
  });
  
  return transformed;
}

/**
 * Fetch top AI-ranked articles
 */
export async function fetchTopArticles(limit = 8) {
  try {
    // Add cache-busting parameter to ensure fresh data
    const timestamp = new Date().getTime();
    const response = await fetch(
      `${API_BASE_URL}/articles/?ordering=-relevance_score&page_size=${limit}&_t=${timestamp}`,
      {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Debug logging
    console.log('API Response:', data);
    console.log('Number of articles:', data.results.length);
    console.log('Articles with images:', data.results.filter(a => a.cover_media).length);
    
    // Transform backend data to frontend format
    const articles = data.results.map(transformArticle);
    
    return {
      success: true,
      articles,
      count: data.count
    };
  } catch (error) {
    console.error('Error fetching articles:', error);
    
    // Check if it's a connection refused error (backend not running)
    if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED')) {
      console.warn('Backend server is not running. Please start the backend server or deploy to production.');
      return {
        success: false,
        articles: [],
        error: 'Backend server is not running. Please start the Django server with: cd backend && python manage.py runserver'
      };
    }
    
    return {
      success: false,
      articles: [],
      error: error.message
    };
  }
}

/**
 * Fetch a single article by ID
 */
export async function fetchArticle(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/articles/${id}/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return {
      success: true,
      article: transformArticle(data)
    };
  } catch (error) {
    console.error('Error fetching article:', error);
    return {
      success: false,
      article: null,
      error: error.message
    };
  }
}

/**
 * Generate structured AI summary for an article
 */
export async function generateArticleSummary(articleId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/chat/summary/${articleId}/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return {
      success: true,
      summary: data
    };
  } catch (error) {
    console.error('Error generating article summary:', error);
    return {
      success: false,
      summary: null,
      error: error.message
    };
  }
}

/**
 * Send a chat message to the AI assistant
 */
export async function sendChatMessage(message, conversationHistory = []) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/chat/message/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          history: conversationHistory
        }),
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return {
      success: true,
      response: data.response,
      timestamp: data.timestamp
    };
  } catch (error) {
    console.error('Error sending chat message:', error);
    return {
      success: false,
      response: null,
      error: error.message
    };
  }
}

/**
 * Generate or retrieve daily audio news segment
 */
export async function generateDailyAudioSegment() {
  try {
    const url = `${API_BASE_URL}/audio/daily-segment/`;
    console.log('Making API call to:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return {
      success: data.success,
      audioUrl: data.segment?.audio_url,
      scriptText: data.segment?.script_text,
      date: data.segment?.date,
      articleCount: data.segment?.article_count,
      durationSeconds: data.segment?.duration_seconds,
      cached: data.cached,
      error: null
    };
  } catch (error) {
    console.error('Error generating audio segment:', error);
    return {
      success: false,
      audioUrl: null,
      scriptText: null,
      date: null,
      articleCount: 0,
      cached: false,
      error: error.message
    };
  }
}

