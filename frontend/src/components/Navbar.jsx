import logo from '../assets/vayucheck-logo.png';

export default function Navbar({ theme, toggleTheme, setSidebarCollapsed, sidebarCollapsed, handleNavigation, activeLink, isHomePage }) {
  const handleToggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  return (
    <header>
      <nav className={`p-4 text-2xl font-bold text-center transition-all duration-300 ${
        theme === 'dark' 
          ? 'bg-gradient-to-r from-purple-600 via-pink-500 to-purple-600 text-white neon-glow-pink animated-bg shadow-2xl' 
          : 'bg-gradient-to-r from-green-500 via-teal-500 to-emerald-500 text-white shadow-xl'
      }`} role="banner" aria-label="Main navigation">
        <div className="relative flex items-center justify-between">
          {/* Left: Sidebar Toggle */}
          <div className="flex-1 flex justify-start">
            <button
              onClick={handleToggleSidebar}
              className="p-2 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 hover:scale-110 hover:bg-white/10"
              aria-label={sidebarCollapsed ? "Open sidebar" : "Close sidebar"}
            >
              {sidebarCollapsed ? (
                  <svg className="h-5 w-5" stroke="currentColor" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
              ) : (
                  <svg className="h-5 w-5" stroke="currentColor" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              )}
            </button>
          </div>
        
          {/* Center: Logo and Title */}
          <div className="flex-1 flex justify-center">
            <div className="flex items-center space-x-3">
              <img src={logo} alt="VayuCheck Logo" className="w-8 h-8 rounded-full bg-white object-contain shadow-lg transition-transform duration-300 hover:scale-110" style={{background: 'white'}} aria-hidden="true" role="presentation" />
              <h1 className={`bg-clip-text text-transparent font-extrabold ${
                  theme === 'dark'
                    ? 'bg-gradient-to-r from-white via-purple-200 to-pink-200'
                    : 'bg-gradient-to-r from-white via-green-200 to-teal-200'
                }`}>
                VayuCheck+ 
              </h1>
            </div>
          </div>
          
          {/* Right: Theme Toggle */}
          <div className="flex-1 flex justify-end">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 hover:scale-110 hover:bg-white/10"
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {theme === 'dark' ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
              ) : (
                <svg width="20" height="20" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"></path></svg>
              )}
            </button>
          </div>
        </div>
        
        {/* Navigation Links for different sections */}
        <div className="mt-4 flex justify-center space-x-8 text-sm font-medium">
          <button onClick={() => handleNavigation('airQuality')} className={`pb-1 border-b-2 transition-all duration-300 hover:scale-105 ${
            isHomePage && activeLink === 'airQuality'
              ? (theme === 'dark' ? 'border-pink-300 text-white hover:border-white' : 'border-teal-200 text-white hover:border-white')
              : (theme === 'dark' ? 'border-transparent text-gray-300 hover:border-white hover:text-white' : 'border-transparent text-teal-100 hover:border-white hover:text-white')
          }`}>
            Air Quality
          </button>
          <button onClick={() => handleNavigation('healthCheck')} className={`pb-1 border-b-2 transition-all duration-300 hover:scale-105 ${
            isHomePage && activeLink === 'healthCheck'
              ? (theme === 'dark' ? 'border-pink-300 text-white hover:border-white' : 'border-teal-200 text-white hover:border-white')
              : (theme === 'dark' ? 'border-transparent text-gray-300 hover:border-white hover:text-white' : 'border-transparent text-teal-100 hover:border-white hover:text-white')
          }`}>
            Health Check
          </button>
        </div>
      </nav>
    </header>
  );
}
