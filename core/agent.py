import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from config import settings
from core.types import (
    ChatMessage,
    ToolCall,
    ToolResult,
    AgentRunContext,
    AgentResponse,
    StreamChunk
)
from core.llm import OcgLLMClient
from mcp_client.manager import MCPManager
from plugins.manager import PluginManager
from skills.manager import SkillManager
from core.memory import memory_manager, MemoryManager
from database.repository import db_repo

logger = logging.getLogger("Ocg_agent.core")

BASE_SYSTEM_PROMPT = """You are an advanced, helpful, and highly intelligent AI agent powered by Ocg/Ocg3.8-27B.
You are equipped with powerful tools provided via the Model Context Protocol (MCP), extensible modular plugins, and persistent long-term memory.

Tool Usage Guidelines:
1. When a user request requires factual data, calculations, system inspection, or web research, invoke the appropriate tool.
2. Tools with prefix 'mcp__' are provided by external MCP servers.
3. Tools with prefix 'plugin__' are provided by local application plugins.
4. Tools with prefix 'memory__' allow inspecting, storing, or updating long-term memory and self-improvised rules.
5. Execute tools thoughtfully. If a tool call fails or returns partial info, interpret the result and adapt.
6. Provide concise, clear, and well-structured markdown answers.
"""

class OcgAgent:
    """
    Main Autonomous ReAct Agent for Ocg/Ocg3.8-27B.
    Integrates LLM inference, MCP servers, plugins, dynamic skills, and long-term memory.
    """

    def __init__(
        self,
        llm_client: Optional[OcgLLMClient] = None,
        mcp_manager: Optional[MCPManager] = None,
        plugin_manager: Optional[PluginManager] = None,
        skill_manager: Optional[SkillManager] = None,
        mem_manager: Optional[MemoryManager] = None,
    ):
        self.llm = llm_client or OcgLLMClient()
        self.mcp = mcp_manager or MCPManager()
        self.plugins = plugin_manager or PluginManager()
        self.skills = skill_manager or SkillManager()
        self.memory = mem_manager or memory_manager

    async def initialize(self):
        """Initialize MCP servers and plugins."""
        await self.mcp.initialize()

    async def _ensure_initialized(self):
        if not self.mcp._is_running:
            await self.mcp.initialize()

    def _build_system_prompt(self, active_skills: List[str], retrieved_memories: Optional[List[Dict[str, Any]]] = None) -> str:
        prompt = BASE_SYSTEM_PROMPT
        skills_instructions = self.skills.build_system_instructions(active_skills)
        if skills_instructions:
            prompt += f"\n{skills_instructions}"
        if retrieved_memories:
            mem_instructions = self.memory.format_memory_instructions(retrieved_memories)
            if mem_instructions:
                prompt += f"\n{mem_instructions}"
        return prompt

    def _get_all_tools(self) -> List[Dict[str, Any]]:
        """Combine all MCP, Plugin, and Memory tools into OpenAI function calling format."""
        mcp_tools = self.mcp.get_all_tools()
        plugin_tools = self.plugins.get_all_tools()
        mem_tools = self.memory.get_agent_tools()
        return mcp_tools + plugin_tools + mem_tools

    async def _execute_single_tool(self, tool_call: ToolCall, user_id: str = "guest") -> ToolResult:
        """Route tool call to MCP manager, Plugin manager, or Memory manager."""
        name = tool_call.function.name
        raw_args = tool_call.function.arguments

        try:
            arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            arguments = {}

        logger.info(f"Dispatching tool call '{name}' with args: {arguments}")

        # Dispatch to MCP
        if self.mcp.can_handle(name):
            result = await self.mcp.execute_tool(tool_call.id, name, arguments)
        # Dispatch to Plugin
        elif self.plugins.can_handle(name):
            result = await self.plugins.execute_tool(tool_call.id, name, arguments)
        # Dispatch to Memory
        elif self.memory.can_handle(name):
            mem_out = await self.memory.execute_tool(name, arguments, user_id=user_id)
            result = ToolResult(
                tool_call_id=tool_call.id,
                tool_name=name,
                content=mem_out,
                is_error=False
            )
        else:
            result = ToolResult(
                tool_call_id=tool_call.id,
                tool_name=name,
                content=f"Error: Unknown tool '{name}'.",
                is_error=True
            )

        # Run after-tool hooks
        result = await self.plugins.run_after_tool_hooks(name, arguments, result)
        return result


    async def run(
        self,
        user_message: str,
        context: Optional[AgentRunContext] = None,
        max_turns: int = 10,
    ) -> AgentResponse:
        """
        Execute an agent turn synchronously with ReAct reasoning and tool dispatch.
        """
        ctx = context or AgentRunContext()
        await self._ensure_initialized()

        # 1. Pre-agent run hooks
        processed_message = await self.plugins.run_before_agent_hooks(ctx, user_message)

        # 2. Skill selection (explicit + auto-detected)
        auto_skills = self.skills.detect_relevant_skills(processed_message)
        active_skills = list(set(ctx.active_skills + auto_skills))

        # 3. Save user message to database
        await db_repo.save_message(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            role="user",
            content=processed_message
        )

        # 4. Retrieve long-term memories & self-improvised rules
        retrieved_memories = await self.memory.retrieve_relevant_memories(processed_message, ctx.user_id)

        # 5. Load history and build message trajectory
        history = await db_repo.get_messages(ctx.session_id, ctx.user_id)
        system_prompt = self._build_system_prompt(active_skills, retrieved_memories)
        messages: List[ChatMessage] = [ChatMessage(role="system", content=system_prompt)] + history

        all_tools = self._get_all_tools()
        executed_tools: List[ToolResult] = []

        # Check if LLM is configured; if mock/dev, produce structured mock response
        if not self.llm.is_configured():
            mock_reply = await self._generate_mock_turn(processed_message, all_tools)
            await db_repo.save_message(
                session_id=ctx.session_id,
                user_id=ctx.user_id,
                role="assistant",
                content=mock_reply.content,
                tool_results=mock_reply.tool_executions
            )
            # Trigger background learning
            asyncio.create_task(self.memory.auto_extract_and_learn(processed_message, mock_reply.content, ctx.user_id, self.llm))
            return mock_reply

        # 6. ReAct Loop
        for turn in range(max_turns):
            try:
                response_msg = await self.llm.generate_response(messages, tools=all_tools)
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                error_content = f"⚠️ LLM Inference Error: {str(e)}\n\nPlease ensure your API Key and endpoint in .env or Settings are valid."
                return AgentResponse(content=error_content, tool_executions=executed_tools, finish_reason="error")

            messages.append(response_msg)

            # If model requested tool calls
            if response_msg.tool_calls:
                for tc in response_msg.tool_calls:
                    res = await self._execute_single_tool(tc, user_id=ctx.user_id)
                    executed_tools.append(res)

                    # Add tool result message for LLM
                    messages.append(ChatMessage(
                        role="tool",
                        name=tc.function.name,
                        tool_call_id=tc.id,
                        content=res.content
                    ))
            else:
                # Agent produced final answer
                final_response = AgentResponse(
                    content=response_msg.content or "",
                    tool_executions=executed_tools,
                    finish_reason="stop"
                )

                # Post-agent hooks
                final_response = await self.plugins.run_after_agent_hooks(ctx, final_response)

                # Persist to database
                await db_repo.save_message(
                    session_id=ctx.session_id,
                    user_id=ctx.user_id,
                    role="assistant",
                    content=final_response.content,
                    tool_results=executed_tools
                )

                # Automatically extract memories and self-improvise rules
                asyncio.create_task(self.memory.auto_extract_and_learn(processed_message, final_response.content, ctx.user_id, self.llm))

                return final_response

        # Max turns exceeded fallback
        fallback = AgentResponse(
            content="Max reasoning steps reached. Please refine your query.",
            tool_executions=executed_tools,
            finish_reason="length"
        )
        return fallback

    async def stream_chat(
        self,
        user_message: str,
        context: Optional[AgentRunContext] = None,
        max_turns: int = 10,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming chat supporting real-time tokens, tool call notifications,
        and tool execution results via Server-Sent Events (SSE).
        """
        ctx = context or AgentRunContext()
        await self._ensure_initialized()

        # Pre-hooks
        processed_message = await self.plugins.run_before_agent_hooks(ctx, user_message)

        # Skills detection
        auto_skills = self.skills.detect_relevant_skills(processed_message)
        active_skills = list(set(ctx.active_skills + auto_skills))

        if active_skills:
            yield {
                "event": "skills_applied",
                "data": {"skills": active_skills}
            }

        # Memory retrieval
        retrieved_memories = await self.memory.retrieve_relevant_memories(processed_message, ctx.user_id)
        if retrieved_memories:
            yield {
                "event": "memory_applied",
                "data": {
                    "count": len(retrieved_memories),
                    "items": [f"[{m.get('category', '').upper()}] {m.get('key', '')}" for m in retrieved_memories]
                }
            }

        # Save user message
        await db_repo.save_message(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            role="user",
            content=processed_message
        )

        history = await db_repo.get_messages(ctx.session_id, ctx.user_id)
        system_prompt = self._build_system_prompt(active_skills, retrieved_memories)
        messages: List[ChatMessage] = [ChatMessage(role="system", content=system_prompt)] + history

        all_tools = self._get_all_tools()
        executed_tools: List[ToolResult] = []

        # If LLM API key not configured yet, stream demo fallback
        if not self.llm.is_configured():
            async for chunk in self._stream_mock_turn(processed_message, all_tools, ctx):
                yield chunk
            # Trigger background learning
            asyncio.create_task(self.memory.auto_extract_and_learn(processed_message, "Demo response", ctx.user_id, self.llm))
            return

        final_content = ""

        # ReAct loop
        for turn in range(max_turns):
            turn_text = ""
            tool_calls: Optional[List[ToolCall]] = None

            async for chunk in self.llm.stream_response(messages, tools=all_tools):
                if chunk["type"] == "token":
                    turn_text += chunk["content"]
                    yield {"event": "token", "data": {"token": chunk["content"]}}
                elif chunk["type"] == "tool_calls":
                    tool_calls = chunk["calls"]

            if tool_calls:
                messages.append(ChatMessage(role="assistant", content=turn_text, tool_calls=tool_calls))
                for tc in tool_calls:
                    yield {
                        "event": "tool_call",
                        "data": {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }

                    res = await self._execute_single_tool(tc, user_id=ctx.user_id)
                    executed_tools.append(res)

                    yield {
                        "event": "tool_result",
                        "data": {
                            "id": tc.id,
                            "name": tc.function.name,
                            "content": res.content,
                            "is_error": res.is_error
                        }
                    }

                    messages.append(ChatMessage(
                        role="tool",
                        name=tc.function.name,
                        tool_call_id=tc.id,
                        content=res.content
                    ))
            else:
                final_content = turn_text
                break

        # Save assistant message
        await db_repo.save_message(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            role="assistant",
            content=final_content,
            tool_results=executed_tools
        )

        # Trigger autonomous memory recording and self-improvisation
        asyncio.create_task(self.memory.auto_extract_and_learn(processed_message, final_content, ctx.user_id, self.llm))

        yield {
            "event": "done",
            "data": {
                "session_id": ctx.session_id,
                "tool_count": len(executed_tools),
                "content": final_content
            }
        }

    async def _generate_mock_turn(self, user_prompt: str, tools: List[Dict[str, Any]]) -> AgentResponse:
        """
        Intelligent local demo fallback when LLM API key is not yet set in .env.
        Demonstrates tools and skills cleanly.
        """
        lower = user_prompt.lower()
        executed = []

        if "time" in lower or "date" in lower:
            t = await self._execute_single_tool(ToolCall(
                id="call_time_demo",
                function={"name": "mcp__utilities__get_system_time", "arguments": "{}"}
            ))
            executed.append(t)
            reply = f"I invoked the MCP utility tool to check the system time:\n\n`{t.content}`\n\n*(Powered by Ocg/Ocg3.8-27B agent engine)*"
        elif "calc" in lower or "math" in lower or "+" in lower or "*" in lower:
            t = await self._execute_single_tool(ToolCall(
                id="call_calc_demo",
                function={"name": "plugin__system_tools__calculator", "arguments": json.dumps({"expression": "2 ** 10 + 42"})}
            ))
            executed.append(t)
            reply = f"I invoked the System Tools plugin calculator tool:\n\n{t.content}\n\n*(Powered by Ocg/Ocg3.8-27B)*"
        elif any(kw in lower for kw in ["hello", "hi", "hey", "greet", "who are you", "what are you", "introduce"]):
            reply = (
                f"👋 Hello! I am **OCG Agent**, an autonomous AI assistant powered by the ReAct reasoning loop.\n\n"
                f"I support:\n"
                f"- 🔌 **MCP Servers** — {len(self.mcp.get_all_tools())} tool(s) loaded\n"
                f"- 🧩 **Python Plugins** — {len(self.plugins.get_all_tools())} tool(s) available\n"
                f"- 📚 **Skills** — {len(self.skills.skills)} loaded\n"
                f"- 🧠 **Long-term Memory** — automatic per-user memory with self-improvisation\n\n"
                f"> ⚠️ **Demo Mode** — To unlock live LLM inference, add your `LLM_API_KEY` in `.env` or the ⚙️ Settings tab."
            )
        elif any(kw in lower for kw in ["help", "what can", "capable", "features", "support"]):
            reply = (
                f"I can help with many tasks:\n\n"
                f"| Category | Examples |\n"
                f"|---|---|\n"
                f"| 🕒 Time & System | \"What time is it?\", \"Check system info\" |\n"
                f"| 🧮 Calculations | \"Calculate 2^16\", \"sqrt(144)\" |\n"
                f"| 🏛️ Code Architecture | \"Design a microservice for payments\" |\n"
                f"| 🔍 Web Research | \"Research best practices for FastAPI\" |\n"
                f"| 📦 Marketplace | Install MCP servers, plugins, skills from GitHub |\n"
                f"| 🧠 Memory | Remembers preferences, rules, and project context |\n\n"
                f"> ⚠️ **Demo Mode** — add `LLM_API_KEY` in Settings to enable live AI responses."
            )
        elif any(kw in lower for kw in ["memory", "remember", "forget", "learn", "rule", "preference"]):
            reply = (
                f"🧠 **Long-Term Memory System**\n\n"
                f"This agent automatically records:\n"
                f"- **Facts** — user preferences, coding style, tool choices\n"
                f"- **Project Context** — tech stack, architecture decisions\n"
                f"- **Rules** — behavioral guidelines the agent follows\n"
                f"- **Self-Improvised Learnings** — patterns from past corrections\n\n"
                f"Open the **🧠 Memory & Evolution** modal from the sidebar to view, add, or delete memories.\n\n"
                f"> ⚠️ Demo Mode — live memory extraction requires a configured LLM API key."
            )
        elif any(kw in lower for kw in ["marketplace", "install", "plugin", "skill", "mcp", "github", "extension"]):
            reply = (
                f"📦 **Marketplace & Extensibility Hub**\n\n"
                f"You can install from:\n"
                f"- **Curated Catalog** — pre-verified MCP servers, plugins, and skills\n"
                f"- **GitHub Repos** — paste any GitHub URL to clone & install\n"
                f"- **Raw URLs** — direct Python files or markdown skill files\n"
                f"- **Inline Code** — paste Python plugin code directly\n\n"
                f"Click **📦 Marketplace** in the sidebar or navbar to get started!\n\n"
                f"Currently active: **{len(self.mcp.get_all_tools())} MCP tools**, **{len(self.plugins.get_all_tools())} plugin tools**, **{len(self.skills.skills)} skills**."
            )
        else:
            # Generic contextual fallback — never repeat the same startup message
            excerpt = user_prompt[:100] + ('...' if len(user_prompt) > 100 else '')
            reply = (
                f"I received your message: *\"{excerpt}\"*\n\n"
                f"**OCG Agent** is running in **Demo Mode** (no LLM API key configured). "
                f"To get real AI responses:\n\n"
                f"1. Open **⚙️ Settings** in the bottom-left sidebar\n"
                f"2. Enter your API Base URL (e.g. OpenRouter, Together AI, or Ollama)\n"
                f"3. Paste your `LLM_API_KEY`\n"
                f"4. Click **Save Settings** — live inference activates immediately\n\n"
                f"*{len(self.mcp.get_all_tools())} MCP tools • {len(self.plugins.get_all_tools())} plugin tools • {len(self.skills.skills)} skills ready*"
            )

        return AgentResponse(content=reply, tool_executions=executed)

    async def _stream_mock_turn(self, user_prompt: str, tools: List[Dict[str, Any]], ctx: AgentRunContext) -> AsyncGenerator[Dict[str, Any], None]:
        import asyncio
        resp = await self._generate_mock_turn(user_prompt, tools)

        for t in resp.tool_executions:
            yield {
                "event": "tool_call",
                "data": {"id": t.tool_call_id, "name": t.tool_name, "arguments": "{}"}
            }
            yield {
                "event": "tool_result",
                "data": {"id": t.tool_call_id, "name": t.tool_name, "content": t.content, "is_error": t.is_error}
            }

        # Stream tokens
        words = resp.content.split(" ")
        for w in words:
            yield {"event": "token", "data": {"token": w + " "}}
            await asyncio.sleep(0.015)

        yield {"event": "done", "data": {"session_id": ctx.session_id, "tool_count": len(resp.tool_executions), "content": resp.content}}
