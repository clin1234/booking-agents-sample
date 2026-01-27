import React from 'react';
import './Header.css';
import { ConnectionStatus } from './ConnectionStatus';

interface HeaderProps {
  isConnected: boolean;
  isChecking: boolean;
  isDemo: boolean;
  onRetryConnection: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isConnected,
  isChecking,
  isDemo,
  onRetryConnection,
}) => {
  return (
    <header className="app-header">
      <div className="header-left">
        <img src="/Azure-Cosmos-DB.svg" alt="Logo" className="header-logo" />
        <h1 className="header-title">Contoso Bookings</h1>
        <span className="header-subtitle">AI-Powered Search Workshop</span>
      </div>
      <div className="header-right">
        <ConnectionStatus
          isConnected={isConnected}
          isChecking={isChecking}
          isDemo={isDemo}
          onRetry={onRetryConnection}
        />
      </div>
    </header>
  );
};
