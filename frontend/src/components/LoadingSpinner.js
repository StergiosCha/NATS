import React from 'react';
import { RefreshCw } from 'lucide-react';

const LoadingSpinner = ({ message = 'Loading...', size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex items-center justify-center min-h-96">
      <div className="text-center">
        <RefreshCw className={`${sizeClasses[size]} animate-spin mx-auto mb-4 text-blue-600`} />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;