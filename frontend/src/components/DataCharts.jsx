import { useState, useEffect, useCallback, useMemo } from "react";
import { buildApiUrl } from "../config/api";

const capitalize = (s) => {
  if (typeof s !== 'string' || s.length === 0) return '';
  return s.charAt(0).toUpperCase() + s.slice(1);
};

const DataCharts = ({ activeTab, currentLocation, theme = 'dark' }) => {
  const [chartData, setChartData] = useState(null);
  const [yearlyData, setYearlyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chartTitle, setChartTitle] = useState("");
  const [chartSubtitle, setChartSubtitle] = useState("");

  const isDark = theme === 'dark';

  const generateMockData = useCallback((type) => {
    const now = new Date();
    const data = [];
    for (let i = 30; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      let baseAQI = 50;
      switch (type) {
        case "location": baseAQI = 75 + Math.random() * 100; break;
        case "state": baseAQI = 60 + Math.random() * 80; break;
        case "country": baseAQI = 45 + Math.random() * 70; break;
        case "world": baseAQI = 40 + Math.random() * 60; break;
        default: break;
      }
      data.push({
        date: date.toISOString().split('T')[0],
        aqi: Math.round(baseAQI + (Math.random() - 0.5) * 20),
      });
    }
    return data;
  }, []);

  useEffect(() => {
    if (activeTab && activeTab !== "home") {
      setLoading(true);
      setError("");
      
      const fetchChartData = async () => {
        try {
          const level = activeTab.split('-')[0];
          setChartTitle(`${capitalize(level)} AQI Trends`);
          setChartSubtitle("30-Day Daily AQI Trends");

          let url = `${buildApiUrl("/aqi/charts")}/${level}?days=30`;
          
          if (level === 'state' && currentLocation?.state) {
            url += `&state=${encodeURIComponent(currentLocation.state)}`;
          } else if (level === 'location' && currentLocation) {
            url += `&lat=${currentLocation.lat}&lon=${currentLocation.lon}`;
            if (currentLocation.aqi) {
              url += `&aqi=${currentLocation.aqi}`;
            }
          }

          const response = await fetch(url);
          
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          
          const result = await response.json();
          
          if (result.status === "ok") {
            setChartData(result.data);
            if (level === 'state' && result.state) {
              setChartTitle(`${result.state} AQI Trends`);
            }
            if (result.data.length === 0 && result.message) {
              setError(result.message);
            }
          } else {
            throw new Error("Failed to fetch chart data");
          }
        } catch (err) {
          console.error("Error fetching chart data:", err);
          const level = activeTab.split('-')[0];
          const mockData = generateMockData(level);
          setChartData(mockData);
        } finally {
          setLoading(false);
        }
      };

      const fetchYearlyData = async () => {
        try {
          const level = activeTab.split('-')[0];
          if (["country", "world", "state"].includes(level)) {
            let url = `${buildApiUrl("/aqi/charts")}/${level}/yearly`;
            if (level === 'state' && currentLocation?.state) {
              url += `?state=${encodeURIComponent(currentLocation.state)}`;
            }
            
            const response = await fetch(url);
            if (response.ok) {
              const result = await response.json();
              if (result.status === "ok") {
                setYearlyData(result.data);
              } else {
                setYearlyData(null);
              }
            } else {
              setYearlyData(null);
            }
          } else {
            setYearlyData(null); // Clear data for tabs without yearly view
          }
        } catch (err) {
          console.error("Error fetching yearly data:", err);
          setYearlyData(null);
        }
      };
      
      fetchChartData();
      fetchYearlyData();
    }
  }, [activeTab, currentLocation, generateMockData]);

  const renderLineChart = useCallback((data, title, subtitle) => {
    if (!data || data.length === 0) {
      return null;
    }

    const dataMinAQI = Math.min(...data.map(d => d.aqi));
    const dataMaxAQI = Math.max(...data.map(d => d.aqi));
    const averageAQI = Math.round(data.reduce((acc, d) => acc + d.aqi, 0) / data.length);
    const rangeAQI = dataMaxAQI - dataMinAQI;

    const yAxisMin = Math.max(0, dataMinAQI - 10);
    const chartMaxAQI = dataMaxAQI + 10;
    const range = chartMaxAQI - yAxisMin || 1;
    
    const isYearly = subtitle === "Last 12 Months" || subtitle === "2014-2024" || subtitle === "30-Day Daily AQI Trend";

    return (
      <div className={`rounded-lg border p-6 shadow-xl ${
        isDark 
          ? 'bg-gray-800/50 border-purple-500/30' 
          : 'bg-white/80 border-green-300 backdrop-blur-sm'
      }`}>
        <div className="mb-4">
          <h3 className={`text-xl font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h3>
          <p className={isDark ? 'text-gray-400' : 'text-gray-600'}>{subtitle}</p>
        </div>
        
        <div className="h-64 relative">
          <svg className="w-full h-full" viewBox="0 0 800 220" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={isDark ? "#8B5CF6" : "#10b981"} stopOpacity="1"/>
                <stop offset="100%" stopColor={isDark ? "#EC4899" : "#047857"} stopOpacity="0.3"/>
              </linearGradient>
            </defs>
            {[0, 25, 50, 75, 100].map((percent, i) => (
              <line key={i} x1="0" y1={percent * 2} x2="800" y2={percent * 2} stroke={isDark ? "#4B5563" : "#E5E7EB"} strokeWidth="1"/>
            ))}
            <path
              d={data.length > 1 ? data.map((point, i) => {
                const x = (i / (data.length - 1)) * 800;
                const y = 200 - ((point.aqi - yAxisMin) / range) * 180;
                return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
              }).join(' ') : ''}
              stroke="url(#lineGradient)"
              strokeWidth="3"
              fill="none"
            />
            {/* Data points */}
            {data.map((point, i) => {
              const x = data.length > 1 ? (i / (data.length - 1)) * 800 : 400; // center if only one point
              const y = 200 - ((point.aqi - yAxisMin) / range) * 180;
              return (
                <circle
                  key={`point-${i}`}
                  cx={x}
                  cy={y}
                  r="4"
                  fill={isDark ? "#8B5CF6" : "#10b981"}
                  stroke={isDark ? '#1f2937' : '#fff'}
                  strokeWidth="2"
                />
              );
            })}
            {/* X-axis labels */}
            {data.map((point, i) => {
                const x = data.length > 1 ? (i / (data.length - 1)) * 800 : 400;
                let label = '';

                if (isYearly) {
                    if (activeTab.startsWith('world') && subtitle === "2014-2024") {
                        label = new Date(point.date).getFullYear();
                    } else if (activeTab.startsWith('country') || activeTab.startsWith('state')) {
                         if (subtitle === "Last 12 Months") {
                            label = new Date(point.date).toLocaleDateString('default', { month: 'short' });
                         } else {
                            if (data.length > 15 && i % 5 !== 0) return null;
                            label = new Date(point.date).toLocaleDateString('default', { month: 'short', day: 'numeric' });
                         }
                    }
                } else {
                    if (data.length > 15 && i % 5 !== 0) return null;
                    label = new Date(point.date).toLocaleDateString('default', { month: 'short', day: 'numeric' });
                }
                
                return (
                    <text
                        key={`label-${i}`}
                        x={x}
                        y="218"
                        textAnchor="middle"
                        fontSize="12"
                        fill={isDark ? "#9CA3AF" : "#4B5563"}
                    >
                        {label}
                    </text>
                );
            })}
          </svg>
        </div>
        
        <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <p className={isDark ? 'text-gray-400' : 'text-gray-500'}>Average</p>
            <p className={`font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>{averageAQI}</p>
          </div>
          <div className="text-center">
            <p className={isDark ? 'text-gray-400' : 'text-gray-500'}>Peak</p>
            <p className={`font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>{dataMaxAQI}</p>
          </div>
          <div className="text-center">
            <p className={isDark ? 'text-gray-400' : 'text-gray-500'}>Lowest</p>
            <p className={`font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>{dataMinAQI}</p>
          </div>
          <div className="text-center">
            <p className={isDark ? 'text-gray-400' : 'text-gray-500'}>Range</p>
            <p className={`font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>{rangeAQI}</p>
          </div>
        </div>
      </div>
    );
  }, [isDark, activeTab]);

  const renderBarChart = useCallback((data, title, subtitle) => {
    if (!data || data.length === 0) {
      return null;
    }

    const isYearly = title === "Yearly AQI Overview" || title === "Monthly AQI Overview";
    
    const chartData = isYearly ? data : data.slice(-14);
    
    if (chartData.length === 0) {
      return null;
    }

    const dataMaxAQI = Math.max(...chartData.map(d => d.aqi));
    const chartMaxAQI = dataMaxAQI + 10;
    
    const barGradient = isDark
      ? 'bg-gradient-to-t from-green-500/60 to-green-400/80'
      : 'bg-gradient-to-t from-green-400 to-green-500';

    return (
      <div className={`rounded-lg border p-6 shadow-xl ${
          isDark 
          ? 'bg-gray-800/50 border-purple-500/30' 
          : 'bg-white/80 border-green-300 backdrop-blur-sm'
      }`}>
        <div className="mb-4">
          <h3 className={`text-xl font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h3>
          <p className={isDark ? 'text-gray-400' : 'text-gray-600'}>{subtitle}</p>
        </div>
        <div className="h-64 relative flex items-end gap-2">
          {chartData.map((d, index) => {
            const aqiValue = typeof d.aqi === 'number' ? d.aqi : parseInt(d.aqi) || 0;
            const heightPercentage = Math.max(5, (aqiValue / chartMaxAQI) * 100);
            
            return (
              <div key={`${d.date}-${index}`} className="flex-1 h-full flex flex-col items-center justify-end group">
                <div
                  className={`w-full rounded-t-lg transition-all duration-300 ${barGradient} flex justify-center items-start pt-1`}
                  style={{ height: `${heightPercentage}%` }}
                >
                  <span className="text-white font-bold text-xs" style={{textShadow: '1px 1px 2px rgba(0,0,0,0.5)'}}>
                    {aqiValue}
                  </span>
                </div>
                <p className={`text-xs mt-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {isYearly && activeTab.startsWith("world")
                    ? new Date(d.date).getFullYear()
                    : isYearly
                    ? new Date(d.date).toLocaleDateString('default', { month: 'short' })
                    : new Date(d.date).toLocaleDateString('default', { month: 'short', day: 'numeric' })}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    );
  }, [isDark, activeTab]);
  
  return (
    <div className="p-4 md:p-6">
      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
      {error && (
        <div className="my-4 p-4 text-center text-destructive-foreground bg-destructive rounded-md" role="alert">
          {error}
        </div>
      )}
      {!loading && !error && chartData && (
        <div className="grid grid-cols-1 gap-6">
          {activeTab.startsWith("location") && (
            <>
              {renderLineChart(chartData, chartTitle, chartSubtitle)}
              {renderBarChart(chartData, "Daily AQI Overview", "Last 14 Days")}
            </>
          )}
          {activeTab.startsWith("state") && (
            <>
              {renderLineChart(chartData, chartTitle, "30-Day Daily AQI Trend")}
              {yearlyData ? renderBarChart(yearlyData, "Monthly AQI Overview", "Last 12 Months") : renderBarChart(chartData, "Daily AQI Overview", "Last 14 Days")}
            </>
          )}
          {activeTab.startsWith("country") && (
            <>
              {yearlyData
                ? renderLineChart(yearlyData, "Yearly AQI Trend", "Last 12 Months")
                : renderLineChart(chartData, "Country AQI Trends", "30-Day Daily AQI Trends")}
              {yearlyData 
                ? renderBarChart(yearlyData, "Monthly AQI Overview", "Last 12 Months") 
                : renderBarChart(chartData, "Daily AQI Overview", "Last 14 Days")}
            </>
          )}
          {activeTab.startsWith("world") && (
             <>
               {yearlyData
                ? renderLineChart(yearlyData, "Global AQI Trend", "2014-2024")
                : renderLineChart(chartData, "World AQI Trends", "30-Day Daily AQI Trends")}
               {yearlyData 
                ? renderBarChart(yearlyData, "Yearly AQI Overview", "2014-2024") 
                : renderBarChart(chartData, "Daily AQI Overview", "Last 14 Days")}
             </>
          )}
        </div>
      )}
    </div>
  );
};

export default DataCharts;