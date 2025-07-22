import React from 'react';

const LoadingSpinner = ({ size = "md", text = "Loading...", className = "" }) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8",
    xl: "w-12 h-12"
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-3 ${className}`}>
      <div className="relative">
        <div className={`${sizeClasses[size]} spinner-futuristic`} aria-hidden="true"></div>
        <div className={`${sizeClasses[size]} absolute inset-0 spinner-pulse`} aria-hidden="true"></div>
      </div>
      {text && (
        <p className="text-sm text-gray-400 animate-pulse font-medium">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner; 