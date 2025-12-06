import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart3, Network, FileText, Download, RefreshCw, AlertCircle } from 'lucide-react';
import Plot from 'react-plotly.js';
import toast from 'react-hot-toast';
import apiClient from '../api/client';

const ResultsPage = () => {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (!analysisId) {
      setError('No analysis ID provided');
      setLoading(false);
      return;
    }

    fetchResults();
  }, [analysisId]);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiClient.getResults(analysisId);
      setResults(data);
    } catch (error) {
      console.error('Error fetching results:', error);
      const errorMessage = error.response?.data?.error || 'Failed to load results';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const downloadResults = async (format = 'json') => {
    try {
      const blob = await apiClient.downloadResults(analysisId, format);

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis_${analysisId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`Results downloaded as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Failed to download results');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-red-600 mr-3 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Results</h3>
              <p className="text-red-700 mb-4">{error}</p>
              <div className="flex gap-3">
                <button onClick={fetchResults} className="btn-primary">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Retry
                </button>
                <button onClick={() => navigate('/')} className="btn-secondary">
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center py-12">
        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 mb-4">No results found for this analysis.</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Go to Dashboard
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'embeddings', label: 'Embeddings', icon: BarChart3 },
    { id: 'entities', label: 'Entities', icon: FileText },
    { id: 'network', label: 'Network', icon: Network },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600">Analysis ID: {analysisId}</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => downloadResults('json')}
            className="btn-secondary flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            JSON
          </button>
          <button
            onClick={() => downloadResults('csv')}
            className="btn-secondary flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            CSV
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">
                {results?.stats?.total_documents || 0}
              </div>
              <div className="text-sm text-gray-600">Documents Analyzed</div>
            </div>

            <div className="card text-center">
              <div className="text-2xl font-bold text-green-600 mb-2">
                {results?.stats?.total_entities || 0}
              </div>
              <div className="text-sm text-gray-600">Entities Found</div>
            </div>

            <div className="card text-center">
              <div className="text-2xl font-bold text-purple-600 mb-2">
                {results?.stats?.num_communities || 0}
              </div>
              <div className="text-sm text-gray-600">Communities</div>
            </div>

            <div className="card text-center">
              <div className="text-2xl font-bold text-orange-600 mb-2">
                {results?.stats?.avg_degree?.toFixed(2) || '0.00'}
              </div>
              <div className="text-sm text-gray-600">Avg. Degree</div>
            </div>
          </div>
        )}

        {activeTab === 'embeddings' && (
          <div className="space-y-6">
            {results?.scatter_plot && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Document Embeddings Visualization</h3>
                <div className="h-[600px]">
                  <Plot
                    data={results.scatter_plot.data || []}
                    layout={{
                      ...results.scatter_plot.layout,
                      autosize: true,
                      margin: { l: 60, r: 180, t: 80, b: 60 }
                    }}
                    config={{
                      responsive: true,
                      displayModeBar: true,
                      displaylogo: false,
                      toImageButtonOptions: {
                        format: 'png',
                        filename: 'embeddings_plot'
                      }
                    }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
              </div>
            )}

            {results?.features_chart && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Document Features Comparison</h3>
                <div className="h-[450px]">
                  <Plot
                    data={results.features_chart.data || []}
                    layout={{
                      ...results.features_chart.layout,
                      autosize: true
                    }}
                    config={{ responsive: true, displaylogo: false }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
              </div>
            )}

            {results?.similarity_heatmap && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Document Similarity Matrix</h3>
                <div className="h-[500px]">
                  <Plot
                    data={results.similarity_heatmap.data || []}
                    layout={{
                      ...results.similarity_heatmap.layout,
                      autosize: true
                    }}
                    config={{ responsive: true, displaylogo: false }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
              </div>
            )}

            {results?.clusters && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Document Clusters</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(results.clusters).map(([filename, cluster]) => (
                    <div key={filename} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium truncate mr-2" title={filename}>{filename}</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm whitespace-nowrap">
                        Cluster {cluster}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'entities' && (
          <div className="space-y-6">
            {results?.entities && Object.entries(results.entities).map(([filename, entityData]) => (
              <div key={filename}>
                <h2 className="text-2xl font-bold mb-4">{filename}</h2>

                {entityData.network_path && (
                  <div className="card mb-6">
                    <h3 className="text-lg font-semibold mb-4">Entity Network</h3>
                    <div className="h-[700px]">
                      <iframe
                        src={entityData.network_path.startsWith('http')
                          ? entityData.network_path
                          : `${process.env.REACT_APP_API_URL || 'http://localhost:8052'}/static/networks/${entityData.network_path}`}
                        className="w-full h-full border-0 rounded-lg"
                        title={`Entity Network ${filename}`}
                      />
                    </div>
                  </div>
                )}

                {entityData.visualizations?.analytics_plot && (
                  <div className="card mb-6">
                    <h3 className="text-lg font-semibold mb-4">Entity Analysis Dashboard</h3>
                    <div className="h-[500px]">
                      <Plot
                        data={entityData.visualizations.analytics_plot.data || []}
                        layout={{
                          ...entityData.visualizations.analytics_plot.layout,
                          autosize: true
                        }}
                        config={{ responsive: true, displaylogo: false }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                      />
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  {entityData.entity_counts && (
                    <div className="card">
                      <h4 className="font-semibold mb-3">Entity Types</h4>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {Object.entries(entityData.entity_counts)
                          .sort(([, a], [, b]) => b - a)
                          .map(([type, count]) => (
                            <div key={type} className="flex justify-between items-center">
                              <span className="text-sm font-medium">{type}</span>
                              <span className="px-2 py-1 bg-gray-100 rounded text-sm">{count}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {entityData.importance_scores && (
                    <div className="card">
                      <h4 className="font-semibold mb-3">Top Entities by Importance</h4>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {Object.entries(entityData.importance_scores)
                          .sort(([, a], [, b]) => b - a)
                          .slice(0, 15)
                          .map(([entity, score]) => (
                            <div key={entity} className="flex justify-between items-center">
                              <span className="text-sm truncate flex-1 mr-2" title={entity}>{entity}</span>
                              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm whitespace-nowrap">
                                {(score * 100).toFixed(1)}%
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>

                {entityData.entities && (
                  <div className="card">
                    <h4 className="font-semibold mb-3">All Entities ({Object.keys(entityData.entities).length})</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-96 overflow-y-auto">
                      {Object.entries(entityData.entities).map(([entity, type]) => (
                        <div key={entity} className="p-2 bg-gray-50 rounded text-sm">
                          <span className="font-medium">{entity}</span>
                          <span className="text-xs text-gray-500 ml-2">{type}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {!results?.entities && (
              <div className="card text-center py-12">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No entity data available</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'network' && (
          <div className="space-y-6">
            {results?.network && Object.entries(results.network).map(([filename, networkData]) => (
              <div key={filename}>
                <h2 className="text-2xl font-bold mb-6">{filename}</h2>

                {networkData.network_path && (
                  <div className="card mb-6">
                    <h3 className="text-lg font-semibold mb-4">Network Graph</h3>
                    <div className="h-[800px]">
                      <iframe
                        src={networkData.network_path.startsWith('http')
                          ? networkData.network_path
                          : `${process.env.REACT_APP_API_URL || 'http://localhost:8052'}/static/networks/${networkData.network_path}`}
                        className="w-full h-full border-0 rounded-lg"
                        title={`Network ${filename}`}
                      />
                    </div>
                  </div>
                )}

                {networkData.community_members && (
                  <div className="card mb-6">
                    <h3 className="text-lg font-semibold mb-4">Community Members</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(networkData.community_members)
                        .sort(([a], [b]) => parseInt(a) - parseInt(b))
                        .map(([commId, members]) => (
                          <div key={commId} className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-300">
                            <h4 className="font-bold text-blue-900 mb-3">
                              Community {commId}
                              <span className="ml-2 text-sm font-normal text-blue-700">
                                ({members.length} entities)
                              </span>
                            </h4>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                              {members.map((member, idx) => (
                                <div key={idx} className="flex justify-between items-center p-2 bg-white rounded shadow-sm hover:shadow-md transition-shadow">
                                  <span className="font-medium text-sm truncate mr-2" title={member.entity}>
                                    {member.entity}
                                  </span>
                                  <span className="text-xs bg-blue-200 text-blue-900 px-2 py-1 rounded font-medium whitespace-nowrap">
                                    {member.type}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {networkData.entities && (
                  <div className="card mb-6">
                    <h3 className="text-lg font-semibold mb-4">All Entities ({Object.keys(networkData.entities).length})</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-96 overflow-y-auto">
                      {Object.entries(networkData.entities).slice(0, 100).map(([entity, type]) => (
                        <div key={entity} className="p-2 bg-gray-50 rounded text-sm">
                          <span className="font-medium">{entity}</span>
                          <span className="text-xs text-gray-500 ml-2">{type}</span>
                        </div>
                      ))}
                    </div>
                    {Object.keys(networkData.entities).length > 100 && (
                      <p className="text-sm text-gray-500 mt-2">
                        Showing 100 of {Object.keys(networkData.entities).length} entities
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}

            {!results?.network && (
              <div className="card text-center py-12">
                <Network className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No network data available</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPage;









