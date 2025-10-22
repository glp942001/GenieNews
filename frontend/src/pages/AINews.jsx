import React from 'react'
import NewsGrid from '../components/news/NewsGrid'

const AINews = ({ onRequestSummary }) => {
  return (
    <div className="py-8">
      <NewsGrid onRequestSummary={onRequestSummary} />
    </div>
  )
}

export default AINews

