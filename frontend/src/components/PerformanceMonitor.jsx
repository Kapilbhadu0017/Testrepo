import { useEffect, useState } from 'react';

const PerformanceMonitor = () => {
  const [fps, setFps] = useState(0);
  const [memory, setMemory] = useState(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    let animationId;

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        setFps(Math.round((frameCount * 1000) / (currentTime - lastTime)));
        frameCount = 0;
        lastTime = currentTime;
      }
      
      animationId = requestAnimationFrame(measureFPS);
    };

    const measureMemory = () => {
      if ('memory' in performance) {
        const mem = performance.memory;
        setMemory({
          used: Math.round(mem.usedJSHeapSize / 1024 / 1024),
          total: Math.round(mem.totalJSHeapSize / 1024 / 1024),
          limit: Math.round(mem.jsHeapSizeLimit / 1024 / 1024)
        });
      }
    };

    // Start FPS monitoring
    animationId = requestAnimationFrame(measureFPS);
    
    // Measure memory every 2 seconds
    const memoryInterval = setInterval(measureMemory, 2000);

    // Toggle visibility with Ctrl+Shift+P
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        setIsVisible(prev => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
      clearInterval(memoryInterval);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  if (!isVisible) return null;

  const getFPSColor = (fps) => {
    if (fps >= 55) return 'text-green-400';
    if (fps >= 45) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getMemoryColor = (used, total) => {
    const percentage = (used / total) * 100;
    if (percentage < 70) return 'text-green-400';
    if (percentage < 85) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="fixed top-4 right-4 bg-gray-900/90 backdrop-blur-sm border border-purple-500/30 rounded-lg p-3 text-xs z-50">
      <div className="flex items-center space-x-4">
        <div>
          <div className="text-gray-400">FPS</div>
          <div className={`font-bold ${getFPSColor(fps)}`}>{fps}</div>
        </div>
        {memory && (
          <div>
            <div className="text-gray-400">Memory</div>
            <div className={`font-bold ${getMemoryColor(memory.used, memory.total)}`}>
              {memory.used}MB / {memory.total}MB
            </div>
          </div>
        )}
        <div className="text-gray-500 text-xs">
          Ctrl+Shift+P
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitor; 