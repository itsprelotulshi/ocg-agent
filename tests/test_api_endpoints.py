import asyncio
import os
import sys
import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

async def test_api():
    print("Testing FastAPI app endpoints with ASGITransport...")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Info endpoint
        info_resp = await client.get("/api/info")
        print(f"GET /api/info: {info_resp.status_code}")
        assert info_resp.status_code == 200
        info_data = info_resp.json()
        print(f"Model: {info_data['model']}")
        print(f"MCP tools count: {info_data['mcp_tools_count']}")
        print(f"Plugin tools count: {info_data['plugin_tools_count']}")
        print(f"Skills count: {info_data['skills_count']}")
        assert info_data["model"] is not None


        # 2. Skills endpoint
        skills_resp = await client.get("/api/skills")
        assert skills_resp.status_code == 200
        skills_data = skills_resp.json()
        print(f"GET /api/skills: Found {len(skills_data['skills'])} skills")

        # 3. Plugins endpoint
        plugins_resp = await client.get("/api/plugins")
        assert plugins_resp.status_code == 200
        plugins_data = plugins_resp.json()
        print(f"GET /api/plugins: Found {len(plugins_data['plugins'])} plugins")

        # 4. MCP Status endpoint
        mcp_resp = await client.get("/api/mcp/status")
        assert mcp_resp.status_code == 200
        mcp_data = mcp_resp.json()
        print(f"GET /api/mcp/status: {mcp_data['total_tools']} tools across {len(mcp_data['servers'])} servers")

        # 5. Create Session
        sess_resp = await client.post("/api/sessions", json={"title": "Web Test Conversation"})
        assert sess_resp.status_code == 200
        session = sess_resp.json()["session"]
        print(f"POST /api/sessions: Created {session['id']}")

        # 6. Chat Endpoint
        chat_resp = await client.post("/api/chat", json={
            "message": "Calculate 45 * 2 using your plugin",
            "session_id": session["id"],
            "stream": False
        })
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()
        print(f"POST /api/chat: Response received:\n{chat_data['content']}")

        # 7. Index HTML
        html_resp = await client.get("/")
        assert "<title>" in html_resp.text

        print("GET /: Static HTML served successfully")

    from api.routes import get_agent
    await get_agent().mcp.shutdown()
    print("\nALL API ENDPOINTS TESTED AND VERIFIED! [OK]")

if __name__ == "__main__":
    asyncio.run(test_api())
