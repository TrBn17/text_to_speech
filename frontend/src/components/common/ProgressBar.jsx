import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({
    progress = 0,
    status = 'idle',
    currentStep = '',
    estimatedTime = '',
    showDetails = true
}) => {
    const getStatusIcon = () => {
        switch (status) {
            case 'preparing': return '⚙️';
            case 'uploading': return '📤';
            case 'processing': return '🎵';
            case 'generating': return '🔄';
            case 'downloading': return '⬇️';
            case 'completed': return '✅';
            case 'error': return '❌';
            default: return '⏳';
        }
    };

    const getStatusText = () => {
        switch (status) {
            case 'preparing': return 'Preparing content...';
            case 'uploading': return 'Uploading content...';
            case 'processing': return 'Processing audio...';
            case 'generating': return 'Generating conversation...';
            case 'downloading': return 'Downloading audio...';
            case 'completed': return 'Audio generation completed!';
            case 'error': return 'Generation failed';
            default: return 'Ready to start';
        }
    };

    const isActive = status !== 'idle' && status !== 'completed' && status !== 'error';

    return (
        <div className={`progress-container ${status}`}>
            {showDetails && (
                <div className="progress-header">
                    <div className="progress-status">
                        <span className="status-icon">{getStatusIcon()}</span>
                        <span className="status-text">{getStatusText()}</span>
                    </div>
                    {estimatedTime && isActive && (
                        <div className="estimated-time">
                            <span>~{estimatedTime}</span>
                        </div>
                    )}
                </div>
            )}

            <div className="progress-bar-container">
                <div
                    className={`progress-bar ${isActive ? 'active' : ''} ${status}`}
                    style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                >
                    {isActive && <div className="progress-shimmer"></div>}
                </div>
                <div className="progress-percentage">
                    {Math.round(progress)}%
                </div>
            </div>

            {currentStep && showDetails && (
                <div className="current-step">
                    {currentStep}
                </div>
            )}

            {status === 'error' && (
                <div className="error-message">
                    <span>❌ Something went wrong. Please try again.</span>
                </div>
            )}

            {status === 'completed' && (
                <div className="success-message">
                    <span>🎉 Your audio conversation is ready!</span>
                </div>
            )}
        </div>
    );
};

export default ProgressBar;