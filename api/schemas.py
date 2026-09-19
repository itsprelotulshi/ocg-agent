from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    plugins: List[str] = Field(default_factory=list)
    stream: bool = True

class AuthRequest(BaseModel):
    email: str
    password: str

class SessionCreateRequest(BaseModel):
    title: str = "New Conversation"

class SettingsUpdateRequest(BaseModel):
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None

class MarketplaceInstallRequest(BaseModel):
    type: str  # 'mcp', 'plugin', 'skill'
    id: Optional[str] = None
    name: Optional[str] = None
    source_url: Optional[str] = None  # GitHub repo or raw URL
    code: Optional[str] = None  # Custom Python plugin code or Markdown skill instructions
    config: Optional[Dict[str, Any]] = None  # Custom MCP server config

class MarketplaceUninstallRequest(BaseModel):
    type: str
    id: str

class MemoryCreateRequest(BaseModel):
    category: str  # 'fact', 'project', 'rule', 'learning'
    key: str
    content: str
    source: Optional[str] = "user_specified"
    tags: Optional[List[str]] = None

