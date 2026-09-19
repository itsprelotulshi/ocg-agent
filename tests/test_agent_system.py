import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agent import OcgAgent
from core.types import AgentRunContext
from mcp_client.manager import MCPManager
from plugins.manager import PluginManager
from skills.manager import SkillManager
from database.repository import db_repo
from auth.supabase import supabase_auth

async def run_tests():
    print("=== 1. Testing Skill Manager ===")
    skills = SkillManager("skills/data")
    print(f"Loaded {len(skills.skills)} skills: {list(skills.skills.keys())}")
    assert len(skills.skills) >= 3, "Expected at least 3 skills loaded"

    detected = skills.detect_relevant_skills("Can you review the system architecture and refactor this design?")
    print(f"Detected skills for query: {detected}")
    assert "code_architect" in detected, "Expected 'code_architect' to be detected"

    print("\n=== 2. Testing Plugin Manager ===")
    plugins = PluginManager()
    plugin_tools = plugins.get_all_tools()
    print(f"Loaded {len(plugins.plugins)} plugins with {len(plugin_tools)} tools")
    tool_names = [t["function"]["name"] for t in plugin_tools]
    print(f"Plugin tools: {tool_names}")
    assert "plugin__system_tools__calculator" in tool_names, "Expected calculator tool"

    calc_res = await plugins.execute_tool("call_calc", "plugin__system_tools__calculator", {"expression": "100 * 4 + 2"})
    print(f"Calculator result: {calc_res.content}")
    assert "402" in calc_res.content, "Expected 402 from calculator"

    print("\n=== 3. Testing MCP Manager ===")
    mcp = MCPManager("mcp_servers.json")
    await mcp.initialize()
    mcp_tools = mcp.get_all_tools()
    print(f"Discovered {len(mcp_tools)} MCP tools:")
    for t in mcp_tools:
        print(f"  - {t['function']['name']}")
    assert len(mcp_tools) > 0, "Expected at least 1 MCP tool"

    mcp_res = await mcp.execute_tool("call_time", "mcp__utilities__get_system_time", {})
    print(f"MCP execution output: {mcp_res.content}")
    assert "Current UTC Time" in mcp_res.content, "Expected system time in response"

    print("\n=== 4. Testing Supabase Auth & Repository ===")
    session = await db_repo.create_session("test_user_1", "Test Session")
    print(f"Created session: {session['id']} (Title: {session['title']})")
    assert session["id"] is not None

    msg = await db_repo.save_message(
        session_id=session["id"],
        user_id="test_user_1",
        role="user",
        content="Hello Ocg Agent!"
    )
    print(f"Saved message: {msg['content']}")
    history = await db_repo.get_messages(session["id"], "test_user_1")
    assert len(history) == 1, "Expected 1 message in history"

    print("\n=== 5. Testing Ocg Agent ReAct Execution ===")
    agent = OcgAgent(mcp_manager=mcp, plugin_manager=plugins, skill_manager=skills)
    ctx = AgentRunContext(user_id="test_user_1", session_id=session["id"])

    response = await agent.run("What time is it right now? Please check with your MCP tool.", context=ctx)
    print(f"Agent Response Content:\n{response.content}")
    print(f"Executed Tools Count: {len(response.tool_executions)}")
    assert len(response.tool_executions) > 0, "Expected tool execution"

    print("\n=== 6. Clean Up ===")
    await mcp.shutdown()
    print("ALL TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    asyncio.run(run_tests())
