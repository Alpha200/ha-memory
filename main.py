from dataclasses import dataclass

import arrow
import json
import os
from arrow import Arrow
from fastmcp import FastMCP
from typing import List, Dict, Any, Annotated, Union, TypedDict

mcp = FastMCP("HA Memory")

# Use environment variable for data directory, default to ./data
DATA_DIR = os.getenv("DATA_DIR", "./data")
MEMORIES_FILE = os.path.join(DATA_DIR, "memories.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

memory_entries = dict()

class MemoryResponse(TypedDict):
    title: str
    content: str
    place: str | None
    relative_date: str | None

class MemoryError(TypedDict):
    error: str

@dataclass
class MemoryEntry:
    title: str
    content: str
    place: str
    datetime: Arrow

def save_memories():
    """Save memories to disk"""
    data = {}
    for title, entry in memory_entries.items():
        data[title] = {
            "title": entry.title,
            "content": entry.content,
            "place": entry.place,
            "datetime": entry.datetime.isoformat() if entry.datetime else None
        }

    with open(MEMORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_memories():
    """Load memories from disk"""
    if not os.path.exists(MEMORIES_FILE):
        return

    try:
        with open(MEMORIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for title, entry_data in data.items():
            datetime_obj = None
            if entry_data.get("datetime"):
                datetime_obj = arrow.get(entry_data["datetime"])

            memory_entries[title] = MemoryEntry(
                title=entry_data["title"],
                content=entry_data["content"],
                place=entry_data["place"],
                datetime=datetime_obj
            )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading memories: {e}")

@mcp.tool
async def create_or_update_memory(
        memory_title: Annotated[str, "The title of the memory entry"],
        memory_content: Annotated[str, "The content of the memory entry"],
        place: Annotated[str | None, "A short name of the place this memory is associated with like 'home' or 'work' (optional)"] = None,
        relative_date: Annotated[str | None, "A relative date string like '3 days ago' or 'in 2 weeks' or 'in 1 days at 8:00' that the memory is related to (optional)"] = None
):
    """Create or update a memory entry by title"""

    technical_date = None

    if relative_date is not None and relative_date != "":
        arw = arrow.utcnow()
        technical_date = arw.dehumanize(relative_date)

    entry = MemoryEntry(
        title=memory_title,
        content=memory_content,
        place=place,
        datetime=technical_date,
    )

    memory_entries[memory_title] = entry
    save_memories()

@mcp.tool
async def list_memories() -> List[str]:
    """List all memory titles"""
    return list(memory_entries.keys())

@mcp.tool
async def delete_memory(memory_title: Annotated[str, "The title of the memory entry to delete"]) -> str:
    """Delete a memory entry by title"""
    if memory_title in memory_entries:
        del memory_entries[memory_title]
        save_memories()
        return f"Memory '{memory_title}' deleted successfully"
    else:
        return f"Memory '{memory_title}' not found"

@mcp.tool
async def get_memory(memory_title: Annotated[str, "The title of the memory entry to retrieve"]) -> Union[MemoryResponse, MemoryError]:
    """Get a memory entry by title"""
    if memory_title not in memory_entries:
        return {"error": f"Memory '{memory_title}' not found"}

    entry = memory_entries[memory_title]

    relative_date = None
    if entry.datetime is not None:
        relative_date = entry.datetime.humanize()

    return {
        "title": entry.title,
        "content": entry.content,
        "place": entry.place,
        "relative_date": relative_date
    }

@mcp.tool
async def list_places() -> List[str]:
    """List all unique places from memory entries"""
    places = set()
    for entry in memory_entries.values():
        if entry.place is not None and entry.place.strip() != "":
            places.add(entry.place)
    return sorted(list(places))

@mcp.tool
async def get_memories_by_place(place: Annotated[str, "The place to search for memories"]) -> List[MemoryResponse]:
    """Get all memory entries associated with a specific place"""
    memories = []

    for entry in memory_entries.values():
        if entry.place == place:
            relative_date = None
            if entry.datetime is not None:
                relative_date = entry.datetime.humanize()

            memories.append({
                "title": entry.title,
                "content": entry.content,
                "place": entry.place,
                "relative_date": relative_date
            })

    return memories

if __name__ == "__main__":
    load_memories()
    mcp.run(transport="sse", host="0.0.0.0", port=8080)
