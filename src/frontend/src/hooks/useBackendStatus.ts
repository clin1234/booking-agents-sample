import { useState, useEffect, useCallback } from 'react';
import { BackendStatus } from '../types';

// Helper to get the API base URL, supporting Codespaces
const getApiBaseUrl = (): string => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // Auto-detect Codespaces URL from current hostname
  const hostname = window.location.hostname;
  if (hostname.includes('.app.github.dev') || hostname.includes('.preview.app.github.dev')) {
    // Replace port 3000 with 8000 in the Codespaces URL
    return window.location.origin.replace('-3000.', '-8000.');
  }
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export function useBackendStatus(checkInterval = 30000) {
  const [status, setStatus] = useState<BackendStatus>({
    isConnected: false,
    isChecking: true,
    lastChecked: null,
    error: null,
  });

  const checkConnection = useCallback(async () => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    
    try {
      // Try to reach the backend with a simple request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${API_BASE_URL}/docs`, {
        method: 'HEAD',
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      setStatus({
        isConnected: response.ok,
        isChecking: false,
        lastChecked: new Date(),
        error: response.ok ? null : `Server returned ${response.status}`,
      });
    } catch (error) {
      setStatus({
        isConnected: false,
        isChecking: false,
        lastChecked: new Date(),
        error: error instanceof Error ? error.message : 'Connection failed',
      });
    }
  }, []);

  useEffect(() => {
    // Check immediately
    checkConnection();
    
    // Then check periodically
    const interval = setInterval(checkConnection, checkInterval);
    
    return () => clearInterval(interval);
  }, [checkConnection, checkInterval]);

  return { ...status, refetch: checkConnection };
}
