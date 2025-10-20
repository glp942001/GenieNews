import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import backgroundImage from '../../assets/images/Background2.jpg'

const Header = () => {
  const location = useLocation()
  
  const menuItems = [
    { path: '/', label: 'AI News' },
    { path: '/fintech', label: 'Fintech News' },
    { path: '/credit-genie', label: 'Credit Genie News' }
  ]
  
  return (
    <header className="shadow-lg" style={{
      backgroundImage: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center 85%',
      backgroundRepeat: 'no-repeat'
    }}>
      {/* Title */}
      <div className="py-8">
        <h1 className="text-white text-4xl font-bold text-center">
          The AI Bazaar
        </h1>
      </div>
      
      {/* Navigation Menu */}
      <nav>
        <div className="max-w-7xl mx-auto px-6">
          <ul className="flex justify-center space-x-8">
            {menuItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`block py-4 px-4 text-lg font-medium transition-all ${
                    location.pathname === item.path
                      ? 'text-white border-b-2 border-white'
                      : 'text-purple-200 hover:text-white hover:border-b-2 hover:border-purple-300'
                  }`}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </header>
  )
}

export default Header

