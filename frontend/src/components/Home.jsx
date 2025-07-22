import { useMemo, useCallback } from "react";
import Map from './Map';

export default function Home({ 
  cityInput, 
  setCityInput, 
  suggestions, 
  handleSuggestionClick,
  handleCitySearch,
  handleGetLocation,
  loading,
  error,
  aqiData,
  locationDenied,
  showMap,
  setShowMap,
  onLocationSelect
}) {

  const getAqiColorClass = (aqi) => {
    if (aqi <= 50) return 'text-green-500';
    if (aqi <= 100) return 'text-orange-500'; // Using orange for moderate
    if (aqi <= 150) return 'text-orange-500'; // Using orange for Unhealthy for Sensitive
    if (aqi <= 200) return 'text-red-500';
    if (aqi <= 300) return 'text-purple-500 dark:text-purple-400';
    return 'text-red-700';
  };

  // Memoized function to get AQI status description
  const getAQIStatus = useCallback((aqi) => {
    if (aqi <= 50) return "Good";
    if (aqi <= 100) return "Moderate";
    if (aqi <= 150) return "Unhealthy for Sensitive Groups";
    if (aqi <= 200) return "Unhealthy";
    if (aqi <= 300) return "Very Unhealthy";
    return "Hazardous";
  }, []);

  // Memoized AQI status for current data
  const currentAQIStatus = useMemo(() => {
    return aqiData ? getAQIStatus(aqiData.aqi) : null;
  }, [aqiData, getAQIStatus]);

  return (
    <section className="max-w-4xl mx-auto p-6" aria-labelledby="home-title">
      <header className="mb-8 text-center">
        <h1 id="home-title" className="text-4xl md:text-5xl font-extrabold mb-4 pb-2 bg-gradient-to-r from-green-400 to-teal-500 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
          VayuCheck+
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-Powered Air Quality & Health Monitor
        </p>
      </header>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleCitySearch();
        }}
        className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-8 relative"
        role="search"
        aria-label="Search for air quality by location"
      >
        <div className="w-full relative">
          <label htmlFor="location-input" className="sr-only">
            Enter city, village, or place name
          </label>
          <input
            id="location-input"
            type="text"
            placeholder="Enter city, village, or place"
            value={cityInput}
            onChange={(e) => setCityInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleCitySearch();
              }
            }}
            className="input-themed w-full"
            aria-autocomplete="list"
            aria-controls="suggestions-list"
          />
          {suggestions.length > 0 && (
            <ul
              id="suggestions-list"
              className="absolute top-full left-0 right-0 z-10 mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-y-auto"
              role="listbox"
            >
              {suggestions.map((item, index) => (
                <li
                  key={item.place_id || index}
                  onClick={() => handleSuggestionClick(item)}
                  className="px-4 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100"
                  role="option"
                  aria-selected="false"
                >
                  {item.display_name}
                </li>
              ))}
            </ul>
          )}
        </div>
        <button
          type="submit"
          className="btn btn-primary w-full sm:w-auto"
          disabled={loading}
        >
          Search
        </button>
        <button
          type="button"
          onClick={handleGetLocation}
          className="btn btn-secondary w-full sm:w-auto"
          aria-label="Use my current location"
        >
          <svg
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
              clipRule="evenodd"
            ></path>
          </svg>
        </button>
        <button
          type="button"
          onClick={() => setShowMap(!showMap)}
          className="btn btn-secondary w-full sm:w-auto"
          aria-label="Show map"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="text-foreground"
          >
            {/* Map outline */}
            <path
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Location pin */}
            <circle
              cx="12"
              cy="12"
              r="2"
              fill="currentColor"
            />
            {/* Map grid lines */}
            <path
              d="M7 10h2m6 0h2M7 14h2m6 0h2"
              stroke="currentColor"
              strokeWidth="1"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </form>
      
      <div id="location-help" className="sr-only">
        Enter a city name or use the location button to get current location air quality data. 
        Suggestions will appear as you type. Use arrow keys to navigate suggestions and Enter to select.
      </div>

      {locationDenied && (
        <div className="my-4 p-4 text-center text-amber-800 dark:text-amber-200 bg-amber-100/80 dark:bg-amber-900/40 rounded-md" role="status">
          Location access was denied. Please enable it in your browser settings or search for a city manually.
        </div>
      )}

      {loading && (
        <div className="flex justify-center items-center my-8">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {error && (
        <div className="my-4 p-4 text-center text-destructive-foreground bg-destructive rounded-md" role="alert">
          {error}
        </div>
      )}

      {aqiData && (
        <div
          className="themed-card p-6 mt-8 text-center"
          aria-live="polite"
          aria-atomic="true"
        >
          <h2 className="text-xl font-bold mb-2">
            Current Air Quality in {aqiData.city || aqiData.location || 'Unknown Location'}
          </h2>
          <div
            className={`text-6xl font-bold my-4 ${getAqiColorClass(aqiData.aqi)}`}
          >
            {aqiData.aqi}
          </div>
          <p className="text-2xl font-semibold mb-4">{currentAQIStatus}</p>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 text-sm text-muted-foreground">
            {aqiData.o3 && (
              <div className="themed-card p-3">
                <p className="font-bold">O3</p>
                <p>{aqiData.o3}</p>
              </div>
            )}
            {aqiData.pm25 && (
              <div className="themed-card p-3">
                <p className="font-bold">PM2.5</p>
                <p>{aqiData.pm25}</p>
              </div>
            )}
            {aqiData.pm10 && (
              <div className="themed-card p-3">
                <p className="font-bold">PM10</p>
                <p>{aqiData.pm10}</p>
              </div>
            )}
            {aqiData.so2 && (
              <div className="themed-card p-3">
                <p className="font-bold">SO2</p>
                <p>{aqiData.so2}</p>
              </div>
            )}
            {aqiData.no2 && (
              <div className="themed-card p-3">
                <p className="font-bold">NO2</p>
                <p>{aqiData.no2}</p>
              </div>
            )}
            {aqiData.co && (
              <div className="themed-card p-3">
                <p className="font-bold">CO</p>
                <p>{aqiData.co}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {showMap && <Map onLocationSelect={onLocationSelect} theme={document.documentElement.classList.contains('dark') ? 'dark' : 'light'} />}
    </section>
  );
}