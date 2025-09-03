from dataclasses import dataclass

import arrow
import json
import os
from arrow import Arrow
from fastmcp import FastMCP
from typing import List, Annotated, Union, TypedDict

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
    labels: List[str]
    relevant_start: str | None
    relevant_end: str | None
    modified_at: str

class MemoryError(TypedDict):
    error: str

@dataclass
class MemoryEntry:
    title: str
    content: str
    place: str | None
    labels: List[str]
    relevant_start: Arrow | None
    relevant_end: Arrow | None
    modified_at: Arrow

def save_memories():
    """Save memories to disk"""
    data = {}
    for title, entry in memory_entries.items():
        data[title] = {
            "title": entry.title,
            "content": entry.content,
            "place": entry.place,
            "labels": entry.labels,
            "relevant_start": entry.relevant_start.isoformat() if entry.relevant_start else None,
            "relevant_end": entry.relevant_end.isoformat() if entry.relevant_end else None,
            "modified_at": entry.modified_at.isoformat()
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
            relevant_start = None
            if entry_data.get("relevant_start"):
                relevant_start = arrow.get(entry_data["relevant_start"])

            relevant_end = None
            if entry_data.get("relevant_end"):
                relevant_end = arrow.get(entry_data["relevant_end"])

            modified_at = arrow.utcnow()
            if entry_data.get("modified_at"):
                modified_at = arrow.get(entry_data["modified_at"])

            memory_entries[title] = MemoryEntry(
                title=entry_data["title"],
                content=entry_data["content"],
                place=entry_data.get("place"),
                labels=entry_data.get("labels", []),
                relevant_start=relevant_start,
                relevant_end=relevant_end,
                modified_at=modified_at
            )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading memories: {e}")

@mcp.tool
async def create_or_update_memory(
        memory_title: Annotated[str, "The title of the memory entry"],
        memory_content: Annotated[str, "The content of the memory entry"],
        place: Annotated[str | None, "A short name of the place this memory is associated with like 'home' or 'work' (optional)"] = None,
        labels: Annotated[List[str] | None, "List of labels/tags for this memory (optional)"] = None,
        relevant_start: Annotated[str | None, "ISO date (e.g. 2025-09-02T20:58:43.065489+02:00) when this memory becomes relevant (optional)"] = None,
        relevant_end: Annotated[str | None, "ISO date (e.g. 2025-09-03T20:58:43.065489+02:00) when this memory stops being relevant (optional)"] = None
):
    """Create or update a memory entry by title"""

    if labels is None:
        labels = []

    relevant_start_date = None
    if relevant_start is not None and relevant_start != "":
        relevant_start_date = arrow.get(relevant_start)

    relevant_end_date = None
    if relevant_end is not None and relevant_end != "":
        relevant_end_date = arrow.get(relevant_end)

    entry = MemoryEntry(
        title=memory_title,
        content=memory_content,
        place=place,
        labels=labels or [],
        relevant_start=relevant_start_date,
        relevant_end=relevant_end_date,
        modified_at=arrow.utcnow()
    )

    memory_entries[memory_title] = entry
    save_memories()

@mcp.tool
async def list_memories() -> List[MemoryResponse]:
    """List all memory entries with their basic information"""
    memories = []
    for entry in memory_entries.values():
        memories.append(MemoryResponse(
            title=entry.title,
            content=entry.content,
            place=entry.place,
            labels=entry.labels,
            relevant_start=entry.relevant_start.humanize() if entry.relevant_start else None,
            relevant_end=entry.relevant_end.humanize() if entry.relevant_end else None,
            modified_at=entry.modified_at.humanize()
        ))
    return memories

@mcp.tool
async def delete_memory(memory_title: Annotated[str, "The title of the memory entry to delete"]) -> str:
    """Delete a memory entry by title"""
    if memory_title in memory_entries:
        del memory_entries[memory_title]
        save_memories()
        return f"Memory '{memory_title}' deleted successfully"
    else:
        return f"Memory '{memory_title}' not found"

if __name__ == "__main__":
    load_memories()
    mcp.run(transport="sse", host="0.0.0.0", port=8300)
