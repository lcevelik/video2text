
import React, { useState } from 'react';
import { AlertCircle, Sparkles } from 'lucide-react';
import axios from 'axios';
import DropZone from './ui/DropZone';
import ModernButton from './ui/ModernButton';

const UploadArea = ({ onTranscriptionComplete }) => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [modelSize, setModelSize] = useState('base');

  const handleFileDropped = (droppedFile) => {
    setFile(droppedFile);
    setError(null);
  };

  const handleTranscribe = async () => {
    if (!file) return;

    setIsProcessing(true);
    setProgress(10);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_size', modelSize);

    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 90));
      }, 1000);

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
    <div className="flex flex-col gap-8 max-w-3xl mx-auto mt-12 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
          Upload <span className="bg-gradient-to-r from-accent to-success bg-clip-text text-transparent">Media</span>
        </h1>
        <p className="text-text-secondary text-lg">
          Drag and drop video or audio files to start transcription
        </p>
      </div>

      {/* Drop Zone Card */}
      <div className="bg-sidebar/50 backdrop-blur-md border border-border rounded-2xl p-8 shadow-2xl">
        <DropZone
          onFileDropped={handleFileDropped}
          onClick={() => { }}
        />
      </div>

      {/* Progress Section */}
      {(file || isProcessing) && (
        <div className="bg-sidebar/50 backdrop-blur-md border border-border rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-text-secondary text-sm font-medium">
              {isProcessing ? `Processing... ${progress}% ` : "Ready to transcribe"}
            </span>
            {isProcessing && (
              <Sparkles className="w-5 h-5 text-accent animate-pulse" />
            )}
          </div>

          {isProcessing && (
            <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-accent to-success transition-all duration-300 ease-out"
                style={{ width: `${progress}% ` }}
              />
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-error/10 border border-error/50 rounded-xl flex items-center gap-3 text-error backdrop-blur-md">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Controls */}
      {file && !isProcessing && (
        <div className="bg-sidebar/50 backdrop-blur-md border border-border rounded-2xl p-6 shadow-xl flex flex-col gap-4">
          <div className="flex items-center gap-4">
            <label className="text-text-secondary text-sm font-medium">Model:</label>
            <select
              value={modelSize}
              onChange={(e) => setModelSize(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-border text-text-primary rounded-lg px-4 py-2.5 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all"
            >
              <option value="tiny">Tiny (Fastest)</option>
              <option value="base">Base (Balanced)</option>
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large (Most Accurate)</option>
            </select>
          </div>

          <ModernButton
            primary
            onClick={handleTranscribe}
            className="w-full py-3.5 text-base shadow-lg shadow-accent/20 hover:shadow-accent/30"
          >
            <div className="flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5" />
              Start Transcription
            </div>
          </ModernButton>
        </div>
      )}
    </div>
  );
};

export default UploadArea;
