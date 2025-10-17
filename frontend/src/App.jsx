import React from 'react'
import Header from './components/layout/Header'
import NewsGrid from './components/news/NewsGrid'
import AIChat from './components/chat/AIChat'

function App() {
  return (
    <div className="min-h-screen" style={{backgroundColor: '#fcfaf4'}}>
      <Header />
      <div className="px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-6 gap-8 h-[calc(100vh-200px)] w-full">
          {/* News Grid - Takes up 4 columns on large screens */}
          <div className="lg:col-span-4">
            <NewsGrid />
          </div>
          
          {/* AI Chat - Takes up 2 columns on large screens (reduced by ~20%) */}
          <div className="lg:col-span-2">
            <AIChat />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

