import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, SearchResult } from '../types';
import './ChatPanel.css';

interface ChatPanelProps {
  isBackendConnected: boolean;
  isDemo: boolean;
  onSearch: (query: string) => Promise<{ message: string; listings: SearchResult[] }>;
  onDemoSearch: (query: string) => { message: string; listings: SearchResult[] };
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  isBackendConnected,
  isDemo,
  onSearch,
  onDemoSearch,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'system',
      content: isBackendConnected
        ? "👋 Hi! I'm your AI booking assistant. Tell me what kind of place you're looking for!"
        : "👋 Hi! I'm in demo mode with limited search. Complete Module 2 to enable AI-powered chat!",
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      let response: { message: string; listings: SearchResult[] };
      
      if (isBackendConnected && !isDemo) {
        response = await onSearch(userMessage.content);
      } else {
        // Demo mode: use local search
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate delay
        response = onDemoSearch(userMessage.content);
      }

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: response.message,
        timestamp: new Date(),
        listings: response.listings,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'system',
        content: "Chat isn't available yet — complete Module 2 to enable AI-powered responses!",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h2>AI Assistant</h2>
        {isDemo && <span className="demo-badge">Demo</span>}
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.type}`}>
            <div className="message-avatar">
              {msg.type === 'user' ? '👤' : msg.type === 'system' ? 'ℹ️' : '🤖'}
            </div>
            <div className="message-content">
              <p>{msg.content}</p>
              {msg.listings && msg.listings.length > 0 && (
                <div className="message-listings-note">
                  Found {msg.listings.length} matching {msg.listings.length === 1 ? 'listing' : 'listings'}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={
            isDemo 
              ? "Try: 'cozy apartment downtown'..." 
              : "What kind of place are you looking for?"
          }
          disabled={isLoading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={!inputValue.trim() || isLoading}
          className="chat-submit"
        >
          Send
        </button>
      </form>

      {isDemo && (
        <div className="chat-demo-notice">
          💡 Complete <strong>Module 2</strong> to enable real AI responses!
        </div>
      )}
    </div>
  );
};
