import inspect
import logging
from typing import Dict, Any, List, Optional
from core.types import ToolResult, AgentRunContext, AgentResponse
from plugins.base import BasePlugin, PluginTool
from plugins.builtin.system_tools import SystemToolsPlugin
from plugins.builtin.memory_tools import MemoryToolsPlugin

logger = logging.getLogger("ocg_agent.plugins")

class PluginManager:
    """
    Manages loading, registry, and lifecycle hook dispatching for all agent plugins.
    """

    def __init__(self, installed_dir: str = "plugins/installed"):
        self.installed_dir = installed_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.tool_map: Dict[str, tuple[BasePlugin, PluginTool]] = {}
        self._load_defaults()
        self.load_installed_plugins()

    def _load_defaults(self):
        self.register(SystemToolsPlugin())
        self.register(MemoryToolsPlugin())

    def load_installed_plugins(self):
        """Dynamically discover and load custom plugins from the installed directory."""
        import os
        import sys
        import importlib.util

        if not os.path.exists(self.installed_dir):
            os.makedirs(self.installed_dir, exist_ok=True)
            return

        for fname in os.listdir(self.installed_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                plugin_path = os.path.join(self.installed_dir, fname)
                module_name = f"plugins.installed.{fname[:-3]}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, plugin_path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = mod
                        spec.loader.exec_module(mod)

                        for attr_name in dir(mod):
                            attr = getattr(mod, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, BasePlugin)
                                and attr is not BasePlugin
                            ):
                                plugin_instance = attr()
                                self.register(plugin_instance)
                                logger.info(f"Loaded custom plugin '{plugin_instance.name}' from {plugin_path}")
                except Exception as e:
                    logger.error(f"Failed to load custom plugin {plugin_path}: {e}")

    def reload_all(self):
        """Clear dynamic plugins and re-import defaults and installed plugins."""
        self.plugins.clear()
        self.tool_map.clear()
        self._load_defaults()
        self.load_installed_plugins()

    def register(self, plugin: BasePlugin):
        """Register a plugin and index its tools."""
        self.plugins[plugin.name] = plugin
        for tool in plugin.get_tools():
            schema = tool.to_openai_schema(plugin.name)
            full_name = schema["function"]["name"]
            self.tool_map[full_name] = (plugin, tool)
        logger.info(f"Registered plugin '{plugin.name}' (v{plugin.version}) with {len(plugin.get_tools())} tools.")

    def unregister(self, plugin_name: str):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            self.tool_map = {k: v for k, v in self.tool_map.items() if v[0].name != plugin_name}


    def get_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": p.name,
                "description": p.description,
                "version": p.version,
                "enabled": p.enabled,
                "tools": [t.to_openai_schema(p.name)["function"]["name"] for t in p.get_tools()]
            }
            for p in self.plugins.values()
        ]

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Return all tools from enabled plugins in OpenAI function calling format."""
        tools = []
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            for tool in plugin.get_tools():
                tools.append(tool.to_openai_schema(plugin.name))
        return tools

    def can_handle(self, tool_name: str) -> bool:
        return tool_name in self.tool_map

    async def execute_tool(self, tool_call_id: str, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        if tool_name not in self.tool_map:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content=f"Error: Unknown plugin tool '{tool_name}'",
                is_error=True
            )

        plugin, tool = self.tool_map[tool_name]
        try:
            handler = tool.handler
            if inspect.iscoroutinefunction(handler):
                result_val = await handler(**arguments)
            else:
                result_val = handler(**arguments)

            content = str(result_val) if result_val is not None else "Done"
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content=content,
                is_error=False
            )
        except Exception as e:
            logger.error(f"Error in plugin tool '{tool_name}': {e}")
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content=f"Tool Execution Exception: {str(e)}",
                is_error=True
            )

    # --- Hook Dispatchers ---

    async def run_before_agent_hooks(self, context: AgentRunContext, user_message: str) -> str:
        current_msg = user_message
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            try:
                modified = await plugin.on_before_agent_run(context, current_msg)
                if modified:
                    current_msg = modified
            except Exception as e:
                logger.error(f"Plugin '{plugin.name}' failed in on_before_agent_run: {e}")
        return current_msg

    async def run_after_tool_hooks(self, tool_name: str, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        current_res = result
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            try:
                modified = await plugin.on_after_tool_call(tool_name, arguments, current_res)
                if modified:
                    current_res = modified
            except Exception as e:
                logger.error(f"Plugin '{plugin.name}' failed in on_after_tool_call: {e}")
        return current_res

    async def run_after_agent_hooks(self, context: AgentRunContext, response: AgentResponse) -> AgentResponse:
        current_resp = response
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            try:
                modified = await plugin.on_after_agent_run(context, current_resp)
                if modified:
                    current_resp = modified
            except Exception as e:
                logger.error(f"Plugin '{plugin.name}' failed in on_after_agent_run: {e}")
        return current_resp
