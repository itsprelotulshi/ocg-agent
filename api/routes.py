import json
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from config import settings
from auth.middleware import get_current_user, UserContext
from auth.supabase import supabase_auth
from database.repository import db_repo
from core.agent import OcgAgent
from core.types import AgentRunContext
from core.marketplace import marketplace_manager
from core.memory import memory_manager
from api.schemas import (
    ChatRequest,
    AuthRequest,
    SessionCreateRequest,
    SettingsUpdateRequest,
    MarketplaceInstallRequest,
    MarketplaceUninstallRequest,
    MemoryCreateRequest
)


logger = logging.getLogger("Ocg_agent.api")

router = APIRouter(prefix="/api")

# Agent instance will be injected or accessed from app state
_agent_instance: OcgAgent = None

def set_agent_instance(agent: OcgAgent):
    global _agent_instance
    _agent_instance = agent

def get_agent() -> OcgAgent:
    global _agent_instance
    if not _agent_instance:
        _agent_instance = OcgAgent()
    return _agent_instance

# ==============================================================================
# Authentication Routes (Supabase)
# ==============================================================================

@router.post("/auth/signup")
async def signup(req: AuthRequest):
    try:
        result = await supabase_auth.sign_up(req.email, req.password)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/signin")
async def signin(req: AuthRequest):
    try:
        result = await supabase_auth.sign_in(req.email, req.password)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auth/me")
async def get_me(user: UserContext = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_guest": user.is_guest,
        "supabase_connected": supabase_auth.is_configured()
    }

# ==============================================================================
# Sessions & Conversation History
# ==============================================================================

@router.get("/sessions")
async def list_sessions(user: UserContext = Depends(get_current_user)):
    sessions = await db_repo.list_sessions(user.id)
    return {"sessions": sessions}

@router.post("/sessions")
async def create_session(req: SessionCreateRequest, user: UserContext = Depends(get_current_user)):
    session = await db_repo.create_session(user.id, title=req.title)
    return {"session": session}

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, user: UserContext = Depends(get_current_user)):
    messages = await db_repo.get_messages(session_id, user.id)
    return {"messages": [m.to_dict() for m in messages]}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: UserContext = Depends(get_current_user)):
    success = await db_repo.delete_session(session_id, user.id)
    return {"status": "success" if success else "failed"}

# ==============================================================================
# Chat Execution (ReAct Loop & SSE Streaming)
# ==============================================================================

@router.post("/chat")
async def chat_endpoint(req: ChatRequest, user: UserContext = Depends(get_current_user)):
    agent = get_agent()

    # If no session provided, create one
    session_id = req.session_id
    if not session_id:
        new_session = await db_repo.create_session(user.id, title=req.message[:30] + "...")
        session_id = new_session["id"]

    context = AgentRunContext(
        user_id=user.id,
        session_id=session_id,
        active_skills=req.skills,
        active_plugins=req.plugins,
    )

    if req.stream:
        async def event_generator():
            try:
                # Yield initial session metadata
                yield f"data: {json.dumps({'event': 'session_init', 'data': {'session_id': session_id}})}\n\n"
                async for chunk in agent.stream_chat(req.message, context=context):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as err:
                logger.error(f"Streaming error: {err}")
                yield f"data: {json.dumps({'event': 'error', 'data': {'message': str(err)}})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Non-streaming response
    response = await agent.run(req.message, context=context)
    return {
        "session_id": session_id,
        "content": response.content,
        "tool_executions": [tr.model_dump() for tr in response.tool_executions],
        "finish_reason": response.finish_reason
    }

@router.post("/sessions/{session_id}/chat")
async def session_chat_endpoint(session_id: str, req: ChatRequest, user: UserContext = Depends(get_current_user)):
    req.session_id = session_id
    return await chat_endpoint(req, user)


# ==============================================================================
# MCP Server & Tool Management
# ==============================================================================

@router.get("/mcp/status")
async def get_mcp_status():
    agent = get_agent()
    return {
        "servers": agent.mcp.get_status(),
        "total_tools": len(agent.mcp.get_all_tools())
    }

@router.post("/mcp/reload")
async def reload_mcp():
    agent = get_agent()
    await agent.mcp.shutdown()
    await agent.mcp.initialize()
    return {
        "status": "success",
        "total_tools": len(agent.mcp.get_all_tools())
    }

# ==============================================================================
# Plugins Management
# ==============================================================================

@router.get("/plugins")
async def list_plugins():
    agent = get_agent()
    return {"plugins": agent.plugins.get_status()}

@router.post("/plugins/{plugin_name}/toggle")
async def toggle_plugin(plugin_name: str):
    agent = get_agent()
    plugin = agent.plugins.plugins.get(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    plugin.enabled = not plugin.enabled
    return {"name": plugin.name, "enabled": plugin.enabled}

# ==============================================================================
# Skills Management
# ==============================================================================

@router.get("/skills")
async def list_skills():
    agent = get_agent()
    return {"skills": agent.skills.list_skills()}

@router.post("/skills/{skill_id}/toggle")
async def toggle_skill(skill_id: str):
    agent = get_agent()
    skill = agent.skills.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill.enabled = not skill.enabled
    return {"id": skill.id, "enabled": skill.enabled}

# ==============================================================================
# System Info & Dynamic Runtime Settings
# ==============================================================================

# ==============================================================================
# Marketplace & Extensibility Routes
# ==============================================================================

@router.get("/marketplace/catalog")
async def get_marketplace_catalog():
    return marketplace_manager.get_catalog()

@router.get("/marketplace/installed")
async def get_installed_packages():
    return marketplace_manager.get_installed()

@router.post("/marketplace/install")
async def install_marketplace_item(req: MarketplaceInstallRequest):
    agent = get_agent()
    item_type = req.type.lower()

    try:
        if item_type == "mcp":
            if req.source_url and ("github.com" in req.source_url or req.source_url.startswith("git@")):
                res = await marketplace_manager.install_mcp_from_github(
                    repo_url=req.source_url,
                    server_name=req.id or req.name,
                    mcp_manager=agent.mcp
                )
            elif req.config:
                server_id = req.id or req.name or "custom_mcp"
                res = await marketplace_manager.install_mcp_from_config(
                    server_name=server_id,
                    config=req.config,
                    mcp_manager=agent.mcp
                )
            else:
                raise HTTPException(status_code=400, detail="Missing MCP config or GitHub URL.")
            return {"status": "success", "data": res}

        elif item_type == "plugin":
            plugin_id = req.id or req.name or "custom_plugin"
            res = await marketplace_manager.install_plugin(
                plugin_name=plugin_id,
                code_content=req.code,
                source_url=req.source_url,
                plugin_manager=agent.plugins
            )
            return {"status": "success", "data": res}

        elif item_type == "skill":
            skill_id = req.id or req.name or "custom_skill"
            res = await marketplace_manager.install_skill(
                skill_id=skill_id,
                markdown_content=req.code,
                source_url=req.source_url,
                skill_manager=agent.skills
            )
            return {"status": "success", "data": res}

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported item type '{req.type}'")

    except Exception as e:
        logger.error(f"Installation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/marketplace/uninstall")
async def uninstall_marketplace_item(req: MarketplaceUninstallRequest):
    agent = get_agent()
    try:
        res = await marketplace_manager.uninstall_package(
            package_type=req.type.lower(),
            package_id=req.id,
            mcp_manager=agent.mcp,
            plugin_manager=agent.plugins,
            skill_manager=agent.skills
        )
        return {"status": "success", "data": res}
    except Exception as e:
        logger.error(f"Uninstall failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# Agent Long-Term Memory & Self-Improvisation Routes
# ==============================================================================

@router.get("/memory")
async def list_memories(category: Optional[str] = None, user: UserContext = Depends(get_current_user)):
    memories = await memory_manager.list_memories(user_id=user.id, category=category)
    return {"memories": memories}

@router.post("/memory")
async def create_memory(req: MemoryCreateRequest, user: UserContext = Depends(get_current_user)):
    mem = await memory_manager.add_or_update_memory(
        user_id=user.id,
        category=req.category,
        key=req.key,
        content=req.content,
        source=req.source or "user_specified",
        confidence=1.0,
        tags=req.tags or []
    )
    return {"status": "success", "memory": mem}

@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str, user: UserContext = Depends(get_current_user)):
    success = await memory_manager.delete_memory(memory_id=memory_id, user_id=user.id)
    return {"status": "success" if success else "failed"}

@router.post("/memory/clear")
async def clear_memories(user: UserContext = Depends(get_current_user)):
    cleared = await memory_manager.clear_all(user_id=user.id)
    return {"status": "success", "cleared_count": cleared}

# ==============================================================================
# System Info & Dynamic Runtime Settings
# ==============================================================================

@router.get("/info")
async def get_info(user: UserContext = Depends(get_current_user)):
    agent = get_agent()
    memories = await memory_manager.list_memories(user_id=user.id)
    return {
        "model": agent.llm.model,
        "base_url": agent.llm.base_url,
        "is_llm_configured": agent.llm.is_configured(),
        "supabase_configured": supabase_auth.is_configured(),
        "require_auth": settings.REQUIRE_AUTH,
        "mcp_tools_count": len(agent.mcp.get_all_tools()),
        "plugin_tools_count": len(agent.plugins.get_all_tools()),
        "skills_count": len(agent.skills.skills),
        "memories_count": len(memories)
    }

@router.post("/settings")
async def update_settings(req: SettingsUpdateRequest):
    agent = get_agent()
    if req.model:
        settings.LLM_MODEL = req.model
        agent.llm.model = req.model
    if req.base_url:
        settings.LLM_BASE_URL = req.base_url
        agent.llm.base_url = req.base_url
    if req.api_key:
        settings.LLM_API_KEY = req.api_key
        agent.llm.api_key = req.api_key
        agent.llm.client.api_key = req.api_key
    if req.temperature is not None:
        settings.LLM_TEMPERATURE = req.temperature
        agent.llm.temperature = req.temperature
    if req.max_tokens is not None:
        settings.LLM_MAX_TOKENS = req.max_tokens
        agent.llm.max_tokens = req.max_tokens
    if req.supabase_url:
        settings.SUPABASE_URL = req.supabase_url
    if req.supabase_anon_key:
        settings.SUPABASE_ANON_KEY = req.supabase_anon_key
        supabase_auth.url = settings.SUPABASE_URL
        supabase_auth.anon_key = settings.SUPABASE_ANON_KEY
        supabase_auth._init_client()

    return {"status": "success", "info": await get_info()}

