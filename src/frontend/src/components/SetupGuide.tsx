import React from 'react';
import './SetupGuide.css';

interface SetupGuideProps {
  isVisible: boolean;
  onDismiss: () => void;
}

export const SetupGuide: React.FC<SetupGuideProps> = ({ isVisible, onDismiss }) => {
  if (!isVisible) return null;

  return (
    <div className="setup-guide-overlay">
      <div className="setup-guide">
        <button className="close-button" onClick={onDismiss} aria-label="Close">
          ×
        </button>
        
        <div className="setup-header">
          <div className="setup-icon">🚀</div>
          <h2>Workshop Setup in Progress</h2>
          <p className="setup-subtitle">
            The backend isn't connected yet. Complete the setup modules to unlock full functionality!
          </p>
        </div>

        <div className="setup-progress">
          <div className="progress-track">
            <div className="progress-step current">
              <div className="step-marker">0</div>
              <div className="step-info">
                <span className="step-title">Setup & Environment</span>
                <span className="step-status">← Start here</span>
              </div>
            </div>
            <div className="progress-step">
              <div className="step-marker">1</div>
              <div className="step-info">
                <span className="step-title">Vector Search</span>
                <span className="step-status">Enables: Smart search</span>
              </div>
            </div>
            <div className="progress-step">
              <div className="step-marker">2</div>
              <div className="step-info">
                <span className="step-title">RAG Pattern</span>
                <span className="step-status">Enables: AI chat</span>
              </div>
            </div>
            <div className="progress-step">
              <div className="step-marker">3</div>
              <div className="step-info">
                <span className="step-title">Multi-Agent</span>
                <span className="step-status">Enables: Advanced AI</span>
              </div>
            </div>
          </div>
        </div>

        <div className="setup-actions">
          <h3>Quick Start</h3>
          <ol className="quick-steps">
            <li>
              <strong>Open Module 0:</strong>
              <code>exercises/Module-00.md</code>
            </li>
            <li>
              <strong>Start DocumentDB:</strong>
              <code>docker run -dt -p 10260:10260 --name documentdb-container documentdb --username admin --password password123</code>
            </li>
            <li>
              <strong>Start the backend:</strong>
              <code>cd src/api && uvicorn main:app --reload</code>
            </li>
          </ol>
        </div>

        <div className="demo-notice">
          <span className="demo-badge">Demo Mode Active</span>
          <p>
            You can explore the UI with sample data while completing the setup.
            Real AI-powered search will work once the backend is connected.
          </p>
        </div>

        <button className="continue-button" onClick={onDismiss}>
          Continue in Demo Mode
        </button>
      </div>
    </div>
  );
};
