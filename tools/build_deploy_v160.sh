#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
test -d "$DEST/assets"
while IFS= read -r asset; do
  test -s "$ROOT_DIR/assets/$asset"
done < "$ROOT_DIR/assets_patch_160.txt"
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text()
s,n=re.subn(r'(\bVERSION\s+)(?:00|01)\.\d+',r'\g<1>01.60',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu160"
cd "$ROOT_DIR/build_menu160"
psp-cmake ..
make -B -j"$(nproc)"
test -s EBOOT.PBP
cp EBOOT.PBP "$DEST/EBOOT.PBP"
while IFS= read -r asset; do
  cp "$ROOT_DIR/assets/$asset" "$DEST/assets/$asset"
done < "$ROOT_DIR/assets_patch_160.txt"
echo "NARAKU 1.6.0 counter interactions deployed. Load an in-game save after restarting."
