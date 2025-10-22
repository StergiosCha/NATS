import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, X, BarChart3, Network } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '../api/client';

const UploadPage = () => {
  const [files, setFiles] = useState([]);
  const [analysisType, setAnalysisType] = useState('enhanced_ner');
  const [embeddingType, setEmbeddingType] = useState('sentence_transformer');
  const [reductionMethod, setReductionMethod] = useState('pca');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const navigate = useNavigate();

  // Fixed: Proper dependencies in useCallback
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const reasons = rejectedFiles.map(f => f.errors.map(e => e.message).join(', ')).join('; ');
      toast.error(`Some files were rejected: ${reasons}`);
    }

    const textFiles = acceptedFiles.filter(file => 
      file.type === 'text/plain' || file.name.endsWith('.txt')
    );
    
    if (textFiles.length !== acceptedFiles.length) {
      toast.error('Only .txt files are allowed');
    }
    
    if (textFiles.length > 0) {
      setFiles(prev => [...prev, ...textFiles]);
      toast.success(`${textFiles.length} file(s) added`);
    }
  }, []); // No external dependencies needed

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB max per file
  });

  const removeFile = (indexToRemove) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      toast.error('Please select at least one file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('analysis_type', analysisType);
      formData.append('embedding_type', embeddingType);
      formData.append('reduction_method', reductionMethod);

      // Simulate progress (real progress would need backend support)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const data = await apiClient.analyzeFiles(formData);
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      const analysisId = data.analysis_id;
      toast.success('Analysis completed successfully!');
      
      // Small delay to show 100% progress
      setTimeout(() => {
        navigate(`/results/${analysisId}`);
      }, 500);
      
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.error || 'Upload failed. Please try again.';
      toast.error(errorMessage);
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Text Files</h1>
        <p className="text-gray-600">Upload your text files for comprehensive analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Upload className="w-5 h-5 mr-2" />
            File Upload
          </h2>
          
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            {isDragActive ? (
              <p className="text-blue-600 font-medium">Drop the files here...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2 font-medium">
                  Drag & drop text files here, or click to select
                </p>
                <p className="text-sm text-gray-500">
                  Only .txt files are supported (max 10MB each)
                </p>
              </div>
            )}
          </div>

          {files.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium">Selected Files ({files.length}):</h3>
                <button
                  onClick={() => setFiles([])}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Clear All
                </button>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg group">
                    <div className="flex items-center flex-1 min-w-0 mr-2">
                      <FileText className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" />
                      <span className="text-sm truncate" title={file.name}>{file.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                      <button
                        onClick={() => removeFile(index)}
                        className="p-1 hover:bg-red-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Remove file"
                      >
                        <X className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Analysis Configuration */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Analysis Configuration</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Analysis Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analysis Type
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                className="input-field"
                disabled={isUploading}
              >
                <option value="enhanced_ner">Enhanced Named Entity Recognition</option>
                <option value="enhanced_embeddings">Document Embeddings</option>
                <option value="enhanced_network">Network Analysis</option>
                <option value="comprehensive">Comprehensive Analysis</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">
                {analysisType === 'enhanced_ner' && 'Extract and analyze entities with Greek language support'}
                {analysisType === 'enhanced_embeddings' && 'Create semantic embeddings and clusters'}
                {analysisType === 'enhanced_network' && 'Build entity relationship networks'}
                {analysisType === 'comprehensive' && 'Run all analysis types (takes longer)'}
              </p>
            </div>

            {/* Embedding Type (for embeddings analysis) */}
            {(analysisType === 'enhanced_embeddings' || analysisType === 'comprehensive') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Embedding Model
                </label>
                <select
                  value={embeddingType}
                  onChange={(e) => setEmbeddingType(e.target.value)}
                  className="input-field"
                  disabled={isUploading}
                >
                  <option value="sentence_transformer">Sentence Transformer (Recommended)</option>
                  <option value="doc2vec">Doc2Vec</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Sentence Transformer works better for multilingual content
                </p>
              </div>
            )}

            {/* Reduction Method (for embeddings analysis) */}
            {(analysisType === 'enhanced_embeddings' || analysisType === 'comprehensive') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dimension Reduction
                </label>
                <select
                  value={reductionMethod}
                  onChange={(e) => setReductionMethod(e.target.value)}
                  className="input-field"
                  disabled={isUploading}
                >
                  <option value="pca">PCA (Fast)</option>
                  <option value="tsne">t-SNE (Better separation)</option>
                  <option value="umap">UMAP (Best quality)</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  {reductionMethod === 'pca' && 'Fastest, linear reduction'}
                  {reductionMethod === 'tsne' && 'Better at preserving local structure'}
                  {reductionMethod === 'umap' && 'Best quality, preserves global and local structure'}
                </p>
              </div>
            )}

            {/* Progress Bar */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Processing...</span>
                  <span className="text-gray-900 font-medium">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={files.length === 0 || isUploading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Start Analysis
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Features Overview */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center hover:shadow-lg transition-shadow">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-semibold mb-2">Enhanced NER</h3>
          <p className="text-sm text-gray-600">
            Advanced entity recognition with Greek language support and semantic relationships
          </p>
        </div>
        
        <div className="card text-center hover:shadow-lg transition-shadow">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-semibold mb-2">Document Embeddings</h3>
          <p className="text-sm text-gray-600">
            Multiple embedding models with clustering and similarity analysis
          </p>
        </div>
        
        <div className="card text-center hover:shadow-lg transition-shadow">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Network className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-semibold mb-2">Network Analysis</h3>
          <p className="text-sm text-gray-600">
            Community detection and centrality analysis with interactive visualizations
          </p>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;