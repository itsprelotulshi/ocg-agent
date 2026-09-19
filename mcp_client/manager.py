import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from contextlib import AsyncExitStack

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from core.types import ToolResult

logger = logging.getLogger("ocg_agent.mcp")

class MCPManager:
    """
    Manages connections to multiple Model Context Protocol (MCP) servers
    via Stdio and SSE transports.
    """

    def __init__(self, config_path: str = "mcp_servers.json"):
        self.config_path = config_path
        self.sessions: Dict[str, ClientSession] = {}
        self.server_tools: Dict[str, List[Dict[str, Any]]] = {}
        self.tool_to_server_map: Dict[str, tuple[str, str]] = {}  # full_name -> (server_name, tool_name)
        self.exit_stack: Optional[AsyncExitStack] = None
        self._is_running = False

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            logger.warning(f"MCP config file '{self.config_path}' not found.")
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mcpServers", {})
        except Exception as e:
            logger.error(f"Failed to read MCP config: {e}")
            return {}

    async def initialize(self):
        """Connect to all configured MCP servers and discover their tools."""
        if self._is_running:
            return

        self.exit_stack = AsyncExitStack()
        servers = self.load_config()
        self._is_running = True

        for server_name, server_cfg in servers.items():
            try:
                if "command" in server_cfg:
                    await self._connect_stdio(server_name, server_cfg)
                elif "url" in server_cfg:
                    await self._connect_sse(server_name, server_cfg)
                else:
                    logger.warning(f"Server '{server_name}' configuration unrecognized.")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server '{server_name}': {e}")

        logger.info(f"MCP Manager initialized. Discovered {len(self.tool_to_server_map)} tools across {len(self.sessions)} servers.")

    async def _connect_stdio(self, server_name: str, config: Dict[str, Any]):
        import sys
        cmd = config.get("command")
        if cmd in ("python", "python3"):
            cmd = sys.executable
        args = config.get("args", [])
        env = {**os.environ, **config.get("env", {})}

        params = StdioServerParameters(
            command=cmd,
            args=args,
            env=env
        )

        read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(params))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()

        self.sessions[server_name] = session
        await self._discover_server_tools(server_name, session)

    async def _connect_sse(self, server_name: str, config: Dict[str, Any]):
        url = config.get("url")
        read_stream, write_stream = await self.exit_stack.enter_async_context(sse_client(url))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()

        self.sessions[server_name] = session
        await self._discover_server_tools(server_name, session)

    async def _discover_server_tools(self, server_name: str, session: ClientSession):
        tools_result = await session.list_tools()
        openai_tools: List[Dict[str, Any]] = []

        for tool in tools_result.tools:
            # Format tool name for OpenAI function calling: mcp__{server_name}__{tool.name}
            safe_server_name = server_name.replace("-", "_")
            safe_tool_name = tool.name.replace("-", "_")
            full_name = f"mcp__{safe_server_name}__{safe_tool_name}"

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": full_name,
                    "description": f"[MCP: {server_name}] {tool.description or 'No description provided.'}",
                    "parameters": tool.inputSchema if hasattr(tool, "inputSchema") and tool.inputSchema else {"type": "object", "properties": {}}
                }
            })
            self.tool_to_server_map[full_name] = (server_name, tool.name)

        self.server_tools[server_name] = openai_tools
        logger.info(f"Server '{server_name}' registered {len(openai_tools)} tools.")

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all connected MCP servers in OpenAI function format."""
        all_tools = []
        for tools in self.server_tools.values():
            all_tools.extend(tools)
        return all_tools

    def get_status(self) -> List[Dict[str, Any]]:
        """Get connected server names and their tool counts."""
        return [
            {
                "name": server_name,
                "connected": server_name in self.sessions,
                "tools_count": len(self.server_tools.get(server_name, [])),
                "tools": [t["function"]["name"] for t in self.server_tools.get(server_name, [])]
            }
            for server_name in self.sessions.keys()
        ]

    def can_handle(self, full_tool_name: str) -> bool:
        return full_tool_name in self.tool_to_server_map

    async def execute_tool(self, tool_call_id: str, full_tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Dispatch a tool execution to the appropriate MCP server session."""
        if full_tool_name not in self.tool_to_server_map:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=full_tool_name,
                content=f"Error: Unknown MCP tool '{full_tool_name}'",
                is_error=True
            )

        server_name, original_tool_name = self.tool_to_server_map[full_tool_name]
        session = self.sessions.get(server_name)

        if not session:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=full_tool_name,
                content=f"Error: MCP Server '{server_name}' is not connected.",
                is_error=True
            )

        try:
            result = await session.call_tool(original_tool_name, arguments)
            # Format result content
            output_parts = []
            if hasattr(result, "content") and result.content:
                for item in result.content:
                    if hasattr(item, "text"):
                        output_parts.append(item.text)
                    elif hasattr(item, "data"):
                        output_parts.append(f"[Binary/Image data: {len(item.data)} bytes]")
                    else:
                        output_parts.append(str(item))

            content_str = "\n".join(output_parts) if output_parts else "Success (empty result)"
            is_error = getattr(result, "isError", False) or False

            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=full_tool_name,
                content=content_str,
                is_error=is_error
            )
        except Exception as e:
            logger.error(f"Error executing MCP tool '{full_tool_name}': {e}")
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=full_tool_name,
                content=f"MCP Tool Execution Error: {str(e)}",
                is_error=True
            )

    async def shutdown(self):
        """Close all MCP connections cleanly."""
        if self.exit_stack:
            await self.exit_stack.aclose()
        self.sessions.clear()
        self.server_tools.clear()
        self.tool_to_server_map.clear()
        self._is_running = False
        logger.info("MCP Manager shutdown complete.")
