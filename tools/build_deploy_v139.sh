#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
test -d "$DEST/assets" || { echo "Install the complete game and patch 1.3.8 first."; exit 1; }
while IFS= read -r name; do
    test -s "$ROOT_DIR/assets/$name" || { echo "Missing patch asset: $name"; exit 1; }
done < "$ROOT_DIR/assets_patch_139.txt"
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text()
s,n=re.subn(r'(\bVERSION\s+)(?:00|01)\.\d+',r'\g<1>01.39',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu139"
cd "$ROOT_DIR/build_menu139"
psp-cmake ..
make -B -j"$(nproc)"
test -s EBOOT.PBP
if ! cp EBOOT.PBP "$DEST/EBOOT.PBP"; then
    echo "Build succeeded. Close PPSSPP and run this script again to deploy."
    exit 1
fi
while IFS= read -r name; do
    cp "$ROOT_DIR/assets/$name" "$DEST/assets/$name"
done < "$ROOT_DIR/assets_patch_139.txt"
echo "NARAKU 1.3.9 deployed. Saves and configuration preserved."
