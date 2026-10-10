#!/usr/bin/env bash
set -euo pipefail
GAME_PATH="${1:-/mnt/d/SteamLibrary/steamapps/common/NARAKU}"
DEST="${2:-/mnt/c/Users/Rgood/Documents/PPSSPP/PSP/GAME/NARAKU}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "$GAME_PATH/data/Map001.json" || ! -f "$GAME_PATH/data/CommonEvents.json" ]]; then
  echo "ERROR: NARAKU game directory not found: $GAME_PATH"; exit 1
fi
mkdir -p assets "$DEST/assets"

echo "[1/6] Verifying original NARAKU menu/title/options anchors..."
python3 tools/verify_parity_v060.py "$GAME_PATH"

echo "[2/6] Refreshing parity assets (A1 + Fog A1 + Lucas fall)..."
python3 tools/verify_parity_v056.py "$GAME_PATH"
python3 tools/prepare_parity_v056.py "$GAME_PATH" --out assets

echo "[3/6] Preparing 0.7.7 title / inventory / save-load / options assets..."
python3 tools/prepare_ui_v060.py "$GAME_PATH" --out assets

echo "[4/6] Rebuilding event VM for 0.7.7..."
if [[ -f assets/map139.bin && -f assets/map139_events.bin && -f assets/font_map.bin && -f assets/enri_atlas.rgba8888 ]]; then
  echo "  Existing 0.5.x world detected: using fast VM-only migration."
  python3 tools/prepare_vm_v060.py "$GAME_PATH" --out assets
else
  echo "  Complete world assets not found: doing one full 001-139 conversion."
  python3 tools/prepare_world_v060.py "$GAME_PATH" --out assets
  echo "  Refreshing page-aware early event atlases after full conversion."
  python3 tools/prepare_vm_v060.py "$GAME_PATH" --out assets
fi

echo "[5/6] Building PSP EBOOT.PBP..."
rm -rf build
mkdir build
cd build
psp-cmake ..
make -j"$(nproc)"
test -s EBOOT.PBP
cd "$ROOT_DIR"

echo "[6/6] Deploying NARAKU PSP 0.7.7..."
cp build/EBOOT.PBP "$DEST/EBOOT.PBP"

# Core VM/font/world assets.  Existing 0.5.x world files stay in place during
# the fast path; only bytecode/pictures/UI are replaced.
cp assets/common_vm.bin "$DEST/assets/"
cp assets/map???_vm.bin "$DEST/assets/"
cp assets/font_map.bin assets/font_page*.t8 "$DEST/assets/" 2>/dev/null || true
cp assets/pic_*.p44 "$DEST/assets/" 2>/dev/null || true
cp assets/picture_v050_manifest.json "$DEST/assets/" 2>/dev/null || true
cp assets/picture_v060_manifest.json "$DEST/assets/" 2>/dev/null || true
cp assets/a1_overlay.rgba8888 assets/fog_a1.rgba8888 assets/lucas_fall_atlas.rgba8888 assets/lucas_corpse.rgba8888 assets/key_anim.rgba8888 "$DEST/assets/"
cp assets/ui060.bin assets/ui_iconset.rgba4444 "$DEST/assets/"
cp assets/title_*.rgba8888 "$DEST/assets/"

# 0.7.7 rebuilds page-aware event atlases for the story-critical early maps
# even on the fast migration path.
for n in $(seq -f "%03g" 1 20); do
  cp "assets/map${n}_events.bin" "$DEST/assets/" 2>/dev/null || true
  cp "assets/map${n}_event_atlas.rgba8888" "$DEST/assets/" 2>/dev/null || true
done

cp assets/bgm_title.pcm assets/se_menu_open.pcm assets/se_decision1.pcm assets/se_decision2.pcm \
   assets/se_cancel2.pcm assets/se_cursor2.pcm assets/se_ui_cursor.pcm assets/se_ui_ok.pcm \
   assets/se_ui_cancel.pcm assets/se_ui_buzzer.pcm assets/se_ui_save.pcm assets/se_ui_load.pcm \
   assets/se_evasion1.pcm assets/se_slime_fall.pcm assets/se_se7.pcm \
   assets/se_water.pcm assets/se_water_70_80.pcm assets/se_water_50_80.pcm \
   assets/se_splash.pcm assets/se_splash_step70.pcm assets/se_splash_step120.pcm assets/se_splash_20_70.pcm \
   assets/se_switch1.pcm assets/se_switch2.pcm assets/se_monitor.pcm assets/se_open9.pcm \
   assets/se_gate1.pcm assets/se_gate2.pcm assets/se_sword5.pcm assets/se_hit_axe3.pcm \
   assets/se_bonecrush5.pcm assets/se_equip2.pcm assets/se_slash7.pcm assets/se_blow2.pcm \
   assets/se_monster5.pcm assets/se_hatch_slide.pcm \
   "$DEST/assets/"

# Full conversion fallback created/updated these as well.
if [[ -f assets/map139.bin ]]; then
  cp assets/map???.bin "$DEST/assets/" 2>/dev/null || true
  cp assets/map???_events.bin "$DEST/assets/" 2>/dev/null || true
  cp assets/map???_atlas*.rgba8888 "$DEST/assets/" 2>/dev/null || true
  cp assets/map???_event_atlas.rgba8888 "$DEST/assets/" 2>/dev/null || true
  cp assets/enri_atlas.rgba8888 "$DEST/assets/" 2>/dev/null || true
  cp assets/font_map.bin assets/font_page*.t8 "$DEST/assets/" 2>/dev/null || true
fi

# Migration only: preserve the user's 0.5.x current progress by exposing it as
# File 1 the first time 0.7.7 is installed.  Never overwrite an existing slot.
if [[ -f "$DEST/progress.bin" && ! -e "$DEST/save01.bin" ]]; then
  cp "$DEST/progress.bin" "$DEST/save01.bin"
  echo "  Migrated old progress.bin -> save01.bin (original file preserved)."
fi

echo
echo "Done: NARAKU PSP 0.7.7 deployed to:"
echo "  $DEST"
echo "config.bin and old progress.bin were preserved."
echo "Map menu: CIRCLE (RPG Maker cancel/menu input)."
echo "R Trigger: dash; X: confirm/action."
