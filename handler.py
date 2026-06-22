import time
import subprocess

import requests
import runpod

VLLM_PORT = 8000
BASE = f"http://127.0.0.1:{VLLM_PORT}/v1"

# --- Launch vLLM ONCE per cold start, with the exact args NuExtract3 needs ---
VLLM_CMD = [
    "vllm", "serve", "numind/NuExtract3",
    "--max-num-seqs", "8",
    "--max-model-len", "16384",
    "--trust-remote-code",
    "--chat-template-content-format", "openai",
    "--generation-config", "vllm",
    "--limit-mm-per-prompt", '{"image":6,"video":0}',
    "--gpu-memory-utilization", "0.90",
    "--download-dir", "/runpod-volume/models",
    "--host", "127.0.0.1",
    "--port", str(VLLM_PORT),
]

_proc = subprocess.Popen(VLLM_CMD)


def _wait_ready(timeout=900):
    """Block until the local vLLM server reports healthy (or time out)."""
    url = f"http://127.0.0.1:{VLLM_PORT}/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url, timeout=2).status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    raise RuntimeError("vLLM failed to start within timeout")


_wait_ready()


def handler(event):
    """Forward an OpenAI-style chat-completions payload to the local vLLM server.

    Expected event["input"]:
      {"messages": [...], "max_tokens": 2048, ...}  (standard OpenAI chat request)
    """
    payload = event["input"]
    payload.setdefault("model", "numind/NuExtract3")
    r = requests.post(f"{BASE}/chat/completions", json=payload, timeout=600)
    r.raise_for_status()
    return r.json()


runpod.serverless.start({"handler": handler})
