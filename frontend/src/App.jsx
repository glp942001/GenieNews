import React from 'react'
import Header from './components/layout/Header'
import NewsGrid from './components/news/NewsGrid'
import AIChat from './components/chat/AIChat'

function App() {
  return (
    <div className="min-h-screen" style={{backgroundColor: '#fcfaf4'}}>
      <Header />
      <div className="pl-6 pr-0">
        <div className="grid grid-cols-1 lg:grid-cols-7 gap-8 h-[calc(100vh-120px)] w-full">
          {/* News Grid - Takes up 5 columns on large screens */}
          <div className="lg:col-span-5 py-8">
            <NewsGrid />
          </div>
          
          {/* AI Chat - Takes up 2 columns on large screens (reduced by ~30%) */}
          <div className="lg:col-span-2">
            <AIChat />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

