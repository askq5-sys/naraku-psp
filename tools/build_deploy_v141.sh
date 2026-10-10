#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
test -d "$DEST/assets"
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text()
s,n=re.subn(r'(\bVERSION\s+)(?:00|01)\.\d+',r'\g<1>01.41',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu141"
cd "$ROOT_DIR/build_menu141"
psp-cmake ..
make -B -j"$(nproc)"
test -s EBOOT.PBP
cp EBOOT.PBP "$DEST/EBOOT.PBP"
cp "$ROOT_DIR/assets/map041.bin" "$DEST/assets/map041.bin"
echo "NARAKU 1.4.1 puzzle timeout fix deployed. Load an in-game save after restarting."
