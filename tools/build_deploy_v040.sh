#!/usr/bin/env bash
set -euo pipefail

GAME_PATH="${1:-/mnt/d/SteamLibrary/steamapps/common/NARAKU}"
DEST="${2:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"
mkdir -p assets

# Remove only generated world/runtime assets. Keep intro/audio resources created
# by earlier stages because v0.4.0 still uses them for the opening sequence.
rm -f assets/map[0-9][0-9][0-9].bin \
      assets/map[0-9][0-9][0-9]_vm.bin \
      assets/map[0-9][0-9][0-9]_atlas*.rgba8888 \
      assets/map[0-9][0-9][0-9]_event_atlas.rgba8888 \
      assets/font_map.bin assets/font_page*.t8 \
      assets/world_v040_manifest.json

echo "[1/5] Preparing all Maps 001-139 + v0.4 event VM + runtime font + surfaces..."
python3 tools/prepare_world_v040.py "$GAME_PATH" --out assets

echo "[2/5] Preparing footsteps..."
python3 tools/prepare_audio_v040.py "$GAME_PATH" --out assets

echo "[3/5] Building EBOOT.PBP..."
mkdir -p build
cd build
rm -rf ./*
psp-cmake ..
make -j"$(nproc)"

echo "[4/5] Deploying to PPSSPP Memory Stick..."
mkdir -p "$DEST/assets"
cp EBOOT.PBP "$DEST/EBOOT.PBP"
cd "$ROOT_DIR"

cp assets/enri_atlas.rgba8888 "$DEST/assets/"
cp assets/map[0-9][0-9][0-9].bin "$DEST/assets/"
cp assets/map[0-9][0-9][0-9]_vm.bin "$DEST/assets/"
cp assets/map[0-9][0-9][0-9]_atlas*.rgba8888 "$DEST/assets/"
cp assets/map[0-9][0-9][0-9]_event_atlas.rgba8888 "$DEST/assets/" 2>/dev/null || true
cp assets/font_map.bin "$DEST/assets/"
cp assets/font_page*.t8 "$DEST/assets/"
cp assets/se_step_stone.pcm assets/se_step_soft.pcm "$DEST/assets/"

echo "[5/5] Done."
echo "PPSSPP game: $DEST/EBOOT.PBP"
echo "Maps prepared: 001-139"
echo "R: run (MZ dash speed)"
echo "SELECT in game: temporary language menu"
echo "Hold SELECT during boot: choose language"
echo "Hold TRIANGLE during boot: clear progress"
