# SETUP (Windows 11, home PC)

All commands = PowerShell in `C:\Users\iamap\Development\ClaudeProjects\CatchUP` unless noted.

## 1. Core tools

```powershell
# Git (+ Git Bash; Claude Code on Windows uses it for shell + hooks)
winget install --id Git.Git -e
# uv = fast Python project/venv manager (replaces pip+venv+pyenv)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Node LTS (only for MCP Inspector in module 05)
winget install OpenJS.NodeJS.LTS
```

Restart terminal, then:

```powershell
git init -b main; git add -A; git commit -m "baseline"   # loops + worktrees need git (M07-08)
uv sync                                            # creates .venv, installs pydantic, mcp, pytest
uv run pytest                                      # expect all green
Copy-Item .env.example .env
```

## 2. Ollama + model choice

Check GPU VRAM — this decides model:

```powershell
nvidia-smi --query-gpu=name,memory.total --format=csv
uv run python tools/check_setup.py               # does checks below + recommends model
```

| VRAM | Chat/tool model (`LLM_MODEL`) | Notes |
|---|---|---|
| ≤ 6 GB | `qwen3:4b` | works; expect more tool-call mistakes (good teaching!) |
| 8–12 GB | `qwen3:8b` **(default)** | solid tool calling, ~fast |
| 16 GB | `gpt-oss:20b` or `qwen3:14b` | noticeably smarter agent loops |
| 24 GB+ | `qwen3-coder:30b` / `qwen3:32b` | near "small cloud model" feel |
| DGX at work | anything; serve via vLLM → `LLM_PROVIDER=openai` | M08 parallel fan-out shines |

Newer tags appear constantly — browse https://ollama.com/search?c=tools and swap via `.env`. Rule: Q4_K_M quant minimum for tool calling; below that, JSON/tool reliability drops before chat quality does.

```powershell
ollama pull qwen3:8b            # or your tier's pick
ollama pull nomic-embed-text    # embeddings for RAG (module 04), 274MB
ollama list
uv run python modules/01_raw_api/hello.py   # smoke test
```

**Context length gotcha:** Ollama default context is small (few K tokens) and *silently truncates* overflow. `lib/llm.py` sends `num_ctx=16384` per request (`OLLAMA_NUM_CTX` in `.env`). More context = more VRAM. If loops act amnesiac → context truncation is suspect #1.

## 3. Claude Code (uses your Pro login)

```powershell
irm https://claude.ai/install.ps1 | iex     # native installer
claude --version
claude                                      # first run → /login → choose Claude account (Pro)
```

Inside repo, `claude` auto-loads `CLAUDE.md`, `.claude/` (skills, hooks, agents) and `.mcp.json`. First launch asks to trust folder + approve MCP servers → approve `ember`.

Pro = usage windows (resets every ~5h) + weekly caps. Habits:
- `/model` → Sonnet for daily, Haiku for fan-out/loops, Opus sparingly.
- `/cost` or `/usage` to watch spend. `/clear` between unrelated tasks (cheaper + smarter).
- Loops (M07) always have `MAX_ITERS`.

Hooks in `.claude/settings.json` call `python`. Ensure `python --version` works in Git Bash (install Python via `uv python install 3.12` + add to PATH, or Microsoft Store Python). If your python is `py`, edit commands in `.claude/settings.json`.

## 4. Optional: Gemini free tier (smarter than local, still free)

1. https://aistudio.google.com/apikey → create key.
2. `.env`: `LLM_PROVIDER=openai`, `GEMINI_API_KEY=...`, `LLM_MODEL=gemini-flash-latest`.
3. Same code, different engine. That's the adapter pattern paying off.

Gemini CLI (`npm i -g @google/gemini-cli`) = Google's harness, same concepts as Claude Code. Module 05 plugs same MCP server into both.

## 5. Optional: engines

- **Blender** (4.2+): module 05 installs `ember_blender_addon.py` (Edit → Preferences → Add-ons → Install from Disk).
- **UE5**: module 10 stretch. Enable plugins *Python Editor Script Plugin* (+ *Remote Control API* for MCP route).
- **GameMaker**: module 10 exercise only (agent writes GML loader).

## 6. Sanity checklist

- [ ] `uv run pytest` green
- [ ] `uv run python modules/01_raw_api/hello.py` prints reply
- [ ] `claude -p "say hi"` prints reply (Pro login works headless)
- [ ] `ollama ps` shows model on GPU (`100% GPU`), not CPU
