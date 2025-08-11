from qwen_agent.agents import Assistant
from settings import HOST, PORT, API_KEY, MODEL_ID, TZ

def build_agent():
    llm_cfg = {
        "model": MODEL_ID,
        "model_server": f"http://{HOST}:{PORT}/v1",
        "api_key": API_KEY,
    }
    tools = [{
        "mcpServers": {
            "time": {"command": "uvx", "args": ["mcp-server-time", f"--local-timezone={TZ}"]},
            "fetch": {"command": "uvx", "args": ["mcp-server-fetch"]}
        }
    }, "code_interpreter"]
    return Assistant(llm=llm_cfg, function_list=tools)

def run_once(prompt: str):
    bot = build_agent()
    last = None
    for resp in bot.run(messages=[{"role": "user", "content": prompt}]):
        last = resp
    return last
