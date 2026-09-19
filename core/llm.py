import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
from openai import AsyncOpenAI
from config import settings
from core.types import ChatMessage, ToolCall, FunctionCall

logger = logging.getLogger("Ocg_agent.llm")

class OcgLLMClient:
    """
    OpenAI-compatible client tailored for Ocg models (specifically Ocg/Ocg3.8-27B).
    Works seamlessly with OpenRouter, Together AI, HuggingFace Inference Endpoints,
    vLLM, Ollama, and local proxies.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.model = model or settings.LLM_MODEL
        self.base_url = base_url or settings.LLM_BASE_URL
        self.api_key = api_key or settings.LLM_API_KEY or "not-provided"
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS

        # Custom headers for OpenRouter / HF
        default_headers = {
            "HTTP-Referer": "https://github.com/Ocg-agent",
            "X-Title": "Ocg Agent with MCP & Supabase",
        }

        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers=default_headers,
            max_retries=1,
            timeout=30.0,
        )

    def is_configured(self) -> bool:
        """Check if a valid API key or local endpoint is configured."""
        if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
            return True
        if not self.api_key:
            return False
        invalid_keys = {
            "none", "null", "undefined", "not-provided",
            "your_llm_api_key_here", "mock-dev-key-or-set-your-key"
        }
        return self.api_key.strip().lower() not in invalid_keys

    async def generate_response(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatMessage:
        """
        Non-streaming generation with tool call resolution.
        """
        payload_messages = [msg.to_dict() for msg in messages]

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": payload_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if tools and len(tools) > 0:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = await self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            message_obj = choice.message

            tool_calls = None
            if message_obj.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        type="function",
                        function=FunctionCall(
                            name=tc.function.name,
                            arguments=tc.function.arguments,
                        ),
                    )
                    for tc in message_obj.tool_calls
                ]

            return ChatMessage(
                role="assistant",
                content=message_obj.content or "",
                tool_calls=tool_calls,
            )

        except Exception as e:
            logger.error(f"Error calling Ocg LLM ({self.model}): {e}")
            raise

    async def stream_response(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming generation supporting token streaming and accumulated tool calls.
        Yields events: {'type': 'token', 'content': str} or {'type': 'tool_calls', 'calls': List[ToolCall]}
        """
        payload_messages = [msg.to_dict() for msg in messages]

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": payload_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
        }

        if tools and len(tools) > 0:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        tool_call_chunks: Dict[int, Dict[str, Any]] = {}

        stream = await self.client.chat.completions.create(**kwargs)
        async for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Stream regular text tokens
            if delta.content:
                yield {"type": "token", "content": delta.content}

            # Accumulate streaming tool calls
            if delta.tool_calls:
                for tc_chunk in delta.tool_calls:
                    idx = tc_chunk.index
                    if idx not in tool_call_chunks:
                        tool_call_chunks[idx] = {
                            "id": tc_chunk.id or f"call_{idx}",
                            "name": tc_chunk.function.name if tc_chunk.function else "",
                            "arguments": "",
                        }
                    if tc_chunk.function:
                        if tc_chunk.function.name and not tool_call_chunks[idx]["name"]:
                            tool_call_chunks[idx]["name"] = tc_chunk.function.name
                        if tc_chunk.function.arguments:
                            tool_call_chunks[idx]["arguments"] += tc_chunk.function.arguments

        if tool_call_chunks:
            final_tool_calls = [
                ToolCall(
                    id=item["id"],
                    type="function",
                    function=FunctionCall(name=item["name"], arguments=item["arguments"]),
                )
                for item in tool_call_chunks.values()
            ]
            yield {"type": "tool_calls", "calls": final_tool_calls}

# Backward compatibility alias

