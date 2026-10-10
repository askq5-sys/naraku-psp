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

mkdir -p "$DEST"
if [[ -f "$DEST/progress.bin" ]]; then
    cp -n "$DEST/progress.bin" "$DEST/progress_before_052.bak" || true
fi
if [[ -f "$DEST/config.bin" ]]; then
    cp -n "$DEST/config.bin" "$DEST/config_before_052.bak" || true
fi

# VM/assets are unchanged from 0.5.1, but rebuild them so the installed build
# is deterministic and parity checks run against the user's exact Steam copy.
rm -f assets/map[0-9][0-9][0-9]_vm.bin \
      assets/font_map.bin assets/font_page*.t8 \
      assets/common_vm.bin

echo "[1/5] Verifying original NARAKU movement-speed/parity anchors..."
python3 tools/verify_parity_v052.py "$GAME_PATH"

echo "[2/5] Rebuilding maps/VM/font..."
python3 tools/prepare_world_v051.py "$GAME_PATH" --out assets

echo "[3/5] Preparing original-event SE variants..."
python3 tools/prepare_audio_v051.py "$GAME_PATH" --out assets

echo "[4/5] Building PSP EBOOT.PBP..."
mkdir -p build
cd build
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP

echo "[5/5] Deploying to PPSSPP Memory Stick..."
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
for f in assets/pic_*.p44; do
    [[ -f "$f" ]] && cp "$f" "$DEST/assets/"
done
cp assets/se_bonecrush4.pcm \
   assets/se_water.pcm \
   assets/se_splash.pcm \
   assets/se_splash_step70.pcm \
   assets/se_splash_step120.pcm \
   assets/se_bonecrush4_100.pcm \
   "$DEST/assets/"
rm -f "$DEST/assets/se_step_stone.pcm" "$DEST/assets/se_step_soft.pcm"

echo "Done: NARAKU PSP 0.5.2 movement-speed parity hotfix deployed to:"
echo "  $DEST"
echo "Existing progress.bin/config.bin were preserved."
echo "NOTE: pre-0.5.2 saves did not store base move speed; for the cleanest parity test, start a new game once."
