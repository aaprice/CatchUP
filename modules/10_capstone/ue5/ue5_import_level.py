"""Run INSIDE Unreal Editor (UE5.1+). Spawns grey-box of an Ember Crypt level from JSON.

Setup: Edit > Plugins > enable "Python Editor Script Plugin" (+ "Editor Scripting Utilities" on older 5.x). Restart.
Run:   Tools > Execute Python Script... > pick this file
   or  Output Log, switch "Cmd" to "Python":  exec(open(r"C:/Users/iamap/Development/ClaudeProjects/CatchUP/modules/10_capstone/ue5/ue5_import_level.py").read())
Undo:  Ctrl+Z (wrapped in a transaction) or re-run (clears 'Ember' folder first).

Untested against your exact UE version: if an API name errors, paste the error into Claude Code and let it fix
this script (good mini-loop exercise: Output Log = verifier).
"""
import json

import unreal

LEVEL_JSON = globals().get("LEVEL_JSON") or r"C:/Users/iamap/Development/ClaudeProjects/CatchUP/game/data/level_01.json"
TILE = 200.0        # cm per grid cell (UE units = cm)
WALL_H = 300.0
FOLDER = "Ember"

actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
load = unreal.EditorAssetLibrary.load_asset
CUBE = load("/Engine/BasicShapes/Cube.Cube")          # 100cm cube, pivot at center
CYL = load("/Engine/BasicShapes/Cylinder.Cylinder")
CONE = load("/Engine/BasicShapes/Cone.Cone")
SPHERE = load("/Engine/BasicShapes/Sphere.Sphere")


def spawn(mesh, x, y, z, sx, sy, sz, label, sub):
    a = actors.spawn_actor_from_object(mesh, unreal.Vector(x, y, z))
    a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
    a.set_actor_label(label)
    a.set_folder_path(f"{FOLDER}/{sub}")
    return a


with open(LEVEL_JSON, encoding="utf-8") as f:
    lv = json.load(f)

with unreal.ScopedEditorTransaction("Ember import"):
    for a in actors.get_all_level_actors():                      # clear previous import
        if str(a.get_folder_path()).startswith(FOLDER):
            actors.destroy_actor(a)
    rows = lv["map"]
    h, w = len(rows), len(rows[0])
    s = TILE / 100.0
    spawn(CUBE, (w - 1) * TILE / 2, (h - 1) * TILE / 2, -5, w * s, h * s, 0.1, "Floor", "Floor")
    for y, row in enumerate(rows):                               # UE: +X forward, +Y right -> grid y maps to +Y
        for x, ch in enumerate(row):
            wx, wy = x * TILE, y * TILE
            if ch == "#":
                spawn(CUBE, wx, wy, WALL_H / 2, s, s, WALL_H / 100, f"Wall_{x}_{y}", "Walls")
            elif ch == "D":
                spawn(CUBE, wx, wy, WALL_H / 2, s * 0.9, s * 0.3, WALL_H / 100 * 0.9, f"Door_{x}_{y}", "Doors")
            elif ch == "@":
                spawn(CYL, wx, wy, 5, s * 0.7, s * 0.7, 0.1, "PlayerStart_Marker", "Markers")
            elif ch == ">":
                spawn(CYL, wx, wy, 5, s * 0.8, s * 0.8, 0.1, "Exit_Marker", "Markers")
    for e in lv.get("enemies", []):
        spawn(CONE, e["x"] * TILE, e["y"] * TILE, 75, s * 0.6, s * 0.6, 1.5, f"Enemy_{e['id']}_{e['x']}_{e['y']}", "Enemies")
    for i in lv.get("items", []):
        spawn(SPHERE, i["x"] * TILE, i["y"] * TILE, 50, 0.6, 0.6, 0.6, f"Item_{i['id']}_{i['x']}_{i['y']}", "Items")

unreal.log(f"Ember import done: {lv['name']} {w}x{h}")
