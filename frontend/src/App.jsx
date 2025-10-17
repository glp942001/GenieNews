import React from 'react'
import Header from './components/layout/Header'
import NewsGrid from './components/news/NewsGrid'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <NewsGrid />
    </div>
  )
}

export default App

