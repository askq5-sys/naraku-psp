#!/usr/bin/env bash
set -euo pipefail

GAME_PATH="${1:-/mnt/d/SteamLibrary/steamapps/common/NARAKU}"
DEST="${2:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p assets

if [[ ! -f "$GAME_PATH/data/System.json" ]]; then
    echo "ERROR: RPG Maker game directory not found: $GAME_PATH"
    exit 1
fi

# Preserve the existing save and language settings. The new build may retain
# them as-is; a backup lets the user roll back without losing a playthrough.
if [[ -f "$DEST/progress.bin" ]]; then
    cp -n "$DEST/progress.bin" "$DEST/progress_before_050.bak" || true
fi
if [[ -f "$DEST/config.bin" ]]; then
    cp -n "$DEST/config.bin" "$DEST/config_before_050.bak" || true
fi

# Force fresh map bytecode: the Move Route payload changed in v0.5.0.
rm -f assets/map[0-9][0-9][0-9]_vm.bin \
      assets/font_map.bin assets/font_page*.t8 \
      assets/common_vm.bin

echo "[1/5] Maps 001-139, original pictures, common events, CJK font..."
python3 tools/prepare_world_v050.py "$GAME_PATH" --out assets

echo "[2/5] Footstep audio..."
python3 tools/prepare_audio_v040.py "$GAME_PATH" --out assets

echo "[3/5] Building PSP EBOOT.PBP..."
mkdir -p build
cd build
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP

echo "[4/5] Deploying directly to PPSSPP Memory Stick..."
mkdir -p "$DEST/assets"
cp EBOOT.PBP "$DEST/EBOOT.PBP"
cd "$ROOT_DIR"
cp assets/enri_atlas.rgba8888 "$DEST/assets/"
cp assets/map[0-9][0-9][0-9].bin "$DEST/assets/"
cp assets/map[0-9][0-9][0-9]_vm.bin "$DEST/assets/"
cp assets/map[0-9][0-9][0-9]_atlas*.rgba8888 "$DEST/assets/"
for f in assets/map[0-9][0-9][0-9]_event_atlas.rgba8888; do
    [[ -f "$f" ]] && cp "$f" "$DEST/assets/"
done
cp assets/font_map.bin assets/font_page*.t8 "$DEST/assets/"
cp assets/common_vm.bin "$DEST/assets/"
cp assets/pic_*.p44 "$DEST/assets/"
cp assets/se_step_stone.pcm assets/se_step_soft.pcm "$DEST/assets/"

echo "[5/5] Done. NARAKU PSP 0.5.0 staged at $DEST"
echo "NOTE: Existing progress.bin and config.bin have NOT been deleted."
echo "CONTROLS: PSP R shoulder = dash; PPSSPP settings -> Controls -> Control mapping."
