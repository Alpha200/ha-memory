# HA Memory

A FastMCP-based memory management service that allows you to store, retrieve, and organize memories with timestamps, location information, labels, and relevance periods.

## Features

- 📝 **Create and Update Memories**: Store memories with titles, content, and optional metadata
- 📍 **Location Tracking**: Associate memories with specific places
- 🏷️ **Label System**: Tag memories with multiple labels for better organization
- ⏰ **Relevance Periods**: Set when memories become relevant and when they expire using ISO date strings (e.g., 2025-09-02T20:58:43.065489+02:00)
- 🔍 **Advanced Search**: Find memories by title, location, labels, or relevance period
- 📅 **Modification Tracking**: Automatic tracking of when memories were last updated
- 💾 **Persistent Storage**: All memories are saved to JSON file with automatic persistence
- 🐳 **Docker Ready**: Containerized application with volume mounting for data persistence

## API Endpoints

The service provides the following MCP tools:

### Memory Management
- `create_or_update_memory` - Create or update a memory entry with labels and relevance periods (relevant_start and relevant_end must be ISO date strings)
- `list_memories` - List all memory entries with complete information (title, content, place, labels, dates)
- `get_memory` - Retrieve a specific memory by title
- `delete_memory` - Delete a memory entry

### Search and Filter
- `get_memories_by_place` - Get all memories for a specific place
- `get_memories_by_label` - Get all memories that contain a specific label
- `get_relevant_memories` - Get memories that are currently relevant (within their date range)

### Organization
- `list_places` - List all unique places from memories
- `list_labels` - List all unique labels from memories

## Quick Start

### Using Docker (Recommended)

1. **Pull and run from GitHub Container Registry:**
   ```bash
   docker run -d -p 8300:8300 -v $(pwd)/data:/app/data --name ha-memory ghcr.io/YOUR_USERNAME/ha-memory:latest
   ```

2. **Or build locally:**
   ```bash
   docker build -t ha-memory .
   docker run -d -p 8300:8300 -v $(pwd)/data:/app/data --name ha-memory ha-memory
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

The service will be available at `http://localhost:8300`

## Data Persistence

- **Docker**: Memories are stored in `/app/data/memories.json` inside the container, mounted to `./data/` on your host
- **Local**: Memories are stored in `./data/memories.json` by default
- **Custom Path**: Set the `DATA_DIR` environment variable to use a different location

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DATA_DIR` | `./data` | Directory where memories.json will be stored |
| `HOST` | `0.0.0.0` | Host address to bind the server |
| `PORT` | `8300` | Port to run the server on |

## Development

### Requirements
- Python 3.13+
- Poetry for dependency management
- Docker (optional)

### Project Structure
```
├── main.py              # Main application file
├── pyproject.toml       # Poetry configuration
├── Dockerfile           # Docker configuration
├── .dockerignore        # Docker ignore file
└── data/               # Data directory (created automatically)
    └── memories.json   # Persistent storage file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if available)
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
