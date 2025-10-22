import React from 'react'

const NewsCard = ({ article, size = 'small', onRequestSummary }) => {
  // Determine if this is headline 5 or 6 (should have image below title)
  const isImageBelowTitle = size === 'medium' || (size === 'small' && (article.id === 5 || article.id === 6));
  const isHorizontal = size === 'horizontal';
  
  // Function to format summary with proper paragraph breaks
  const formatSummary = (summary) => {
    if (!summary) return '';
    
    // Split by double newlines or periods followed by space and capital letter
    const paragraphs = summary
      .split(/\n\n|\. (?=[A-Z])/)
      .filter(p => p.trim().length > 0)
      .map(p => p.trim());
    
    return paragraphs;
  };
  
  const sizeClasses = {
    large: 'col-span-2 row-span-2',
    medium: 'col-span-1 row-span-1',
    small: 'col-span-1 row-span-1',
    horizontal: 'col-span-2'
  }

  const textSizeClasses = {
    large: 'text-lg',
    medium: 'text-sm',
    small: 'text-xs',
    horizontal: 'text-base'
  }

  const summarySizeClasses = {
    large: 'text-sm',
    medium: 'text-xs',
    small: 'text-xs',
    horizontal: 'text-xs'
  }

  const handleCardClick = () => {
    if (article.url) {
      window.open(article.url, '_blank', 'noopener,noreferrer')
    }
  }

  const handleAISummary = (e) => {
    e.stopPropagation()
    // Trigger AI summary request via App-level state
    if (onRequestSummary) {
      onRequestSummary(article)
    }
  }


  const renderImage = () => {
    console.log(`Rendering image for article ${article.id}:`, {
      title: article.headline.substring(0, 30),
      imageUrl: article.imageUrl,
      hasImageUrl: !!article.imageUrl
    });
    
    if (article.imageUrl) {
      return (
        <img 
          src={article.imageUrl} 
          alt={article.headline}
          className="w-full h-full object-cover"
          onLoad={() => console.log(`✅ Image loaded for article ${article.id}`)}
          onError={(e) => {
            console.log(`❌ Image failed to load for article ${article.id}:`, article.imageUrl);
            e.target.style.display = 'none'
            e.target.parentElement.querySelector('.fallback-icon')?.classList.remove('hidden')
          }}
        />
      )
    }
    console.log(`❌ No imageUrl for article ${article.id}`);
    return null
  }

  // Horizontal layout for Row 2
  if (isHorizontal) {
    return (
      <div onClick={handleCardClick} className="bg-white rounded-xl shadow-md hover:shadow-lg hover:scale-[1.01] transition-all duration-300 p-6 cursor-pointer w-full overflow-y-auto group">
        {/* Top Section: Source and Title */}
        <div className="mb-4">
          {/* Source and Time */}
          <div className="text-xs text-gray-500 mb-2">
            {article.source} • {article.timeAgo}
          </div>
          
          {/* Headline */}
          <h2 className="text-lg font-bold text-gray-800 leading-tight line-clamp-2">
            {article.headline}
          </h2>
        </div>

        {/* Middle Section: Two-column layout */}
        <div className="flex gap-4 mb-4">
          {/* Left Column: Photo */}
          <div className="flex-shrink-0 w-1/4">
            <div className="w-full h-32 bg-gray-200 rounded-lg overflow-hidden relative">
              {renderImage()}
              {!article.imageUrl && (
                <div className="fallback-icon bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 h-full">
                  <div className="text-center">
                    <div className="text-2xl mb-1">📰</div>
                    <div className="text-xs font-medium">News Image</div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Right Column: Summary */}
          <div className="flex-1">
            {article.summary && (
              <div className="text-sm text-gray-600 leading-relaxed space-y-2">
                {formatSummary(article.summary).slice(0, 2).map((paragraph, index) => (
                  <p key={index} className="mb-2 last:mb-0">
                    {paragraph}
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Bottom Section: Continued Summary and Action Buttons */}
        <div className="flex justify-between items-end">
          {/* Continued Summary */}
          {article.summary && formatSummary(article.summary).length > 2 && (
            <div className="flex-1 mr-4">
              <div className="text-sm text-gray-600 leading-relaxed">
                {formatSummary(article.summary).slice(2, 3).map((paragraph, index) => (
                  <p key={index} className="mb-1">
                    {paragraph}
                  </p>
                ))}
              </div>
              <div className="mt-1 text-xs text-purple-600 font-medium">
                Read full article →
              </div>
            </div>
          )}
          
          {/* Action Buttons - Bottom Right */}
          <div className="flex gap-2 flex-shrink-0">
            {/* AI Summary Button - Purple */}
            <button
              onClick={handleAISummary}
              className="bg-purple-600 hover:bg-purple-700 text-white rounded-full shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center w-8 h-8 text-sm"
              title="AI Summary"
            >
              <span>✨</span>
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
      <div
        onClick={handleCardClick}
        className={`
          ${sizeClasses[size]}
          bg-white 
          rounded-xl 
          shadow-md 
          hover:shadow-lg
          hover:scale-[1.01]
          transition-all 
          duration-300 
          p-5 
          cursor-pointer
          h-full
          w-full
          flex
          flex-col
          overflow-y-auto
          group
        `}
      >
      <div className="flex-1 flex flex-col min-h-0">
        {/* Top Section: Source and Title */}
        <div className="mb-3">
          {/* Source and Time */}
          <div className="text-xs text-gray-500 mb-2">
            {article.source} • {article.timeAgo}
          </div>
          
          {/* Headline */}
          <h2 className={`${textSizeClasses[size]} font-bold text-gray-800 mb-3 leading-tight ${
            size === 'small' ? 'line-clamp-2' : size === 'medium' ? 'line-clamp-2' : 'line-clamp-3'
          }`}>
            {article.headline}
          </h2>
        </div>

        {/* Middle Section: Image */}
        <div className="mb-3">
          <div className={`w-full bg-gray-200 rounded-lg overflow-hidden flex-shrink-0 relative ${
            size === 'large' ? 'h-24' : size === 'medium' ? 'h-20' : 'h-16'
          }`}>
            {renderImage()}
            {!article.imageUrl && (
              <div className="fallback-icon bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 absolute inset-0">
                <div className="text-center">
                  <div className={`${size === 'large' ? 'text-xl' : size === 'medium' ? 'text-lg' : 'text-base'} mb-1`}>📰</div>
                  <div className="text-[10px] font-medium">News Image</div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Bottom Section: Summary */}
        {article.summary && (
          <div className="flex-1 overflow-y-auto">
            <div className={`${summarySizeClasses[size]} text-gray-600 leading-relaxed space-y-2`}>
              {formatSummary(article.summary).slice(0, 2).map((paragraph, index) => (
                <p key={index} className="mb-2 last:mb-0">
                  {paragraph}
                </p>
              ))}
            </div>
            <div className="mt-2 text-xs text-purple-600 font-medium">
              Read full article →
            </div>
          </div>
        )}
      </div>
      
      {/* Action Buttons - Bottom Right */}
      <div className="flex justify-end gap-1 mt-1 flex-shrink-0">
        {/* AI Summary Button - Purple */}
        <button
          onClick={handleAISummary}
          className={`
            bg-purple-600 
            hover:bg-purple-700 
            text-white 
            rounded-full 
            shadow-md 
            hover:shadow-lg 
            transition-all 
            duration-200
            flex 
            items-center 
            justify-center
            flex-shrink-0
            ${size === 'large' ? 'w-7 h-7 text-sm' : size === 'medium' ? 'w-6 h-6 text-xs' : 'w-5 h-5 text-xs'}
          `}
          title="AI Summary"
        >
          <span>✨</span>
        </button>
      </div>
    </div>
  )
}

export default NewsCard

