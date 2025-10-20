import React from 'react'
import NewsCard from './NewsCard'
import VideoPlayer from './VideoPlayer'
import { mockNewsData } from '../../data/mockNews'

const NewsGrid = () => {
  return (
    <div className="grid grid-cols-2 gap-4 auto-rows-auto">
        {/* Row 1: Video (col 1), News container (col 2) */}
        <div className="col-span-1" style={{ height: '350px' }}>
          <VideoPlayer />
        </div>
        <div className="col-span-1" style={{ height: '350px' }}>
          <NewsCard article={mockNewsData[0]} size="medium" />
        </div>
        
        {/* Row 2: Horizontal News container spanning both columns */}
        <div className="col-span-2" style={{ minHeight: '220px' }}>
          <NewsCard article={mockNewsData[1]} size="horizontal" />
        </div>
        
        {/* Row 3: News container (col 1), News container (col 2) */}
        <div className="col-span-1" style={{ height: '320px' }}>
          <NewsCard article={mockNewsData[2]} size="medium" />
        </div>
        <div className="col-span-1" style={{ height: '320px' }}>
          <NewsCard article={mockNewsData[3]} size="medium" />
        </div>
        
        {/* Row 4: News container (col 1), News container (col 2) */}
        <div className="col-span-1" style={{ height: '320px' }}>
          <NewsCard article={mockNewsData[4]} size="medium" />
        </div>
        <div className="col-span-1" style={{ height: '320px' }}>
          <NewsCard article={mockNewsData[5]} size="medium" />
        </div>
      </div>
  )
}

export default NewsGrid

