import React from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full">
            <div className="bg-white rounded-xl shadow-lg border border-red-200 p-8">
              <div className="flex items-start mb-6">
                <div className="flex-shrink-0">
                  <AlertCircle className="w-10 h-10 text-red-600" />
                </div>
                <div className="ml-4 flex-1">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">
                    Something went wrong
                  </h1>
                  <p className="text-gray-600 mb-4">
                    We're sorry, but something unexpected happened. This error has been logged.
                  </p>
                  
                  {process.env.NODE_ENV === 'development' && this.state.error && (
                    <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                      <p className="text-sm font-mono text-red-600 mb-2">
                        {this.state.error.toString()}
                      </p>
                      {this.state.errorInfo && (
                        <details className="mt-2">
                          <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-900">
                            Stack trace
                          </summary>
                          <pre className="mt-2 text-xs text-gray-700 overflow-auto max-h-64">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </details>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={this.handleReload}
                  className="btn-primary flex items-center"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reload Page
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="btn-secondary flex items-center"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go to Homepage
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;