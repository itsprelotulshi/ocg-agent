import uuid
import datetime
import logging
from typing import List, Dict, Any, Optional
from auth.supabase import supabase_auth
from core.types import ChatMessage, ToolCall, ToolResult

logger = logging.getLogger("ocg_agent.database")

class DatabaseRepository:
    """
    Data repository for sessions and chat messages.
    Syncs with Supabase PostgreSQL when available, and falls back to
    an in-memory store for guest/development mode.
    """

    def __init__(self):
        # In-memory storage fallback:
        # sessions: {session_id: {id, user_id, title, created_at, updated_at}}
        # messages: {session_id: [message_dict, ...]}
        self._local_sessions: Dict[str, Dict[str, Any]] = {}
        self._local_messages: Dict[str, List[Dict[str, Any]]] = {}

    def _now_iso(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def _is_valid_uuid(self, val: Any) -> bool:
        if not val or not isinstance(val, str):
            return False
        try:
            uuid.UUID(val)
            return True
        except (ValueError, TypeError):
            return False

    async def list_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        client = supabase_auth.client
        if client:
            try:
                query = client.table("sessions").select("*")
                if self._is_valid_uuid(user_id):
                    query = query.eq("user_id", user_id)
                elif user_id.startswith("guest") or not user_id:
                    query = query.or_(f"user_id.is.null")
                res = query.order("updated_at", desc=True).execute()
                return res.data or []
            except Exception as e:
                logger.warning(f"Supabase list_sessions failed, using local: {e}")

        # Local fallback
        return [
            s for s in self._local_sessions.values()
            if s.get("user_id") == user_id or user_id.startswith("guest")
        ]

    async def create_session(self, user_id: str, title: str = "New Conversation") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        record = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": self._now_iso(),
            "updated_at": self._now_iso()
        }

        client = supabase_auth.client
        if client:
            try:
                sb_record = dict(record)
                if not self._is_valid_uuid(user_id):
                    sb_record["user_id"] = None
                res = client.table("sessions").insert(sb_record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.warning(f"Supabase create_session failed: {e}")

        # Local fallback
        self._local_sessions[session_id] = record
        self._local_messages[session_id] = []
        return record

    async def get_messages(self, session_id: str, user_id: str) -> List[ChatMessage]:
        client = supabase_auth.client
        if client:
            try:
                res = client.table("messages").select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
                if res.data:
                    messages: List[ChatMessage] = []
                    for row in res.data:
                        tool_calls = None
                        if row.get("tool_calls"):
                            tool_calls = [ToolCall(**tc) for tc in row["tool_calls"]]
                        messages.append(ChatMessage(
                            id=row.get("id"),
                            role=row["role"],
                            content=row.get("content") or "",
                            tool_calls=tool_calls,
                            created_at=row.get("created_at")
                        ))
                    return messages
            except Exception as e:
                logger.warning(f"Supabase get_messages failed, using local: {e}")

        # Local fallback
        raw_msgs = self._local_messages.get(session_id, [])
        messages = []
        for row in raw_msgs:
            tool_calls = None
            if row.get("tool_calls"):
                tool_calls = [ToolCall(**tc) for tc in row["tool_calls"]]
            messages.append(ChatMessage(
                id=row.get("id"),
                role=row["role"],
                content=row.get("content") or "",
                tool_calls=tool_calls,
                created_at=row.get("created_at")
            ))
        return messages

    async def save_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[ToolCall]] = None,
        tool_results: Optional[List[ToolResult]] = None
    ) -> Dict[str, Any]:
        msg_id = str(uuid.uuid4())
        record = {
            "id": msg_id,
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content or "",
            "tool_calls": [tc.model_dump() for tc in tool_calls] if tool_calls else [],
            "tool_results": [tr.model_dump() for tr in tool_results] if tool_results else [],
            "created_at": self._now_iso()
        }

        client = supabase_auth.client
        if client:
            try:
                sb_record = dict(record)
                if not self._is_valid_uuid(user_id):
                    sb_record["user_id"] = None
                client.table("messages").insert(sb_record).execute()
                # Update session's updated_at
                client.table("sessions").update({"updated_at": self._now_iso()}).eq("id", session_id).execute()
                return record
            except Exception as e:
                logger.warning(f"Supabase save_message failed: {e}")

        # Local fallback
        if session_id not in self._local_messages:
            self._local_messages[session_id] = []
        self._local_messages[session_id].append(record)

        if session_id in self._local_sessions:
            self._local_sessions[session_id]["updated_at"] = self._now_iso()

        return record

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        client = supabase_auth.client
        if client:
            try:
                query = client.table("sessions").delete().eq("id", session_id)
                if self._is_valid_uuid(user_id):
                    query = query.eq("user_id", user_id)
                query.execute()
                return True
            except Exception as e:
                logger.warning(f"Supabase delete_session failed: {e}")

        # Local fallback
        if session_id in self._local_sessions:
            del self._local_sessions[session_id]
            self._local_messages.pop(session_id, None)
            return True
        return False

    # ==============================================================================
    # Agent Long-Term Memory Persistence (Supabase + Persistent Local JSON fallback)
    # ==============================================================================

    def _get_local_memories_file(self) -> str:
        import os
        os.makedirs("data", exist_ok=True)
        return os.path.join("data", "memories.json")

    def _load_local_memories(self) -> List[Dict[str, Any]]:
        import os
        import json
        fpath = self._get_local_memories_file()
        if not os.path.exists(fpath):
            return []
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read local memories file: {e}")
            return []

    def _save_local_memories(self, memories: List[Dict[str, Any]]):
        import json
        fpath = self._get_local_memories_file()
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to write local memories file: {e}")

    async def list_memories(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        client = supabase_auth.client
        if client:
            try:
                query = client.table("agent_memories").select("*")
                if user_id and not user_id.startswith("guest"):
                    query = query.or_(f"user_id.eq.{user_id},user_id.eq.global")
                if category:
                    query = query.eq("category", category)
                res = query.order("updated_at", desc=True).execute()
                if res.data is not None:
                    return res.data
            except Exception as e:
                logger.warning(f"Supabase list_memories failed, using local: {e}")

        # Local JSON store fallback
        memories = self._load_local_memories()
        results = []
        for m in memories:
            if m.get("user_id") == user_id or m.get("user_id") == "global" or user_id.startswith("guest"):
                if not category or m.get("category") == category:
                    results.append(m)
        # Sort by updated_at desc
        results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return results

    async def save_memory(
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
        client = supabase_auth.client
        mem_id = memory_id or str(uuid.uuid4())
        record = {
            "id": mem_id,
            "user_id": user_id,
            "category": category,
            "key": key.strip(),
            "content": content.strip(),
            "source": source,
            "confidence": confidence,
            "tags": tags or [],
            "access_count": 0,
            "updated_at": self._now_iso()
        }

        # Check for existing duplicate by key and category in local first to update
        local_mems = self._load_local_memories()
        existing_idx = None
        for i, m in enumerate(local_mems):
            if m.get("id") == mem_id or (m.get("user_id") == user_id and m.get("category") == category and m.get("key").lower() == key.strip().lower()):
                existing_idx = i
                break

        if existing_idx is not None:
            record["id"] = local_mems[existing_idx]["id"]
            record["created_at"] = local_mems[existing_idx].get("created_at", self._now_iso())
            record["access_count"] = local_mems[existing_idx].get("access_count", 0) + 1
            local_mems[existing_idx] = record
        else:
            record["created_at"] = self._now_iso()
            local_mems.append(record)

        self._save_local_memories(local_mems)

        if client:
            try:
                # Upsert into Supabase
                res = client.table("agent_memories").upsert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.warning(f"Supabase save_memory failed: {e}")

        return record

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        client = supabase_auth.client
        if client:
            try:
                client.table("agent_memories").delete().eq("id", memory_id).execute()
            except Exception as e:
                logger.warning(f"Supabase delete_memory failed: {e}")

        local_mems = self._load_local_memories()
        new_mems = [m for m in local_mems if m.get("id") != memory_id]
        if len(new_mems) != len(local_mems):
            self._save_local_memories(new_mems)
            return True
        return False

    async def clear_memories(self, user_id: str) -> int:
        client = supabase_auth.client
        if client:
            try:
                if user_id.startswith("guest"):
                    client.table("agent_memories").delete().execute()
                else:
                    client.table("agent_memories").delete().eq("user_id", user_id).execute()
            except Exception as e:
                logger.warning(f"Supabase clear_memories failed: {e}")

        local_mems = self._load_local_memories()
        if user_id.startswith("guest"):
            cleared = len(local_mems)
            self._save_local_memories([])
            return cleared
        else:
            filtered = [m for m in local_mems if m.get("user_id") != user_id]
            cleared = len(local_mems) - len(filtered)
            self._save_local_memories(filtered)
            return cleared

# Global instance
db_repo = DatabaseRepository()

