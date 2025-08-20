# vLLM + PydanticAI Agent (MCP) + Open WebUI
GPU-served LLM with vLLM, a lightweight PydanticAI agent that launches MCP tools (time server; optional Airbnb), and Open WebUI for chatting with the model.
Model: Qwen/Qwen3-30B-A3B-Instruct-2507-FP8
Tooling: PydanticAI MCPServerStdio (uses official mcp-server-time; optional @openbnb/mcp-server-airbnb)
UI: Open WebUI (speaks OpenAI API to vLLM directly)
Client (browser) ──> Open WebUI ──> vLLM (OpenAI API)
                      ^
                      |
               (optional) You can also call the agent directly
                           Agent (PydanticAI) ──> MCP servers (time, airbnb...)
Repo Structure
./
├─ docker-compose.yml
└─ services/
   └─ agent/
      ├─ Dockerfile
      ├─ requirements.txt
      └─ app.py
Prerequisites
NVIDIA GPU with recent drivers
Docker and Docker Compose
nvidia-container-toolkit configured so containers can see the GPU
Optional: a Hugging Face token (HF_TOKEN) if the model requires it
Host timezone assumed: Asia/Tashkent (configurable).
Quick Start
Clone & Configure
## optional if you need HF auth
export HF_TOKEN=hf_xxx
Build & Run
docker compose up -d --build
Verify services
## vLLM OpenAI API
curl -sS -H "Authorization: Bearer token-abc123" http://localhost:8000/v1/models

## Agent (PydanticAI + MCP)
curl -sS http://localhost:8081/healthz

## Open WebUI (UI on :3000)
curl -sS -I http://localhost:3000/
Open your browser: http://<HOST_IP>:3000 (e.g. http://68.183.196.39:3000)
Environment Variables (compose)
OPENAI_BASE_URL – where the agent calls the model (defaults to http://vllm:8000/v1)
OPENAI_API_KEY – vLLM API key (defaults to token-abc123)
USE_MCP – true to use MCP time tool, false to use local @Tool (Step 4 vs Step 5)
ENABLE_AIRBNB – true to enable Airbnb MCP via npx
LOCAL_TIMEZONE – e.g. Asia/Tashkent
HF_TOKEN – (on vllm) for model downloads if needed
Port Map
Service	Port (Host)	Purpose
vLLM	8000	OpenAI-compatible API
Agent	8081	Minimal HTTP wrapper for agent
Open WebUI	3000	Web UI
Expose only what you need in your firewall/security group.
Using the Services
1) vLLM (raw OpenAI API)
List models
curl -sS -H "Authorization: Bearer token-abc123" http://<HOST_IP>:8000/v1/models
Chat completion
curl -sS -X POST http://<HOST_IP>:8000/v1/chat/completions \
  -H "Authorization: Bearer token-abc123" -H "Content-Type: application/json" \
  -d '{
    "model":"qwen3-30b-a3b-instruct-fp8",
    "temperature":0,
    "max_tokens":64,
    "messages":[{"role":"user","content":"Say hello from vLLM."}]
  }'
Tool-calling demo (2-round flow)
When the model calls a tool, it returns empty content and a tool_calls array. You must execute the tool and send its result back in a second request.
Round 1 — ask:
RESP=$(curl -sS -X POST http://<HOST_IP>:8000/v1/chat/completions \
  -H "Authorization: Bearer token-abc123" -H "Content-Type: application/json" \
  -d '{
    "model":"qwen3-30b-a3b-instruct-fp8",
    "messages":[
      {"role":"system","content":"Emit exactly one tool call and nothing else."},
      {"role":"user","content":"What is the current Tashkent time?"}
    ],
    "tools":[{"type":"function","function":{"name":"get_current_time","parameters":{"type":"object","properties":{}}}}],
    "tool_choice":{"type":"function","function":{"name":"get_current_time"}}
  }')
echo "$RESP"
You’ll see:
"message":{"content":"","tool_calls":[{"id":"chatcmpl-tool-...","function":{"name":"get_current_time","arguments":"{}"}}]}
Round 2 — execute tool yourself and return result:
CALL_ID=$(echo "$RESP" | jq -r '.choices[0].message.tool_calls[0].id')
TOOL_RESULT=$(TZ=Asia/Tashkent date -Iseconds)

curl -sS -X POST http://<HOST_IP>:8000/v1/chat/completions \
  -H "Authorization: Bearer token-abc123" -H "Content-Type: application/json" \
  -d '{
    "model":"qwen3-30b-a3b-instruct-fp8",
    "messages":[
      {"role":"system","content":"Emit exactly one tool call and nothing else."},
      {"role":"user","content":"What is the current Tashkent time?"},
      {"role":"assistant","tool_calls":[{"id":"'"$CALL_ID"'","type":"function","function":{"name":"get_current_time","arguments":"{}"}}]},
      {"role":"tool","tool_call_id":"'"$CALL_ID"'","content":"\"'"$TOOL_RESULT"'\""}
    ]
  }'
Now you’ll get a natural-language answer.
2) Agent (PydanticAI + MCP)
The agent wraps all of that orchestration for you.
Health
curl -sS http://<HOST_IP>:8081/healthz
Ask for date/time (uses MCP time server if USE_MCP=true)
curl -sS -X POST http://<HOST_IP>:8081/run \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What’s the date today?"}'
(Optional) Airbnb search
Enable ENABLE_AIRBNB=true in docker-compose.yml, rebuild, then:
curl -sS -X POST http://<HOST_IP>:8081/run \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Find a place to stay in Vancouver for next Sunday for 3 nights for 2 adults\"}"
3) Open WebUI
Browse to http://<HOST_IP>:3000.
It’s already configured to use http://vllm:8000/v1 and DEFAULT_MODEL=qwen3-30b-a3b-instruct-fp8.
Configuration Notes
Model & memory: This Qwen3 30B FP8 model is large; ensure GPU VRAM is sufficient. Tune --gpu-memory-utilization and --max-model-len if needed.
Downloads: First launch will download weights to the hf-cache volume. Keep it persistent for faster restarts.
Timezone: LOCAL_TIMEZONE defaults to Asia/Tashkent for the MCP time tool.
Node.js: Only required if you enable the Airbnb MCP (the agent image installs Node 18).
Troubleshooting
Empty assistant content when tool-calling: This is expected. The model only requests a tool; your code must run it and send a role:"tool" message back (the agent service does this for you).
401/403 from vLLM: Ensure OPENAI_API_KEY in clients matches --api-key on vLLM.
Can’t reach vLLM from host: Check firewall; port 8000 must be open if you call it externally.
WebUI hitting wrong backend: Env vars are set in compose; if you changed ports, update OPENAI_API_BASE_URL.
GPU not visible: Confirm nvidia-container-toolkit is installed and Docker runtime can access GPUs (gpus: all).
Model not loading: Provide HF_TOKEN and verify the model name/branch. Check container logs.
Production Tips
Auth: Put vLLM/Agent behind a reverse proxy (e.g., Nginx/Caddy) with TLS and auth; avoid exposing raw ports publicly.
Resource limits: Pin CPU/memory in Compose if co-hosting services.
Autosave WebUI: Set ENABLE_PERSISTENT_CONFIG=true if you want UI settings saved across restarts.
Updates: Rebuild periodically to pick up vllm-openai and WebUI improvements.
Extend with More MCP Servers (Weather – Step 7)
Add another MCP server exactly like Airbnb:
## in services/agent/app.py
from pydantic_ai.mcp import MCPServerStdio

if os.getenv("ENABLE_WEATHER","false").lower()=="true":
    weather_server = MCPServerStdio("npx", args=["-y","@vendor/mcp-server-weather"])
    toolsets.append(weather_server)
Update system_prompt to instruct the agent to check weather before suggesting dates.
Then set ENABLE_WEATHER=true and rebuild.
Stop / Restart / Reset
## stop
docker compose down

## stop & remove volumes (clears model cache/data)
docker compose down -v

## restart
docker compose up -d --build
