import os
import json
import shutil
import asyncio
import logging
import subprocess
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger("ocg_agent.marketplace")

# Predefined curated catalog of community MCPs, Plugins, and Skills
CURATED_CATALOG = {
    "mcp": [
        {
            "id": "filesystem",
            "name": "Filesystem MCP",
            "description": "Secure file system access to read, write, list, and search files inside workspace directories.",
            "category": "System",
            "author": "Model Context Protocol",
            "icon": "📁",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "d:/agy_projects"]
            }
        },
        {
            "id": "sqlite",
            "name": "SQLite MCP",
            "description": "Direct read and write inspection for local SQLite relational database files with schema exploration.",
            "category": "Database",
            "author": "Model Context Protocol",
            "icon": "🗄️",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "data/agent.db"]
            }
        },
        {
            "id": "github",
            "name": "GitHub Official MCP",
            "description": "Manage GitHub repos, inspect issues, list pull requests, and commit files via official MCP server.",
            "category": "Developer Tools",
            "author": "Model Context Protocol",
            "icon": "🐙",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""}
            }
        },
        {
            "id": "brave-search",
            "name": "Brave Web Search MCP",
            "description": "Real-time web searches and news summaries powered by Brave Search API.",
            "category": "Web Search",
            "author": "Brave / MCP",
            "icon": "🔍",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {"BRAVE_API_KEY": ""}
            }
        },
        {
            "id": "fetch",
            "name": "Fetch & Web Content MCP",
            "description": "Converts HTML web pages and API responses into clean markdown for fast context ingestion.",
            "category": "Web Tools",
            "author": "Model Context Protocol",
            "icon": "🌐",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-fetch"]
            }
        },
        {
            "id": "puppeteer",
            "name": "Puppeteer Browser Automation MCP",
            "description": "Headless browser automation to navigate pages, capture screenshots, and click elements.",
            "category": "Automation",
            "author": "Model Context Protocol",
            "icon": "🤖",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
            }
        }
    ],
    "plugins": [
        {
            "id": "git_tools",
            "name": "Git Repository Assistant",
            "description": "Inspect git status, branch information, latest commit logs, and git diff summaries.",
            "category": "Dev Tools",
            "author": "Community",
            "icon": "🌿",
            "filename": "git_tools.py",
            "code": '''import subprocess
from plugins.base import BasePlugin

class GitToolsPlugin(BasePlugin):
    name = "git_tools"
    description = "Inspect git status, branch, and commit logs directly."
    version = "1.0.0"

    def register_tools(self):
        self.add_tool(
            name="git_status",
            description="Run git status to see modified, untracked, and staged files.",
            parameters={"type": "object", "properties": {}},
            handler=self.git_status
        )
        self.add_tool(
            name="git_log",
            description="Show the last N commits from git log.",
            parameters={
                "type": "object",
                "properties": {"limit": {"type": "integer", "description": "Number of commits to show, default 5"}}
            },
            handler=self.git_log
        )

    def git_status(self) -> str:
        try:
            res = subprocess.run(["git", "status", "-s"], capture_output=True, text=True, timeout=10)
            return res.stdout or "Working directory clean."
        except Exception as e:
            return f"Error executing git status: {e}"

    def git_log(self, limit: int = 5) -> str:
        try:
            res = subprocess.run(["git", "log", f"-n{limit}", "--oneline"], capture_output=True, text=True, timeout=10)
            return res.stdout or "No commits found."
        except Exception as e:
            return f"Error executing git log: {e}"
'''
        },
        {
            "id": "code_analyzer",
            "name": "Python Code Analyzer",
            "description": "Performs fast syntax validation and AST metrics for Python snippets.",
            "category": "Code Quality",
            "author": "Community",
            "icon": "🔬",
            "filename": "code_analyzer.py",
            "code": '''import ast
from plugins.base import BasePlugin

class CodeAnalyzerPlugin(BasePlugin):
    name = "code_analyzer"
    description = "Analyzes Python code for syntax errors and structural metrics."
    version = "1.0.0"

    def register_tools(self):
        self.add_tool(
            name="validate_python_syntax",
            description="Check if a Python code snippet is syntactically valid and report node counts.",
            parameters={
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Python code snippet"}},
                "required": ["code"]
            },
            handler=self.validate_syntax
        )

    def validate_syntax(self, code: str) -> str:
        try:
            parsed = ast.parse(code)
            node_count = sum(1 for _ in ast.walk(parsed))
            functions = [n.name for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef)]
            classes = [n.name for n in ast.walk(parsed) if isinstance(n, ast.ClassDef)]
            return f"Syntax Valid! Nodes: {node_count}, Classes: {classes}, Functions: {functions}"
        except SyntaxError as se:
            return f"Syntax Error on line {se.lineno}: {se.msg}"
        except Exception as e:
            return f"Analysis error: {e}"
'''
        }
    ],
    "skills": [
        {
            "id": "fullstack_engineer",
            "name": "Fullstack Software Engineer",
            "description": "Architects modern fullstack applications with FastAPI, PostgreSQL, Vue/React, and REST/SSE APIs.",
            "category": "Engineering",
            "author": "Community",
            "icon": "⚡",
            "triggers": ["fullstack", "architecture", "api design", "database schema"],
            "instructions": """---
name: Fullstack Engineer
description: Expert fullstack application designer
triggers: fullstack, architecture, api design, database schema
---
When tasked with software development:
1. Always prioritize modular, scalable, clean architectures with separation of concerns.
2. For backend APIs, write strongly typed schemas (Pydantic / TypeScript).
3. Ensure robust error handling and database index optimization.
4. Provide idiomatic and production-ready code rather than minimal toy snippets.
"""
        },
        {
            "id": "security_auditor",
            "name": "Security & Pentesting Auditor",
            "description": "Identifies OWASP vulnerabilities, SQL injection risks, RCE threats, and credential leakage.",
            "category": "Security",
            "author": "Community",
            "icon": "🛡️",
            "triggers": ["security", "audit", "vulnerability", "auth check", "owasp"],
            "instructions": """---
name: Security Auditor
description: Hardens systems and identifies vulnerabilities
triggers: security, audit, vulnerability, auth check, owasp
---
When reviewing code or infrastructure:
1. Thoroughly verify authentication and authorization checks (e.g. Supabase RLS, JWT validation).
2. Scan for untrusted input injection (SQLi, XSS, SSRF, command injection).
3. Warn if secrets or private keys are hardcoded in source files.
4. Recommend least-privilege security postures and cryptographic best practices.
"""
        },
        {
            "id": "devops_cloud",
            "name": "DevOps & Cloud Architect",
            "description": "Designs Docker containers, CI/CD pipelines, Kubernetes manifests, and cloud deployment flows.",
            "category": "DevOps",
            "author": "Community",
            "icon": "☁️",
            "triggers": ["docker", "deploy", "ci/cd", "kubernetes", "cloud"],
            "instructions": """---
name: DevOps & Cloud Architect
description: Cloud infrastructure, Docker containerization and CI/CD expert
triggers: docker, deploy, ci/cd, kubernetes, cloud
---
When handling deployment, containers, or CI/CD:
1. Create lightweight, multi-stage Dockerfiles with non-root runtime users.
2. Automate healthchecks, logging, and environment variable configuration.
3. Structure reproducible GitHub Actions or CI workflows.
"""
        }
    ]
}

class MarketplaceManager:
    """
    Manages package installation from GitHub repositories, direct URLs,
    curated marketplace catalogs, and custom configurations.
    """

    def __init__(self, data_file: str = "data/installed_marketplace.json"):
        self.data_file = data_file
        self.installed_packages: Dict[str, Any] = self._load_installed()

    def _load_installed(self) -> Dict[str, Any]:
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.data_file):
            return {"mcp": {}, "plugins": {}, "skills": {}}
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load installed marketplace data: {e}")
            return {"mcp": {}, "plugins": {}, "skills": {}}

    def _save_installed(self):
        os.makedirs("data", exist_ok=True)
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.installed_packages, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save installed marketplace data: {e}")

    def get_catalog(self) -> Dict[str, Any]:
        return CURATED_CATALOG

    def get_installed(self) -> Dict[str, Any]:
        return self.installed_packages

    # ==============================================================================
    # MCP Server Installation
    # ==============================================================================

    async def install_mcp_from_config(
        self,
        server_name: str,
        config: Dict[str, Any],
        mcp_manager: Any
    ) -> Dict[str, Any]:
        """Install an MCP server directly by stdio or SSE config."""
        mcp_cfg_path = "mcp_servers.json"
        data = {}
        if os.path.exists(mcp_cfg_path):
            try:
                with open(mcp_cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        if "mcpServers" not in data:
            data["mcpServers"] = {}

        data["mcpServers"][server_name] = config

        with open(mcp_cfg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Record metadata
        self.installed_packages["mcp"][server_name] = {
            "name": server_name,
            "type": "mcp",
            "source": "config",
            "config": config,
            "installed_at": str(asyncio.get_event_loop().time())
        }
        self._save_installed()

        # Reload MCP
        await mcp_manager.shutdown()
        await mcp_manager.initialize()

        return {"status": "success", "server_name": server_name, "tools": mcp_manager.get_status()}

    async def install_mcp_from_github(
        self,
        repo_url: str,
        server_name: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        mcp_manager: Any = None
    ) -> Dict[str, Any]:
        """
        Clone an MCP server from GitHub into mcp_servers/installed/<name>
        and auto-detect setup requirements.
        """
        clean_url = repo_url.strip()
        if clean_url.endswith("/"):
            clean_url = clean_url[:-1]

        repo_name = clean_url.split("/")[-1].replace(".git", "")
        name = server_name or repo_name.lower().replace("-", "_")

        target_dir = os.path.join("mcp_servers", "installed", name)
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)

        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        # Clone repository
        logger.info(f"Cloning MCP server from {clean_url} into {target_dir}...")
        clone_cmd = ["git", "clone", "--depth", "1", clean_url, target_dir]
        proc = await asyncio.create_subprocess_exec(
            *clone_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Git clone failed: {stderr.decode()}")

        # Auto-configure command if not explicitly given
        final_cmd = command
        final_args = args or []
        req_txt = os.path.join(target_dir, "requirements.txt")
        pkg_json = os.path.join(target_dir, "package.json")

        if not final_cmd:
            if os.path.exists(req_txt):
                # Install pip dependencies
                logger.info(f"Installing Python dependencies from {req_txt}...")
                import sys
                pip_proc = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "pip", "install", "-r", req_txt,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await pip_proc.communicate()

                # Look for server entrypoint
                candidates = ["server.py", "main.py", f"{name}.py", "run.py"]
                entry = "main.py"
                for c in candidates:
                    if os.path.exists(os.path.join(target_dir, c)):
                        entry = c
                        break
                final_cmd = "python"
                final_args = [f"mcp_servers/installed/{name}/{entry}"]

            elif os.path.exists(pkg_json):
                # Run npm install
                logger.info("Installing Node dependencies...")
                npm_proc = await asyncio.create_subprocess_exec(
                    "npm", "install", "--production",
                    cwd=target_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await npm_proc.communicate()
                final_cmd = "node"
                final_args = [f"mcp_servers/installed/{name}/index.js"]
            else:
                final_cmd = "python"
                final_args = [f"mcp_servers/installed/{name}/main.py"]

        config = {
            "command": final_cmd,
            "args": final_args,
            "env": env or {}
        }

        return await self.install_mcp_from_config(name, config, mcp_manager)

    # ==============================================================================
    # Plugin Installation
    # ==============================================================================

    async def install_plugin(
        self,
        plugin_name: str,
        code_content: Optional[str] = None,
        source_url: Optional[str] = None,
        plugin_manager: Any = None
    ) -> Dict[str, Any]:
        """Install a custom Python plugin from source URL or raw code."""
        os.makedirs("plugins/installed", exist_ok=True)
        filename = f"{plugin_name.lower().replace('-', '_')}.py"
        target_path = os.path.join("plugins", "installed", filename)

        if source_url:
            raw_url = source_url.strip()
            # Convert github blob to raw if needed
            if "github.com" in raw_url and "/blob/" in raw_url:
                raw_url = raw_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                res = await client.get(raw_url)
                if res.status_code != 200:
                    raise RuntimeError(f"Failed to download plugin from {raw_url} (HTTP {res.status_code})")
                code_content = res.text

        if not code_content:
            raise ValueError("No plugin code provided.")

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(code_content)

        # Reload plugins
        if plugin_manager:
            plugin_manager.reload_all()

        self.installed_packages["plugins"][plugin_name] = {
            "name": plugin_name,
            "type": "plugin",
            "file": target_path,
            "source": source_url or "custom_code"
        }
        self._save_installed()

        return {"status": "success", "plugin_name": plugin_name, "path": target_path}

    # ==============================================================================
    # Skill Installation
    # ==============================================================================

    async def install_skill(
        self,
        skill_id: str,
        markdown_content: Optional[str] = None,
        source_url: Optional[str] = None,
        skill_manager: Any = None
    ) -> Dict[str, Any]:
        """Install a custom markdown skill from URL or raw text."""
        os.makedirs("skills/data", exist_ok=True)
        clean_id = skill_id.lower().replace(" ", "_").replace("-", "_")
        target_path = os.path.join("skills", "data", f"{clean_id}.md")

        if source_url:
            raw_url = source_url.strip()
            if "github.com" in raw_url and "/blob/" in raw_url:
                raw_url = raw_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                res = await client.get(raw_url)
                if res.status_code != 200:
                    raise RuntimeError(f"Failed to download skill from {raw_url} (HTTP {res.status_code})")
                markdown_content = res.text

        if not markdown_content:
            raise ValueError("No skill markdown content provided.")

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Reload skills
        if skill_manager:
            skill_manager.load_all()

        self.installed_packages["skills"][clean_id] = {
            "id": clean_id,
            "type": "skill",
            "file": target_path,
            "source": source_url or "custom_markdown"
        }
        self._save_installed()

        return {"status": "success", "skill_id": clean_id, "path": target_path}

    # ==============================================================================
    # Uninstall Package
    # ==============================================================================

    async def uninstall_package(
        self,
        package_type: str,
        package_id: str,
        mcp_manager: Any = None,
        plugin_manager: Any = None,
        skill_manager: Any = None
    ) -> Dict[str, Any]:
        """Uninstall an MCP server, plugin, or skill."""
        if package_type == "mcp":
            mcp_cfg_path = "mcp_servers.json"
            if os.path.exists(mcp_cfg_path):
                with open(mcp_cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "mcpServers" in data and package_id in data["mcpServers"]:
                    del data["mcpServers"][package_id]
                    with open(mcp_cfg_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

            installed_dir = os.path.join("mcp_servers", "installed", package_id)
            if os.path.exists(installed_dir):
                shutil.rmtree(installed_dir, ignore_errors=True)

            self.installed_packages["mcp"].pop(package_id, None)
            self._save_installed()

            if mcp_manager:
                await mcp_manager.shutdown()
                await mcp_manager.initialize()

        elif package_type == "plugin":
            filename = f"{package_id.lower().replace('-', '_')}.py"
            target_path = os.path.join("plugins", "installed", filename)
            if os.path.exists(target_path):
                os.remove(target_path)

            self.installed_packages["plugins"].pop(package_id, None)
            self._save_installed()

            if plugin_manager:
                plugin_manager.reload_all()

        elif package_type == "skill":
            clean_id = package_id.lower().replace(" ", "_").replace("-", "_")
            target_path = os.path.join("skills", "data", f"{clean_id}.md")
            if os.path.exists(target_path):
                os.remove(target_path)

            self.installed_packages["skills"].pop(clean_id, None)
            self._save_installed()

            if skill_manager:
                skill_manager.load_all()

        return {"status": "success", "package_type": package_type, "package_id": package_id}

# Global instance
marketplace_manager = MarketplaceManager()
