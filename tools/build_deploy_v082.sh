#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
test -d "$DEST/assets" || { echo "Deploy the complete game first: $DEST/assets is missing"; exit 1; }
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text();s,n=re.subn(r'(\bVERSION\s+)00\.\d+',r'\g<1>00.82',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu082"
cd "$ROOT_DIR/build_menu082"
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP
if ! cp EBOOT.PBP "$DEST/EBOOT.PBP"; then
    echo "Build succeeded, but deploy failed. Close PPSSPP and copy manually:"
    echo "$ROOT_DIR/build_menu082/EBOOT.PBP -> $DEST/EBOOT.PBP"
    exit 1
fi
echo "NARAKU 0.8.2 deployed; assets, saves and XMB configuration preserved."
