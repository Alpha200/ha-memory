from dataclasses import dataclass
import arrow
import json
import os
import uuid
from arrow import Arrow
from typing import Dict, Literal

@dataclass
class MemoryEntry:
    id: str
    content: str
    place: str | None
    type: Literal["user", "system", "instructions"]
    created_at: Arrow
    modified_at: Arrow

class MemoryManager:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.memories_file = os.path.join(data_dir, "memories.json")
        self.memory_entries: Dict[str, MemoryEntry] = {}

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

    def save_memories(self):
        """Save memories to disk"""
        data = {
            "version": 2,
            "memories": {}
        }

        for memory_id, entry in self.memory_entries.items():
            data["memories"][memory_id] = {
                "content": entry.content,
                "place": entry.place,
                "type": entry.type,
                "created_at": entry.created_at.isoformat(),
                "modified_at": entry.modified_at.isoformat()
            }

        with open(self.memories_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def migrate_memories_v1_to_v2(self, old_data):
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

    def load_memories(self):
        """Load memories from disk"""
        if not os.path.exists(self.memories_file):
            return

        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if this is an empty file or old format (version 1)
            if not data:
                return

            # Check version
            version = data.get("version", 1)

            if version == 1:
                # This is old format, migrate it
                print("Migrating memories from version 1 to version 2...")
                migrated_memories = self.migrate_memories_v1_to_v2(data)
                self.memory_entries.update(migrated_memories)
                # Save in new format
                self.save_memories()
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

                self.memory_entries[memory_id] = MemoryEntry(
                    id=memory_id,
                    content=entry_data["content"],
                    place=entry_data.get("place"),
                    type=entry_data.get("type", "user"),
                    created_at=created_at,
                    modified_at=modified_at
                )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading memories: {e}")

    def create_or_update_memory(self, content: str, memory_id: str = None, place: str = None, memory_type: Literal["user", "system", "instructions"] = "user") -> str:
        """Create a new memory entry or update an existing one by ID"""
        # If no ID provided, create a new memory
        if memory_id is None:
            memory_id = str(uuid.uuid4())
            created_at = arrow.utcnow()
        else:
            # Check if memory exists for update
            if memory_id in self.memory_entries:
                created_at = self.memory_entries[memory_id].created_at
            else:
                created_at = arrow.utcnow()

        entry = MemoryEntry(
            id=memory_id,
            content=content,
            place=place,
            type=memory_type,
            created_at=created_at,
            modified_at=arrow.utcnow()
        )

        self.memory_entries[memory_id] = entry
        self.save_memories()
        return memory_id

    def get_all_memories(self) -> Dict[str, MemoryEntry]:
        """Get all memory entries"""
        return self.memory_entries.copy()

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry by ID. Returns True if deleted, False if not found"""
        if memory_id in self.memory_entries:
            del self.memory_entries[memory_id]
            self.save_memories()
            return True
        return False
