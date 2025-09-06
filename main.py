from dataclasses import dataclass

import arrow
import json
import os
import uuid
from arrow import Arrow
from fastmcp import FastMCP
from typing import List, Annotated, TypedDict, Literal

mcp = FastMCP("HA Memory")

DATA_DIR = os.getenv("DATA_DIR", "./data")
MEMORIES_FILE = os.path.join(DATA_DIR, "memories.json")

os.makedirs(DATA_DIR, exist_ok=True)

memory_entries = dict()

class MemoryResponse(TypedDict):
    id: str
    content: str
    place: str | None
    type: Literal["user", "system"]
    created_at: str
    modified_at: str

class MemoryError(TypedDict):
    error: str

@dataclass
class MemoryEntry:
    id: str
    content: str
    place: str | None
    type: Literal["user", "system"]
    created_at: Arrow
    modified_at: Arrow

def save_memories():
    """Save memories to disk"""
    data = {
        "version": 2,
        "memories": {}
    }

    for memory_id, entry in memory_entries.items():
        data["memories"][memory_id] = {
            "content": entry.content,
            "place": entry.place,
            "type": entry.type,
            "created_at": entry.created_at.isoformat(),
            "modified_at": entry.modified_at.isoformat()
        }

    with open(MEMORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def migrate_memories_v1_to_v2(old_data):
    """Migrate memories from version 1 (old format) to version 2 (new format)"""
    migrated_memories = {}
    current_time = arrow.utcnow()

    for title, entry_data in old_data.items():
        # Generate new UUID for this memory
        memory_id = str(uuid.uuid4())

        # Combine title and content
        content = f"{entry_data['title']} - {entry_data['content']}"

        # Determine type based on labels
        memory_type = "user"
        if "labels" in entry_data and "system-notes" in entry_data.get("labels", []):
            memory_type = "system"

        # Create migrated entry
        migrated_memories[memory_id] = MemoryEntry(
            id=memory_id,
            content=content,
            place=entry_data.get("place"),
            type=memory_type,
            created_at=current_time,
            modified_at=current_time
        )

    return migrated_memories

def load_memories():
    """Load memories from disk"""
    if not os.path.exists(MEMORIES_FILE):
        return

    try:
        with open(MEMORIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if this is an empty file or old format (version 1)
        if not data:
            return

        # Check version
        version = data.get("version", 1)

        if version == 1:
            # This is old format, migrate it
            print("Migrating memories from version 1 to version 2...")
            migrated_memories = migrate_memories_v1_to_v2(data)
            memory_entries.update(migrated_memories)
            # Save in new format
            save_memories()
            print(f"Successfully migrated {len(migrated_memories)} memories to version 2")
            return

        # Version 2 format
        memories_data = data.get("memories", {})

        for memory_id, entry_data in memories_data.items():
            created_at = arrow.utcnow()
            if entry_data.get("created_at"):
                created_at = arrow.get(entry_data["created_at"])

            modified_at = arrow.utcnow()
            if entry_data.get("modified_at"):
                modified_at = arrow.get(entry_data["modified_at"])

            memory_entries[memory_id] = MemoryEntry(
                id=memory_id,
                content=entry_data["content"],
                place=entry_data.get("place"),
                type=entry_data.get("type", "user"),
                created_at=created_at,
                modified_at=modified_at
            )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading memories: {e}")

@mcp.tool
async def create_or_update_memory(
        memory_content: Annotated[str, "The content of the memory entry"],
        memory_id: Annotated[str | None, "The ID of the memory entry to update (optional, will create new if not provided)"] = None,
        place: Annotated[str | None, "A short name of the place this memory is associated with like 'home' or 'work' (optional)"] = None,
        memory_type: Annotated[Literal["user", "system"], "The type of memory: 'user' for user memories or 'system' for system-generated memories"] = "user"
):
    """Create a new memory entry or update an existing one by ID"""

    # If no ID provided, create a new memory
    if memory_id is None:
        memory_id = str(uuid.uuid4())
        created_at = arrow.utcnow()
    else:
        # Check if memory exists for update
        if memory_id in memory_entries:
            created_at = memory_entries[memory_id].created_at
        else:
            created_at = arrow.utcnow()

    entry = MemoryEntry(
        id=memory_id,
        content=memory_content,
        place=place,
        type=memory_type,
        created_at=created_at,
        modified_at=arrow.utcnow()
    )

    memory_entries[memory_id] = entry
    save_memories()
    return memory_id

@mcp.tool
async def list_memories() -> List[MemoryResponse]:
    """List all memory entries with their basic information"""
    memories = []
    for entry in memory_entries.values():
        memories.append(MemoryResponse(
            id=entry.id,
            content=entry.content,
            place=entry.place,
            type=entry.type,
            created_at=entry.created_at.humanize(),
            modified_at=entry.modified_at.humanize()
        ))
    return memories

@mcp.tool
async def delete_memory(memory_id: Annotated[str, "The ID of the memory entry to delete"]) -> str:
    """Delete a memory entry by ID"""
    if memory_id in memory_entries:
        del memory_entries[memory_id]
        save_memories()
        return f"Memory '{memory_id}' deleted successfully"
    else:
        return f"Memory '{memory_id}' not found"

if __name__ == "__main__":
    load_memories()
    mcp.run(transport="sse", host="0.0.0.0", port=8300)
