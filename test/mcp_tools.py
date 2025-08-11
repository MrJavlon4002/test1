import subprocess, atexit
from settings import TZ

_procs = []

def start_mcp_tools():
    # Requires: pip install uv  (uses uvx to fetch official MCP reference servers)
    _procs.append(subprocess.Popen(["uvx", "mcp-server-time", f"--local-timezone={TZ}"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
    _procs.append(subprocess.Popen(["uvx", "mcp-server-fetch"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

def stop_mcp_tools():
    for p in _procs:
        if p.poll() is None:
            p.terminate()
    for p in _procs:
        try:
            p.wait(timeout=5)
        except Exception:
            p.kill()

atexit.register(stop_mcp_tools)
