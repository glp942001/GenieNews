import React, { useState, useEffect, useRef } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import Header from './components/layout/Header'
import AIChat from './components/chat/AIChat'
import AINews from './pages/AINews'
import FintechNews from './pages/FintechNews'
import CreditGenieNews from './pages/CreditGenieNews'

function AppContent() {
  // Initialize sidebar width from localStorage or default to 400px
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const saved = localStorage.getItem('aiChatWidth')
    return saved ? parseInt(saved) : 400
  })
  const [isResizing, setIsResizing] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(() => {
    const saved = localStorage.getItem('aiChatOpen')
    return saved !== null ? saved === 'true' : true // Default to open
  })
  const containerRef = useRef(null)

  // Save width to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('aiChatWidth', sidebarWidth.toString())
  }, [sidebarWidth])

  // Save chat open state to localStorage
  useEffect(() => {
    localStorage.setItem('aiChatOpen', isChatOpen.toString())
  }, [isChatOpen])

  // Handle mouse move during resize
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing || !containerRef.current) return

      const containerRect = containerRef.current.getBoundingClientRect()
      const newWidth = containerRect.right - e.clientX
      
      // Set min and max width constraints
      const minWidth = 300
      const maxWidth = containerRect.width * 0.6 // Max 60% of container width
      
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setSidebarWidth(newWidth)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.body.style.cursor = 'default'
      document.body.style.userSelect = 'auto'
    }

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing])

  const handleResizeStart = () => {
    setIsResizing(true)
  }

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen)
  }

  return (
    <div style={{backgroundColor: '#fcfaf4', height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column'}}>
      <Header />
      
      {/* All pages with resizable chat */}
      <div className="p-0 m-0" style={{ flex: 1, overflow: 'hidden' }}>
        <div 
          ref={containerRef}
          className="flex gap-0 w-full h-full relative"
        >
          {/* Page Content - Takes up remaining space */}
          <div className={`flex-1 overflow-auto pl-6 ${isChatOpen ? 'pr-10' : 'pr-16'}`}>
            <Routes>
              <Route path="/" element={<AINews />} />
              <Route path="/fintech" element={<FintechNews />} />
              <Route path="/credit-genie" element={<CreditGenieNews />} />
            </Routes>
          </div>
          
          {isChatOpen ? (
            <>
              {/* Resize Handle */}
              <div
                onMouseDown={handleResizeStart}
                className={`w-1 bg-gray-300 hover:bg-purple-500 cursor-col-resize transition-colors relative group ${
                  isResizing ? 'bg-purple-500' : ''
                }`}
                style={{ flexShrink: 0 }}
              >
                {/* Visual indicator */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-400 group-hover:bg-purple-600 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  <div className="flex space-x-0.5">
                    <div className="w-0.5 h-4 bg-white rounded"></div>
                    <div className="w-0.5 h-4 bg-white rounded"></div>
                  </div>
                </div>
              </div>
              
              {/* AI Chat - Fixed width controlled by state, extends to bottom */}
              <div 
                style={{ 
                  width: `${sidebarWidth}px`,
                  flexShrink: 0,
                  height: '100%'
                }}
                className="overflow-visible relative"
              >
                {/* Close Button - Anchored to chat border */}
                <button
                  onClick={toggleChat}
                  className="absolute top-1/2 -translate-y-1/2 -left-3.5 w-7 h-7 bg-purple-600 hover:bg-purple-700 text-white rounded-full flex items-center justify-center shadow-lg z-20"
                  title="Close sidebar"
                >
                  <svg 
                    width="16" 
                    height="16" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  >
                    {/* Right-pointing chevron (collapse icon) */}
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </button>
                <AIChat />
              </div>
            </>
          ) : (
            /* Open Chat Button - When chat is closed */
            <button 
              className="absolute top-1/2 -translate-y-1/2 right-4 bg-purple-600 hover:bg-purple-700 cursor-pointer transition-all shadow-lg flex items-center justify-center rounded-full w-8 h-8 z-10"
              onClick={toggleChat}
              title="Open sidebar"
            >
              <svg 
                width="18" 
                height="18" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className="text-white"
              >
                {/* Left-pointing chevron (expand icon) */}
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}

export default App

