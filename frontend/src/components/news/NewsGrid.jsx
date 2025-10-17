import React from 'react'
import NewsCard from './NewsCard'

const NewsGrid = () => {
  const newsArticles = [
    { id: 1, headline: 'Headline 1', size: 'large' },
    { id: 2, headline: 'Headline 2', size: 'medium' },
    { id: 3, headline: 'Headline 3', size: 'medium' },
    { id: 4, headline: 'Headline 4', size: 'small' },
    { id: 5, headline: 'Headline 5', size: 'small' },
    { id: 6, headline: 'Headline 6', size: 'small' },
    { id: 7, headline: 'Headline 7', size: 'small' },
    { id: 8, headline: 'Headline 8', size: 'small' },
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-3 auto-rows-[200px] gap-4">
        {newsArticles.map((article) => (
          <NewsCard
            key={article.id}
            headline={article.headline}
            size={article.size}
          />
        ))}
      </div>
    </div>
  )
}

export default NewsGrid

