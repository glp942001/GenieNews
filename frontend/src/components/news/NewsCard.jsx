import React from 'react'

const NewsCard = ({ article, size = 'small' }) => {
  // Determine if this is headline 5 or 6 (should have image below title)
  const isImageBelowTitle = size === 'medium' || (size === 'small' && (article.id === 5 || article.id === 6));
  const isHorizontal = size === 'horizontal';
  
  const sizeClasses = {
    large: 'col-span-2 row-span-2',
    medium: 'col-span-1 row-span-1',
    small: 'col-span-1 row-span-1',
    horizontal: 'col-span-2'
  }

  const textSizeClasses = {
    large: 'text-lg',
    medium: 'text-sm',
    small: 'text-xs'
  }

  const summarySizeClasses = {
    large: 'text-xs',
    medium: 'text-[11px]',
    small: 'text-[10px]'
  }

  const handleAISummary = (e) => {
    e.stopPropagation()
    // TODO: Implement AI summary functionality
    console.log('AI Summary clicked for:', article.headline)
  }

  const handleVoice = (e) => {
    e.stopPropagation()
    // TODO: Implement voice/read aloud functionality
    console.log('Voice button clicked for:', article.headline)
  }

  // Horizontal layout for Row 2
  if (isHorizontal) {
    return (
      <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 p-4 cursor-pointer w-full overflow-hidden">
        <div className="flex gap-6 h-full">
          {/* Left side: Title and Image */}
          <div className="flex-shrink-0 w-1/3 flex flex-col">
            {/* Source and Time */}
            <div className="text-xs text-gray-500 mb-2">
              {article.source} • {article.timeAgo}
            </div>
            
            {/* Headline */}
            <h2 className="text-lg font-semibold text-gray-800 mb-3 leading-tight line-clamp-3">
              {article.headline}
            </h2>
            
            {/* Image */}
            <div className="w-full bg-gray-200 rounded-lg overflow-hidden flex-1">
              <div className="bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 h-full min-h-[200px]">
                <div className="text-center">
                  <div className="text-3xl mb-1">📰</div>
                  <div className="text-xs font-medium">News Image</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Right side: Summary and Buttons */}
          <div className="flex-1 flex flex-col">
            {/* Summary */}
            {article.summary && (
              <p className="text-sm text-gray-700 leading-snug line-clamp-8 flex-1">
                {article.summary}
              </p>
            )}
            
            {/* Action Buttons - Bottom Right */}
            <div className="flex justify-end gap-2 mt-3 flex-shrink-0">
              {/* Voice Button - Blue */}
              <button
                onClick={handleVoice}
                className="bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center flex-shrink-0 w-9 h-9 text-lg"
                title="Read Aloud"
              >
                <span>🔊</span>
              </button>
              
              {/* AI Summary Button - Purple */}
              <button
                onClick={handleAISummary}
                className="bg-purple-600 hover:bg-purple-700 text-white rounded-full shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center flex-shrink-0 w-9 h-9 text-lg"
                title="AI Summary"
              >
                <span>✨</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`
        ${sizeClasses[size]}
        bg-white 
        rounded-2xl 
        shadow-md 
        hover:shadow-xl
        transition-all 
        duration-300 
        p-4 
        cursor-pointer
        h-full
        w-full
        flex
        flex-col
        overflow-hidden
      `}
    >
      <div className="flex-1 flex flex-col min-h-0">
        {/* For medium containers and headlines 5&6, show title first, then image */}
        {isImageBelowTitle ? (
          <>
            {/* Source and Time */}
            <div className="text-xs text-gray-500 mb-2">
              {article.source} • {article.timeAgo}
            </div>
            
            {/* Headline */}
            <h2 className={`${textSizeClasses[size]} font-semibold text-gray-800 mb-2 leading-tight ${
              size === 'small' ? 'line-clamp-2' : size === 'medium' ? 'line-clamp-2' : 'line-clamp-3'
            }`}>
              {article.headline}
            </h2>
            
            {/* Mock Image Placeholder - below title for medium */}
            <div className="w-full mb-2 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
              <div className={`bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 ${
                size === 'large' ? 'h-40' : size === 'medium' ? 'h-24' : 'h-20'
              }`}>
                <div className="text-center">
                  <div className={`${size === 'large' ? 'text-2xl' : size === 'medium' ? 'text-xl' : 'text-lg'} mb-1`}>📰</div>
                  <div className="text-[10px] font-medium">News Image</div>
                </div>
              </div>
            </div>
            
            {/* Summary */}
            {article.summary && (
              <p className={`${summarySizeClasses[size]} text-gray-700 leading-snug ${
                size === 'large' ? 'line-clamp-6' : 'line-clamp-4'
              }`}>
                {article.summary}
              </p>
            )}
          </>
        ) : (
          <>
            {/* For large containers and headlines 7&8, show image first */}
            {/* Mock Image Placeholder */}
            <div className="w-full mb-2 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
              <div className={`bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 ${
                size === 'large' ? 'h-40' : size === 'medium' ? 'h-24' : 'h-20'
              }`}>
                <div className="text-center">
                  <div className={`${size === 'large' ? 'text-2xl' : size === 'medium' ? 'text-xl' : 'text-lg'} mb-1`}>📰</div>
                  <div className="text-[10px] font-medium">News Image</div>
                </div>
              </div>
            </div>
            
            {/* Source and Time */}
            <div className="text-xs text-gray-500 mb-1 truncate">
              {article.source} • {article.timeAgo}
            </div>
            
            {/* Headline */}
            <h2 className={`${textSizeClasses[size]} font-semibold text-gray-800 mb-2 leading-tight ${
              size === 'small' ? 'line-clamp-2' : size === 'medium' ? 'line-clamp-2' : 'line-clamp-3'
            }`}>
              {article.headline}
            </h2>
            
            {/* Summary */}
            {article.summary && (
              <p className={`${summarySizeClasses[size]} text-gray-700 leading-snug ${
                size === 'large' ? 'line-clamp-8' : size === 'medium' ? 'line-clamp-5' : 'line-clamp-4'
              }`}>
                {article.summary}
              </p>
            )}
          </>
        )}
      </div>
      
      {/* Action Buttons - Bottom Right */}
      <div className="flex justify-end gap-2 mt-1.5 flex-shrink-0">
        {/* Voice Button - Blue */}
        <button
          onClick={handleVoice}
          className={`
            bg-blue-600 
            hover:bg-blue-700 
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
            ${size === 'large' ? 'w-9 h-9 text-lg' : size === 'medium' ? 'w-7 h-7 text-sm' : 'w-6 h-6 text-xs'}
          `}
          title="Read Aloud"
        >
          <span>🔊</span>
        </button>
        
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
            ${size === 'large' ? 'w-9 h-9 text-lg' : size === 'medium' ? 'w-7 h-7 text-sm' : 'w-6 h-6 text-xs'}
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

