import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, Network, FileText, Upload, TrendingUp, Users, Globe } from 'lucide-react';

const Dashboard = () => {
  // Fixed: Static color classes instead of dynamic template literals
  const colorClasses = {
    blue: {
      bg: 'bg-blue-100',
      text: 'text-blue-600',
      icon: 'text-blue-600'
    },
    green: {
      bg: 'bg-green-100',
      text: 'text-green-600',
      icon: 'text-green-600'
    },
    purple: {
      bg: 'bg-purple-100',
      text: 'text-purple-600',
      icon: 'text-purple-600'
    }
  };

  const features = [
    {
      icon: FileText,
      title: 'Enhanced NER',
      description: 'Advanced named entity recognition with Greek language support, custom patterns, and semantic relationship detection.',
      color: 'blue',
      stats: '19 entity types'
    },
    {
      icon: BarChart3,
      title: 'Document Embeddings',
      description: 'Multiple embedding models including Sentence Transformers and Doc2Vec with clustering and similarity analysis.',
      color: 'green',
      stats: '3 reduction methods'
    },
    {
      icon: Network,
      title: 'Network Analysis',
      description: 'Community detection using Louvain algorithm, centrality measures, and interactive network visualizations.',
      color: 'purple',
      stats: 'Advanced algorithms'
    }
  ];

  const recentAnalyses = [
    { id: '1', name: 'Greek Literature Analysis', type: 'Comprehensive', date: '2024-01-15', status: 'completed' },
    { id: '2', name: 'News Articles Processing', type: 'NER', date: '2024-01-14', status: 'completed' },
    { id: '3', name: 'Academic Papers', type: 'Embeddings', date: '2024-01-13', status: 'completed' },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          NATS - Natural Language Analysis & Text Suite
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Advanced text analysis platform with enhanced embeddings, sophisticated NER, 
          and comprehensive network analysis for Greek and multilingual content.
        </p>
        <Link to="/upload" className="inline-flex items-center btn-primary text-lg px-8 py-3">
          <Upload className="w-5 h-5 mr-2" />
          Start Analysis
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div className="card text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">19</div>
          <div className="text-sm text-gray-600">Entity Types</div>
        </div>
        
        <div className="card text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">3</div>
          <div className="text-sm text-gray-600">Embedding Models</div>
        </div>
        
        <div className="card text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Network className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">5+</div>
          <div className="text-sm text-gray-600">Centrality Measures</div>
        </div>
        
        <div className="card text-center">
          <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <TrendingUp className="w-6 h-6 text-orange-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">100%</div>
          <div className="text-sm text-gray-600">Greek Support</div>
        </div>
      </div>

      {/* Features */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Advanced Analysis Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            const colors = colorClasses[feature.color];
            
            return (
              <div key={index} className="card hover:shadow-xl transition-shadow duration-300">
                <div className={`w-16 h-16 ${colors.bg} rounded-xl flex items-center justify-center mb-6`}>
                  <Icon className={`w-8 h-8 ${colors.icon}`} />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-600 mb-4">{feature.description}</p>
                <div className={`text-sm font-medium ${colors.text}`}>
                  {feature.stats}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Recent Analyses</h2>
          <Link to="/upload" className="text-blue-600 hover:text-blue-700 font-medium">
            View All →
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recentAnalyses.map((analysis) => (
            <div key={analysis.id} className="card">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold">{analysis.name}</h3>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  analysis.status === 'completed' 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {analysis.status}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">Type: {analysis.type}</p>
              <p className="text-sm text-gray-500">{analysis.date}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Getting Started */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Upload your text files and discover insights with our advanced analysis tools. 
            Support for Greek and multilingual content with comprehensive visualizations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/upload" className="inline-flex items-center btn-primary">
              <Upload className="w-4 h-4 mr-2" />
              Upload Files
            </Link>
            <button className="inline-flex items-center btn-secondary">
              <Globe className="w-4 h-4 mr-2" />
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;






