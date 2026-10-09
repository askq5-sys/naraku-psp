#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
test -d "$DEST/assets" || { echo "Deploy the complete game first: $DEST/assets is missing"; exit 1; }
python3 - "$ROOT_DIR/CMakeLists.txt" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text();s,n=re.subn(r'(\bVERSION\s+)(?:00|01)\.\d+',r'\g<1>01.20',s,count=1)
if n:p.write_text(s)
PY
mkdir -p "$ROOT_DIR/build_menu120"
cd "$ROOT_DIR/build_menu120"
psp-cmake ..
make -B -j"$(nproc)"
test -s EBOOT.PBP
if ! cp EBOOT.PBP "$DEST/EBOOT.PBP"; then
    echo "Build succeeded, but deploy failed. Close PPSSPP and copy manually:"
    echo "$ROOT_DIR/build_menu120/EBOOT.PBP -> $DEST/EBOOT.PBP"
    exit 1
fi
for font_file in "$ROOT_DIR/assets/font_map.bin" "$ROOT_DIR"/assets/font_page*.t8; do
    test -s "$font_file" || { echo "Font patch asset missing: $font_file"; exit 1; }
    cp "$font_file" "$DEST/assets/$(basename "$font_file")"
done
cp "$ROOT_DIR/assets/pic_009.p44" "$DEST/assets/pic_009.p44"
cp "$ROOT_DIR/assets/ui_iconset.rgba4444" "$DEST/assets/ui_iconset.rgba4444"
for fall_file in map001_events.bin map001_event_atlas.rgba8888; do
    cp "$ROOT_DIR/assets/$fall_file" "$DEST/assets/$fall_file"
done
for text_file in "$ROOT_DIR"/assets/map*_vm.bin; do
    cp "$text_file" "$DEST/assets/$(basename "$text_file")"
done
for story_file in "$ROOT_DIR"/assets/map023_* "$ROOT_DIR"/assets/map012_* "$ROOT_DIR"/assets/map013_* "$ROOT_DIR"/assets/map026_* "$ROOT_DIR"/assets/map024_* "$ROOT_DIR"/assets/map025_* "$ROOT_DIR"/assets/*_exact_*.pcm; do
    case "$story_file" in *_preview.png) continue ;; esac
    test -f "$story_file" || continue
    cp "$story_file" "$DEST/assets/$(basename "$story_file")"
done
echo "NARAKU 1.2.0 deployed; assets, saves and XMB configuration preserved."
