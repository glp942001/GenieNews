import React, { useState, useEffect } from 'react'
import { generateDailyAudioSegment } from '../../services/api'

const AudioPlayer = () => {
  const [audioUrl, setAudioUrl] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load audio segment on component mount
  useEffect(() => {
    loadAudioSegment()
  }, [])

  const loadAudioSegment = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await generateDailyAudioSegment()
      
      if (result.success) {
        setAudioUrl(result.audioUrl)
      } else {
        setError(result.error || 'No audio segment available yet')
      }
    } catch (err) {
      setError('Failed to load audio segment')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 w-full overflow-hidden">
        {/* Audio Player Container */}
        <div className="relative w-full bg-white flex flex-col items-center justify-center p-6">
          
          {isLoading && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto mb-3"></div>
              <p className="text-gray-800 text-base font-semibold">Loading audio...</p>
            </div>
          )}

          {error && !isLoading && (
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-3 mx-auto">
                <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M18 3a1 1 0 00-1.447-.894L8.763 6H5a3 3 0 000 6h.28l1.771 5.316A1 1 0 008 18h1a1 1 0 001-1v-4.382l6.553 3.276A1 1 0 0018 15V3z" />
                </svg>
              </div>
              <h3 className="text-gray-800 text-lg font-bold mb-2">The AI Boost Podcast</h3>
              <p className="text-gray-600 text-sm mb-3">{error}</p>
              <p className="text-gray-500 text-xs">Audio segments are generated automatically.</p>
            </div>
          )}

          {audioUrl && !isLoading && (
            <div className="w-full">
              <div className="text-center mb-4">
                <h3 className="text-gray-800 text-xl font-bold">The AI Boost Podcast</h3>
              </div>

              {/* HTML5 Audio Player */}
              <audio
                controls
                className="w-full"
                style={{
                  height: '48px',
                  borderRadius: '8px'
                }}
              >
                <source src={audioUrl} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>
          )}
        </div>
      </div>
    )
}

export default AudioPlayer

