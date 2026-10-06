# CLAUDE.md — project memory (auto-loaded by Claude Code every session)

> Teaching note (M06): this file = persistent context. Keep it SHORT, factual, imperative.
> Every line costs tokens every session. Put long reference material in skills (loaded on demand).

## What this repo is
Learning repo: AI engineering (harness, tools, MCP, loops, multi-agent, evals) using tiny roguelike **Ember Crypt**.
Owner = senior dev learning AI tooling. When asked to explain, be terse ("caveman" style: drop articles/filler, keep all technical detail), use analogies + code + ASCII diagrams.

## Commands
- Tests: `uv run pytest` (must stay green; harness tests use MockLLM, no model needed)
- Play: `uv run python -m game.play --level <name>`
- Bot playtest: `uv run python -m game.autoplay --level <name>`
- Balance: `uv run python -m game.balance --json`
- Local LLM scripts: `uv run python modules/<NN_x>/<script>.py` (Ollama must be running)

## Layout
- `game/` pure deterministic sim. `content.py` pydantic schemas = source of truth. `level.py` = validator.
- `lib/` mini agent framework (llm adapters, harness loop, tools, tracing, MCP bridge).
- `modules/NN_*/` lessons. `capstone/` pipeline. `.claude/` skills, hooks, agents. `.mcp.json` servers.

## Rules
- Game content (`game/data/*.json`) MUST validate. Use `mcp__ember__validate_level_json` / `propose_entity`, or run tests.
- Generated content goes to `game/data/generated/`, never overwrite `level_01.json`, `items.json`, `enemies.json` unless asked.
- Keep `game/` free of I/O and randomness (determinism = testability).
- Windows host: prefer PowerShell-compatible commands in docs; Python for scripts/hooks.
- Don't `git push`. Commit only when asked.
