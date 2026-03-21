# DocumentDB Bookings - Frontend

A React-based frontend for the AI-Powered Booking Search Workshop. This application provides a progressive experience that works **from day 0** and gets better as you complete each workshop module.

## Features

### Progressive Experience

| Stage | Backend State | Frontend Behavior |
|-------|---------------|-------------------|
| **Pre-Setup** | Nothing running | Demo mode with sample listings + setup guide |
| **Post Module 0** | DocumentDB running | Map + listings display |
| **Post Module 1** | Vector search works | Basic semantic search |
| **Post Module 2** | RAG chat works | Full conversational AI chat |
| **Post Module 3** | Multi-agent works | Advanced AI with agent routing |

### Demo Mode

When the backend isn't connected, the frontend automatically:
- Shows a **Setup Guide** with instructions
- Loads **sample listings** from embedded data
- Provides **basic text search** functionality
- Displays listings on an **interactive map**

## Getting Started

### In GitHub Codespaces (Recommended)

```bash
# Install dependencies
npm install

# Copy demo data to public folder (if not already there)
npm run copy-data

# Start development server
npm start
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Run development server on http://localhost:3000 |
| `npm run build` | Build for production |
| `npm test` | Run tests |
| `npm run copy-data` | Copy embedded_data.json to public folder |

## Architecture

```
src/
 components/           # UI Components
    Header.tsx        # App header with connection status
    SetupGuide.tsx    # Modal showing setup instructions
    MapView.tsx       # Leaflet map with listing markers
    ListingsPanel.tsx # List of search results
    ListingCard.tsx   # Individual listing card
    ChatPanel.tsx     # AI chat interface
    ConnectionStatus.tsx
 hooks/                # Custom React hooks
    useBackendStatus.ts  # Backend connection checker
    useDemoData.ts       # Demo data loader
 types.ts              # TypeScript type definitions
 App.tsx               # Main application component
 App.css               # Global styles
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Leaflet + react-leaflet** - Interactive maps
- **CSS** - Plain CSS (no framework) for reliability in Codespaces

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |

## How It Works

1. **On load**: Frontend checks if backend is available
2. **Backend offline**: Shows Setup Guide + Demo Mode
3. **Backend online**: Connects to real AI-powered search
4. **Chat**: Sends queries to backend `/query_message` endpoint
5. **Results**: Displays listings on map and in cards panel
