import React, { useState, useEffect } from 'react'
import NewsCard from './NewsCard'
import AudioPlayer from './AudioPlayer'
import { fetchTopArticles } from '../../services/api'

const NewsGrid = ({ onRequestSummary }) => {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadArticles = async () => {
      setLoading(true)
      console.log('Loading articles with fresh data...')
      const result = await fetchTopArticles(8)
      
      if (result.success) {
        console.log('Articles loaded:', result.articles.length)
        console.log('Articles with images:', result.articles.filter(a => a.imageUrl).length)
        setArticles(result.articles)
        setError(null)
      } else {
        setError(result.error)
        console.error('Failed to load articles:', result.error)
      }
      
      setLoading(false)
    }

    loadArticles()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading AI-ranked news...</p>
        </div>
      </div>
    )
  }

  if (error) {
    // Check if it's a backend connection error
    const isBackendError = error.includes('Backend server is not running') || 
                          error.includes('Failed to fetch') || 
                          error.includes('ERR_CONNECTION_REFUSED');
    
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center bg-red-50 p-8 rounded-xl max-w-lg">
          <div className="text-4xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold text-red-800 mb-2">
            {isBackendError ? 'Backend Server Not Running' : 'Error Loading Articles'}
          </h3>
          <p className="text-red-600 mb-4">{error}</p>
          
          {isBackendError && (
            <div className="bg-blue-50 p-4 rounded-lg mb-4 text-left">
              <h4 className="font-semibold text-blue-800 mb-2">To fix this:</h4>
              <ol className="text-sm text-blue-700 space-y-1">
                <li>1. Open terminal in the project root</li>
                <li>2. Run: <code className="bg-blue-100 px-1 rounded">cd backend</code></li>
                <li>3. Run: <code className="bg-blue-100 px-1 rounded">python manage.py runserver</code></li>
                <li>4. Refresh this page</li>
              </ol>
            </div>
          )}
          
          <button 
            onClick={() => window.location.reload()} 
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (articles.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center bg-yellow-50 p-8 rounded-xl max-w-md">
          <div className="text-4xl mb-4">📰</div>
          <h3 className="text-xl font-semibold text-yellow-800 mb-2">No Articles Available</h3>
          <p className="text-yellow-600">No curated articles found. Please run article ingestion and curation first.</p>
        </div>
      </div>
    )
  }

  // Pad with empty placeholders if we have fewer than 6 articles
  const displayArticles = [...articles]
  while (displayArticles.length < 6) {
    displayArticles.push(null)
  }

  return (
    <div className="flex flex-col gap-6">
        {/* Row 1: Audio player spanning full width */}
        <div className="w-full">
          <AudioPlayer />
        </div>
        
        {/* Row 2: First news container */}
        <div className="w-full" style={{ minHeight: '140px' }}>
          {displayArticles[0] && <NewsCard article={displayArticles[0]} size="horizontal" onRequestSummary={onRequestSummary} />}
        </div>
        
        {/* Row 3: Second news container */}
        <div className="w-full" style={{ minHeight: '140px' }}>
          {displayArticles[1] && <NewsCard article={displayArticles[1]} size="horizontal" onRequestSummary={onRequestSummary} />}
        </div>
        
        {/* Row 4: Third news container */}
        <div className="w-full" style={{ minHeight: '140px' }}>
          {displayArticles[2] && <NewsCard article={displayArticles[2]} size="horizontal" onRequestSummary={onRequestSummary} />}
        </div>
        
        {/* Row 5: Fourth news container */}
        <div className="w-full" style={{ minHeight: '140px' }}>
          {displayArticles[3] && <NewsCard article={displayArticles[3]} size="horizontal" onRequestSummary={onRequestSummary} />}
        </div>
        
        {/* Row 6: Fifth news container */}
        <div className="w-full" style={{ minHeight: '140px' }}>
          {displayArticles[4] && <NewsCard article={displayArticles[4]} size="horizontal" onRequestSummary={onRequestSummary} />}
        </div>
        
        {/* Row 7: Sixth news container */}
        <div className="w-full" style={{ minHeight: '140px' }}>
          {displayArticles[5] && <NewsCard article={displayArticles[5]} size="horizontal" onRequestSummary={onRequestSummary} />}
        </div>
      </div>
  )
}

export default NewsGrid

