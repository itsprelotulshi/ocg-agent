import math
import uuid
import httpx
import logging
from typing import Dict, Any
from plugins.base import BasePlugin

logger = logging.getLogger("ocg_agent.plugins.system")

class SystemToolsPlugin(BasePlugin):
    name = "system_tools"
    description = "Provides math computation, webpage fetching, and utility functions."
    version = "1.0.0"

    def register_tools(self):
        self.add_tool(
            name="calculator",
            description="Safely evaluates standard mathematical and scientific expressions (e.g., '2 ** 8 + sqrt(144) * sin(pi/2)').",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate."
                    }
                },
                "required": ["expression"]
            },
            handler=self.calculate
        )

        self.add_tool(
            name="fetch_url",
            description="Fetches text or markdown content from a public web URL.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full HTTP/HTTPS URL to fetch."
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum number of characters to return (default: 4000)."
                    }
                },
                "required": ["url"]
            },
            handler=self.fetch_url
        )

        self.add_tool(
            name="generate_uuid",
            description="Generates a unique UUIDv4 string with optional prefix.",
            parameters={
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "Optional prefix to prepend to the UUID."
                    }
                }
            },
            handler=self.generate_uuid
        )

    def calculate(self, expression: str) -> str:
        safe_dict = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "log": math.log, "log10": math.log10,
            "exp": math.exp, "pi": math.pi, "e": math.e,
            "ceil": math.ceil, "floor": math.floor
        }
        try:
            # Clean expression
            cleaned = expression.strip().replace("^", "**")
            result = eval(cleaned, {"__builtins__": {}}, safe_dict)
            return f"Result: {result}"
        except Exception as e:
            return f"Math Evaluation Error: {str(e)}"

    async def fetch_url(self, url: str, max_length: int = 4000) -> str:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) QwenAgent/1.0"}
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                text = resp.text
                if len(text) > max_length:
                    return text[:max_length] + f"\n... [Truncated. Total length: {len(text)} characters]"
                return text
        except Exception as e:
            return f"Error fetching URL '{url}': {str(e)}"

    def generate_uuid(self, prefix: str = "") -> str:
        uid = str(uuid.uuid4())
        return f"{prefix}_{uid}" if prefix else uid
