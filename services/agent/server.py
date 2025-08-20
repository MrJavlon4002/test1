import os
from fastapi import FastAPI
from pydantic import BaseModel

from pydantic_ai import Agent, Tool
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://vllm:8000/v1")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "token-abc123")

provider = OpenAIProvider(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
model = OpenAIModel("qwen3-30b-a3b-instruct-fp8", provider=provider)

USE_MCP = os.getenv("USE_MCP", "true").lower() == "true"
ENABLE_AIRBNB = os.getenv("ENABLE_AIRBNB", "false").lower() == "true"
LOCAL_TZ = os.getenv("LOCAL_TIMEZONE", "Asia/Tashkent")

toolsets = []

# Step 4: custom tool (use when USE_MCP=false)
@Tool
def get_current_date() -> str:
    """Return the current date/time as 'YYYY-MM-DD HH:MM:SS'."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 5: MCP time server (use when USE_MCP=true)
if USE_MCP:
    time_server = MCPServerStdio(
        "python",
        args=["-m", "mcp_server_time", f"--local-timezone={LOCAL_TZ}"],
    )
    toolsets.append(time_server)

# Step 6: Airbnb MCP (optional)
if ENABLE_AIRBNB:
    airbnb_server = MCPServerStdio(
        "npx", args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"]
    )
    toolsets.append(airbnb_server)

system_prompt = """
You are a helpful travel & utilities agent.

Tools:
- get_current_time(params: dict) via MCP time server (or local get_current_date if MCP disabled)
- airbnb_search(params: dict) and airbnb_listing_details(params: dict) if Airbnb MCP is enabled

For date/time questions, call the time tool first.
For Airbnb queries, first get the current time, then airbnb_search, then airbnb_listing_details if needed.
"""

if USE_MCP:
    agent = Agent(model=model, toolsets=toolsets, system_prompt=system_prompt)
else:
    agent = Agent(model=model, tools=[get_current_date], system_prompt=system_prompt)

class RunBody(BaseModel):
    prompt: str

app = FastAPI()

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/run")
async def run(body: RunBody):
    async with agent:
        result = await agent.run(body.prompt)
    return {"response": result.data}
