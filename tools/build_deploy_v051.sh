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
    cp -n "$DEST/progress.bin" "$DEST/progress_before_051.bak" || true
fi
if [[ -f "$DEST/config.bin" ]]; then
    cp -n "$DEST/config.bin" "$DEST/config_before_051.bak" || true
fi

# Force only the generated files whose format/content changed.  Existing
# copyrighted converted assets are otherwise reused when the converter can.
rm -f assets/map[0-9][0-9][0-9]_vm.bin \
      assets/font_map.bin assets/font_page*.t8 \
      assets/common_vm.bin

echo "[1/5] Verifying parity anchors against the original RPG Maker data..."
python3 tools/verify_parity_v051.py "$GAME_PATH"

echo "[2/5] Rebuilding maps/VM/font with original-behaviour fixes..."
python3 tools/prepare_world_v051.py "$GAME_PATH" --out assets

echo "[3/5] Preparing only SE variants that exist in original RPG Maker events..."
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

# These files were introduced by the experimental v0.4 dry-surface footstep
# system.  v0.5.1 deliberately does not use them because the original NARAKU
# does not automatically play dry-floor footsteps.
rm -f "$DEST/assets/se_step_stone.pcm" "$DEST/assets/se_step_soft.pcm"

echo "Done: NARAKU PSP 0.5.1 parity/fix build deployed to:"
echo "  $DEST"
echo "Existing progress.bin/config.bin were preserved."
echo "PSP R shoulder remains the dash mapping; NARAKU maps have dashing enabled."
