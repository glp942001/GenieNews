import React from 'react'

const NewsCard = ({ article, size = 'small' }) => {
  // Determine if this is headline 5 or 6 (should have image below title)
  const isImageBelowTitle = size === 'medium' || (size === 'small' && (article.id === 5 || article.id === 6));
  const sizeClasses = {
    large: 'col-span-2 row-span-2',
    medium: 'col-span-1 row-span-1',
    small: 'col-span-1 row-span-1'
  }

  const textSizeClasses = {
    large: 'text-2xl',
    medium: 'text-lg',
    small: 'text-sm'
  }

  const summarySizeClasses = {
    large: 'text-sm',
    medium: 'text-xs',
    small: 'text-xs'
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
        justify-between
      `}
    >
      <div className="flex-1 flex flex-col">
        {/* For medium containers and headlines 5&6, show title first, then image */}
        {isImageBelowTitle ? (
          <>
            {/* Source and Time */}
            <div className="text-xs text-gray-500 mb-2">
              {article.source} • {article.timeAgo}
            </div>
            
            {/* Headline */}
            <h2 className={`${textSizeClasses[size]} font-semibold text-gray-800 mb-2 leading-tight overflow-hidden ${
              size === 'small' ? 'h-10' : size === 'medium' ? 'h-14' : 'h-18'
            }`}>
              {article.headline}
            </h2>
            
            {/* Mock Image Placeholder - below title for medium */}
            <div className="w-full mb-2 bg-gray-200 rounded-lg overflow-hidden">
              <div className={`bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 ${
                size === 'large' ? 'h-40' : size === 'medium' ? 'h-24' : 'h-16'
              }`}>
                <div className="text-center">
                  <div className={`${size === 'large' ? 'text-3xl' : size === 'medium' ? 'text-2xl' : 'text-xl'} mb-1`}>📰</div>
                  <div className={`${size === 'large' ? 'text-xs' : 'text-xs'} font-medium`}>News Image</div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* For large containers and headlines 7&8, show image first */}
            {/* Mock Image Placeholder */}
            <div className="w-full mb-2 bg-gray-200 rounded-lg overflow-hidden">
              <div className={`bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-gray-600 ${
                size === 'large' ? 'h-40' : size === 'medium' ? 'h-24' : 'h-16'
              }`}>
                <div className="text-center">
                  <div className={`${size === 'large' ? 'text-3xl' : size === 'medium' ? 'text-2xl' : 'text-xl'} mb-1`}>📰</div>
                  <div className={`${size === 'large' ? 'text-xs' : 'text-xs'} font-medium`}>News Image</div>
                </div>
              </div>
            </div>
            
            {/* Source and Time */}
            <div className="text-xs text-gray-500 mb-2">
              {article.source} • {article.timeAgo}
            </div>
            
            {/* Headline */}
            <h2 className={`${textSizeClasses[size]} font-semibold text-gray-800 mb-1 leading-tight overflow-hidden ${
              size === 'small' ? 'h-10' : size === 'medium' ? 'h-14' : 'h-18'
            }`}>
              {article.headline}
            </h2>
            
            {/* Summary for large cards */}
            {size === 'large' && article.summary && (
              <p className={`${summarySizeClasses[size]} text-gray-600 leading-relaxed mb-3`}>
                {article.summary}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default NewsCard

