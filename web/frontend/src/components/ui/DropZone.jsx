import React, { useState, useRef } from 'react';
import { Upload } from 'lucide-react';

const DropZone = ({ onFileDropped, onClick, className = '' }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [hasFile, setHasFile] = useState(false);
    const [fileName, setFileName] = useState('');
    const fileInputRef = useRef(null);

    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFileInput = (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFile = (file) => {
        setHasFile(true);
        setFileName(file.name);
        if (onFileDropped) {
            onFileDropped(file);
        }
    };

    const handleClick = () => {
        if (onClick) {
            onClick();
        } else {
            fileInputRef.current?.click();
        }
    };

    return (
        <div
            onClick={handleClick}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className={`
        relative h-[150px] rounded-lg border-2 border-dashed transition-all duration-200 cursor-pointer flex flex-col items-center justify-center p-4
        ${isDragging
                    ? 'border-accent bg-bg-tertiary'
                    : hasFile
                        ? 'border-accent bg-background'
                        : 'border-border bg-background hover:border-accent hover:bg-bg-tertiary'
                }
        ${className}
      `}
        >
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileInput}
                className="hidden"
                accept="video/*,audio/*"
            />

            {hasFile ? (
                <div className="flex flex-col items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center text-accent">
                        <Upload className="w-5 h-5" />
                    </div>
                    <span className="text-accent font-semibold text-sm">✓ {fileName}</span>
                </div>
            ) : (
                <div className="flex flex-col items-center gap-2">
                    <span className="text-text-secondary text-sm font-medium">
                        Drag and drop video/audio file
                    </span>
                </div>
            )}
        </div>
    );
};

export default DropZone;
