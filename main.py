import os
from fastmcp import FastMCP
from typing import List, Annotated, TypedDict, Literal
from memory_manager import MemoryManager

mcp = FastMCP("HA Memory")

DATA_DIR = os.getenv("DATA_DIR", "./data")

# Initialize memory manager
memory_manager = MemoryManager(DATA_DIR)

class MemoryResponse(TypedDict):
    id: str
    content: str
    place: str | None
    type: Literal["user", "system"]
    created_at: str
    modified_at: str

class MemoryError(TypedDict):
    error: str

@mcp.tool
async def create_or_update_memory(
        memory_content: Annotated[str, "The content of the memory entry"],
        memory_id: Annotated[str | None, "The ID of the memory entry to update (optional, will create new if not provided)"] = None,
        place: Annotated[str | None, "A short name of the place this memory is associated with like 'home' or 'work' (optional)"] = None,
        memory_type: Annotated[Literal["user", "system"], "The type of memory: 'user' for user memories or 'system' for system-generated memories"] = "user"
):
    """Create a new memory entry or update an existing one by ID"""
    return memory_manager.create_or_update_memory(memory_content, memory_id, place, memory_type)

@mcp.tool
async def list_memories() -> List[MemoryResponse]:
    """List all memory entries with their basic information"""
    memories = []
    for entry in memory_manager.get_all_memories().values():
        memories.append(MemoryResponse(
            id=entry.id,
            content=entry.content,
            place=entry.place,
            type=entry.type,
            created_at=entry.created_at.isoformat(),
            modified_at=entry.modified_at.isoformat()
        ))
    return memories

@mcp.tool
async def delete_memory(memory_id: Annotated[str, "The ID of the memory entry to delete"]) -> str:
    """Delete a memory entry by ID"""
    if memory_manager.delete_memory(memory_id):
        return f"Memory '{memory_id}' deleted successfully"
    else:
        return f"Memory '{memory_id}' not found"

if __name__ == "__main__":
    memory_manager.load_memories()
    mcp.run(transport="sse", host="0.0.0.0", port=8300)
