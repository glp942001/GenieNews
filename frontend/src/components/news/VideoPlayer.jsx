import React, { useState } from 'react'
import Toast from '../common/Toast'

const VideoPlayer = () => {
  const [showToast, setShowToast] = useState(false)

  const handlePlayClick = () => {
    setShowToast(true)
  }

  return (
    <>
      <Toast
        message="Video functionality coming soon! 🎥"
        isVisible={showToast}
        onClose={() => setShowToast(false)}
        type="info"
        duration={3000}
      />
      
      <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 w-full overflow-hidden" style={{ height: '300px' }}>
        {/* Video Container */}
        <div className="relative w-full h-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center cursor-pointer group"
             onClick={handlePlayClick}>
          
          {/* Play Button */}
          <button 
            className="w-16 h-16 bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl group-hover:scale-110"
            onClick={handlePlayClick}
          >
            {/* Play Icon Triangle */}
            <div className="w-0 h-0 border-l-[20px] border-l-gray-800 border-t-[12px] border-t-transparent border-b-[12px] border-b-transparent ml-1"></div>
          </button>

          {/* Optional: Video Title Overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-3">
            <h3 className="text-white text-sm font-bold">AI News Summary</h3>
            <p className="text-gray-200 text-xs mt-1">Click to play</p>
          </div>
        </div>
      </div>
    </>
  )
}

export default VideoPlayer

