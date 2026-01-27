// Core types for the Contoso Bookings application

export interface Listing {
  id: string;
  listing_url: string;
  name: string;
  description: string;
  neighborhood_overview: string;
  latitude: string;
  longitude: string;
  price: string;
  amenities: string; // JSON string of amenities array
  beds: string;
  bedrooms: string;
  bathrooms: string;
  bathrooms_text: string;
  property_type: string;
  room_type: string;
  host_about: string;
  // Vector embedding (present in embedded_data.json)
  description_embedding?: number[];
}

export interface SearchResult {
  id: string;
  name: string;
  price: number;
  lat: number;
  lng: number;
  similarity_score?: number;
  property_type?: string;
  bedrooms?: string;
  amenities?: string[];
  description?: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  listings?: SearchResult[];
}

export interface BackendStatus {
  isConnected: boolean;
  isChecking: boolean;
  lastChecked: Date | null;
  error: string | null;
}

export type WorkshopStage = 
  | 'pre-setup'      // Nothing running
  | 'module-0'       // DocumentDB running, data loaded
  | 'module-1'       // Vector search works
  | 'module-2'       // RAG chat works
  | 'module-3';      // Multi-agent works

export interface AppState {
  stage: WorkshopStage;
  backendStatus: BackendStatus;
  userLocation: { lat: number; lng: number } | null;
  listings: SearchResult[];
  isDemo: boolean;
}
