import { useEffect } from "react";

const COLLAPSED_WIDTH = 'w-0'; // No bar when collapsed
const EXPANDED_WIDTH = 'w-56';

const Sidebar = ({ activeTab, onTabChange, collapsed, setCollapsed, theme }) => {
  const menuItems = [
    {
      id: "home",
      label: "Home",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M3 12l9-8 9 8M4 10v10a1 1 0 001 1h3a1 1 0 001-1v-4h2v4a1 1 0 001 1h3a1 1 0 001-1V10"/></svg>
      ),
      description: "Main dashboard"
    },
    {
      id: "location-charts",
      label: "Location Data",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="10" r="3.5"/><path d="M12 21c4.97-5.5 8-9.5 8-13A8 8 0 1 0 4 8c0 3.5 3.03 7.5 8 13z"/></svg>
      ),
      description: "Local AQI charts"
    },
    {
      id: "state-charts",
      label: "State Data",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><rect x="3" y="7" width="18" height="10" rx="2"/><path d="M7 7V5a5 5 0 0110 0v2"/></svg>
      ),
      description: "State-level trends"
    },
    {
      id: "country-charts",
      label: "Country Data",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/></svg>
      ),
      description: "Country statistics"
    },
    {
      id: "world-charts",
      label: "World Data",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/><path d="M8 12a4 4 0 018 0"/></svg>
      ),
      description: "Global AQI trends"
    },
    {
      id: "health-trends",
      label: "Health Trends",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M3 17l6-6 4 4 8-8"/><circle cx="7.5" cy="17.5" r="1.5"/><circle cx="17.5" cy="7.5" r="1.5"/></svg>
      ),
      description: "Health data analysis"
    },
    {
      id: "comparisons",
      label: "Comparisons",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M6 20V10M12 20V4M18 20v-6"/></svg>
      ),
      description: "Compare locations"
    }
  ];

  const handleToggle = () => setCollapsed(!collapsed);
  const isDark = theme === 'dark';

  return (
    <>
      {/* Sidebar Panel */}
      <div
        className={`fixed left-0 top-0 h-screen z-40 flex flex-col transition-all duration-300 ${collapsed ? 'w-0' : 'w-56'} ${
          isDark
            ? 'bg-gray-900 border-r border-gray-800'
            : 'bg-white border-r border-gray-100 shadow-sm'
        }`}
        style={{ overflow: 'hidden' }}
      >
        {/* Menu */}
        {!collapsed && (
          <div className="flex flex-col flex-1 pt-8 overflow-y-auto">
            <nav className="flex-1 px-4 space-y-2">
              {menuItems.map((item) => {
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onTabChange(item.id)}
                    className={`w-full flex items-center space-x-3 py-2.5 px-3 rounded-lg transition-all duration-200 group relative text-left ${
                      isActive
                        ? isDark
                          ? 'bg-purple-600/20 text-purple-300 border-l-4 border-purple-400'
                          : 'bg-green-100 text-green-800 font-semibold border-l-4 border-green-500'
                        : isDark
                          ? 'text-gray-400 hover:bg-gray-800 hover:text-white border-l-4 border-transparent'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-4 border-transparent'
                    }`}
                    aria-label={item.description}
                  >
                    <span className={`flex-shrink-0 transition-colors duration-200 ${isActive ? '' : 'opacity-80'}`}>{item.icon}</span>
                    <div className="flex-grow">
                      <div className="text-sm leading-tight">{item.label}</div>
                    </div>
                  </button>
                );
              })}
            </nav>

            {/* Footer */}
            <div className="p-4 mt-auto">
              <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-800/50' : 'bg-gray-50'}`}>
                <p className={`text-xs text-center ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  VayuDev
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Sidebar; 