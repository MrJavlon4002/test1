import time
from threading import Thread
from server import start_vllm
from mcp_tools import start_mcp_tools
from agent_app import run_once

def _drain(name, proc):
    if not proc: return
    for line in iter(proc.stdout.readline, b""):
        if not line: break

if __name__ == "__main__":
    vllm_proc = start_vllm()
    Thread(target=_drain, args=("vllm", vllm_proc), daemon=True).start()
    time.sleep(3)

    start_mcp_tools()
    time.sleep(2)

    out = run_once("https://qwenlm.github.io/blog/ Introduce the latest developments of Qwen")
    print(out)
