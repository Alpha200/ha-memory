# HA Memory

A FastMCP-based memory management service that allows you to store, retrieve, and organize memories with timestamps and location information.

## Features

- 📝 **Create and Update Memories**: Store memories with titles, content, and optional metadata
- 📍 **Location Tracking**: Associate memories with specific places
- ⏰ **Relative Dates**: Use natural language for dates like "3 days ago" or "in 2 weeks"
- 🔍 **Search and Filter**: Find memories by title or location
- 💾 **Persistent Storage**: All memories are saved to JSON file with automatic persistence
- 🐳 **Docker Ready**: Containerized application with volume mounting for data persistence

## API Endpoints

The service provides the following MCP tools:

- `create_or_update_memory` - Create or update a memory entry
- `list_memories` - List all memory titles
- `get_memory` - Retrieve a specific memory by title
- `delete_memory` - Delete a memory entry
- `list_places` - List all unique places from memories
- `get_memories_by_place` - Get all memories for a specific place

## Quick Start

### Using Docker (Recommended)

1. **Pull and run from GitHub Container Registry:**
   ```bash
   docker run -d -p 8080:8080 -v $(pwd)/data:/app/data --name ha-memory ghcr.io/YOUR_USERNAME/ha-memory:latest
   ```

2. **Or build locally:**
   ```bash
   docker build -t ha-memory .
   docker run -d -p 8080:8080 -v $(pwd)/data:/app/data --name ha-memory ha-memory
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Run the application:**
   ```bash
   poetry run python main.py
   ```

The service will be available at `http://localhost:8080`

## Data Persistence

- **Docker**: Memories are stored in `/app/data/memories.json` inside the container, mounted to `./data/` on your host
- **Local**: Memories are stored in `./data/memories.json` by default
- **Custom Path**: Set the `DATA_DIR` environment variable to use a different location

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DATA_DIR` | `./data` | Directory where memories.json will be stored |
| `HOST` | `0.0.0.0` | Host address to bind the server |
| `PORT` | `8080` | Port to run the server on |

## Development

### Requirements
- Python 3.13+
- Poetry for dependency management
- Docker (optional)