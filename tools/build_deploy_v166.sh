#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
test -d "$DEST/assets"
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text()
s,n=re.subn(r'(\bVERSION\s+)(?:00|01)\.\d+',r'\g<1>01.66',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu166"
cd "$ROOT_DIR/build_menu166"
psp-cmake ..
make -B -j"$(nproc)"
test -s EBOOT.PBP
cp EBOOT.PBP "$DEST/EBOOT.PBP"
echo "NARAKU 1.6.6 rooftop horizontal framing adjustment deployed. Load an in-game save after restarting."
