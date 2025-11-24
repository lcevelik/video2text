import React from 'react';

const ModernButton = ({ children, primary = false, onClick, className = '', disabled = false }) => {
    const baseStyles = "px-5 py-2.5 rounded-lg font-bold text-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed";

    const primaryStyles = "bg-gradient-to-r from-accent to-success text-white hover:from-accent-hover hover:to-success border-none shadow-lg";
    const secondaryStyles = "bg-transparent text-text-primary border-2 border-border hover:bg-bg-tertiary hover:border-accent active:bg-sidebar";

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`${baseStyles} ${primary ? primaryStyles : secondaryStyles} ${className}`}
        >
            {children}
        </button>
    );
};

export default ModernButton;
