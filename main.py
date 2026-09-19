import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from core.agent import OcgAgent
from api.routes import router as api_router, set_agent_instance

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Ocg_agent.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Ocg AI Agent with MCP & Plugins...")
    agent = OcgAgent()
    await agent.initialize()
    set_agent_instance(agent)
    logger.info(f"Agent initialized successfully with model: {settings.LLM_MODEL}")
    yield
    logger.info("Shutting down Ocg Agent and closing MCP server connections...")
    await agent.mcp.shutdown()
    logger.info("Agent shutdown complete.")

app = FastAPI(
    title="Ocg AI Agent",
    description="Autonomous Agent powered by Ocg/Ocg3.8-27B with MCP, Plugins, Skills, and Supabase Auth",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(api_router)

# Mount Static UI Files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
