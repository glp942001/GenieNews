import React from 'react'

const VideoPlayer = () => {
  const handlePlayClick = () => {
    // TODO: Implement video playback functionality
    console.log('Play button clicked')
  }

  return (
    <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 w-full overflow-hidden" style={{ height: '350px' }}>
      {/* Video Container */}
      <div className="relative w-full h-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center cursor-pointer group"
           onClick={handlePlayClick}>
        
        {/* Play Button */}
        <button 
          className="w-24 h-24 bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full flex items-center justify-center transition-all duration-300 shadow-2xl group-hover:scale-110"
          onClick={handlePlayClick}
        >
          {/* Play Icon Triangle */}
          <div className="w-0 h-0 border-l-[30px] border-l-gray-800 border-t-[20px] border-t-transparent border-b-[20px] border-b-transparent ml-2"></div>
        </button>

        {/* Optional: Video Title Overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-6">
          <h3 className="text-white text-xl font-bold">AI News Summary</h3>
          <p className="text-gray-200 text-sm mt-1">Click to play</p>
        </div>
      </div>
    </div>
  )
}

export default VideoPlayer

