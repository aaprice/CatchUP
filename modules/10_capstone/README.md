# M10 — Capstone: "Ember Crypt: One Level", built by agents

Goal: integrate everything. You direct; agents build; verifiers gate; you ship one polished level + engine blockout.

## Pipeline

```
 pitch ─► [studio: multi-agent] ─► new enemies/items/lore
               │
               ▼
          [forge: gen→verify→critic loop] ─► level JSON
               │
               ▼
          [GATES: validator · bot playtest · balance]  ── fail ──► loop again / fix with Claude Code
               │ pass
               ▼
   play in terminal · Blender blockout (MCP) · UE5 grey-box (Python / Remote Control) · REPORT.md
```
`capstone/build.py` = **workflow** (code-sequenced) wrapping **agents** (LLM inside each step). Deterministic skeleton, agentic muscles.

## Run (local track — free)

```powershell
uv run python capstone/build.py --pitch "frost-bitten crypt wing where the Long Winter never ended" --name frost_wing
uv run python -m game.play --level frost_wing
type capstone\REPORT_frost_wing.md
```

## Run (Claude Code track — Pro)

Same pipeline, but you drive with skills/subagents/MCP, interactive:
```
claude
> Read capstone/build.py to understand our pipeline. Then, WITHOUT running it, do the same with your own tools:
  1) design 2 new enemies + 1 item for theme "fungal ossuary" (validate via ember MCP, save to game/data/generated/enemies_fungal.json / items_fungal.json)
  2) /level-forge "fungal ossuary 18x10 using the new enemies, locked door" fungal_ossuary
  3) qa-verifier subagent on fungal_ossuary
  4) build it in Blender, render preview, look at it, add 4 props for atmosphere, render again
  5) write capstone/REPORT_fungal_ossuary.md
```
Compare with local track: quality, iterations, your interventions, usage spent.

## Engines

**Blender:** add-on from M05 running → `uv run python capstone/build.py ... --blender`, or via Claude Code `blender` MCP.

**Unreal Engine 5:**
1. Plugins: *Python Editor Script Plugin* (+ *Remote Control API* for MCP route). Restart editor.
2. Direct: Tools → Execute Python Script → `modules/10_capstone/ue5/ue5_import_level.py` (edit `LEVEL_JSON` path first).
3. Agent route: `claude mcp add unreal -- uv run python modules/10_capstone/ue5/unreal_mcp_server.py` → "import frost_wing into unreal".
4. Stretch: ask Claude Code to extend importer: point lights at braziers, PlayerStart actor at `@`, nav mesh bounds volume.

**GameMaker (exercise):** agent writes `ember_room_loader` GML script: reads level JSON (`json_parse` on file contents) at room start, `instance_create_layer` walls/doors/enemies by grid × 32px. Give Claude Code your GM project folder (`GameMakerProjects/...`), let it create script + objects, you run in GM. Verifier = you playing.

## Assignment (rubric — grade yourself, or `/tutor 10 review`)

| Criterion | Bar |
|---|---|
| Level passes all gates | validator ✓, bot wins w/ ≥5 hp, no balance flags |
| Uses ≥2 agent-made enemies + 1 item | from studio, lore-consistent |
| Loop evidence | trace shows ≥1 failed iteration fixed by feedback |
| Eval evidence | levelgen funnel + shopkeeper eval numbers before/after one change you made |
| Harness evidence | one hook or skill YOU wrote that caught a real problem |
| Engine | Blender render PNG or UE5 screenshot of blockout |
| Write-up | REPORT: what agents did well, where they failed, what verifier saved you |

## Level-ups after capstone

- Swap Ollama for DGX-served bigger model (`LLM_PROVIDER=openai`, vLLM) → rerun evals. Data-driven model choice.
- Turn `.claude/` + `.mcp.json` into plugin; use it in a real work repo (OneSAF scenario files? Same pattern: schemas + validator + MCP + loop).
- Port shopkeeper NPC into UE5/GameMaker at runtime calling Ollama HTTP — real LLM NPC in an engine.
- Read: Anthropic *Building Effective Agents*; Claude Code docs (hooks, skills, subagents); MCP spec; Hamel Husain on evals; Geoffrey Huntley on Ralph; Addy Osmani on loop engineering.

Done? Tick PROGRESS.md. You're caught up.
