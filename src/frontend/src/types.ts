// Core types for the DocumentDB Bookings application

export interface Listing {
  id: number;
  listing_url: string;
  name: string;
  description: string;
  neighborhood_overview: string;
  latitude: number;
  longitude: number;
  price: number | null;
  amenities: string[]; // Array of amenities
  beds: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  bathrooms_text: string;
  property_type: string;
  room_type: string;
  host_about: string;
  // Vector embedding (present in embedded_data.json)
  description_embedding?: number[];
}

export interface SearchResult {
  id: number;
  name: string;
  price: number;
  lat: number;
  lng: number;
  similarity_score?: number;
  property_type?: string;
  bedrooms?: number | null;
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
