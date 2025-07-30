import Navbar from "./components/Navbar";
import Home from "./components/Home";
import HealthForm from "./components/HealthForm";
import Sidebar from "./components/Sidebar";
import DataCharts from "./components/DataCharts";
import ParticlesBackground from "./components/ParticlesBackground";
import PerformanceMonitor from "./components/PerformanceMonitor";
import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { buildApiUrl } from "./config/api";
import ReactMarkdown from 'react-markdown';

const SIDEBAR_WIDTH = 224; // 56 * 4 (w-56 in px)

export default function App() {
  // State lifted from Home component
  const [cityInput, setCityInput] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [locationDenied, setLocationDenied] = useState(false);
  const [homeLoading, setHomeLoading] = useState(false);
  const [currentAqiData, setCurrentAqiData] = useState(null);
  const [homeError, setHomeError] = useState("");
  const [showMap, setShowMap] = useState(false);

  // App-specific state
  const [advice, setAdvice] = useState("");
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [shouldScrollToAdvice, setShouldScrollToAdvice] = useState(false);
  const [activeTab, setActiveTab] = useState("home");
  const [activeLink, setActiveLink] = useState('airQuality');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);
  const [theme, setTheme] = useState('light');
  const [scrollToSection, setScrollToSection] = useState(null);

  const healthFormRef = useRef();
  const adviceSectionRef = useRef();
  const homeSectionRef = useRef(null);
  const healthFormSectionRef = useRef(null);
  const isFromSuggestionRef = useRef(false);

  // Common cities for fallback (memoized)
  const commonCities = useMemo(() => [
    { display_name: "New York, NY, USA", lat: "40.7128", lon: "-74.0060" },
    { display_name: "Los Angeles, CA, USA", lat: "34.0522", lon: "-118.2437" },
    { display_name: "London, UK", lat: "51.5074", lon: "-0.1278" },
    { display_name: "Tokyo, Japan", lat: "35.6895", lon: "139.6917" },
    { display_name: "Sydney, Australia", lat: "-33.8688", lon: "151.2093" },
  ], []);

  // Effect to toggle the 'dark' class on the <html> element
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const handleNavigation = (section) => {
    setActiveTab('home');
    setActiveLink(section);
    setScrollToSection(section);
  };

  useEffect(() => {
    if (scrollToSection && activeTab === 'home') {
      let targetRef;
      if (scrollToSection === 'airQuality') {
        targetRef = homeSectionRef;
      } else if (scrollToSection === 'healthCheck') {
        targetRef = healthFormSectionRef;
      }

      if (targetRef && targetRef.current) {
        targetRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      setScrollToSection(null); // Reset after scrolling
    }
  }, [activeTab, scrollToSection]);

  const fetchAQI = useCallback(async (location) => {
    setHomeLoading(true);
    setHomeError("");
    // We don't clear currentAqiData here to keep showing old data while new data loads
    
    if (!location || typeof location.lat !== 'number' || typeof location.lon !== 'number') {
      setHomeError("Invalid location coordinates provided.");
      setHomeLoading(false);
      return;
    }
    
    try {
      const res = await fetch(buildApiUrl("/aqi/aqi"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(location),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const result = await res.json();
      
      if (!result || typeof result !== 'object') {
        throw new Error("Invalid response format from server");
      }
      
      const finalData = { ...result, ...location };
      setCurrentAqiData(finalData);
    } catch (error) {
      console.error("Error fetching AQI:", error);
      setHomeError("Could not fetch AQI data. Please try again.");
    } finally {
      setHomeLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isFromSuggestionRef.current) return;

    if (cityInput.trim().length < 3) {
      setSuggestions([]);
      return;
    }

    const abortController = new AbortController();

    fetch(
      `${buildApiUrl(`/suggestions?query=${encodeURIComponent(cityInput)}`)}`,
      { signal: abortController.signal }
    )
      .then(res => res.json())
      .then(data => {
        if (data.length < 3) {
          const filteredCities = commonCities.filter(city => 
            city.display_name.toLowerCase().includes(cityInput.toLowerCase())
          );
          setSuggestions([...data, ...filteredCities]);
        } else {
          setSuggestions(data);
        }
      })
      .catch(error => {
        if (error.name !== 'AbortError') {
          console.error("Error fetching suggestions:", error);
          setSuggestions([]);
        }
      });

    return () => abortController.abort();
  }, [cityInput, commonCities]);

  const handleGetLocation = useCallback(() => {
    if ("geolocation" in navigator) {
      setHomeLoading(true);
      setHomeError("");
      setLocationDenied(false);

      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const { latitude, longitude } = pos.coords;
          let locationPayload = { lat: latitude, lon: longitude };

          try {
            const reverseGeocodeUrl = `${buildApiUrl(`/reverse-geocode?lat=${latitude}&lon=${longitude}`)}`;
            const reverseGeocodeRes = await fetch(reverseGeocodeUrl);
            
            if (reverseGeocodeRes.ok) {
              const locationData = await reverseGeocodeRes.json();
              if (locationData && locationData.display_name) {
                setCityInput(locationData.display_name);
                if (locationData.address && locationData.address.state) {
                  locationPayload.state = locationData.address.state;
                }
              }
            }
          } catch (error) {
            console.error("Error reverse geocoding:", error);
          } finally {
            await fetchAQI(locationPayload);
            setHomeLoading(false);
          }
        },
        (error) => {
          console.error("Geolocation error:", error);
          setHomeError("Could not get your location. Please enable location services.");
          setLocationDenied(true);
          setHomeLoading(false);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
      );
    } else {
      setLocationDenied(true);
      setHomeError("Geolocation is not supported by your browser.");
    }
  }, [fetchAQI]);

  const handleCitySearch = useCallback(async () => {
    if (!cityInput.trim()) {
      setHomeError("Please enter a city name.");
      return;
    }
    
    setHomeLoading(true);
    setHomeError("");

    if (suggestions.length > 0) {
      isFromSuggestionRef.current = true;
      const firstSuggestion = suggestions[0];
      setCityInput(firstSuggestion.display_name);
      setSuggestions([]);
      await fetchAQI({ lat: parseFloat(firstSuggestion.lat), lon: parseFloat(firstSuggestion.lon), state: firstSuggestion.address?.state || null });
      setTimeout(() => { isFromSuggestionRef.current = false; }, 100);
    } else {
       setHomeError("Location not found. Please select from the suggestions.");
       setHomeLoading(false);
    }
  }, [cityInput, suggestions, fetchAQI]);

  const handleSuggestionClick = useCallback((item) => {
    isFromSuggestionRef.current = true;
    setCityInput(item.display_name);
    setSuggestions([]);
    
    const location = { 
      lat: parseFloat(item.lat), 
      lon: parseFloat(item.lon),
      state: item.address?.state || null
    };
    
    fetchAQI(location);
    
    setTimeout(() => { isFromSuggestionRef.current = false; }, 100);
  }, [fetchAQI]);
  
  const handleLocationSelect = useCallback(async (latlng) => {
    await fetchAQI({ lat: latlng.lat, lon: latlng.lng });
    setShowMap(false);
  }, [fetchAQI]);

  // Listen for sidebar state from Sidebar component
  const handleSidebarState = useCallback((collapsed) => {
    setSidebarCollapsed(collapsed);
  }, []);

  // Handle scrolling to advice section
  useEffect(() => {
    if (shouldScrollToAdvice && advice && adviceSectionRef.current) {
      adviceSectionRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
      setShouldScrollToAdvice(false);
    }
  }, [advice, shouldScrollToAdvice]);

  const handleGetAIAdvice = useCallback(async () => {
    if (!healthFormRef.current) return;
    
    const { selected, notes, age, conditions, addictions } = healthFormRef.current.getFormData();
    const hasAqi = currentAqiData?.aqi && currentAqiData.aqi > 0;
    const hasSymptoms = selected.length > 0;
    const hasConditions = conditions && conditions.length > 0 && conditions[0] !== "None";
    const hasAddictions = addictions && addictions.length > 0 && addictions[0] !== "None";
    
    // Allow advice if user has any health information (symptoms, conditions, addictions, or AQI)
    if (!hasAqi && !hasSymptoms && !hasConditions && !hasAddictions) {
      setAdvice("Please check air quality or select at least one symptom, condition, or addiction to get personalized advice.");
      setShouldScrollToAdvice(true);
      return;
    }

    setAdviceLoading(true);
    setAdvice("");

    const payload = {
      symptoms: selected,
      notes,
      aqi: currentAqiData?.aqi || 0,
      age: age ? parseInt(age) : null,
      conditions,
      addictions,
    };

    try {
      const res = await fetch(buildApiUrl("/suggest/ask-vayu"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const result = await res.json();
      if (result.suggestion) {
        setAdvice(result.suggestion);
        setShouldScrollToAdvice(true);
      } else {
        setAdvice("Something went wrong while getting advice. Please try again.");
        setShouldScrollToAdvice(true);
      }
    } catch (err) {
      console.error("Error getting health advice:", err);
      // Check if the error is a result of a 429 status code
      if (err.message.includes("429")) {
        setAdvice("Gemini quota limit reached, please try again later.");
      } else {
        setAdvice("Error contacting backend. Please check your connection and try again.");
      }
      setShouldScrollToAdvice(true);
    } finally {
      setAdviceLoading(false);
    }
  }, [currentAqiData]);

  // Memoized left margin calculation
  const leftMargin = useMemo(() => {
    return sidebarCollapsed ? 0 : SIDEBAR_WIDTH;
  }, [sidebarCollapsed]);

  // Memoized main content to prevent unnecessary re-renders
  const mainContent = useMemo(() => {
    if (activeTab === "home") {
      return (
        <>
          <div ref={homeSectionRef}>
            <Home
              cityInput={cityInput}
              setCityInput={setCityInput}
              suggestions={suggestions}
              handleSuggestionClick={handleSuggestionClick}
              handleCitySearch={handleCitySearch}
              handleGetLocation={handleGetLocation}
              loading={homeLoading}
              error={homeError}
              aqiData={currentAqiData}
              locationDenied={locationDenied}
              showMap={showMap}
              setShowMap={setShowMap}
              onLocationSelect={handleLocationSelect}
            />
          </div>
          <div ref={healthFormSectionRef}>
            <HealthForm 
              ref={healthFormRef}
              aqiValue={currentAqiData?.aqi || 0}
              onGetAIAdvice={handleGetAIAdvice}
              loading={adviceLoading}
              theme={theme}
            />
          </div>
          
          {/* AI Advice Section */}
          {advice && (
            <div 
              ref={adviceSectionRef}
              id="ai-advice-section" 
              className="mt-8 p-6 bg-white dark:bg-gradient-to-r dark:from-blue-900/30 dark:to-purple-900/30 border border-green-300 dark:border-blue-500/50 rounded-lg dark:neon-glow-blue max-w-4xl mx-auto shadow-lg" 
              role="alert" 
              aria-live="polite"
            >
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-green-500 dark:bg-blue-500 rounded-full flex-shrink-0 mt-1" aria-hidden="true"></div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-green-800 dark:text-blue-300 mb-2">AI Health Advice</h3>
                  <div className="prose prose-invert text-gray-700 dark:text-blue-200 leading-relaxed">
                    <ReactMarkdown>{advice}</ReactMarkdown>
                  </div>
                  <p className="text-xs text-green-600 dark:text-blue-300 mt-3">
                    💡 This advice is based on your symptoms and current air quality. Always consult a healthcare professional for medical concerns.
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      );
    } else {
      return (
        <DataCharts 
          activeTab={activeTab} 
          currentLocation={currentAqiData}
          theme={theme}
        />
      );
    }
  }, [
    activeTab, currentAqiData, advice, adviceLoading, theme,
    cityInput, suggestions, homeLoading, homeError, locationDenied, showMap,
    handleSuggestionClick, handleCitySearch, handleGetLocation, handleLocationSelect, handleGetAIAdvice
  ]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      {/* Firefly particles background */}
      <div className="block">
        <ParticlesBackground />
      </div>
      {/* Watermark */}
      <div className="fixed inset-0 pointer-events-none z-0 flex items-center justify-center opacity-5">
        <div className="text-8xl font-bold text-gray-600 dark:text-white transform -rotate-12 select-none">
          VayuDev
        </div>
      </div>
      
      {/* Performance Monitor (Development Only) */}
      {process.env.NODE_ENV === 'development' && <PerformanceMonitor />}
      
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} collapsed={sidebarCollapsed} setCollapsed={handleSidebarState} theme={theme} />
      
      {/* Header (Navbar) - moves with sidebar */}
      <div
        className="transition-all duration-200"
        style={{ marginLeft: leftMargin }}
      >
        <Navbar 
          theme={theme} 
          toggleTheme={toggleTheme} 
          sidebarCollapsed={sidebarCollapsed}
          setSidebarCollapsed={setSidebarCollapsed}
          handleNavigation={handleNavigation}
          activeLink={activeLink}
          isHomePage={activeTab === 'home'}
        />
      </div>
      
      <main 
        id="main-content" 
        className={`transition-all duration-200 px-4 py-8 relative z-10`}
        style={{ marginLeft: leftMargin }}
        tabIndex="-1"
      >
        <div className="container mx-auto">
          {mainContent}
          {/* <AskVayuChat /> */}
        </div>
      </main>
      
      {/* Footer with accessibility info */}
      <footer className="mt-16 pb-8 text-center text-sm text-gray-600 dark:text-gray-400 relative z-10">
        <p>
          VayuCheck+ - AI-Powered Air Quality & Health Companion
        </p>
        <p className="mt-2">
          Built with accessibility in mind. Use Tab to navigate, Enter/Space to activate.
        </p>
        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
          © 2024 VayuDev
        </p>
      </footer>
    </div>
  );
}