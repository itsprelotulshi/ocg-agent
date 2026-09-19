import re
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from database.repository import db_repo

logger = logging.getLogger("ocg_agent.memory")

class MemoryItem(BaseModel):
    id: Optional[str] = None
    user_id: str = "guest"
    category: str = Field(description="One of: 'fact', 'project', 'rule', 'learning'")
    key: str
    content: str
    source: str = "auto_extracted"  # 'auto_extracted', 'user_specified', 'agent_improvised'
    confidence: float = 1.0
    tags: List[str] = Field(default_factory=list)
    access_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class MemoryManager:
    """
    Manages long-term persistent memory and self-improvisation for the agent.
    Automatically synthesizes important facts, project guidelines, user preferences,
    and self-learned rules to inject into the agent prompt on every conversation turn.
    """

    def __init__(self):
        pass

    async def list_memories(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return await db_repo.list_memories(user_id=user_id, category=category)

    async def add_or_update_memory(
        self,
        user_id: str,
        category: str,
        key: str,
        content: str,
        source: str = "auto_extracted",
        confidence: float = 1.0,
        tags: Optional[List[str]] = None,
        memory_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        valid_categories = {"fact", "project", "rule", "learning"}
        if category not in valid_categories:
            category = "fact"
        return await db_repo.save_memory(
            user_id=user_id,
            category=category,
            key=key,
            content=content,
            source=source,
            confidence=confidence,
            tags=tags or [],
            memory_id=memory_id,
        )

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        return await db_repo.delete_memory(memory_id=memory_id, user_id=user_id)

    async def clear_all(self, user_id: str) -> int:
        return await db_repo.clear_memories(user_id=user_id)

    async def retrieve_relevant_memories(self, user_query: str, user_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Retrieves:
        1. All active 'rule' and 'learning' items (global behavioral guidelines for self-improvisation).
        2. 'fact' and 'project' items that match words in the user query.
        """
        all_memories = await db_repo.list_memories(user_id=user_id)
        if not all_memories:
            return []

        rules_and_learnings = []
        contextual_matches = []
        tokens = set(re.findall(r"\w+", user_query.lower()))

        for mem in all_memories:
            cat = mem.get("category")
            if cat in ("rule", "learning"):
                rules_and_learnings.append(mem)
            else:
                # Check keyword match in key, content, or tags
                key_text = mem.get("key", "").lower()
                content_text = mem.get("content", "").lower()
                tags = [t.lower() for t in mem.get("tags", [])]

                mem_tokens = set(re.findall(r"\w+", f"{key_text} {content_text} {' '.join(tags)}"))
                overlap = tokens.intersection(mem_tokens)
                if overlap or len(all_memories) <= 8:  # If few memories, include all facts
                    score = len(overlap)
                    contextual_matches.append((score, mem))

        # Sort contextual matches by match score descending
        contextual_matches.sort(key=lambda x: x[0], reverse=True)
        sorted_matches = [m[1] for m in contextual_matches]

        combined = rules_and_learnings + sorted_matches
        # Deduplicate while preserving order
        seen_ids = set()
        deduped = []
        for m in combined:
            m_id = m.get("id")
            if m_id not in seen_ids:
                seen_ids.add(m_id)
                deduped.append(m)
            if len(deduped) >= limit:
                break

        return deduped

    def format_memory_instructions(self, memories: List[Dict[str, Any]]) -> str:
        """Format retrieved memories into a system prompt section."""
        if not memories:
            return ""

        lines = [
            "\n### 🧠 Long-Term Memory & Self-Improvised Guidelines:",
            "The following facts, project rules, and learned guidelines have been automatically remembered from prior interactions.",
            "You MUST adhere to these guidelines and reference recorded facts accurately:",
        ]

        for m in memories:
            cat = m.get("category", "fact").upper()
            key = m.get("key", "")
            content = m.get("content", "")
            source = m.get("source", "recorded")
            lines.append(f"- **[{cat}] {key}**: {content} *(source: {source})*")

        return "\n".join(lines)

    async def auto_extract_and_learn(
        self,
        user_message: str,
        assistant_response: str,
        user_id: str,
        llm_client: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Synthesize the conversation turn to discover:
        1. User facts & preferences (name, tech stack, preferences)
        2. Project architecture & conventions
        3. User corrections & self-improvement rules
        """
        extracted_items: List[Dict[str, Any]] = []
        text = user_message.strip()

        # Rule / Correction Patterns (Self-Improvisation)
        correction_patterns = [
            (r"(?:actually|no|incorrect|that's wrong|don't do that)[,\s]+(?:it's|it is|use|you should|always|please)\s+(.+)", "correction"),
            (r"(?:from now on|in the future|always|remember to)\s+(.+)", "future_rule"),
            (r"(?:never|do not|don't ever)\s+(.+)", "negative_constraint"),
            (r"(?:prefer|i prefer|we prefer)\s+(.+)", "preference"),
        ]

        # Explicit Fact Patterns
        fact_patterns = [
            (r"(?:my name is|call me|i am)\s+([A-Z][a-zA-Z0-9_\-]+)", "user_name", "User's name is {match}"),
            (r"(?:i am using|we use|our stack is|our database is|the project uses)\s+([^.\n]+)", "tech_stack", "Tech stack / project uses {match}"),
            (r"(?:remember that|note that|keep in mind that)\s+([^.\n]+)", "important_fact", "{match}"),
        ]

        # 1. Heuristic Extraction for fast & reliable zero-latency discovery
        for pattern, key_prefix, template in fact_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                content = template.format(match=val)
                item = await self.add_or_update_memory(
                    user_id=user_id,
                    category="fact" if "name" in key_prefix else "project",
                    key=f"{key_prefix}_{val[:15].replace(' ', '_').lower()}",
                    content=content,
                    source="auto_extracted",
                    confidence=0.9,
                    tags=["heuristic", key_prefix]
                )
                extracted_items.append(item)

        for pattern, rule_type in correction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rule_detail = match.group(1).strip()
                if len(rule_detail) > 4:
                    item = await self.add_or_update_memory(
                        user_id=user_id,
                        category="learning" if rule_type == "correction" else "rule",
                        key=f"{rule_type}_{rule_detail[:20].replace(' ', '_').lower()}",
                        content=f"Learned guideline: {rule_detail}",
                        source="agent_improvised",
                        confidence=0.95,
                        tags=["self_improvise", rule_type]
                    )
                    extracted_items.append(item)

        # 2. LLM-based intelligent extraction if LLM is configured and message is informative
        if llm_client and hasattr(llm_client, "is_configured") and llm_client.is_configured() and len(text) > 20:
            try:
                prompt = (
                    "Analyze the user's message and agent's response. Extract any important facts, user preferences, "
                    "project technical context, or corrections/guidelines that should be stored permanently in long-term memory "
                    "so the agent remembers and improves in future conversations.\n\n"
                    f"User: {user_message}\n"
                    f"Assistant: {assistant_response[:300]}\n\n"
                    "Respond with valid JSON ONLY in this format:\n"
                    "{\n"
                    '  "memories": [\n'
                    '    {"category": "fact|project|rule|learning", "key": "short_unique_key", "content": "detailed statement"}\n'
                    "  ]\n"
                    "}\n"
                    "If nothing important to remember, return {\"memories\": []}."
                )
                from core.types import ChatMessage
                messages = [
                    ChatMessage(role="system", content="You are an autonomous memory extraction system. Output JSON only."),
                    ChatMessage(role="user", content=prompt)
                ]
                resp = await llm_client.generate_response(messages, tools=None)
                raw_json = resp.content.strip()
                # Remove markdown codeblocks if wrapped
                if raw_json.startswith("```"):
                    raw_json = re.sub(r"^```(?:json)?\n|\n```$", "", raw_json).strip()

                parsed = json.loads(raw_json)
                for mem in parsed.get("memories", []):
                    cat = mem.get("category", "fact")
                    k = mem.get("key", "").strip()
                    c = mem.get("content", "").strip()
                    if k and c:
                        saved = await self.add_or_update_memory(
                            user_id=user_id,
                            category=cat,
                            key=k,
                            content=c,
                            source="llm_synthesized",
                            confidence=0.92,
                            tags=["llm_extracted"]
                        )
                        extracted_items.append(saved)
            except Exception as e:
                logger.debug(f"LLM memory extraction skipped or error: {e}")

        return extracted_items

    # ==============================================================================
    # Agent Tools Exposure
    # ==============================================================================

    def get_agent_tools(self) -> List[Dict[str, Any]]:
        """Return memory tools formatted for OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "memory__remember",
                    "description": "Store an important fact, user preference, project architecture rule, or self-improvised guideline permanently in long-term memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["fact", "project", "rule", "learning"],
                                "description": "Type of memory: 'fact' (personal/general fact), 'project' (repo/architecture), 'rule' (behavior constraint), 'learning' (self-learned correction/guideline)."
                            },
                            "key": {
                                "type": "string",
                                "description": "Short, clear identifier for this memory (e.g. 'preferred_language', 'auth_strategy')."
                            },
                            "content": {
                                "type": "string",
                                "description": "Full detailed content or rule to remember."
                            }
                        },
                        "required": ["category", "key", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "memory__search",
                    "description": "Search the agent's long-term memory for previously recorded facts, rules, or self-improvised learnings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Keywords or concept to search for in memory."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "memory__improvise_rule",
                    "description": "Record a new self-improvised rule or guideline learned from user feedback, error correction, or domain insight.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rule_key": {
                                "type": "string",
                                "description": "Name or topic of the guideline (e.g., 'avoid_raw_sql', 'prefer_dataclasses')."
                            },
                            "instruction": {
                                "type": "string",
                                "description": "The exact behavioral rule the agent should follow in future conversations."
                            }
                        },
                        "required": ["rule_key", "instruction"]
                    }
                }
            }
        ]

    def can_handle(self, tool_name: str) -> bool:
        return tool_name in {"memory__remember", "memory__search", "memory__improvise_rule"}

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], user_id: str = "guest") -> str:
        """Handle execution of memory tools."""
        try:
            if tool_name == "memory__remember":
                category = arguments.get("category", "fact")
                key = arguments.get("key", "")
                content = arguments.get("content", "")
                await self.add_or_update_memory(
                    user_id=user_id,
                    category=category,
                    key=key,
                    content=content,
                    source="agent_tool",
                    confidence=1.0,
                    tags=["explicit_agent_tool"]
                )
                return f"Successfully saved to long-term memory: [{category.upper()}] '{key}': {content}"

            elif tool_name == "memory__search":
                query = arguments.get("query", "")
                matches = await self.retrieve_relevant_memories(user_query=query, user_id=user_id)
                if not matches:
                    return f"No memories found matching '{query}'."
                out = [f"Found {len(matches)} relevant memory items:"]
                for m in matches:
                    out.append(f"- [{m.get('category').upper()}] {m.get('key')}: {m.get('content')}")
                return "\n".join(out)

            elif tool_name == "memory__improvise_rule":
                rule_key = arguments.get("rule_key", "")
                instruction = arguments.get("instruction", "")
                await self.add_or_update_memory(
                    user_id=user_id,
                    category="learning",
                    key=rule_key,
                    content=instruction,
                    source="agent_improvised",
                    confidence=1.0,
                    tags=["self_improvise"]
                )
                return f"Self-improvement rule recorded: '{rule_key}' -> {instruction}. I will apply this in all future interactions."

            return f"Unknown memory tool '{tool_name}'."
        except Exception as e:
            return f"Error executing memory tool: {str(e)}"

# Global instance
memory_manager = MemoryManager()
