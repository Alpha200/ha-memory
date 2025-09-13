import os
import threading
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastmcp import FastMCP
from typing import List, Annotated, TypedDict, Literal
from memory_manager import MemoryManager

mcp = FastMCP("HA Memory")

DATA_DIR = os.getenv("DATA_DIR", "./data")

# Initialize memory manager
memory_manager = MemoryManager(DATA_DIR)

# Initialize FastAPI app for web UI
web_app = FastAPI(title="HA Memory Web UI", description="Web interface for viewing memories")

# Templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

class MemoryResponse(TypedDict):
    id: str
    content: str
    place: str | None
    type: Literal["user", "system", "instructions"]
    created_at: str
    modified_at: str

class MemoryError(TypedDict):
    error: str

# MCP Tools
@mcp.tool
async def create_or_update_memory(
        memory_content: Annotated[str, "The content of the memory entry"],
        memory_id: Annotated[str | None, "The ID of the memory entry to update (optional, will create new if not provided)"] = None,
        place: Annotated[str | None, "A short name of the place this memory is associated with like 'home' or 'work' (optional)"] = None,
        memory_type: Annotated[Literal["user", "system", "instructions"], "The type of memory: 'user' for user memories, 'system' for system-generated memories, or 'instructions' for instruction memories"] = "user"
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

# Web UI Routes
@web_app.get("/", response_class=HTMLResponse)
async def read_memories_ui(request: Request, type: str | None = None):  # 'type' query param for filtering
    """Web interface to view all memories (optional filter by ?type=user|system|instructions)"""
    # Load fresh data each time
    memory_manager.load_memories()

    all_memories = []
    for entry in memory_manager.get_all_memories().values():
        all_memories.append({
            'id': entry.id,
            'content': entry.content,
            'place': entry.place,
            'type': entry.type,
            'created_at': entry.created_at.format('YYYY-MM-DD HH:mm'),
            'modified_at': entry.modified_at.format('YYYY-MM-DD HH:mm')
        })

    overall_count = len(all_memories)

    selected_type = 'all'
    filtered_memories = all_memories
    if type and type.lower() in {"user", "system", "instructions"}:  # validate
        selected_type = type.lower()
        filtered_memories = [m for m in all_memories if m['type'] == selected_type]

    # Sort memories: instructions first (newest first), then user memories (newest first), then system memories (newest first)
    instructions_memories = [m for m in filtered_memories if m['type'] == 'instructions']
    user_memories = [m for m in filtered_memories if m['type'] == 'user']
    system_memories = [m for m in filtered_memories if m['type'] == 'system']
    instructions_memories.sort(key=lambda x: x['modified_at'], reverse=True)
    user_memories.sort(key=lambda x: x['modified_at'], reverse=True)
    system_memories.sort(key=lambda x: x['modified_at'], reverse=True)
    filtered_memories = instructions_memories + user_memories + system_memories

    return templates.TemplateResponse("memories.html", {
        "request": request,
        "memories": filtered_memories,
        "total_count": len(filtered_memories),
        "overall_count": overall_count,
        "selected_type": selected_type
    })

@web_app.get("/api/memories")
async def get_memories_json(type: str | None = None):
    """API endpoint to get memories as JSON (optional filter by ?type=user|system|instructions)"""
    # Load fresh data each time
    memory_manager.load_memories()

    memories = []
    for entry in memory_manager.get_all_memories().values():
        memories.append({
            'id': entry.id,
            'content': entry.content,
            'place': entry.place,
            'type': entry.type,
            'created_at': entry.created_at.isoformat(),
            'modified_at': entry.modified_at.isoformat()
        })

    overall_count = len(memories)

    if type and type.lower() in {"user", "system", "instructions"}:
        memories = [m for m in memories if m['type'] == type.lower()]

    # Sort memories: instructions first (newest first), then user memories (newest first), then system memories (newest first)
    instructions_memories = [m for m in memories if m['type'] == 'instructions']
    user_memories = [m for m in memories if m['type'] == 'user']
    system_memories = [m for m in memories if m['type'] == 'system']
    instructions_memories.sort(key=lambda x: x['modified_at'], reverse=True)
    user_memories.sort(key=lambda x: x['modified_at'], reverse=True)
    system_memories.sort(key=lambda x: x['modified_at'], reverse=True)
    memories = instructions_memories + user_memories + system_memories

    return {"memories": memories, "total_count": len(memories), "overall_count": overall_count, "selected_type": type.lower() if type and type.lower() in {"user", "system", "instructions"} else 'all'}

@web_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "HA Memory Web UI"}

@web_app.delete("/api/memories/{memory_id}")
async def delete_memory_api(memory_id: str):
    """API endpoint to delete a memory by ID"""
    if memory_manager.delete_memory(memory_id):
        return {"success": True, "message": f"Memory '{memory_id}' deleted successfully"}
    else:
        return {"success": False, "message": f"Memory '{memory_id}' not found"}

def run_web_server():
    """Run the web UI server in a separate thread"""
    uvicorn.run(web_app, host="0.0.0.0", port=8301, log_level="info")

def run_mcp_server():
    """Run the MCP server"""
    mcp.run(transport="sse", host="0.0.0.0", port=8300)

if __name__ == "__main__":
    memory_manager.load_memories()

    print("Starting HA Memory servers...")
    print("MCP server will be available at: http://0.0.0.0:8300")
    print("Web interface will be available at: http://0.0.0.0:8301")

    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Run MCP server in main thread
    run_mcp_server()
