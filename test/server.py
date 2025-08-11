import os, sys, subprocess, atexit
from settings import MODEL_ID, HOST, PORT, API_KEY, MAX_MODEL_LEN, TP_SIZE, REASONING_PARSER

_proc = None

def start_vllm():
    global _proc
    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL_ID,
        "--host", HOST, "--port", str(PORT),
        "--dtype", "auto",
        "--max-model-len", str(MAX_MODEL_LEN),
        "--tensor-parallel-size", str(TP_SIZE),
        "--api-key", API_KEY,
        "--reasoning-parser", REASONING_PARSER
    ]
    _proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return _proc

def stop_vllm():
    global _proc
    if _proc and _proc.poll() is None:
        _proc.terminate()
        _proc.wait()

atexit.register(stop_vllm)
