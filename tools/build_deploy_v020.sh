#!/usr/bin/env bash
set -euo pipefail

GAME_PATH="${1:-/mnt/d/SteamLibrary/steamapps/common/NARAKU}"
DEST="${2:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/4] Preparing Maps 001-030..."
python3 tools/prepare_world_v020.py "$GAME_PATH" --out assets

echo "[2/4] Building EBOOT.PBP..."
mkdir -p build
cd build
rm -rf ./*
psp-cmake ..
make -j"$(nproc)"

echo "[3/4] Deploying to PPSSPP Memory Stick..."
mkdir -p "$DEST/assets"
cp EBOOT.PBP "$DEST/EBOOT.PBP"
cd "$ROOT_DIR"
cp assets/enri_atlas.rgba8888 "$DEST/assets/"
cp assets/map*.bin "$DEST/assets/"
cp assets/map*_atlas*.rgba8888 "$DEST/assets/"
cp assets/map*_event_atlas.rgba8888 "$DEST/assets/" 2>/dev/null || true
cp assets/m*_e*_*.rgba8888 "$DEST/assets/" 2>/dev/null || true

echo "[4/4] Done."
echo "PPSSPP game: $DEST/EBOOT.PBP"
echo "Hold SELECT during boot: choose language"
echo "Hold TRIANGLE during boot: clear progress"
echo "SELECT in game: temporary language menu"
