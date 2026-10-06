"""STRETCH (M05/M10) — MCP server driving UE5 editor through Remote Control API (HTTP, port 30010).

UE setup: enable plugins "Remote Control API" + "Python Editor Script Plugin", restart, open a level.
Remote Control web server starts with editor (check Output Log for 30010; console: WebControl.StartServer).
Register in Claude Code:  claude mcp add unreal -- uv run python modules/10_capstone/ue5/unreal_mcp_server.py

Pattern identical to blender bridge: MCP server outside engine, whitelisted calls into engine.
Untested against your UE version: if a call fails, have Claude Code read the error + UE Remote Control docs and fix.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from mcp.server.mcpserver import MCPServer  # noqa: E402

UE = "http://127.0.0.1:30010/remote/object/call"
PY_LIB = "/Script/PythonScriptPlugin.Default__PythonScriptLibrary"
IMPORTER = ROOT / "modules/10_capstone/ue5/ue5_import_level.py"
mcp = MCPServer("unreal", instructions="Drives Unreal Editor. Call ue_ping first.")


def call(object_path: str, function: str, params: dict) -> str:
    body = json.dumps({"objectPath": object_path, "functionName": function, "parameters": params,
                       "generateTransaction": True}).encode()
    req = urllib.request.Request(UE, data=body, method="PUT", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode() or "ok"
    except urllib.error.HTTPError as e:
        return f"ERROR HTTP {e.code}: {e.read().decode()[:400]}"
    except urllib.error.URLError as e:
        return f"ERROR: UE Remote Control not reachable ({e.reason}). Editor open + plugin enabled?"


def run_py(code: str) -> str:
    return call(PY_LIB, "ExecutePythonCommand", {"PythonCommand": code})


@mcp.tool()
def ue_ping() -> str:
    """Check Unreal Editor reachable (logs a line in UE Output Log)."""
    return run_py("import unreal; unreal.log('ember mcp ping')")


@mcp.tool()
def ue_import_level(level_name: str = "level_01") -> str:
    """Spawn grey-box of an Ember Crypt level in the open UE level (clears previous 'Ember' folder)."""
    p = ROOT / "game/data" / f"{level_name}.json"
    if not p.exists():
        p = ROOT / "game/data/generated" / f"{level_name}.json"
    if not p.exists():
        return f"ERROR: no level {level_name}"
    code = f"LEVEL_JSON=r'{p.as_posix()}'\nexec(open(r'{IMPORTER.as_posix()}').read())"
    return run_py(code)


if __name__ == "__main__":
    mcp.run()
