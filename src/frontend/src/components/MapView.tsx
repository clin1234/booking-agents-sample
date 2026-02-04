import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { SearchResult } from '../types';
import './MapView.css';

// Fix default marker icon issue with webpack/CRA
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const SelectedIcon = L.icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="30" height="45">
      <path fill="#0078d4" stroke="#fff" stroke-width="1" d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24c0-6.6-5.4-12-12-12z"/>
      <circle fill="#fff" cx="12" cy="12" r="5"/>
    </svg>
  `),
  iconSize: [30, 45],
  iconAnchor: [15, 45],
  popupAnchor: [0, -40],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapViewProps {
  listings: SearchResult[];
  selectedId?: number;
  onSelectListing: (listing: SearchResult) => void;
  center?: { lat: number; lng: number };
}

// Component to handle map view updates
const MapUpdater: React.FC<{ listings: SearchResult[]; center?: { lat: number; lng: number } }> = ({ 
  listings, 
  center 
}) => {
  const map = useMap();
  
  useEffect(() => {
    if (listings.length > 0) {
      const bounds = L.latLngBounds(
        listings.map(l => [l.lat, l.lng] as L.LatLngExpression)
      );
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
    } else if (center) {
      map.setView([center.lat, center.lng], 12);
    }
  }, [listings, center, map]);
  
  return null;
};

export const MapView: React.FC<MapViewProps> = ({
  listings,
  selectedId,
  onSelectListing,
  center = { lat: 39.7392, lng: -104.9903 }, // Denver default
}) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="map-view">
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={12}
        className="map-container"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapUpdater listings={listings} center={center} />
        
        {listings.map((listing) => (
          <Marker
            key={listing.id}
            position={[listing.lat, listing.lng] as L.LatLngExpression}
            icon={listing.id === selectedId ? SelectedIcon : DefaultIcon}
            eventHandlers={{
              click: () => onSelectListing(listing),
            }}
          >
            <Popup>
              <div className="popup-content">
                <h4>{listing.name}</h4>
                <p className="popup-price">{formatPrice(listing.price)}/night</p>
                {listing.property_type && (
                  <p className="popup-type">{listing.property_type}</p>
                )}
                {listing.similarity_score !== undefined && (
                  <p className="popup-score">
                    Match: {(listing.similarity_score * 100).toFixed(0)}%
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      {listings.length === 0 && (
        <div className="map-overlay">
          <div className="map-empty-message">
            <span className="map-icon">🗺️</span>
            <p>Search for properties to see them on the map</p>
          </div>
        </div>
      )}
    </div>
  );
};
