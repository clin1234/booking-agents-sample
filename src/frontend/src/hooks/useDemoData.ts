import { useState, useEffect, useCallback } from 'react';
import { Listing, SearchResult } from '../types';

export function useDemoData() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch the embedded data from the public folder or data folder
    const loadData = async () => {
      try {
        // Try to load from the data folder (relative to public for CRA)
        const response = await fetch('/embedded_data.json');
        if (response.ok) {
          const data = await response.json();
          setListings(data);
        } else {
          // Fallback: generate some demo data if file not available
          console.warn('Could not load embedded_data.json, using fallback demo data');
          setListings(getFallbackData());
        }
      } catch (err) {
        console.warn('Failed to load demo data:', err);
        setListings(getFallbackData());
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  // Convert raw listings to search results format
  const getSearchResults = useCallback((limit = 10): SearchResult[] => {
    return listings.slice(0, limit).map(listing => ({
      id: listing.id,
      name: listing.name,
      price: listing.price ?? 0,
      lat: listing.latitude,
      lng: listing.longitude,
      property_type: listing.property_type,
      bedrooms: listing.bedrooms,
      amenities: listing.amenities ?? [],
      description: listing.description,
    }));
  }, [listings]);

  // Simple text search for demo mode
  const searchListings = useCallback((query: string, limit = 5): SearchResult[] => {
    const lowerQuery = query.toLowerCase();
    
    const matched = listings
      .filter(listing => 
        listing.name.toLowerCase().includes(lowerQuery) ||
        listing.description.toLowerCase().includes(lowerQuery) ||
        listing.neighborhood_overview.toLowerCase().includes(lowerQuery) ||
        listing.property_type.toLowerCase().includes(lowerQuery)
      )
      .slice(0, limit)
      .map(listing => ({
        id: listing.id,
        name: listing.name,
        price: listing.price ?? 0,
        lat: listing.latitude,
        lng: listing.longitude,
        property_type: listing.property_type,
        bedrooms: listing.bedrooms,
        amenities: listing.amenities ?? [],
        description: listing.description,
        similarity_score: 0.85 + Math.random() * 0.15, // Fake score for demo
      }));

    // If no matches, return random listings
    if (matched.length === 0) {
      return getSearchResults(limit);
    }

    return matched;
  }, [listings, getSearchResults]);

  return {
    listings,
    isLoading,
    error,
    getSearchResults,
    searchListings,
    totalCount: listings.length,
  };
}

// Fallback demo data in case the JSON file isn't available
function getFallbackData(): Listing[] {
  return [
    {
      id: 1,
      listing_url: "#",
      name: "Cozy Downtown Loft",
      description: "Modern loft in the heart of downtown with stunning city views. Perfect for couples or solo travelers looking for an urban retreat.",
      neighborhood_overview: "Located in the vibrant downtown area with restaurants, cafes, and nightlife just steps away.",
      latitude: 39.7392,
      longitude: -104.9903,
      price: 125.0,
      amenities: ["WiFi", "Kitchen", "Air conditioning", "Workspace"],
      beds: 1,
      bedrooms: 1,
      bathrooms: 1,
      bathrooms_text: "1 bath",
      property_type: "Entire loft",
      room_type: "Entire home/apt",
      host_about: "Local host with years of experience.",
    },
    {
      id: 2,
      listing_url: "#",
      name: "Charming Victorian Home",
      description: "Beautiful Victorian home with original architecture and modern amenities. Spacious backyard and parking included.",
      neighborhood_overview: "Quiet residential neighborhood perfect for families, close to parks and schools.",
      latitude: 39.7512,
      longitude: -105.0008,
      price: 195.0,
      amenities: ["WiFi", "Kitchen", "Parking", "Washer", "Dryer", "Backyard"],
      beds: 3,
      bedrooms: 3,
      bathrooms: 2,
      bathrooms_text: "2 baths",
      property_type: "Entire home",
      room_type: "Entire home/apt",
      host_about: "We love hosting guests!",
    },
    {
      id: 3,
      listing_url: "#",
      name: "Mountain View Retreat",
      description: "Escape to this peaceful retreat with stunning mountain views. Great for hikers and nature lovers.",
      neighborhood_overview: "Nestled in the foothills with easy access to hiking trails and outdoor activities.",
      latitude: 39.78,
      longitude: -105.05,
      price: 175.0,
      amenities: ["WiFi", "Kitchen", "Fireplace", "Hot tub", "Mountain view"],
      beds: 2,
      bedrooms: 2,
      bathrooms: 1.5,
      bathrooms_text: "1.5 baths",
      property_type: "Entire cabin",
      room_type: "Entire home/apt",
      host_about: "Adventure seekers welcome!",
    },
    {
      id: 4,
      listing_url: "#",
      name: "Artsy Studio Near Museums",
      description: "Creative studio space near the art district. Walking distance to museums and galleries.",
      neighborhood_overview: "In the heart of the arts district with galleries, studios, and cafes.",
      latitude: 39.728,
      longitude: -104.985,
      price: 89.0,
      amenities: ["WiFi", "Kitchen", "Workspace", "Art supplies"],
      beds: 1,
      bedrooms: 0,
      bathrooms: 1,
      bathrooms_text: "1 bath",
      property_type: "Entire studio",
      room_type: "Entire home/apt",
      host_about: "Artist and creative host.",
    },
    {
      id: 5,
      listing_url: "#",
      name: "Family-Friendly Suburban Home",
      description: "Spacious family home with game room, large yard, and quiet neighborhood. Perfect for family vacations.",
      neighborhood_overview: "Safe, quiet suburb with excellent schools and family activities nearby.",
      latitude: 39.71,
      longitude: -104.92,
      price: 225.0,
      amenities: ["WiFi", "Kitchen", "Game room", "Yard", "Parking", "BBQ grill"],
      beds: 5,
      bedrooms: 4,
      bathrooms: 3,
      bathrooms_text: "3 baths",
      property_type: "Entire home",
      room_type: "Entire home/apt",
      host_about: "We're a family who loves to host other families!",
    },
  ];
}
