import React, { useEffect } from 'react'

const Toast = ({ message, isVisible, onClose, duration = 3000, type = 'info' }) => {
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      
      return () => clearTimeout(timer)
    }
  }, [isVisible, duration, onClose])

  if (!isVisible) return null

  const typeStyles = {
    info: 'bg-gradient-to-r from-blue-600 to-blue-700 border-blue-400',
    success: 'bg-gradient-to-r from-green-600 to-green-700 border-green-400',
    warning: 'bg-gradient-to-r from-yellow-600 to-yellow-700 border-yellow-400',
    error: 'bg-gradient-to-r from-red-600 to-red-700 border-red-400',
  }

  const icons = {
    info: '🎬',
    success: '✅',
    warning: '⚠️',
    error: '❌',
  }

  return (
    <div className="fixed top-8 left-1/2 transform -translate-x-1/2 z-50 animate-slideDown">
      <div 
        className={`
          ${typeStyles[type]}
          text-white
          px-8 py-4
          rounded-2xl
          shadow-2xl
          border-2
          backdrop-blur-sm
          flex items-center gap-4
          min-w-[320px]
          animate-bounce-subtle
        `}
      >
        <span className="text-3xl animate-pulse">{icons[type]}</span>
        <div className="flex-1">
          <p className="text-lg font-semibold leading-tight">{message}</p>
        </div>
        <button
          onClick={onClose}
          className="ml-2 text-white hover:text-gray-200 transition-colors text-2xl leading-none"
          aria-label="Close"
        >
          ×
        </button>
      </div>
    </div>
  )
}

export default Toast

