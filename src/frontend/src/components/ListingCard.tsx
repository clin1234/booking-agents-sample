import React from 'react';
import { SearchResult } from '../types';
import './ListingCard.css';

interface ListingCardProps {
  listing: SearchResult;
  isSelected?: boolean;
  onClick?: () => void;
}

export const ListingCard: React.FC<ListingCardProps> = ({ 
  listing, 
  isSelected = false,
  onClick 
}) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const formatAmenities = (amenities?: string[]) => {
    if (!amenities || amenities.length === 0) return [];
    // Show first 3 amenities
    return amenities.slice(0, 3);
  };

  return (
    <div 
      className={`listing-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="listing-header">
        <h3 className="listing-name">{listing.name}</h3>
        <span className="listing-price">{formatPrice(listing.price)}<small>/night</small></span>
      </div>
      
      <div className="listing-details">
        {listing.property_type && (
          <span className="listing-type">{listing.property_type}</span>
        )}
        {listing.bedrooms && (
          <span className="listing-beds">
            {listing.bedrooms} {parseInt(listing.bedrooms) === 1 ? 'bedroom' : 'bedrooms'}
          </span>
        )}
      </div>

      {listing.similarity_score !== undefined && (
        <div className="listing-score">
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ width: `${listing.similarity_score * 100}%` }}
            />
          </div>
          <span className="score-label">
            {(listing.similarity_score * 100).toFixed(0)}% match
          </span>
        </div>
      )}

      {listing.amenities && listing.amenities.length > 0 && (
        <div className="listing-amenities">
          {formatAmenities(listing.amenities).map((amenity, idx) => (
            <span key={idx} className="amenity-tag">{amenity}</span>
          ))}
          {listing.amenities.length > 3 && (
            <span className="amenity-more">+{listing.amenities.length - 3} more</span>
          )}
        </div>
      )}

      {listing.description && (
        <p className="listing-description">
          {listing.description.slice(0, 120)}
          {listing.description.length > 120 ? '...' : ''}
        </p>
      )}
    </div>
  );
};
