import React, { useState, useCallback } from 'react';
import { Upload, FileAudio, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';

const UploadArea = ({ onTranscriptionComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [modelSize, setModelSize] = useState('base');

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleTranscribe = async () => {
    if (!file) return;

    setIsProcessing(true);
    setProgress(10); // Started
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_size', modelSize);

    try {
      // In a real app, we'd use a websocket or polling for real progress.
      // Here we simulate progress while waiting.
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 90));
      }, 1000);

      // Using localhost:8000 for backend
      const response = await axios.post('http://localhost:8000/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        onTranscriptionComplete(response.data);
      }, 500);

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Transcription failed. Ensure backend is running.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center max-w-3xl mx-auto">
      <div className="w-full mb-8 text-center">
        <h1 className="text-3xl font-bold mb-2">Upload Media</h1>
        <p className="text-text-secondary">Drag and drop video or audio files to start transcription</p>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`w-full aspect-video max-h-[400px] border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-all duration-300 bg-gray-900/50 backdrop-blur-sm
          ${isDragging ? 'border-blue-500 bg-blue-500/10 scale-[1.02]' : 'border-gray-700 hover:border-gray-600'}
        `}
      >
        {file ? (
          <div className="text-center p-8">
            <div className="w-20 h-20 bg-blue-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileAudio className="w-10 h-10 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-1">{file.name}</h3>
            <p className="text-text-secondary mb-6">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
            
            {!isProcessing && (
              <button 
                onClick={() => setFile(null)}
                className="text-sm text-red-400 hover:text-red-300 transition-colors"
              >
                Remove File
              </button>
            )}
          </div>
        ) : (
          <div className="text-center p-8">
            <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Upload className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Drag & Drop</h3>
            <p className="text-text-secondary mb-6">or click to browse files</p>
            <label className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg cursor-pointer transition-colors font-medium">
              Browse Files
              <input type="file" className="hidden" onChange={handleFileSelect} accept="audio/*,video/*" />
            </label>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-6 w-full p-4 bg-red-900/20 border border-red-900/50 rounded-lg flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {file && !isProcessing && (
        <div className="mt-8 flex gap-4 w-full justify-center items-center animate-fade-in">
           <select 
            value={modelSize} 
            onChange={(e) => setModelSize(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
           >
             <option value="tiny">Tiny (Fastest)</option>
             <option value="base">Base (Balanced)</option>
             <option value="small">Small</option>
             <option value="medium">Medium</option>
             <option value="large">Large (Most Accurate)</option>
           </select>

           <button
            onClick={handleTranscribe}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white rounded-lg shadow-lg shadow-blue-900/30 font-semibold transition-all transform hover:scale-105"
           >
             Start Transcription
           </button>
        </div>
      )}

      {isProcessing && (
        <div className="mt-8 w-full max-w-md">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-blue-400 font-medium">Transcribing...</span>
            <span className="text-text-secondary">{progress}%</span>
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 transition-all duration-300 ease-out relative overflow-hidden"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>
          <p className="text-center text-xs text-text-secondary mt-4">
            This may take a few minutes depending on file size and model selection.
          </p>
        </div>
      )}
    </div>
  );
};

export default UploadArea;
