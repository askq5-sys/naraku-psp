#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
for asset in ICON0.PNG PIC1.PNG SND0.AT3; do
  test -s "$ROOT_DIR/xmb/$asset" || { echo "Missing XMB asset: $asset"; exit 1; }
done
test -d "$DEST/assets" || { echo "Build/deploy the complete game first: $DEST/assets is missing"; exit 1; }
mkdir -p "$ROOT_DIR/build_xmb"
cd "$ROOT_DIR/build_xmb"
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP
cp EBOOT.PBP "$DEST/EBOOT.PBP"
echo "XMB icon, background and music embedded in $DEST/EBOOT.PBP"
