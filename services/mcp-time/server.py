from datetime import datetime
import pytz
from mcp.server.fastmcp import FastMCP  # Import the correct FastMCP module

# Initialize the FastMCP server
mcp = FastMCP("tashkent-time")

# Define the tool that returns the current time in Asia/Tashkent
@mcp.tool()
def get_tashkent_time() -> str:
    """Return the current date/time in Asia/Tashkent (ISO 8601)."""
    tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz).isoformat()

# Run the server (over stdio)
if __name__ == "__main__":
    mcp.run(transport="stdio")  # Ensure the server listens for connections over stdio
