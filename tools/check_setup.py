"""Environment check + model recommendation.  uv run python tools/check_setup.py"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.llm import load_env  # noqa: E402

load_env()
OK, BAD, WARN = "\033[32mOK\033[0m", "\033[31mMISSING\033[0m", "\033[33mWARN\033[0m"
if os.name == "nt":
    os.system("")


def run(cmd: list[str]) -> str | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return None


def main() -> None:
    print(f"python {sys.version.split()[0]}  {OK if sys.version_info >= (3, 11) else BAD + ' need 3.11+'}")
    for tool in ("git", "ollama", "claude", "node", "npx"):
        print(f"{tool:<8} {OK if shutil.which(tool) else BAD}")

    vram_gb = None
    smi = run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
    if smi:
        name, mem = [s.strip() for s in smi.splitlines()[0].split(",")]
        vram_gb = int(mem) / 1024
        print(f"GPU      {name} {vram_gb:.1f} GB")
    else:
        print(f"GPU      {WARN} nvidia-smi not found; CPU inference will be slow")

    rec = ("qwen3:4b" if not vram_gb or vram_gb < 7 else "qwen3:8b" if vram_gb < 15
           else "gpt-oss:20b" if vram_gb < 23 else "qwen3-coder:30b")
    print(f"recommended LLM_MODEL = {rec}   (current: {os.getenv('LLM_MODEL', 'qwen3:8b')})")

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        tags = json.loads(urllib.request.urlopen(f"{host}/api/tags", timeout=5).read())
        have = [m["name"] for m in tags.get("models", [])]
        print(f"ollama   {OK} server up; models: {have}")
        for want in (os.getenv("LLM_MODEL", "qwen3:8b"), os.getenv("EMBED_MODEL", "nomic-embed-text")):
            hit = any(h == want or h.split(":")[0] == want for h in have)
            print(f"  {want:<22} {OK if hit else BAD + f'  -> ollama pull {want}'}")
    except Exception as e:
        print(f"ollama   {BAD} server not reachable at {host} ({e}). Start Ollama app.")

    if shutil.which("claude"):
        print("claude   run `claude -p \"say hi\"` once to confirm Pro login works headless")


if __name__ == "__main__":
    main()
