import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';

// Fix for default marker icons in react-leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});
L.Marker.prototype.options.icon = DefaultIcon;

interface MapProps {
  user_coordinates: { lat: number; lng: number };
  search_map_results: { name: String; price: number; similarity_score: number; lat: number; lng: number }[];
}

const Map: React.FC<MapProps> = ({ user_coordinates, search_map_results }) => {
  return (
    <MapContainer
      center={[user_coordinates.lat, user_coordinates.lng]}
      zoom={10}
      style={{ width: '100%', height: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* User location marker */}
      <CircleMarker
        center={[user_coordinates.lat, user_coordinates.lng]}
        radius={10}
        pathOptions={{ color: 'blue', fillColor: 'blue', fillOpacity: 0.6 }}
      >
        <Popup>Your location</Popup>
      </CircleMarker>

      {/* Search result markers */}
      {search_map_results.map((search_result, index) => (
        <Marker key={index} position={[search_result.lat, search_result.lng]}>
          <Popup>
            <div className="marker-popup">
              <h3>{search_result.name}</h3>
              <p>Price: ${search_result.price} per day</p>
              <p>Similarity Score: {search_result.similarity_score}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default Map;