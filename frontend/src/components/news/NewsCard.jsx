import React from 'react'

const NewsCard = ({ headline, size = 'small' }) => {
  const sizeClasses = {
    large: 'col-span-2 row-span-2',
    medium: 'col-span-1 row-span-1',
    small: 'col-span-1 row-span-1'
  }

  const textSizeClasses = {
    large: 'text-3xl',
    medium: 'text-xl',
    small: 'text-lg'
  }

  return (
    <div
      className={`
        ${sizeClasses[size]}
        bg-white 
        border-2 
        border-gray-200 
        rounded-lg 
        shadow-md 
        hover:shadow-xl 
        hover:border-purple-400
        transition-all 
        duration-300 
        p-6 
        flex 
        items-center 
        justify-center
        cursor-pointer
      `}
    >
      <h2 className={`${textSizeClasses[size]} font-semibold text-gray-800 text-center`}>
        {headline}
      </h2>
    </div>
  )
}

export default NewsCard

