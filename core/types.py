from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON-encoded string

class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: FunctionCall

class ToolResult(BaseModel):
    tool_call_id: str
    tool_name: str
    content: str
    is_error: bool = False

class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"role": self.role}
        if self.id is not None:
            data["id"] = self.id
        if self.content is not None:
            data["content"] = self.content
        if self.name is not None:
            data["name"] = self.name
        if self.tool_call_id is not None:
            data["tool_call_id"] = self.tool_call_id
        if self.tool_calls is not None:
            data["tool_calls"] = [tc.model_dump() for tc in self.tool_calls]
        if self.created_at is not None:
            data["created_at"] = self.created_at
        return data

class AgentRunContext(BaseModel):
    user_id: str = "guest_user"
    session_id: str = "default_session"
    active_skills: List[str] = Field(default_factory=list)
    active_plugins: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentResponse(BaseModel):
    content: str
    tool_executions: List[ToolResult] = Field(default_factory=list)
    finish_reason: str = "stop"

class StreamChunk(BaseModel):
    event: Literal["token", "thought", "tool_call", "tool_result", "skill_applied", "error", "done"]
    data: Dict[str, Any]
