# HA Memory

A FastMCP-based memory management system for storing and retrieving memories with UUID-based identification.

## Features

- **UUID-based identification**: Each memory entry has a unique UUID4 identifier
- **Type classification**: Memories can be classified as "user" or "system" type
- **Location tracking**: Optional place field to associate memories with locations
- **Timestamp tracking**: Both creation and modification timestamps
- **Persistent storage**: Memories are stored in JSON format on disk

## Memory Structure

Each memory entry contains:
- `id`: Unique UUID4 identifier
- `content`: The actual memory content
- `place`: Optional location name (e.g., "home", "work")
- `type`: Either "user" (user-created) or "system" (system-generated)
- `created_at`: Timestamp when the memory was first created
- `modified_at`: Timestamp when the memory was last modified

## API Endpoints

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

## Configuration

Set the `DATA_DIR` environment variable to specify where memory data should be stored. Defaults to `./data`.

## Running

```bash
python main.py
```

The server will start on `0.0.0.0:8300` using SSE transport.

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
