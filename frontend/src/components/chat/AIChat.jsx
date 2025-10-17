import React, { useState } from 'react'

const AIChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your AI assistant. I can help you summarize news articles or answer questions about the latest AI developments. What would you like to know?",
      isAI: true,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputText.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputText,
      isAI: false,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    // Simulate AI response (replace with actual API call later)
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        text: "I understand you're asking about: \"" + inputText + "\". This is a mock response. In the future, I'll be able to analyze and summarize the news articles for you!",
        isAI: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
      setIsLoading(false)
    }, 1500)
  }

  const quickActions = [
    "Summarize today's news",
    "What's the latest on AI?",
    "Explain GPT-5",
    "AI funding trends"
  ]

  const handleQuickAction = (action) => {
    setInputText(action)
  }

  return (
    <div className="bg-gray-900 border-2 border-gray-700 shadow-md h-full flex flex-col min-h-[600px]">
      {/* Chat Header */}
      <div className="bg-gray-800 text-white p-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold">AI Assistant</h3>
        <p className="text-sm text-gray-300">Ask me about the news</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isAI ? 'justify-start' : 'justify-end'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.isAI
                  ? 'bg-gray-700 text-gray-100'
                  : 'bg-purple-600 text-white'
              }`}
            >
              <p className="text-sm">{message.text}</p>
              <p className={`text-xs mt-1 ${
                message.isAI ? 'text-gray-400' : 'text-purple-200'
              }`}>
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="px-4 pb-2">
        <p className="text-xs text-gray-400 mb-2">Quick actions:</p>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action)}
              className="px-3 py-1 bg-gray-700 text-gray-200 text-xs rounded-full hover:bg-gray-600 transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask about the news..."
            className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default AIChat
