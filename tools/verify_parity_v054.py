#!/usr/bin/env python3
import json, sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
map7 = root / "data" / "Map007.json"
if not map7.is_file():
    raise SystemExit(f"ERROR: game data not found under {root}")

data = json.loads(map7.read_text(encoding="utf-8"))
ev = data["events"][25]
if not ev or ev.get("name") != "出入口":
    raise SystemExit("ERROR: Map007 Event 25 parity anchor changed")

page = ev["pages"][0]
cmds = page["list"]

routes = []
transfer = None
for c in cmds:
    if c.get("code") == 201:
        transfer = c.get("parameters")
    if c.get("code") == 205:
        p = c.get("parameters") or []
        if len(p) >= 2 and p[0] == -1:
            route = p[1] or {}
            routes.append([
                (int(rc.get("code", 0)), rc.get("parameters") or [])
                for rc in (route.get("list") or [])
                if int(rc.get("code", 0)) != 0
            ])

expected_transfer = [0, 1, 8, 4, 0, 2]
if transfer != expected_transfer:
    raise SystemExit(f"ERROR: expected Map007 Event25 transfer {expected_transfer}, got {transfer}")

# Original sequence:
#   Through ON
#   Jump (0,+3)
#   Move Left -> Through OFF -> Change Speed 3
expected = [
    [(37, [])],
    [(14, [0, 3])],
    [(2, []), (38, []), (29, [3])],
]
if routes[:3] != expected:
    raise SystemExit(f"ERROR: corpse-pile slide route changed: {routes[:3]}")

print("Map007 Event25 transfer: Map001 (8,4)")
print("Forced-route sequence: Through ON -> Jump (0,+3) -> Left -> Through OFF -> Speed 3")
print("Cross-route Through persistence parity anchor: OK")
