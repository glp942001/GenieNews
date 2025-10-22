import React, { useState, useEffect, useRef } from 'react'
import { generateArticleSummary, sendChatMessage } from '../../services/api'

const AIChat = ({ summaryRequest, onSummaryProcessed }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai-text',
      text: "Hi! I'm Genie-AI. Click the purple ✨ button on any article to get a detailed summary, or ask me questions about the latest AI news!",
      isAI: true,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle article summary requests from parent
  useEffect(() => {
    if (summaryRequest) {
      handleArticleSummary(summaryRequest)
      onSummaryProcessed()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [summaryRequest])

  // Generate conversation history for API calls
  const getConversationHistory = () => {
    return messages
      .filter(msg => msg.type === 'ai-text' || msg.type === 'user')
      .slice(-6) // Keep last 6 messages
      .map(msg => ({
        role: msg.isAI ? 'assistant' : 'user',
        content: msg.text
      }))
  }

  const handleArticleSummary = async (request) => {
    setIsLoading(true)

    try {
      const result = await generateArticleSummary(request.articleId)
      
      if (result.success) {
        const summaryMessage = {
          id: Date.now(),
          type: 'article-summary',
          articleId: result.summary.article_id,
          title: result.summary.title,
          source: result.summary.source,
          url: result.summary.url,
          sections: result.summary.sections,
          isAI: true,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, summaryMessage])
      } else {
        // Error message
        const errorMessage = {
          id: Date.now(),
          type: 'ai-text',
          text: `Sorry, I couldn't generate a summary for that article. Error: ${result.error}`,
          isAI: true,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Error generating summary:', error)
      const errorMessage = {
        id: Date.now(),
        type: 'ai-text',
        text: 'Sorry, something went wrong while generating the summary. Please try again.',
        isAI: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputText.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputText,
      isAI: false,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const messageToSend = inputText
    setInputText('')
    setIsLoading(true)

    try {
      const conversationHistory = getConversationHistory()
      const result = await sendChatMessage(messageToSend, conversationHistory)
      
      if (result.success) {
        const aiResponse = {
          id: Date.now() + 1,
          type: 'ai-text',
          text: result.response,
          isAI: true,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, aiResponse])
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'ai-text',
          text: `Sorry, I couldn't process your message. Error: ${result.error}`,
          isAI: true,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai-text',
        text: 'Sorry, something went wrong. Please try again.',
        isAI: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const quickActions = [
    "What are the top stories?",
    "Any AI breakthroughs?",
    "Summarize key trends",
    "What's most important?"
  ]

  const handleQuickAction = (action) => {
    setInputText(action)
  }

  // Render different message types
  const renderMessage = (message) => {
    if (message.type === 'article-summary') {
      return (
        <div className="flex justify-start">
          <div className="max-w-[90%] bg-gray-700 text-gray-100 p-3 rounded-lg shadow-lg">
            <div className="mb-2 pb-2 border-b border-gray-600">
              <h4 className="font-bold text-sm mb-1">{message.title}</h4>
              <p className="text-xs text-gray-300">{message.source}</p>
            </div>
            
            {message.sections.categories && Array.isArray(message.sections.categories) ? (
              <div className="space-y-4">
                {message.sections.categories.map((category, catIndex) => (
                  <div key={catIndex} className="space-y-2">
                    <h5 className="font-semibold text-sm text-gray-300 border-b border-gray-600 pb-1">
                      {category.name}
                    </h5>
                    <ul className="space-y-2">
                      {category.points.map((point, pointIndex) => (
                        <li key={pointIndex} className="text-xs leading-relaxed flex items-start">
                          <span className="text-gray-400 mr-2 mt-0.5">•</span>
                          <span className="flex-1">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ) : Array.isArray(message.sections.keypoints) && message.sections.keypoints.length > 0 ? (
              <div className="space-y-1">
                <h5 className="font-semibold text-xs mb-1 text-gray-300">🔑 Key Points</h5>
                <ul className="space-y-0.5">
                  {message.sections.keypoints.map((point, index) => (
                    <li key={index} className="text-xs leading-relaxed flex items-start">
                      <span className="text-gray-400 mr-1 mt-0.5">•</span>
                      <span>{point.replace('• ', '')}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : message.sections.what ? (
              <div className="space-y-3">
                <div>
                  <h5 className="font-semibold text-sm mb-1 text-gray-300">📋 WHAT</h5>
                  <p className="text-sm leading-relaxed">{message.sections.what}</p>
                </div>
                
                <div>
                  <h5 className="font-semibold text-sm mb-1 text-gray-300">💡 WHY IT MATTERS</h5>
                  <p className="text-sm leading-relaxed">{message.sections.why_it_matters}</p>
                </div>
                
                <div>
                  <h5 className="font-semibold text-sm mb-1 text-gray-300">🎯 TAKEAWAY</h5>
                  <p className="text-sm leading-relaxed">{message.sections.takeaway}</p>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <h5 className="font-semibold text-sm mb-2 text-gray-300">📄 Summary</h5>
                <p className="text-sm leading-relaxed text-gray-300">
                  No structured summary available for this article.
                </p>
              </div>
            )}
            
            <a 
              href={message.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-block mt-3 text-xs text-gray-300 hover:text-white underline"
            >
              Read full article →
            </a>
            
            <p className="text-xs mt-2 text-gray-400">
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </p>
          </div>
        </div>
      )
    }

    // Regular text messages
    return (
      <div className={`flex ${message.isAI ? 'justify-start' : 'justify-end'}`}>
        <div
          className={`max-w-[80%] p-2 rounded-lg ${
            message.isAI
              ? 'bg-gray-700 text-gray-100'
              : 'bg-purple-600 text-white'
          }`}
        >
          <p className="text-xs whitespace-pre-wrap">{message.text}</p>
          <p className={`text-xs mt-0.5 ${
            message.isAI ? 'text-gray-400' : 'text-purple-200'
          }`}>
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900 border-2 border-gray-700 shadow-md h-full flex flex-col">
      {/* Chat Header */}
      <div className="bg-gray-800 text-white p-3 pl-8 border-b border-gray-700">
        <h3 className="text-sm font-semibold">Genie-AI</h3>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-2 overflow-y-auto space-y-2">
        {messages.map((message) => (
          <div key={message.id}>
            {renderMessage(message)}
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
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-2 pb-1">
        <p className="text-xs text-gray-400 mb-1">Quick actions:</p>
        <div className="flex flex-wrap gap-1">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action)}
              className="px-2 py-1 bg-gray-700 text-gray-200 text-xs rounded-full hover:bg-gray-600 transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="p-2 border-t border-gray-700">
        <div className="flex space-x-1">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask about the news..."
            className="flex-1 px-2 py-1 bg-gray-800 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent placeholder-gray-400 text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="px-3 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default AIChat
