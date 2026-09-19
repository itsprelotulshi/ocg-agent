from typing import Dict, Any
from plugins.base import BasePlugin

class MemoryToolsPlugin(BasePlugin):
    name = "memory_tools"
    description = "Provides an agent scratchpad to store and retrieve intermediate facts, variables, or findings."
    version = "1.0.0"

    def __init__(self):
        self._memory_store: Dict[str, str] = {}
        super().__init__()

    def register_tools(self):
        self.add_tool(
            name="save_to_scratchpad",
            description="Save a key-value pair to the agent's active session scratchpad.",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key or label for the information."},
                    "value": {"type": "string", "description": "The detailed value or text to store."}
                },
                "required": ["key", "value"]
            },
            handler=self.save_key
        )

        self.add_tool(
            name="read_from_scratchpad",
            description="Retrieve a value from the scratchpad by key, or all saved keys if key is 'all'.",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key to retrieve, or 'all' to see all entries."}
                },
                "required": ["key"]
            },
            handler=self.read_key
        )

        self.add_tool(
            name="clear_scratchpad",
            description="Clears all scratchpad memories.",
            parameters={"type": "object", "properties": {}},
            handler=self.clear_all
        )

    def save_key(self, key: str, value: str) -> str:
        self._memory_store[key.strip()] = value.strip()
        return f"Stored '{key}' successfully into scratchpad."

    def read_key(self, key: str) -> str:
        k = key.strip()
        if k.lower() == "all":
            if not self._memory_store:
                return "Scratchpad is currently empty."
            return "\n".join([f"- {k}: {v}" for k, v in self._memory_store.items()])
        if k in self._memory_store:
            return f"{k}: {self._memory_store[k]}"
        return f"Key '{k}' not found in scratchpad."

    def clear_all(self) -> str:
        count = len(self._memory_store)
        self._memory_store.clear()
        return f"Cleared {count} items from scratchpad."
