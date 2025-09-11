# 🧠 HA Memory

A FastMCP-based memory management system with a modern web interface for storing, viewing, and managing memories with UUID-based identification.

## Features

- **Modern Web Interface**: Beautiful, responsive web UI for viewing and managing memories
- **UUID-based identification**: Each memory entry has a unique UUID4 identifier
- **Type classification**: Memories can be classified as "user" or "system" type
- **Smart sorting**: User memories appear first, system memories at the bottom
- **Location tracking**: Optional place field to associate memories with locations
- **Timestamp tracking**: Both creation and modification timestamps
- **Persistent storage**: Memories are stored in JSON format on disk
- **Real-time updates**: Web interface auto-refreshes every 30 seconds
- **Filtering**: Filter memories by type (All, User, System)
- **Delete functionality**: Remove memories directly from the web interface

## Memory Structure

Each memory entry contains:
- `id`: Unique UUID4 identifier
- `content`: The actual memory content
- `place`: Optional location name (e.g., "home", "work")
- `type`: Either "user" (user-created) or "system" (system-generated)
- `created_at`: Timestamp when the memory was first created
- `modified_at`: Timestamp when the memory was last modified

## Web Interface

The web interface is available at `http://localhost:8301` and provides:

- **Memory Listing**: View all memories with clean, card-based layout
- **Type Filtering**: Filter by All, User, or System memories
- **Memory Counts**: See filtered count vs total count
- **Delete Confirmation**: Safe deletion with confirmation dialogs
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark Theme**: Modern dark theme with gradient backgrounds

### Features
- User memories are prioritized and shown first
- System memories appear at the bottom
- Each memory type has distinct color coding (blue for user, purple for system)
- Place tags are shown when available
- Creation and modification timestamps are displayed
- Smooth animations and hover effects

## MCP Tools

### Create or Update Memory
```
create_or_update_memory(memory_content, memory_id=None, place=None, memory_type="user")
```
- Creates a new memory if no `memory_id` is provided
- Updates existing memory if `memory_id` exists
- Returns the memory ID (UUID)

### List All Memories
```
list_memories()
```
- Returns all stored memories with human-readable timestamps
- Includes all memory fields in the response

### Delete Memory
```
delete_memory(memory_id)
```
- Deletes a memory entry by its UUID
- Returns confirmation message

## API Endpoints

The web interface uses these REST API endpoints:

- `GET /` - Main web interface
- `GET /?type=user|system` - Filtered web interface
- `GET /api/memories` - JSON API for all memories
- `GET /api/memories?type=user|system` - Filtered JSON API
- `DELETE /api/memories/{memory_id}` - Delete a specific memory
- `GET /health` - Health check endpoint

## Configuration

Set the `DATA_DIR` environment variable to specify where memory data should be stored. Defaults to `./data`.

## Running

```bash
python main.py
```

This starts both servers:
- **MCP Server**: `http://0.0.0.0:8300` (for MCP clients)
- **Web Interface**: `http://0.0.0.0:8301` (for browser access)

## Data Storage

Memories are stored in `{DATA_DIR}/memories.json` with the following structure:

```json
{
  "uuid-here": {
    "id": "uuid-here",
    "content": "Memory content",
    "place": "home", 
    "type": "user",
    "created_at": "2025-09-06T12:00:00+00:00",
    "modified_at": "2025-09-06T12:00:00+00:00"
  }
}
```

## Development

Built with:
- **FastMCP**: For MCP protocol support
- **FastAPI**: For web API and interface
- **Jinja2**: For HTML templating
- **Modern CSS**: Responsive design with dark theme
