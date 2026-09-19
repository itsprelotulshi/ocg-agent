import datetime
import hashlib
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server instance
server = FastMCP("utility_server")


@server.tool()
def get_system_time(timezone_name: str = "UTC") -> str:
    """Get the current system date, time, and UTC timestamp."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"Current UTC Time: {now.isoformat()} (requested timezone: {timezone_name})"

@server.tool()
def compute_hash(text: str, algorithm: str = "sha256") -> str:
    """Compute a cryptographic hash (md5, sha1, sha256, sha512) for a given text."""
    algo = algorithm.lower().strip()
    if algo not in hashlib.algorithms_available:
        return f"Error: Unsupported algorithm '{algorithm}'. Available: sha256, md5, sha1, sha512"
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return f"{algorithm.upper()} digest: {h.hexdigest()}"

@server.tool()
def inspect_environment() -> str:
    """Inspect the local environment details, OS, and workspace paths."""
    return (
        f"OS: {os.name}\n"
        f"Current Directory: {os.getcwd()}\n"
        f"Files in directory: {', '.join(os.listdir('.'))[:300]}"
    )

if __name__ == "__main__":
    server.run(transport="stdio")
