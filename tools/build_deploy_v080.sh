#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
test -d "$DEST/assets" || { echo "Deploy the complete game first: $DEST/assets is missing"; exit 1; }
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text();s,n=re.subn(r'(\bVERSION\s+)00\.\d+',r'\g<1>00.80',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu080"
cd "$ROOT_DIR/build_menu080"
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP
cp EBOOT.PBP "$DEST/EBOOT.PBP"
echo "NARAKU 0.8.0 deployed; assets, saves and XMB configuration preserved."
