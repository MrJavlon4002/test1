# vLLM + Qwen3-30B-A3B (FP8) + MCP (Tashkent time) + Open WebUI

## Prereqs
1) NVIDIA driver + CUDA on host, and NVIDIA Container Toolkit installed  
   - https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
2) Docker + Docker Compose
3) (Optional) export HF_TOKEN

## Start
cp .env.example .env  # and edit if needed
docker compose up -d --build

- vLLM API:    http://localhost:8000/v1  (api key: token-abc123)
- Open WebUI:  http://localhost:3000

## Test vLLM
curl http://localhost:8000/v1/models
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer token-abc123" -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-30b-a3b-thinking-fp8",
    "messages": [{"role":"user","content":"Say hello"}],
    "max_tokens": 256
  }'

## About Qwen3 “Thinking”
- FP8 variant: Qwen/Qwen3-30B-A3B-Thinking-2507-FP8 (262k ctx).  
  See Qwen docs for thinking/non-thinking toggles via `chat_template_kwargs`.  
  Example: `"extra_body": {"chat_template_kwargs": {"enable_thinking": true}}`  
