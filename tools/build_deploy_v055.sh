#!/usr/bin/env bash
set -euo pipefail

GAME_PATH="${1:-/mnt/d/SteamLibrary/steamapps/common/NARAKU}"
DEST="${2:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "$GAME_PATH/data/Map007.json" ]]; then
    echo "ERROR: RPG Maker game directory not found: $GAME_PATH"
    exit 1
fi
if [[ ! -d "$DEST/assets" ]]; then
    echo "ERROR: existing 0.5.x deployment not found: $DEST/assets"
    echo "Install any working 0.5.x build first, then apply this hotfix."
    exit 1
fi

echo "[1/3] Verifying original transparency / intro parity anchors..."
python3 tools/verify_parity_v055.py "$GAME_PATH"

echo "[2/3] Building PSP EBOOT.PBP..."
mkdir -p build
cd build
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP

echo "[3/3] Deploying hotfix EBOOT..."
cp EBOOT.PBP "$DEST/EBOOT.PBP"

echo
echo "Done: NARAKU PSP 0.5.5 transparency + intro parity hotfix deployed to:"
echo "  $DEST"
echo "Assets, config.bin and progress.bin were not touched."
