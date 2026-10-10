#!/usr/bin/env bash
set -euo pipefail
GAME_PATH="${1:-/mnt/d/SteamLibrary/steamapps/common/NARAKU}"
DEST="${2:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "$GAME_PATH/data/Map001.json" ]]; then
  echo "ERROR: RPG Maker game directory not found: $GAME_PATH"; exit 1
fi
if [[ ! -d "$DEST/assets" ]]; then
  echo "ERROR: existing 0.5.x deployment not found: $DEST/assets"; exit 1
fi

echo "[1/4] Verifying original A1 / Lucas-fall parity anchors..."
python3 tools/verify_parity_v056.py "$GAME_PATH"

echo "[2/4] Regenerating only the two affected assets from your Steam copy..."
python3 tools/prepare_parity_v056.py "$GAME_PATH" --out assets

echo "[3/4] Building PSP EBOOT.PBP..."
mkdir -p build
cd build
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP
cd "$ROOT_DIR"

echo "[4/4] Deploying 0.5.6 hotfix..."
cp build/EBOOT.PBP "$DEST/EBOOT.PBP"
cp assets/a1_overlay.rgba8888 "$DEST/assets/a1_overlay.rgba8888"
cp assets/lucas_fall_atlas.rgba8888 "$DEST/assets/lucas_fall_atlas.rgba8888"

echo
echo "Done: NARAKU PSP 0.5.6 deployed to:"
echo "  $DEST"
echo "progress.bin and config.bin were not touched."
