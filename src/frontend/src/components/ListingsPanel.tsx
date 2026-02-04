import React from 'react';
import { SearchResult } from '../types';
import { ListingCard } from './ListingCard';
import './ListingsPanel.css';

interface ListingsPanelProps {
  listings: SearchResult[];
  selectedId?: number;
  onSelectListing: (listing: SearchResult) => void;
  isLoading?: boolean;
  isDemo?: boolean;
}

export const ListingsPanel: React.FC<ListingsPanelProps> = ({
  listings,
  selectedId,
  onSelectListing,
  isLoading = false,
  isDemo = false,
}) => {
  if (isLoading) {
    return (
      <div className="listings-panel">
        <div className="listings-header">
          <h2>Listings</h2>
        </div>
        <div className="listings-loading">
          <div className="loading-spinner"></div>
          <p>Searching for properties...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="listings-panel">
      <div className="listings-header">
        <h2>Listings</h2>
        <span className="listings-count">
          {listings.length} {listings.length === 1 ? 'result' : 'results'}
          {isDemo && <span className="demo-indicator"> (Demo)</span>}
        </span>
      </div>

      {listings.length === 0 ? (
        <div className="listings-empty">
          <div className="empty-icon">🏠</div>
          <p>No listings to display yet.</p>
          <p className="empty-hint">
            {isDemo 
              ? 'Try searching for properties in the chat!'
              : 'Complete the setup to enable AI-powered search.'}
          </p>
        </div>
      ) : (
        <div className="listings-grid">
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              isSelected={listing.id === selectedId}
              onClick={() => onSelectListing(listing)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
