from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from core.types import AgentRunContext, AgentResponse, ToolResult

class PluginTool:
    """Represents a tool exposed by a plugin."""
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Any]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_openai_schema(self, plugin_prefix: str = "") -> Dict[str, Any]:
        full_name = f"plugin__{plugin_prefix}__{self.name}" if plugin_prefix else f"plugin__{self.name}"
        return {
            "type": "function",
            "function": {
                "name": full_name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

class BasePlugin(ABC):
    """
    Abstract Base Class for Agent Plugins.
    Plugins can expose native tools and hook into the agent lifecycle.
    """

    name: str = "base_plugin"
    description: str = "Base plugin description"
    version: str = "1.0.0"
    enabled: bool = True

    def __init__(self):
        self._tools: Dict[str, PluginTool] = {}
        self.register_tools()

    @abstractmethod
    def register_tools(self):
        """Register tools provided by this plugin using `add_tool`."""
        pass

    def add_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Any]
    ):
        self._tools[name] = PluginTool(name, description, parameters, handler)

    def get_tools(self) -> List[PluginTool]:
        return list(self._tools.values())

    # --- Lifecycle Hooks (Override as needed) ---

    async def on_before_agent_run(self, context: AgentRunContext, user_message: str) -> Optional[str]:
        """Called before the agent starts processing. Return modified user message or None."""
        return None

    async def on_after_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: ToolResult) -> Optional[ToolResult]:
        """Called immediately after any tool execution. Return modified ToolResult or None."""
        return None

    async def on_after_agent_run(self, context: AgentRunContext, response: AgentResponse) -> Optional[AgentResponse]:
        """Called after the agent concludes its response. Return modified AgentResponse or None."""
        return None
