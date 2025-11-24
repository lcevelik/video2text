import React from 'react';

const Card = ({ title, children, className = '' }) => {
    return (
        <div className={`bg-card-bg border border-border rounded-xl p-5 ${className}`}>
            {title && (
                <h3 className="text-lg font-bold text-text-primary mb-4">{title}</h3>
            )}
            <div className="flex flex-col gap-4">
                {children}
            </div>
        </div>
    );
};

export default Card;
