#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
test -d "$DEST/assets"
# Keep installed sprite references and commands from earlier stages.
for src in "$DEST/assets"/map*_vm.bin "$DEST/assets/common_vm.bin"; do
    test -f "$src" || continue
    name="${src##*/}"
    test -f "$ROOT_DIR/assets/$name" || cp "$src" "$ROOT_DIR/assets/$name"
done
python3 "$ROOT_DIR/tools/update_window_styles_v174.py" "$ROOT_DIR/assets"
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text()
s,n=re.subn(r'(\bVERSION\s+)(?:00|01)\.\d+',r'\g<1>01.74',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu174"
cd "$ROOT_DIR/build_menu174"
psp-cmake ..
make -B -j"$(nproc)"
test -s EBOOT.PBP
while IFS= read -r name; do
    test -s "$ROOT_DIR/assets/$name"
    cp "$ROOT_DIR/assets/$name" "$DEST/assets/$name"
done < "$ROOT_DIR/assets_patch_174.txt"
for src in "$ROOT_DIR/assets"/map*_vm.bin "$ROOT_DIR/assets/common_vm.bin"; do
    test -f "$src" || continue
    cp "$src" "$DEST/assets/${src##*/}"
done
cp EBOOT.PBP "$DEST/EBOOT.PBP"
echo "NARAKU 1.7.4 original dialogue and choice window modes deployed. Load an in-game save after restarting."
