"""
Curated Catalog of the Top 100 Model Context Protocol (MCP) Servers from GitHub.
Categorized into Databases, Developer Tools, Cloud & DevOps, Search & Web,
Productivity & Notes, Document Processing, and AI & Science.
"""

TOP_100_MCP_SERVERS = [
    # ── 1. Official & Core MCP Servers (1-15) ──
    {
        "id": "filesystem",
        "name": "Filesystem MCP",
        "description": "Secure file system access to read, write, list, and search files inside workspace directories.",
        "category": "System & Files",
        "author": "Model Context Protocol",
        "icon": "📁",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
        }
    },
    {
        "id": "sqlite",
        "name": "SQLite MCP",
        "description": "Direct read and write inspection for local SQLite relational database files with schema exploration.",
        "category": "Databases",
        "author": "Model Context Protocol",
        "icon": "🗄️",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-sqlite", "--db-path", "data/agent.db"]
        }
    },
    {
        "id": "postgres",
        "name": "PostgreSQL MCP",
        "description": "Inspect, query, and manage PostgreSQL databases with schema introspection and query execution.",
        "category": "Databases",
        "author": "Model Context Protocol",
        "icon": "🐘",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
        }
    },
    {
        "id": "github",
        "name": "GitHub Official MCP",
        "description": "Manage GitHub repos, inspect issues, list pull requests, and commit files via official MCP server.",
        "category": "Developer Tools",
        "author": "Model Context Protocol",
        "icon": "🐙",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""}
        }
    },
    {
        "id": "gitlab",
        "name": "GitLab MCP",
        "description": "Interact with GitLab projects, issues, merge requests, branches, and CI/CD pipelines.",
        "category": "Developer Tools",
        "author": "Model Context Protocol",
        "icon": "🦊",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/gitlab",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gitlab"],
            "env": {"GITLAB_PERSONAL_ACCESS_TOKEN": ""}
        }
    },
    {
        "id": "brave-search",
        "name": "Brave Web Search MCP",
        "description": "Real-time web searches and news summaries powered by Brave Search API.",
        "category": "Search & Web",
        "author": "Brave / MCP",
        "icon": "🔍",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
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
        "category": "Search & Web",
        "author": "Model Context Protocol",
        "icon": "🌐",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/fetch",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        }
    },
    {
        "id": "puppeteer",
        "name": "Puppeteer Browser Automation MCP",
        "description": "Headless browser automation to navigate pages, capture screenshots, and click elements.",
        "category": "Search & Web",
        "author": "Model Context Protocol",
        "icon": "🤖",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
        }
    },
    {
        "id": "slack",
        "name": "Slack MCP",
        "description": "Access and post Slack messages, manage channels, and search conversation history.",
        "category": "Productivity & Notes",
        "author": "Model Context Protocol",
        "icon": "💬",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {"SLACK_BOT_TOKEN": "", "SLACK_TEAM_ID": ""}
        }
    },
    {
        "id": "google-maps",
        "name": "Google Maps MCP",
        "description": "Query location coordinates, driving directions, geocoding, and local places via Google Maps.",
        "category": "Search & Web",
        "author": "Model Context Protocol",
        "icon": "🗺️",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-google-maps"],
            "env": {"GOOGLE_MAPS_API_KEY": ""}
        }
    },
    {
        "id": "google-drive",
        "name": "Google Drive MCP",
        "description": "Search, read, and browse documents and spreadsheets stored in Google Drive.",
        "category": "Productivity & Notes",
        "author": "Model Context Protocol",
        "icon": "📄",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-google-drive"]
        }
    },
    {
        "id": "sentry",
        "name": "Sentry Error Tracking MCP",
        "description": "Retrieve application issues, crash stack traces, and production errors from Sentry.io.",
        "category": "Developer Tools",
        "author": "Model Context Protocol",
        "icon": "🚨",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sentry",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-sentry", "--auth-token", ""]
        }
    },
    {
        "id": "memory",
        "name": "Knowledge Graph Memory MCP",
        "description": "Persistent graph-based knowledge and entity relationship memory server.",
        "category": "AI & Science",
        "author": "Model Context Protocol",
        "icon": "🧠",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        }
    },
    {
        "id": "everything",
        "name": "MCP Everything Reference Server",
        "description": "Reference MCP test server implementing prompts, resources, notifications, and all tool capabilities.",
        "category": "Developer Tools",
        "author": "Model Context Protocol",
        "icon": "🧩",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/everything",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-everything"]
        }
    },
    {
        "id": "sequential-thinking",
        "name": "Sequential Thinking MCP",
        "description": "Step-by-step sequential reasoning tool for deep problem decomposition and planning.",
        "category": "AI & Science",
        "author": "Model Context Protocol",
        "icon": "🤔",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
        }
    },

    # ── 2. Databases & Vector Stores (16-32) ──
    {
        "id": "mysql",
        "name": "MySQL MCP Server",
        "description": "Query MySQL databases, list schemas, execute read queries, and inspect table definitions.",
        "category": "Databases",
        "author": "Community",
        "icon": "🐬",
        "source_url": "https://github.com/designcomputer/mysql_mcp_server",
        "config": {
            "command": "npx",
            "args": ["-y", "mysql-mcp-server"]
        }
    },
    {
        "id": "mongodb",
        "name": "MongoDB MCP Server",
        "description": "Connect to MongoDB databases, run aggregation pipelines, and query BSON documents.",
        "category": "Databases",
        "author": "MongoDB",
        "icon": "🍃",
        "source_url": "https://github.com/mongodb-labs/mcp-server-mongodb",
        "config": {
            "command": "npx",
            "args": ["-y", "mongodb-mcp-server"]
        }
    },
    {
        "id": "redis",
        "name": "Redis MCP Server",
        "description": "Read and write Redis keys, hashes, lists, and execute commands with key pattern search.",
        "category": "Databases",
        "author": "Redis",
        "icon": "🔴",
        "source_url": "https://github.com/redis-developer/mcp-redis",
        "config": {
            "command": "npx",
            "args": ["-y", "@redis/mcp-server-redis"]
        }
    },
    {
        "id": "neo4j",
        "name": "Neo4j Graph Database MCP",
        "description": "Execute Cypher graph queries and inspect knowledge node relationships on Neo4j.",
        "category": "Databases",
        "author": "Neo4j",
        "icon": "🕸️",
        "source_url": "https://github.com/neo4j-contrib/mcp-neo4j",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-neo4j"]
        }
    },
    {
        "id": "supabase-mcp",
        "name": "Supabase Management MCP",
        "description": "Manage Supabase tables, migrations, RLS policies, and run Postgres SQL commands.",
        "category": "Databases",
        "author": "Supabase Community",
        "icon": "⚡",
        "source_url": "https://github.com/supabase-community/supabase-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "supabase-mcp-server"],
            "env": {"SUPABASE_ACCESS_TOKEN": ""}
        }
    },
    {
        "id": "duckdb",
        "name": "DuckDB Analytics MCP",
        "description": "Fast embedded analytical SQL database for querying Parquet files, CSVs, and local data.",
        "category": "Databases",
        "author": "DuckDB Labs",
        "icon": "🦆",
        "source_url": "https://github.com/duckdb/duckdb-mcp",
        "config": {
            "command": "uvx",
            "args": ["duckdb-mcp-server"]
        }
    },
    {
        "id": "clickhouse",
        "name": "ClickHouse Analytical MCP",
        "description": "Fast open-source column-oriented database for real-time analytical reporting and logs.",
        "category": "Databases",
        "author": "ClickHouse",
        "icon": "📊",
        "source_url": "https://github.com/ClickHouse/clickhouse-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "@clickhouse/mcp-server"]
        }
    },
    {
        "id": "snowflake",
        "name": "Snowflake Warehouse MCP",
        "description": "Execute analytical queries and explore schemas inside Snowflake Cloud Data Warehouses.",
        "category": "Databases",
        "author": "Snowflake Community",
        "icon": "❄️",
        "source_url": "https://github.com/snowflakedb/snowflake-mcp",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-snowflake"]
        }
    },
    {
        "id": "bigquery",
        "name": "Google BigQuery MCP",
        "description": "Query serverless data warehouses and analyze petabyte-scale datasets on Google Cloud.",
        "category": "Databases",
        "author": "Google Cloud Community",
        "icon": "🔎",
        "source_url": "https://github.com/googlecloudplatform/bigquery-mcp",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-bigquery"]
        }
    },
    {
        "id": "qdrant",
        "name": "Qdrant Vector Database MCP",
        "description": "Vector search and similarity retrieval for embeddings and document RAG pipelines.",
        "category": "Databases",
        "author": "Qdrant",
        "icon": "🎯",
        "source_url": "https://github.com/qdrant/mcp-server-qdrant",
        "config": {
            "command": "uvx",
            "args": ["qdrant-mcp"]
        }
    },
    {
        "id": "chroma",
        "name": "ChromaDB Vector Store MCP",
        "description": "Open-source embedding database for AI applications, semantic search, and document store.",
        "category": "Databases",
        "author": "Chroma",
        "icon": "🌈",
        "source_url": "https://github.com/chroma-core/chroma-mcp",
        "config": {
            "command": "uvx",
            "args": ["chroma-mcp-server"]
        }
    },
    {
        "id": "weaviate",
        "name": "Weaviate Vector Search MCP",
        "description": "Hybrid and vector search across multimodal objects using Weaviate GraphQL and REST APIs.",
        "category": "Databases",
        "author": "Weaviate",
        "icon": "🔮",
        "source_url": "https://github.com/weaviate/weaviate-mcp",
        "config": {
            "command": "uvx",
            "args": ["weaviate-mcp"]
        }
    },
    {
        "id": "pinecone",
        "name": "Pinecone Managed Vector MCP",
        "description": "Index, query, and manage vector embeddings on Pinecone serverless vector infrastructure.",
        "category": "Databases",
        "author": "Pinecone",
        "icon": "🌲",
        "source_url": "https://github.com/pinecone-io/pinecone-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "@pinecone-database/mcp"]
        }
    },
    {
        "id": "elasticsearch",
        "name": "Elasticsearch & Kibana MCP",
        "description": "Perform full-text search, aggregation queries, and index management on Elasticsearch.",
        "category": "Databases",
        "author": "Elastic",
        "icon": "🟡",
        "source_url": "https://github.com/elastic/elasticsearch-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "elasticsearch-mcp-server"]
        }
    },
    {
        "id": "surrealdb",
        "name": "SurrealDB Multi-Model MCP",
        "description": "Document, graph, and relational queries combined in SurrealQL for real-time web apps.",
        "category": "Databases",
        "author": "SurrealDB",
        "icon": "🌀",
        "source_url": "https://github.com/surrealdb/surrealdb-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "surrealdb-mcp"]
        }
    },
    {
        "id": "timescaledb",
        "name": "TimescaleDB Time-Series MCP",
        "description": "Query high-frequency metrics, financial ticks, and IoT telemetry data on PostgreSQL.",
        "category": "Databases",
        "author": "Timescale",
        "icon": "⏱️",
        "source_url": "https://github.com/timescale/timescaledb-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "timescaledb-mcp"]
        }
    },
    {
        "id": "meilisearch",
        "name": "Meilisearch Fast Search MCP",
        "description": "Ultra-fast typo-tolerant full-text search engine for instant application queries.",
        "category": "Databases",
        "author": "Meilisearch",
        "icon": "⚡",
        "source_url": "https://github.com/meilisearch/meilisearch-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "meilisearch-mcp"]
        }
    },

    # ── 3. Developer Tools, Containers & Cloud (33-50) ──
    {
        "id": "docker",
        "name": "Docker Management MCP",
        "description": "Manage Docker containers, list images, inspect volume mounts, and view container logs.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🐳",
        "source_url": "https://github.com/ckreiling/mcp-server-docker",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-docker"]
        }
    },
    {
        "id": "kubernetes",
        "name": "Kubernetes Cluster MCP",
        "description": "Inspect pods, deployments, services, namespaces, and cluster resources via kubectl.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "☸️",
        "source_url": "https://github.com/strowk/mcp-k8s-go",
        "config": {
            "command": "npx",
            "args": ["-y", "kubernetes-mcp-server"]
        }
    },
    {
        "id": "git",
        "name": "Local Git CLI MCP",
        "description": "Inspect git status, commit history, diffs, blame, and branch management locally.",
        "category": "Developer Tools",
        "author": "Model Context Protocol",
        "icon": "🌿",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/git",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-git"]
        }
    },
    {
        "id": "terraform",
        "name": "Terraform IaC MCP",
        "description": "Validate, plan, inspect state files, and analyze Terraform Infrastructure as Code modules.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🏗️",
        "source_url": "https://github.com/hashicorp/terraform-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "terraform-mcp-server"]
        }
    },
    {
        "id": "ansible",
        "name": "Ansible Automation MCP",
        "description": "Inspect Ansible playbooks, inventory hosts, roles, and validate automation syntax.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🅰️",
        "source_url": "https://github.com/ansible-community/ansible-mcp",
        "config": {
            "command": "uvx",
            "args": ["ansible-mcp"]
        }
    },
    {
        "id": "aws",
        "name": "AWS Cloud Services MCP",
        "description": "Query AWS S3 buckets, EC2 instances, Lambda functions, and CloudWatch metrics.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "☁️",
        "source_url": "https://github.com/aws/mcp-server-aws",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-aws"]
        }
    },
    {
        "id": "azure",
        "name": "Azure Cloud Services MCP",
        "description": "Azure cloud resource management for resource groups, virtual machines, and blob storage.",
        "category": "Developer Tools",
        "author": "Microsoft Community",
        "icon": "🔷",
        "source_url": "https://github.com/Azure/azure-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "@azure/mcp-server"]
        }
    },
    {
        "id": "cloudflare",
        "name": "Cloudflare Edge MCP",
        "description": "Manage Cloudflare DNS records, Workers scripts, KV namespaces, and security zone rules.",
        "category": "Developer Tools",
        "author": "Cloudflare Community",
        "icon": "🟧",
        "source_url": "https://github.com/cloudflare/mcp-server-cloudflare",
        "config": {
            "command": "npx",
            "args": ["-y", "cloudflare-mcp-server"],
            "env": {"CLOUDFLARE_API_TOKEN": ""}
        }
    },
    {
        "id": "vercel",
        "name": "Vercel Platform MCP",
        "description": "Inspect Vercel deployments, production domains, environment variables, and build logs.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "▲",
        "source_url": "https://github.com/vercel/mcp-vercel",
        "config": {
            "command": "npx",
            "args": ["-y", "vercel-mcp"],
            "env": {"VERCEL_API_TOKEN": ""}
        }
    },
    {
        "id": "datadog",
        "name": "Datadog Monitoring MCP",
        "description": "Query system metrics, APM performance traces, monitors, and error logs in Datadog.",
        "category": "Developer Tools",
        "author": "Datadog Community",
        "icon": "🐶",
        "source_url": "https://github.com/datadog/datadog-mcp",
        "config": {
            "command": "uvx",
            "args": ["datadog-mcp"]
        }
    },
    {
        "id": "grafana",
        "name": "Grafana & Prometheus MCP",
        "description": "Search Grafana dashboards, inspect metrics data sources, and query Prometheus alerts.",
        "category": "Developer Tools",
        "author": "Grafana Community",
        "icon": "📈",
        "source_url": "https://github.com/grafana/grafana-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "grafana-mcp-server"]
        }
    },
    {
        "id": "linear",
        "name": "Linear Issue Tracker MCP",
        "description": "Read, create, and manage issues, project cycles, and roadmap milestones on Linear.",
        "category": "Developer Tools",
        "author": "Linear Community",
        "icon": "📐",
        "source_url": "https://github.com/linear/mcp-server-linear",
        "config": {
            "command": "npx",
            "args": ["-y", "linear-mcp-server"],
            "env": {"LINEAR_API_KEY": ""}
        }
    },
    {
        "id": "jira",
        "name": "Atlassian Jira MCP",
        "description": "Query Jira issues, active sprints, backlogs, transitions, and board components.",
        "category": "Developer Tools",
        "author": "Atlassian Community",
        "icon": "🎫",
        "source_url": "https://github.com/atlassian/jira-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "jira-mcp-server"]
        }
    },
    {
        "id": "npm",
        "name": "NPM Registry Explorer MCP",
        "description": "Search Node.js packages, inspect registry versions, dependencies, and bundle sizes.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "📦",
        "source_url": "https://github.com/npm/npm-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "npm-mcp-server"]
        }
    },
    {
        "id": "pypi",
        "name": "PyPI Package Explorer MCP",
        "description": "Search Python packages, release histories, documentation links, and dependencies.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🐍",
        "source_url": "https://github.com/pypa/pypi-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["pypi-mcp-server"]
        }
    },
    {
        "id": "curl-http",
        "name": "cURL & REST Client MCP",
        "description": "Robust HTTP/REST/GraphQL client to perform API requests with headers and payload formatting.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🔄",
        "source_url": "https://github.com/curl/mcp-server-curl",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-curl"]
        }
    },
    {
        "id": "openapi",
        "name": "OpenAPI Client MCP",
        "description": "Explore, validate, and dynamically execute requests against any OpenAPI v3 specification.",
        "category": "Developer Tools",
        "author": "Model Context Protocol",
        "icon": "📖",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/openapi",
        "config": {
            "command": "npx",
            "args": ["-y", "@mcp/openapi-server"]
        }
    },
    {
        "id": "code-runner",
        "name": "Code Interpreter & Runner MCP",
        "description": "Sandboxed Python and Node.js code execution for computation and algorithm evaluation.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "💻",
        "source_url": "https://github.com/mcp-tools/mcp-code-runner",
        "config": {
            "command": "uvx",
            "args": ["mcp-code-runner"]
        }
    },

    # ── 4. Search, Web & Scraping (51-65) ──
    {
        "id": "tavily",
        "name": "Tavily AI Search MCP",
        "description": "AI-optimized web search engine returning filtered, high-relevance search context.",
        "category": "Search & Web",
        "author": "Tavily",
        "icon": "🦅",
        "source_url": "https://github.com/tavily-ai/tavily-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "tavily-mcp"],
            "env": {"TAVILY_API_KEY": ""}
        }
    },
    {
        "id": "duckduckgo",
        "name": "DuckDuckGo Free Search MCP",
        "description": "Free, privacy-respecting web and news search without API key requirements.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "🦆",
        "source_url": "https://github.com/mcp-tools/duckduckgo-mcp",
        "config": {
            "command": "uvx",
            "args": ["duckduckgo-mcp"]
        }
    },
    {
        "id": "serpapi",
        "name": "SerpApi Multi-Engine Search MCP",
        "description": "Scrape search engine results from Google, Bing, Yahoo, and Baidu with rich snippets.",
        "category": "Search & Web",
        "author": "SerpApi",
        "icon": "🔎",
        "source_url": "https://github.com/serpapi/serpapi-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "serpapi-mcp-server"],
            "env": {"SERPAPI_API_KEY": ""}
        }
    },
    {
        "id": "firecrawl",
        "name": "Firecrawl Web Crawler MCP",
        "description": "Advanced web scraper that crawls entire websites and turns pages into clean markdown.",
        "category": "Search & Web",
        "author": "Mendable / Firecrawl",
        "icon": "🔥",
        "source_url": "https://github.com/mendableai/firecrawl-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "firecrawl-mcp"],
            "env": {"FIRECRAWL_API_KEY": ""}
        }
    },
    {
        "id": "playwright",
        "name": "Playwright Browser Automation MCP",
        "description": "End-to-end browser automation and testing with Playwright supporting Chromium and Firefox.",
        "category": "Search & Web",
        "author": "ExecuteAutomation",
        "icon": "🎭",
        "source_url": "https://github.com/executeautomation/mcp-playwright",
        "config": {
            "command": "npx",
            "args": ["-y", "@executeautomation/playwright-mcp-server"]
        }
    },
    {
        "id": "jina-reader",
        "name": "Jina AI Web Reader MCP",
        "description": "Neural web reader and searcher converting any URL into clean LLM-ready markdown.",
        "category": "Search & Web",
        "author": "Jina AI",
        "icon": "⚡",
        "source_url": "https://github.com/jina-ai/jina-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "jina-mcp-server"]
        }
    },
    {
        "id": "browserless",
        "name": "Browserless Cloud Headless MCP",
        "description": "Cloud-hosted headless Chrome for web scraping, PDF generation, and automation.",
        "category": "Search & Web",
        "author": "Browserless",
        "icon": "🖥️",
        "source_url": "https://github.com/browserless/mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "browserless-mcp"]
        }
    },
    {
        "id": "wikipedia",
        "name": "Wikipedia Knowledge MCP",
        "description": "Search and retrieve comprehensive encyclopedia summaries and section content from Wikipedia.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "📚",
        "source_url": "https://github.com/mcp-tools/mcp-server-wikipedia",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-wikipedia"]
        }
    },
    {
        "id": "arxiv",
        "name": "arXiv Research Papers MCP",
        "description": "Search and read scientific research papers, abstracts, and authors on arXiv.org.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "📑",
        "source_url": "https://github.com/mcp-tools/mcp-server-arxiv",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-arxiv"]
        }
    },
    {
        "id": "semantic-scholar",
        "name": "Semantic Scholar Science MCP",
        "description": "Academic paper search, citation graphs, and author profiles via Semantic Scholar.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "🎓",
        "source_url": "https://github.com/mcp-tools/semantic-scholar-mcp",
        "config": {
            "command": "uvx",
            "args": ["semantic-scholar-mcp"]
        }
    },
    {
        "id": "youtube-transcript",
        "name": "YouTube Transcript MCP",
        "description": "Extract full transcripts and captions from YouTube video URLs for instant summarization.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "▶️",
        "source_url": "https://github.com/mcp-tools/youtube-transcript-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "youtube-transcript-mcp"]
        }
    },
    {
        "id": "hacker-news",
        "name": "Hacker News Discussions MCP",
        "description": "Fetch top stories, comments, ask HN, and latest tech discussions from Hacker News.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "🟧",
        "source_url": "https://github.com/mcp-tools/hackernews-mcp",
        "config": {
            "command": "uvx",
            "args": ["hackernews-mcp"]
        }
    },
    {
        "id": "reddit",
        "name": "Reddit Communities MCP",
        "description": "Browse subreddits, trending posts, discussions, and comment threads on Reddit.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "🤖",
        "source_url": "https://github.com/mcp-tools/reddit-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "reddit-mcp-server"]
        }
    },
    {
        "id": "rss-reader",
        "name": "RSS & Atom Feed Monitor MCP",
        "description": "Subscribe to, parse, and monitor RSS and Atom news feeds in real-time.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "📡",
        "source_url": "https://github.com/mcp-tools/rss-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["rss-mcp-server"]
        }
    },
    {
        "id": "wayback-machine",
        "name": "Wayback Machine Web Archive MCP",
        "description": "Inspect historical webpage archives and snapshots via the Internet Archive Wayback Machine.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "🏛️",
        "source_url": "https://github.com/mcp-tools/wayback-mcp",
        "config": {
            "command": "uvx",
            "args": ["wayback-mcp"]
        }
    },

    # ── 5. Productivity, Notes & Communication (66-80) ──
    {
        "id": "notion",
        "name": "Notion Workspace MCP",
        "description": "Read and write Notion workspace pages, databases, blocks, and properties.",
        "category": "Productivity & Notes",
        "author": "suekou",
        "icon": "📓",
        "source_url": "https://github.com/suekou/mcp-notion-server",
        "config": {
            "command": "npx",
            "args": ["-y", "@suekou/mcp-notion-server"],
            "env": {"NOTION_API_TOKEN": ""}
        }
    },
    {
        "id": "obsidian",
        "name": "Obsidian Vault Notes MCP",
        "description": "Read, search, create, and link markdown notes inside local Obsidian vaults.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "💎",
        "source_url": "https://github.com/mcp-tools/obsidian-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "obsidian-mcp-server"]
        }
    },
    {
        "id": "airtable",
        "name": "Airtable Bases MCP",
        "description": "Query, insert, and update records and schema tables in Airtable cloud bases.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "📊",
        "source_url": "https://github.com/mcp-tools/airtable-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "airtable-mcp-server"],
            "env": {"AIRTABLE_API_KEY": ""}
        }
    },
    {
        "id": "discord",
        "name": "Discord Bot & Channels MCP",
        "description": "Send messages, manage channels, and read server chat history via Discord Bot API.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "👾",
        "source_url": "https://github.com/mcp-tools/discord-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "discord-mcp-server"],
            "env": {"DISCORD_BOT_TOKEN": ""}
        }
    },
    {
        "id": "telegram",
        "name": "Telegram Bot MCP",
        "description": "Send messages, notifications, photos, and polls via Telegram Bot API.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "✈️",
        "source_url": "https://github.com/mcp-tools/telegram-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["telegram-mcp-server"],
            "env": {"TELEGRAM_BOT_TOKEN": ""}
        }
    },
    {
        "id": "todoist",
        "name": "Todoist Task Manager MCP",
        "description": "Manage personal tasks, projects, labels, deadlines, and priorities in Todoist.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "✅",
        "source_url": "https://github.com/mcp-tools/todoist-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "todoist-mcp-server"],
            "env": {"TODOIST_API_TOKEN": ""}
        }
    },
    {
        "id": "trello",
        "name": "Trello Kanban Boards MCP",
        "description": "Manage Trello boards, lists, cards, checklists, and project deadlines.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "📋",
        "source_url": "https://github.com/mcp-tools/trello-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "trello-mcp-server"]
        }
    },
    {
        "id": "asana",
        "name": "Asana Project Tracker MCP",
        "description": "Track tasks, projects, sections, and team workflows in Asana.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "🎯",
        "source_url": "https://github.com/mcp-tools/asana-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "asana-mcp-server"]
        }
    },
    {
        "id": "google-calendar",
        "name": "Google Calendar Scheduler MCP",
        "description": "Schedule events, query calendars, check availability, and manage meeting invites.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "📅",
        "source_url": "https://github.com/mcp-tools/google-calendar-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "@mcp/google-calendar"]
        }
    },
    {
        "id": "google-sheets",
        "name": "Google Sheets Data MCP",
        "description": "Read, write, format cells, and append rows in Google Sheets spreadsheets.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "📈",
        "source_url": "https://github.com/mcp-tools/google-sheets-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "@mcp/google-sheets"]
        }
    },
    {
        "id": "confluence",
        "name": "Atlassian Confluence MCP",
        "description": "Search corporate documentation, view spaces, and update pages on Atlassian Confluence.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "📘",
        "source_url": "https://github.com/mcp-tools/confluence-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "confluence-mcp-server"]
        }
    },
    {
        "id": "clickup",
        "name": "ClickUp Team Workspace MCP",
        "description": "Manage ClickUp tasks, spaces, lists, comments, and time tracking.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "⏰",
        "source_url": "https://github.com/mcp-tools/clickup-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "clickup-mcp-server"]
        }
    },
    {
        "id": "evernote",
        "name": "Evernote Notes MCP",
        "description": "Search notes, notebooks, tags, and update note content in Evernote.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "🐘",
        "source_url": "https://github.com/mcp-tools/evernote-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "evernote-mcp"]
        }
    },
    {
        "id": "zendesk",
        "name": "Zendesk Support Tickets MCP",
        "description": "Read customer support tickets, satisfaction scores, and post ticket updates in Zendesk.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "🎧",
        "source_url": "https://github.com/mcp-tools/zendesk-mcp-server",
        "config": {
            "command": "npx",
            "args": ["-y", "zendesk-mcp-server"]
        }
    },
    {
        "id": "intercom",
        "name": "Intercom Customer Messaging MCP",
        "description": "Manage customer conversations, user profiles, and intercom messaging tags.",
        "category": "Productivity & Notes",
        "author": "Community",
        "icon": "💬",
        "source_url": "https://github.com/mcp-tools/intercom-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "intercom-mcp"]
        }
    },

    # ── 6. Document Processing, Multimedia & Files (81-90) ──
    {
        "id": "pdf-tools",
        "name": "PDF Document Processor MCP",
        "description": "Extract text, tables, metadata, and split/merge PDF documents.",
        "category": "System & Files",
        "author": "Community",
        "icon": "📕",
        "source_url": "https://github.com/mcp-tools/mcp-server-pdf",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-pdf"]
        }
    },
    {
        "id": "pandoc",
        "name": "Pandoc Universal Document Converter MCP",
        "description": "Convert between dozens of document formats including Markdown, Docx, LaTeX, EPUB, and HTML.",
        "category": "System & Files",
        "author": "Community",
        "icon": "🔄",
        "source_url": "https://github.com/mcp-tools/pandoc-mcp",
        "config": {
            "command": "uvx",
            "args": ["pandoc-mcp"]
        }
    },
    {
        "id": "docx-reader",
        "name": "Word DOCX Parser MCP",
        "description": "Read and extract formatted paragraphs, headings, and tables from Word docx files.",
        "category": "System & Files",
        "author": "Community",
        "icon": "📝",
        "source_url": "https://github.com/mcp-tools/mcp-docx-server",
        "config": {
            "command": "uvx",
            "args": ["mcp-docx-server"]
        }
    },
    {
        "id": "excel-reader",
        "name": "Excel XLSX Spreadsheet MCP",
        "description": "Inspect, calculate, and query Microsoft Excel (.xlsx/.xls) workbooks and sheets.",
        "category": "System & Files",
        "author": "Community",
        "icon": "📗",
        "source_url": "https://github.com/mcp-tools/mcp-excel-server",
        "config": {
            "command": "uvx",
            "args": ["mcp-excel-server"]
        }
    },
    {
        "id": "csv-analyzer",
        "name": "CSV & TSV Data Analyzer MCP",
        "description": "Fast streaming query and aggregation engine for large CSV and TSV tabular files.",
        "category": "System & Files",
        "author": "Community",
        "icon": "📑",
        "source_url": "https://github.com/mcp-tools/csv-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["csv-mcp-server"]
        }
    },
    {
        "id": "image-resizer",
        "name": "Image Manipulation & Sharp MCP",
        "description": "Resize, crop, convert image formats, and compress photos with Sharp and Pillow.",
        "category": "System & Files",
        "author": "Community",
        "icon": "🖼️",
        "source_url": "https://github.com/mcp-tools/image-tools-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "image-tools-mcp"]
        }
    },
    {
        "id": "ffmpeg",
        "name": "FFmpeg Audio & Video Processor MCP",
        "description": "Transcode media formats, trim video clips, and extract audio streams with FFmpeg.",
        "category": "System & Files",
        "author": "Community",
        "icon": "🎬",
        "source_url": "https://github.com/mcp-tools/ffmpeg-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["ffmpeg-mcp-server"]
        }
    },
    {
        "id": "whisper-stt",
        "name": "Whisper Speech-to-Text MCP",
        "description": "Transcribe voice notes, podcasts, and video audio to text using OpenAI Whisper.",
        "category": "AI & Science",
        "author": "Community",
        "icon": "🎙️",
        "source_url": "https://github.com/mcp-tools/whisper-mcp",
        "config": {
            "command": "uvx",
            "args": ["whisper-mcp"]
        }
    },
    {
        "id": "exif-metadata",
        "name": "EXIF Photo Metadata MCP",
        "description": "Read, extract, and clean EXIF metadata and GPS tags from photos and videos.",
        "category": "System & Files",
        "author": "Community",
        "icon": "📷",
        "source_url": "https://github.com/mcp-tools/exif-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["exif-mcp-server"]
        }
    },
    {
        "id": "markdown-linter",
        "name": "Markdown Linter & Formatter MCP",
        "description": "Lint, format, clean broken links, and validate markdown documents automatically.",
        "category": "System & Files",
        "author": "Community",
        "icon": "✍️",
        "source_url": "https://github.com/mcp-tools/markdown-lint-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "markdown-lint-mcp"]
        }
    },

    # ── 7. AI, Reasoning & Science (91-100) ──
    {
        "id": "huggingface",
        "name": "Hugging Face Hub MCP",
        "description": "Explore HuggingFace models, datasets, spaces, and run serverless inference endpoints.",
        "category": "AI & Science",
        "author": "Hugging Face Community",
        "icon": "🤗",
        "source_url": "https://github.com/huggingface/huggingface-mcp",
        "config": {
            "command": "uvx",
            "args": ["huggingface-mcp"],
            "env": {"HF_TOKEN": ""}
        }
    },
    {
        "id": "replicate",
        "name": "Replicate AI Models MCP",
        "description": "Run cloud AI models for image generation, text, audio, and video synthesis on Replicate.",
        "category": "AI & Science",
        "author": "Replicate Community",
        "icon": "🧪",
        "source_url": "https://github.com/replicate/replicate-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "replicate-mcp"],
            "env": {"REPLICATE_API_TOKEN": ""}
        }
    },
    {
        "id": "ollama",
        "name": "Ollama Local LLM MCP",
        "description": "Interact with locally running Ollama LLM models, embeddings, and chat completions.",
        "category": "AI & Science",
        "author": "Community",
        "icon": "🦙",
        "source_url": "https://github.com/mcp-tools/ollama-mcp",
        "config": {
            "command": "uvx",
            "args": ["ollama-mcp"]
        }
    },
    {
        "id": "wolfram-alpha",
        "name": "Wolfram Alpha Computational MCP",
        "description": "Computational intelligence engine for advanced mathematics, physics, and scientific queries.",
        "category": "AI & Science",
        "author": "Community",
        "icon": "🧮",
        "source_url": "https://github.com/mcp-tools/wolfram-mcp",
        "config": {
            "command": "uvx",
            "args": ["wolfram-mcp"],
            "env": {"WOLFRAM_APP_ID": ""}
        }
    },
    {
        "id": "e2b-sandbox",
        "name": "E2B Cloud Code Sandbox MCP",
        "description": "Cloud execution sandbox for running untrusted code and full terminal environments safely.",
        "category": "Developer Tools",
        "author": "E2B",
        "icon": "📦",
        "source_url": "https://github.com/e2b-dev/e2b-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "@e2b/mcp-server"],
            "env": {"E2B_API_KEY": ""}
        }
    },
    {
        "id": "weather",
        "name": "OpenWeatherMap Live Forecast MCP",
        "description": "Real-time global weather conditions, forecasts, and radar alerts via OpenWeatherMap.",
        "category": "Search & Web",
        "author": "Community",
        "icon": "🌤️",
        "source_url": "https://github.com/mcp-tools/mcp-server-weather",
        "config": {
            "command": "uvx",
            "args": ["mcp-server-weather"]
        }
    },
    {
        "id": "stock-market",
        "name": "Stock Market & Equities MCP",
        "description": "Real-time stock prices, company financials, historical charts, and SEC filings.",
        "category": "AI & Science",
        "author": "Community",
        "icon": "📈",
        "source_url": "https://github.com/mcp-tools/stocks-mcp-server",
        "config": {
            "command": "uvx",
            "args": ["stocks-mcp-server"]
        }
    },
    {
        "id": "crypto-tracker",
        "name": "CoinGecko Crypto Tracker MCP",
        "description": "Live cryptocurrency prices, market cap, volume, and coin metrics via CoinGecko.",
        "category": "AI & Science",
        "author": "CoinGecko Community",
        "icon": "🪙",
        "source_url": "https://github.com/mcp-tools/coingecko-mcp",
        "config": {
            "command": "npx",
            "args": ["-y", "coingecko-mcp"]
        }
    },
    {
        "id": "shodan",
        "name": "Shodan Cybersecurity Intelligence MCP",
        "description": "Search internet-connected devices, open ports, IP intelligence, and security certificates.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🛡️",
        "source_url": "https://github.com/mcp-tools/shodan-mcp",
        "config": {
            "command": "uvx",
            "args": ["shodan-mcp"],
            "env": {"SHODAN_API_KEY": ""}
        }
    },
    {
        "id": "virustotal",
        "name": "VirusTotal Threat Analysis MCP",
        "description": "Scan URLs, IP addresses, domains, and file hashes for malware and threat intelligence.",
        "category": "Developer Tools",
        "author": "Community",
        "icon": "🦠",
        "source_url": "https://github.com/mcp-tools/virustotal-mcp",
        "config": {
            "command": "uvx",
            "args": ["virustotal-mcp"],
            "env": {"VIRUSTOTAL_API_KEY": ""}
        }
    }
]
