import React from 'react';
import './ConnectionStatus.css';

interface ConnectionStatusProps {
  isConnected: boolean;
  isChecking: boolean;
  isDemo: boolean;
  onRetry: () => void;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  isChecking,
  isDemo,
  onRetry,
}) => {
  if (isChecking) {
    return (
      <div className="connection-status checking">
        <span className="status-dot"></span>
        <span className="status-text">Checking backend...</span>
      </div>
    );
  }

  if (isConnected) {
    return (
      <div className="connection-status connected">
        <span className="status-dot"></span>
        <span className="status-text">Backend connected</span>
      </div>
    );
  }

  return (
    <div className="connection-status disconnected">
      <span className="status-dot"></span>
      <span className="status-text">
        {isDemo ? 'Demo mode' : 'Backend offline'}
      </span>
      <button className="retry-button" onClick={onRetry} title="Retry connection">
        ↻
      </button>
    </div>
  );
};
