# HA Memory

A sophisticated memory management system for Home Assistant that provides both MCP (Model Context Protocol) server capabilities and a beautiful web interface for storing, retrieving, and managing digital memories.

## Features

- **Multiple Memory Types**: Support for three distinct memory types:
  - **Instructions**: High-priority memories for system instructions and commands
  - **User**: Personal memories and notes from users
  - **System**: System-generated memories and automated notes

- **MCP Server**: Full Model Context Protocol implementation for AI assistant integration
- **Web Interface**: Modern, responsive web UI for viewing and managing memories
- **Real-time Management**: Create, update, delete, and filter memories in real-time
- **Smart Sorting**: Automatic prioritization with instructions first, followed by user and system memories
- **Place Tagging**: Associate memories with specific locations or contexts

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run with Docker
docker build -t ha-memory .
docker run -p 8300:8300 -p 8301:8301 -v ./data:/app/data ha-memory
```

### Manual Installation

```bash
# Install dependencies
poetry install

# Run the application
poetry run python main.py
```

## Services

The application runs two services simultaneously:

- **MCP Server**: `http://localhost:8300` - Model Context Protocol interface
- **Web Interface**: `http://localhost:8301` - Interactive web UI

## Memory Types

### Instructions 🟢
- Highest priority memories
- Displayed first in all views
- Ideal for system instructions, commands, and critical information
- Green color coding in the UI

### User 🔵
- Personal memories and user-generated content
- Medium priority
- Blue color coding in the UI

### System 🟣
- System-generated memories and automated notes
- Lowest priority (displayed last)
- Purple color coding in the UI

## API Usage

### REST API

#### Get Memories
```bash
# Get all memories
GET /api/memories

# Filter by type
GET /api/memories?type=instructions
GET /api/memories?type=user
GET /api/memories?type=system
```

#### Delete Memory
```bash
DELETE /api/memories/{memory_id}
```

## Web Interface

The web interface provides:

- **Filter by Type**: Quick buttons to filter by memory type
- **Real-time Counts**: Live memory statistics
- **Responsive Design**: Works on desktop and mobile devices
- **Delete Functionality**: Remove memories with confirmation
- **Auto-refresh**: Updates every 30 seconds
- **Smooth Animations**: Fade-in/out effects for better UX

### Filtering

Use the filter buttons to view specific memory types:
- **All**: Show all memories (default sorting: instructions → user → system)
- **Instructions**: Show only instruction memories
- **User**: Show only user memories  
- **System**: Show only system memories

## Data Storage

Memories are stored in JSON format in the `./data/memories.json` file. The data directory is configurable via the `DATA_DIR` environment variable.

### Data Format
```json
{
  "version": 2,
  "memories": {
    "memory-id": {
      "content": "Memory content",
      "place": "optional-place",
      "type": "instructions|user|system",
      "created_at": "2024-01-01T00:00:00+00:00",
      "modified_at": "2024-01-01T00:00:00+00:00"
    }
  }
}
```

## Configuration

### Environment Variables

- `DATA_DIR`: Directory for data storage (default: `./data`)

### Docker Configuration

The included Dockerfile provides:
- Python 3.13 runtime
- Poetry for dependency management
- Volume mounting for persistent data
- Health checks for both services
- Optimized multi-stage build

## Development

### Prerequisites
- Python 3.11+
- Poetry for dependency management

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd ha-memory

# Install dependencies
poetry install

# Run in development mode
poetry run python main.py
```

### Project Structure
```
ha-memory/
├── main.py              # Main application with MCP and web servers
├── memory_manager.py    # Core memory management logic
├── templates/
│   └── memories.html    # Web interface template
├── data/               # Data storage directory
│   └── memories.json   # Memory data file
├── Dockerfile          # Container configuration
├── pyproject.toml      # Python dependencies
└── README.md           # This file
```

## Migration

The system automatically migrates from version 1 to version 2 data format when needed. No manual intervention required.

## Health Checks

- Web Interface: `GET /health`
- Returns: `{"status": "ok", "service": "HA Memory Web UI"}`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
