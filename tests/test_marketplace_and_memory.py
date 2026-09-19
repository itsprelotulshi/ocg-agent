import os
import sys
import asyncio
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.memory import memory_manager
from core.marketplace import marketplace_manager
from main import app

async def run_tests():
    print("=" * 60)
    print("[TEST] Running Tests for Marketplace & Memory System")
    print("=" * 60)


    # -------------------------------------------------------------
    # 1. Test MemoryManager Direct Operations
    # -------------------------------------------------------------
    print("\n--- 1. Testing MemoryManager Direct Operations ---")

    # Clean test memory
    await memory_manager.clear_all(user_id="test_user")

    # Add Fact
    m1 = await memory_manager.add_or_update_memory(
        user_id="test_user",
        category="fact",
        key="user_preferred_stack",
        content="User exclusively uses Python with FastAPI and PostgreSQL.",
        source="user_specified"
    )
    print(f"Added Fact: [{m1['category']}] {m1['key']}")
    assert m1["key"] == "user_preferred_stack"

    # Add Rule
    m2 = await memory_manager.add_or_update_memory(
        user_id="test_user",
        category="rule",
        key="concise_answers",
        content="Always respond with concise, bulleted markdown without fluff.",
        source="user_specified"
    )
    print(f"Added Rule: [{m2['category']}] {m2['key']}")

    # Add Self-Learned Guideline (Self-Improvisation)
    m3 = await memory_manager.add_or_update_memory(
        user_id="test_user",
        category="learning",
        key="sqlite_syntax_fix",
        content="When executing SQL on SQLite, use PRAGMA table_info instead of information_schema.",
        source="agent_improvised"
    )
    print(f"Added Learning: [{m3['category']}] {m3['key']}")

    # Test Retrieval
    retrieved = await memory_manager.retrieve_relevant_memories(
        user_query="Tell me about python database options",
        user_id="test_user"
    )
    print(f"Retrieved {len(retrieved)} relevant memories for query.")
    assert len(retrieved) >= 2
    keys = [m["key"] for m in retrieved]
    assert "concise_answers" in keys  # Rules are always included
    assert "sqlite_syntax_fix" in keys  # Learnings are always included

    # Test Prompt Injection formatting
    prompt_snippet = memory_manager.format_memory_instructions(retrieved)
    print("Formatted System Instructions:\n", prompt_snippet)
    assert "### 🧠 Long-Term Memory & Self-Improvised Guidelines:" in prompt_snippet
    assert "concise_answers" in prompt_snippet

    # Test Heuristic Auto-Extraction
    new_facts = await memory_manager.auto_extract_and_learn(
        user_message="Actually, that's wrong, always use UTC timestamps in ISO 8601 format.",
        assistant_response="Understood, I will format timestamps accordingly.",
        user_id="test_user"
    )
    print(f"Auto-extracted {len(new_facts)} new memories/rules from user correction.")
    assert len(new_facts) >= 1
    assert any("correction" in f.get("key", "") or "timestamp" in f.get("content", "").lower() for f in new_facts)

    # Test Memory Agent Tools
    tool_search = await memory_manager.execute_tool("memory__search", {"query": "python"}, user_id="test_user")
    print(f"Executed tool memory__search:\n{tool_search}")
    assert "user_preferred_stack" in tool_search

    tool_remember = await memory_manager.execute_tool(
        "memory__remember",
        {"category": "project", "key": "project_domain", "content": "Autonomous Agent Platform"},
        user_id="test_user"
    )
    print(f"Executed tool memory__remember: {tool_remember}")
    assert "Autonomous Agent Platform" in tool_remember

    # -------------------------------------------------------------
    # 2. Test MarketplaceManager Operations
    # -------------------------------------------------------------
    print("\n--- 2. Testing MarketplaceManager Operations ---")
    catalog = marketplace_manager.get_catalog()
    assert "mcp" in catalog and "plugins" in catalog and "skills" in catalog
    print(f"Catalog loaded: {len(catalog['mcp'])} MCPs, {len(catalog['plugins'])} Plugins, {len(catalog['skills'])} Skills")

    # Install a test Skill
    skill_test = await marketplace_manager.install_skill(
        skill_id="test_dev_skill",
        markdown_content="""---
name: Test Developer
description: Skill for automated tests
triggers: test, testdev
---
Always verify code before responding.
"""
    )
    print(f"Installed Skill: {skill_test}")
    assert os.path.exists(skill_test["path"])

    # Install a test Plugin
    plugin_test = await marketplace_manager.install_plugin(
        plugin_name="test_math_helper",
        code_content="""from plugins.base import BasePlugin

class TestMathHelperPlugin(BasePlugin):
    name = "test_math_helper"
    description = "Test plugin"
    version = "1.0.0"

    def register_tools(self):
        self.add_tool(
            name="multiply_ten",
            description="Multiplies number by 10",
            parameters={"type": "object", "properties": {"n": {"type": "number"}}, "required": ["n"]},
            handler=self.mult
        )

    def mult(self, n: float) -> float:
        return n * 10
"""
    )
    print(f"Installed Plugin: {plugin_test}")
    assert os.path.exists(plugin_test["path"])

    # Test Uninstall
    uninstalled_skill = await marketplace_manager.uninstall_package("skill", "test_dev_skill")
    assert not os.path.exists(skill_test["path"])
    print(f"Uninstalled Skill: {uninstalled_skill}")

    uninstalled_plugin = await marketplace_manager.uninstall_package("plugin", "test_math_helper")
    assert not os.path.exists(plugin_test["path"])
    print(f"Uninstalled Plugin: {uninstalled_plugin}")

    # -------------------------------------------------------------
    # 3. Test HTTP Endpoints
    # -------------------------------------------------------------
    print("\n--- 3. Testing HTTP API Endpoints ---")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/info
        info_resp = await client.get("/api/info")
        assert info_resp.status_code == 200
        info = info_resp.json()
        print(f"API Info: Model={info['model']}, Memories={info['memories_count']}, MCP tools={info['mcp_tools_count']}")

        # GET /api/marketplace/catalog
        cat_resp = await client.get("/api/marketplace/catalog")
        assert cat_resp.status_code == 200
        assert "filesystem" in [m["id"] for m in cat_resp.json()["mcp"]]
        print("GET /api/marketplace/catalog: verified curated catalog")

        # GET /api/memory
        mem_resp = await client.get("/api/memory")
        assert mem_resp.status_code == 200
        mems = mem_resp.json()["memories"]
        print(f"GET /api/memory: Found {len(mems)} total memories")

        # POST /api/memory
        post_mem = await client.post("/api/memory", json={
            "category": "fact",
            "key": "api_test_fact",
            "content": "API memory integration works seamlessly."
        })
        assert post_mem.status_code == 200
        created_mem = post_mem.json()["memory"]
        print(f"POST /api/memory: Created memory ID {created_mem['id']}")

        # DELETE /api/memory/{id}
        del_resp = await client.delete(f"/api/memory/{created_mem['id']}")
        assert del_resp.status_code == 200
        print(f"DELETE /api/memory/{created_mem['id']}: Success")

    from api.routes import get_agent
    await get_agent().mcp.shutdown()
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL MARKETPLACE AND MEMORY TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
