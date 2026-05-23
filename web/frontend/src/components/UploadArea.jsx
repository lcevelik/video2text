import React, { useState, useEffect } from 'react';
import { AlertCircle, Upload } from 'lucide-react';
import axios from 'axios';
import DropZone from './ui/DropZone';
import MultiLanguageDialog from './MultiLanguageDialog';

const UploadArea = ({ onTranscriptionComplete }) => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [showDialog, setShowDialog] = useState(false);

  const handleFileDropped = (droppedFile) => {
    setFile(droppedFile);
    setError(null);
    // Auto-show dialog when file is dropped (matches desktop behavior)
    setShowDialog(true);
  };

  const handleDialogConfirm = async (options) => {
    setShowDialog(false);
    await handleTranscribe(options);
  };

  const handleTranscribe = async (options) => {
    if (!file) return;

    setIsProcessing(true);
    setProgress(10);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    // Add language options to formData
    if (options.isMulti) {
      formData.append('language_mode', 'multi');
      formData.append('languages', JSON.stringify(options.languages));
    } else {
      formData.append('language_mode', 'single');
      formData.append('language', options.language);
    }

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
    <div className="flex flex-col h-full">
      <div className="mb-6">
        <p className="text-gray-400 text-sm">
          Drag and drop video/audio file
        </p>
      </div>

      <div className="flex-1 flex flex-col gap-6">
        {/* Drop Zone */}
        <div className="flex-1 min-h-[200px]">
          <DropZone
            onFileDropped={handleFileDropped}
            onClick={() => { }}
          />
        </div>

        {/* Progress */}
        {file && (
          <div className="text-sm text-gray-400">
            {isProcessing ? 'Transcribing...' : 'Ready to transcribe'}
          </div>
        )}

        {isProcessing && (
          <div className="h-6 bg-[#333] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#00dcd0] transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Info tip */}
        <p className="text-xs text-[#00dcd0]">
          ℹ️ Files automatically transcribe when dropped or selected
        </p>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>

      <MultiLanguageDialog
        isOpen={showDialog}
        onClose={() => setShowDialog(false)}
        onConfirm={handleDialogConfirm}
      />
    </div>
  );
};

export default UploadArea;
