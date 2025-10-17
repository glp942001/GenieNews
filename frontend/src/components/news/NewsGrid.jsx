import React from 'react'
import NewsCard from './NewsCard'
import { mockNewsData } from '../../data/mockNews'

const NewsGrid = () => {
  return (
    <div className="grid grid-cols-4 grid-rows-3 gap-4 h-[800px]">
        {/* Headline 1: rows 1-2, columns 1-2 (2x2) */}
        <div className="col-span-2 row-span-2">
          <NewsCard article={mockNewsData[0]} size="large" />
        </div>
        
        {/* Headline 2: row 1, column 3 */}
        <div className="col-span-1 row-span-1">
          <NewsCard article={mockNewsData[1]} size="medium" />
        </div>
        
        {/* Headline 3: row 1, column 4 */}
        <div className="col-span-1 row-span-1">
          <NewsCard article={mockNewsData[2]} size="medium" />
        </div>
        
        {/* Headline 4: row 2, columns 3-4 (1x2) */}
        <div className="col-span-2 row-span-1">
          <NewsCard article={mockNewsData[3]} size="medium" />
        </div>
        
        {/* Headline 5: row 3, column 1 */}
        <div className="col-span-1 row-span-1">
          <NewsCard article={mockNewsData[4]} size="small" />
        </div>
        
        {/* Headline 6: row 3, column 2 */}
        <div className="col-span-1 row-span-1">
          <NewsCard article={mockNewsData[5]} size="small" />
        </div>
        
        {/* Headline 7: row 3, column 3 */}
        <div className="col-span-1 row-span-1">
          <NewsCard article={mockNewsData[6]} size="small" />
        </div>
        
        {/* Headline 8: row 3, column 4 */}
        <div className="col-span-1 row-span-1">
          <NewsCard article={mockNewsData[7]} size="small" />
        </div>
      </div>
  )
}

export default NewsGrid

